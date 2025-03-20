import {
  showErrorValidation,
  getCookie,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".motrum-slider-requsites");
  if (wrapper) {
    const phoneButton = wrapper.querySelector(".phone-button");
    const callBackOverlay = document.querySelector(".overlay_callback");
    const closeBtn = callBackOverlay.querySelector(".close_btn");
    const modalWindow = callBackOverlay.querySelector(".modal_window");
    const nameInput = modalWindow.querySelector(".name_input");
    const nameError = modalWindow.querySelector(".name_error");
    const phoneInput = modalWindow.querySelector(".phone_input");
    const phoneError = modalWindow.querySelector(".phone_error");
    const submitBtn = modalWindow.querySelector(".submit_btn");

    const mask = IMask(phoneInput, maskOptions);

    phoneButton.onclick = () => {
      callBackOverlay.classList.add("show");
      setTimeout(() => {
        callBackOverlay.classList.add("visible");
      }, 600);
      document.body.style.overflowY = "hidden";
    };

    closeBtn.onclick = () => closeOverlay();

    function closeOverlay() {
      callBackOverlay.classList.remove("visible");
      setTimeout(() => {
        callBackOverlay.classList.remove("show");
      }, 600);
      nameInput.value = "";
      phoneInput.value = "";
      document.body.style.overflowY = "auto";
    }

    function validateForm() {
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
        showErrorValidation("Некорректный номер", phoneError);
        validate = false;
      }
      return validate;
    }

    submitBtn.onclick = () => {
      const val = validateForm();
      if (val) {
        const dataObj = {
          name: nameInput.value,
          phone: phoneInput.value,
        };
        const data = JSON.stringify(dataObj);

        setPreloaderInButton(submitBtn);

        fetch("", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        }).then((response) => {
          if (response.status >= 200 && response.status < 300) {
            closeOverlay();
            hidePreloaderAndEnabledButton(submitBtn);
          } else {
            setErrorModal();
          }
        });
      }
    };
  }
});
