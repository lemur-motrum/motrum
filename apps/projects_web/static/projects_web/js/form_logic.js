import {
  showErrorValidation,
  maskOptions,
  getCookie,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "../../../../core/static/core/js/functions.js";

import { setErrorModal } from "../../../../core/static/core/js/error_modal.js";
import { successModal } from "../../../../core/static/core/js/sucessModal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const formWrapper = document.querySelector(".project_one_form");
  if (formWrapper) {
    const form = formWrapper.querySelector(".project_one_submiting_form");
    const nameInput = formWrapper.querySelector(".name_input");
    const nameError = formWrapper.querySelector(".name_error");
    const phoneInput = formWrapper.querySelector(".phone_input");
    const phoneError = formWrapper.querySelector(".phone_error");
    const btn = form.querySelector("button");

    const mask = IMask(phoneInput, maskOptions);

    function validate() {
      let validate = true;
      if (!nameInput.value) {
        showErrorValidation("Обязательное поле", nameError);
        validate = false;
      }
      if (!phoneInput.value) {
        showErrorValidation("Обязательное поле", phoneError);
        validate = false;
      }
      if (phoneInput.value && phoneInput.value.length < 18) {
        showErrorValidation("Некорректный номер телефона", phoneError);
        validate = false;
      }
      return validate;
    }

    function resetInputs() {
      phoneInput.value = "";
      nameInput.value = "";
    }

    form.onsubmit = (e) => {
      let val = validate();
      e.preventDefault();
      if (val) {
        const dataObj = {
          name: nameInput.value,
          phone: mask.unmaskedValue,
          url: window.location.href,
        };
        const data = JSON.stringify(dataObj);

        setPreloaderInButton(btn);

        fetch("/api/v1/core/forms/send-form-calculate-project/", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status >= 200 && response.status < 300) {
              ym(37794920, "reachGoal", "send_form_calculate_project");
              resetInputs();
              hidePreloaderAndEnabledButton(btn);
              successModal(
                "Спасибо за заявку, мы свяжемся с вами в ближайшее время"
              );
            } else {
              setErrorModal();
            }
          })
          .catch((error) => console.error(error));
      }
    };
  }
});
