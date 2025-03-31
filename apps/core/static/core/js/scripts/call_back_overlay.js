import {
  showErrorValidation,
  getCookie,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";
import { successModal } from "/static/core/js/sucessModal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".motrum-slider-requsites");
  if (wrapper) {
    const videos = document.querySelectorAll(".slider_video");
    if (videos.length > 0) {
      const video1 = document.querySelector(".video_1");

      video1.onclick = () => {
        window.location.href = "/cobots/";
      };
      const video2 = document.querySelector(".video_2");

      video2.onclick = () => {
        window.location.href = "/marking/";
      };

      const video3 = document.querySelector(".video_3");

      video3.onclick = () => {
        window.location.href = "/solutions/";
      };
    }

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

    const circlePhoneIcon = wrapper.querySelector(".circle");
    const phoneIconImg = circlePhoneIcon.querySelector("img");

    phoneButton.onmouseover = () => {
      phoneIconImg.classList.add("rotate");
    };

    phoneButton.onmouseout = () => {
      phoneIconImg.classList.remove("rotate");
    };

    phoneButton.onclick = () => {
      ym(37794920, "reachGoal", "open_callback_overlay");
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
          phone: mask.unmaskedValue,
          url: window.location.href,
        };
        const data = JSON.stringify(dataObj);

        setPreloaderInButton(submitBtn);

        fetch("/api/v1/core/forms/send-form-callback/", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        }).then((response) => {
          if (response.status >= 200 && response.status < 300) {
            ym(37794920, "reachGoal", "send_callback_form");
            closeOverlay();
            hidePreloaderAndEnabledButton(submitBtn);
            successModal(
              "Спасибо за заявку, мы свяжемся с вами в ближайшее время"
            );
          } else {
            setErrorModal();
          }
        });
      }
    };
  }
});
