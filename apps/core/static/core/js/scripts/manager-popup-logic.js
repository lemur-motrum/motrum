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
  const managerPopUp = document.querySelector(".personal-manager-container");
  if (managerPopUp) {
    const overlay = managerPopUp.querySelector(".manager_callback_overlay");
    const openOverlayBtn = managerPopUp.querySelector(".open_overlay_btn");
    const closeOverlayBtn = overlay.querySelector(".close_btn");

    setTimeout(() => {
      managerPopUp.classList.add("visible");
    }, 3000);

    function openOverlay() {
      overlay.classList.add("show");
      setTimeout(() => {
        overlay.classList.add("visible");
      });
    }

    function closeOverlay() {
      overlay.classList.remove("visible");
      setTimeout(() => {
        overlay.classList.remove("show");
      }, 600);
      const inputs = modalWindow.querySelectorAll("input");
      inputs.forEach((el) => {
        if (el) {
          el.value = "";
        }
      });
      const textArea = modalWindow.querySelector("textarea");
      textArea.value = "";
    }

    openOverlayBtn.onclick = () => openOverlay();
    closeOverlayBtn.onclick = () => closeOverlay();

    const modalWindow = overlay.querySelector(".modal_window");
    const nameInput = modalWindow.querySelector(".name_input");
    const nameError = modalWindow.querySelector(".name_error");
    const phoneInput = modalWindow.querySelector(".phone_input");
    const phoneError = modalWindow.querySelector(".phone_error");
    const textArea = modalWindow.querySelector(".form_textarea");
    const messageError = modalWindow.querySelector(".message_error");
    const submitBtn = modalWindow.querySelector(".submit_btn");

    const phoneMask = phoneInput ? IMask(phoneInput, maskOptions) : "";

    submitBtn.onclick = () => {
      const validate = formValidate();
      let endpoint;
      let data;

      if (validate) {
        setPreloaderInButton(submitBtn);
        if (submitBtn.getAttribute("type-btn") == "no_manager") {
          endpoint = "/api/v1/core/forms/send-form-equipment-selection/";

          const dataObj = {
            name: nameInput.value,
            message: textArea.value ? textArea.value : "",
            url: window.location.href,
            phone: phoneMask.unmaskedValue,
          };

          data = JSON.stringify(dataObj);
        }
        if (submitBtn.getAttribute("type-btn") == "manager_true") {
          const clientIdInput = document.querySelector("#client_id");
          const clientId = clientIdInput.getAttribute("data-user-id");
          const managerId = submitBtn.getAttribute("manager-id");

          endpoint = "/api/v1/core/forms/send-form-personal-manager/";

          const dataObj = {
            message: textArea.value,
            url: window.location.href,
            clientId: clientId,
            managerId: managerId,
          };

          data = JSON.stringify(dataObj);
        }

        fetch(endpoint, {
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
            successModal(
              "Спасибо за заявку, мы свяжемся с вами в ближайшее время"
            );
          } else {
            setErrorModal();
          }
        });
      }
    };

    function formValidate() {
      let validate = true;
      if (nameInput) {
        if (!nameInput.value) {
          validate = false;
          showErrorValidation("Обязательное поле", nameError);
        }
      }
      if (phoneInput) {
        if (!phoneInput.value) {
          validate = false;
          showErrorValidation("Обязательное поле", phoneError);
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          validate = false;
          showErrorValidation("Некорректный номер", phoneError);
        }
      }
      if (!nameInput || !phoneInput) {
        if (!textArea.value) {
          validate = false;
          showErrorValidation("Обязательное поле", messageError);
        }
      }
      return validate;
    }
  }
});
