import {
  showErrorValidation,
  getCookie,
  getDigitsNumber,
} from "/static/core/js/functions.js";
export function changePayment(container, errorFn) {
  if (container) {
    const overlay = document.querySelector(".change_of_payment_overlay");
    const modalWindow = overlay.querySelector(".modal-window");
    const paymentInput = modalWindow.querySelector(".payment_input");
    const paymentError = modalWindow.querySelector(".payment_error");
    const paymentChangeButton = modalWindow.querySelector(
      ".change-payment-btn"
    );

    const interval = setInterval(() => {
      const specifications = container.querySelectorAll(".table_item");
      if (specifications.length > 0) {
        clearInterval(interval);
        specifications.forEach((specification) => {
          const paymentLink = specification.querySelector(
            ".price_bill_sum_paid"
          );
          if (paymentLink) {
            getDigitsNumber(
              paymentLink,
              +paymentLink.getAttribute("bill-sum-paid")
            );
          }
          const paymentBtn = specification.querySelector(".add_payment_button");

          const orderId = specification.getAttribute("order-id");

          function changePayment() {
            paymentBtn.disabled = true;
            paymentBtn.textContent = "";
            paymentBtn.innerHTML = "<div class='small_loader'></div>";

            let finishPromice = false;
            let csrfToken = getCookie("csrftoken");
            fetch(`/api/v1/order/${orderId}/get-payment/`, {
              method: "GET",
              headers: {
                "X-CSRFToken": csrfToken,
              },
            })
              .then((response) => {
                if (response.status == 200) {
                  return response.json();
                } else {
                  throw new Error("Ошибка");
                }
              })
              .then((response) => {
                paymentInput.setAttribute("summ-pay", response.sum_pay);
                finishPromice = true;
              });
            const promiceModalInteval = setInterval(() => {
              if (finishPromice) {
                clearInterval(promiceModalInteval);
                overlay.classList.add("show");
                document.body.style.overflowY = "hidden";
                setTimeout(() => {
                  overlay.classList.add("visible");
                }, 600);
                paymentInput.addEventListener("input", function () {
                  let currentValue = this.value
                    .replace(",", ".")
                    .replace(/[^.\d]+/g, "")
                    .replace(/^([^\.]*\.)|\./g, "$1")
                    .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
                      return a + b + c.slice(0, 2);
                    });
                  if (currentValue > +paymentInput.getAttribute("summ-pay")) {
                    currentValue = +paymentInput.getAttribute("summ-pay");
                  }
                  paymentInput.value = currentValue;
                });

                paymentChangeButton.onclick = () => {
                  if (!paymentInput.value) {
                    errorFn("Поле не заполнено", paymentError);
                  } else {
                    paymentChangeButton.disabled = true;
                    paymentChangeButton.textContent = "";
                    paymentChangeButton.innerHTML =
                      "<div class='small_loader'></div>";
                    const objData = {
                      bill_sum_paid: paymentInput.value,
                    };
                    const data = JSON.stringify(objData);

                    fetch(`/api/v1/order/${orderId}/save-payment/`, {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                      },
                      body: data,
                    })
                      .then((response) => {
                        if (response.status == 200) {
                          return response.json();
                        } else {
                          throw new Error("Ошибка");
                        }
                      })
                      .then((response) => {
                        paymentBtn.classList.add("changed");
                        if (paymentLink.textContent === "0") {
                          paymentLink.setAttribute(
                            "bill-sum-paid",
                            paymentInput.value
                          );
                          getDigitsNumber(
                            paymentLink,
                            +paymentLink.getAttribute("bill-sum-paid")
                          );
                        } else {
                          const count =
                            +paymentLink.getAttribute("bill-sum-paid") +
                            +paymentInput.value;
                          paymentLink.setAttribute("bill-sum-paid", count);
                          getDigitsNumber(
                            paymentLink,
                            +paymentLink.getAttribute("bill-sum-paid")
                          );
                        }
                        const addBillBtn = specification.querySelector(
                          ".create-bill-button"
                        );
                        if (addBillBtn) {
                          addBillBtn.style.display = "none";
                        }

                        overlay.classList.remove("visible");
                        if (overlay.classList.contains("show")) {
                          document.body.style.overflowY = "scroll";
                        }

                        setTimeout(() => {
                          overlay.classList.remove("show");
                          paymentInput.value = "";
                        }, 600);
                        paymentChangeButton.disabled = false;
                        paymentChangeButton.innerHTML = "";
                        paymentChangeButton.textContent = "Внести";

                        const intevalChangeBtn = setInterval(() => {
                          const changedBtn =
                            specification.querySelector("changed");
                          if (changedBtn) {
                            clearInterval(intevalChangeBtn);
                            changedBtn.onclick = () => changePayment();
                          }
                        });
                        paymentBtn.disabled = false;
                        paymentBtn.innerHTML = "";
                        paymentBtn.textContent = "Внести cумму оплаты";
                        console.log(response.is_all_sum);
                        if (response.is_all_sum == true) {
                          paymentBtn.style.display = "none";
                        }
                      });
                  }
                };
              }
            });
          }
          if (paymentBtn) {
            paymentBtn.onclick = () => changePayment();
          }

          overlay.onclick = () => {
            document.querySelectorAll(".add_payment_button").forEach((el) => {
              el.disabled = false;
              el.innerHTML = "";
              el.textContent = "Внести cумму";
            });
            overlay.classList.remove("visible");
            if (overlay.classList.contains("show")) {
              document.body.style.overflowY = "scroll";
            }
            setTimeout(() => {
              overlay.classList.remove("show");
              paymentInput.value = "";
            }, 600);
          };
          modalWindow.onclick = (e) => {
            e.stopPropagation();
          };
        });
      }
    });
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(
    ".all_specifications_table"
  );
  changePayment(specificationContainer, showErrorValidation);
});
