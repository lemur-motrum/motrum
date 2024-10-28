import { getCookie, showErrorValidation } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const specificationWrapper = document.querySelector(
    ".all_specifications_table"
  );
  if (specificationWrapper) {
    const overlay = document.querySelector(".overlay_modal_complete");
    const modalWindow = overlay.querySelector(".modal-window");
    const calendar = modalWindow.querySelector(".calendar");
    const addOrderButton = modalWindow.querySelector(".complete_order_button");
    const error = modalWindow.querySelector(".error");

    const csrfToken = getCookie("csrftoken");
    const interval = setInterval(() => {
      const specifications = specificationWrapper.querySelectorAll(
        ".specification_item"
      );
      if (specifications.length > 0) {
        clearInterval(interval);
        specifications.forEach((specification) => {
          const completeBtn = specification.querySelector(
            ".complete_order_button"
          );
          const orderId = specification.getAttribute("order-id");
          completeBtn.onclick = () => {
            overlay.classList.add("show");
            document.body.style.overflowY = "hidden";
            setTimeout(() => {
              overlay.classList.add("visible");
            }, 600);
          };
          addOrderButton.onclick = () => {
            if (!calendar.value) {
              showErrorValidation("Поле календаря не заполнено", error);
            }
            if (calendar.value) {
              addOrderButton.disabled = true;
              addOrderButton.textContent = "";
              addOrderButton.innerHTML = "<div class='small_loader'></div>";

              const objData = {
                date_completed: calendar.value,
              };
              const data = JSON.stringify(objData);
              fetch(`/api/v1/order/${orderId}/add-date-completed/`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken,
                },
                body: data,
              }).then((response) => {
                if (response.status == 200) {
                  overlay.classList.remove("visible");
                  if (overlay.classList.contains("show")) {
                    document.body.style.overflowY = "scroll";
                  }
                  setTimeout(() => {
                    overlay.classList.remove("show");
                    const currentDate = new Date().toISOString().slice(0, 10);
                    calendar.value = currentDate;
                  }, 600);
                  console.log("ок");
                  addOrderButton.disabled = false;
                  addOrderButton.innerHTML = "";
                  addOrderButton.textContent = "Завершить заказ";
                }
              });
            }
          };
        });
      }
    });

    overlay.onclick = () => {
      overlay.classList.remove("visible");
      if (overlay.classList.contains("show")) {
        document.body.style.overflowY = "scroll";
      }
      setTimeout(() => {
        overlay.classList.remove("show");
        const currentDate = new Date().toISOString().slice(0, 10);
        calendar.value = currentDate;
      }, 600);
    };
    modalWindow.onclick = (e) => {
      e.stopPropagation();
    };
  }
});
