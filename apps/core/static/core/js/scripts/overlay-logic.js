import {
  showErrorValidation,
  getCookie,
  maskOptions,
} from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const enterBtn = document.querySelector(".enter-in-site");
  if (enterBtn) {
    const overlay = document.querySelector(".overlay");

    if (overlay) {
      const autificationForm = overlay.querySelector(".autification-form");
      const phoneInput = autificationForm.querySelector(".phone-input");
      const pinInput = autificationForm.querySelector(".password-input");
      const maskPinOptions = {
        mask: "0000",
        lazy: false,
        overwrite: "shift",
      };

      let amountTime = 119;
      let errorsQuantity = 2;

      function timer() {
        const timer = autificationForm.querySelector(".timer");
        let minutes = Math.floor(amountTime / 60);
        let seconds = amountTime % 60;

        if (seconds < 10) {
          seconds = "0" + seconds;
        }
        if (minutes < 10) {
          minutes = "0" + minutes;
        }
        timer.textContent = `${minutes}:${seconds}`;
        amountTime--;

        if (amountTime < 0) {
          stopTimer();
          amountTime = 0;
          window.location.reload();
        }
        function stopTimer() {
          clearInterval();
        }
      }

      const phoneMask = IMask(phoneInput, maskOptions);
      const pinMask = IMask(pinInput, maskPinOptions);

      const button = autificationForm.querySelector(".autification-button");
      const phoneError = autificationForm.querySelector(".phone-error");
      const pinError = autificationForm.querySelector(".pin-error");
      const pinLabel = autificationForm.querySelector(".password-label");
      const mobHeader = document.querySelector(".user-navigation");
      const burgerMenuNav = document.querySelector(".burger_menu_nav ");

      const privatePolicyContainer = autificationForm.querySelector(
        ".private_policy_container"
      );
      const checkZone = privatePolicyContainer.querySelector(
        ".checked_radio_button"
      );
      const privatePolicyError = autificationForm.querySelector(
        ".privacy_policy_error"
      );

      checkZone.onclick = () => {
        checkZone.classList.toggle("check");
      };

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
          if (checkZone.classList.contains("check")) {
            checkZone.classList.remove("check");
          }
        };
      };
      overlay.querySelector(".modal-window").onclick = (e) => {
        e.stopPropagation();
      };

      button.onclick = (e) => {
        let validate = true;
        e.preventDefault();
        if (!phoneInput.value) {
          validate = false;
          showErrorValidation("Введите номер телефона", phoneError);
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          validate = false;
          showErrorValidation("Введите корректный номер телефона", phoneError);
        }
        if (!checkZone.classList.contains("check")) {
          validate = false;
          showErrorValidation("Требуется согласие", privatePolicyError);
        }

        if (validate) {
          const phone = phoneMask.unmaskedValue;

          const dataArr = {
            phone: phone,
            pin: "",
            first_name: "",
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
                setInterval(timer, 1000);
                button.style.display = "none";
                pinLabel.classList.add("show");
                pinInput.oninput = () => {
                  const arrayPinInputValue = pinInput.value.split("");
                  const validateValue = +arrayPinInputValue[3];
                  if (!isNaN(validateValue)) {
                    pinInput.disabled = true;
                    const dataArr = {
                      phone: phone,
                      pin: pinInput.value,
                      first_name: "",
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
                          window.location.reload(true);
                        }
                        if (response.status == 200) {
                          console.log("Вы вошли");
                          window.location.reload(true);
                        }
                        if (response.status == 400) {
                          if (errorsQuantity == 0) {
                            showErrorValidation(
                              "Повторите после перезагрузки",
                              pinError
                            );
                            window.location.reload();
                          } else {
                            showErrorValidation(
                              `Некорректный Пин-код, осталось попыток ${errorsQuantity}`,
                              pinError
                            );
                            pinInput.value = null;
                            setTimeout(() => {
                              pinInput.disabled = false;
                            }, 1000);
                          }
                          errorsQuantity -= 1;
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
