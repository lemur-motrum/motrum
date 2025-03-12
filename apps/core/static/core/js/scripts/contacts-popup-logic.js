import { version } from "/static/core/js/scripts/version.js";

const { showErrorValidation, isEmailValid } = await import(
  `/static/core/js/functions.js?ver=${version}`
);

window.addEventListener("DOMContentLoaded", () => {
  const contactsBtn = document.querySelector(".contacts-btn");
  if (contactsBtn) {
    const overlay = document.querySelector(".contacts_modal_overlay");
    if (overlay) {
      const closeBtn = overlay.querySelector(".close_btn");
      const modalWindow = overlay.querySelector(".modal_container");
      const nameInput = modalWindow.querySelector(".name_input");
      const nameError = modalWindow.querySelector(".name_error");
      const emailInput = modalWindow.querySelector(".mail_input");
      const emailError = modalWindow.querySelector(".mail_error");
      const textArea = modalWindow.querySelector(".text_area");
      const submitBtn = modalWindow.querySelector(".submit_button");

      contactsBtn.onclick = () => {
        overlay.classList.add("show");
        setTimeout(() => {
          overlay.classList.add("visible");
        }, 600);
        document.body.style.overflowY = "hidden";
      };
      closeBtn.onclick = () => {
        overlay.classList.remove("visible");
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
        document.body.style.overflowY = "scroll";
      };

      submitBtn.onclick = () => {
        if (!nameInput.value) {
          showErrorValidation("Обязательное поле", nameError);
        }
        if (!emailInput.value) {
          showErrorValidation("Обязательное поле", emailError);
        }
        if (emailInput.value && !isEmailValid(emailInput.value)) {
          showErrorValidation("Некорректный E-mail", emailError);
        }
      };
    }
  }
});
