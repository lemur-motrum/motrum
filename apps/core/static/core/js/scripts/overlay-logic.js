import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const enterBtn = document.querySelector(".enter-in-site");
  if (enterBtn) {
    const overlay = document.querySelector(".overlay");
    console.log(overlay);
    if (overlay) {
      const autificationForm = overlay.querySelector(".autification-form");
      const phoneInput = autificationForm.querySelector(".phone-input");
      const maskPhoneOptions = {
        mask: "+{7} (000) 000-00-00",
        prepare: function (appended, masked) {
          if (appended === "8" && masked.value === "") {
            return "7";
          }
          return appended;
        },
      };

      const pinInput = autificationForm.querySelector(".password-input");
      const maskPinOptions = {
        mask: "0000",
        lazy: false,
        overwrite: "shift",
      };

      const phoneMask = IMask(phoneInput, maskPhoneOptions);
      const pinMask = IMask(pinInput, maskPinOptions);

      const button = autificationForm.querySelector(".autification-button");

      const phoneError = autificationForm.querySelector(".phone-error");
      const pinError = autificationForm.querySelector(".pin-error");

      const pinLabel = autificationForm.querySelector(".password-label");
      const mobHeader = document.querySelector(".user-navigation");
      const burgerMenuNav = document.querySelector(".burger_menu_nav ");

      enterBtn.onclick = () => {
        if (mobHeader.classList.contains("show")) {
          mobHeader.classList.remove("show");
          burgerMenuNav.classList.remove("checked");
        }
        overlay.classList.add("show");
        if (overlay.classList.contains("show")) {
          document.body.style.overflow = "hidden";
        }
        setTimeout(() => {
          overlay.classList.add("visible");
        });

        overlay.onclick = () => {
          overlay.classList.remove("visible");
          if (overlay.classList.contains("show")) {
            document.body.style.overflowY = "scroll";
          }
          setTimeout(() => {
            overlay.classList.remove("show");
          }, 600);
          autificationForm.reset();
          pinLabel.classList.remove("show");
          button.style.display = "flex";
        };
      };
      overlay.querySelector(".modal-window").onclick = (e) => {
        e.stopPropagation();
      };

      button.onclick = (e) => {
        e.preventDefault();
        if (!phoneInput.value) {
          showErrorValidation("Введите номер телефона", phoneError);
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          showErrorValidation("Введите корректный номер телефона", phoneError);
        }
        if (phoneInput.value.length == 18) {
          const phone = phoneMask.unmaskedValue;

          const dataArr = {
            phone: phone,
            pin: "",
          };
          const data = JSON.stringify(dataArr);
          fetch("/api/v1/client/login/", {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              response.json();
              if (response.status == 200) {
                button.style.display = "none";
                pinLabel.classList.add("show");
                pinInput.onkeyup = () => {
                  if (pinInput.value.length == 4) {
                    const dataArr = {
                      phone: phone,
                      pin: pinInput.value,
                    };
                    const data = JSON.stringify(dataArr);
                    fetch("/api/v1/client/login/", {
                      method: "POST",
                      body: data,
                      headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                      },
                    })
                      .then((response) => {
                        response.json();
                        if (response.status == 201) {
                          console.log("Новый Клиент");
                          window.location.reload();
                        }
                        if (response.status == 200) {
                          console.log("Вы вошли");
                          window.location.reload();
                        }
                        if (response.status == 400) {
                          showErrorValidation("Некорректный Пин-код", pinError);
                        }
                        if (response.status == 403) {
                          console.log("Вы заблокированы");
                        }
                      })
                      .catch((error) => console.error(error));
                  }
                };
              }
            })
            .catch((error) => console.error(error));
        }
      };
    }
  }
});
