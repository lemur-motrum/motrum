import { showErrorValidation, maskOptions } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const formWrapper = document.querySelector(".project_one_form");
  if (formWrapper) {
    const form = formWrapper.querySelector(".project_one_submiting_form");
    const nameInput = formWrapper.querySelector(".name_input");
    const nameError = formWrapper.querySelector(".name_error");
    const phoneInput = formWrapper.querySelector(".phone_input");
    const phoneError = formWrapper.querySelector(".phone_error");

    const mask = IMask(phoneInput, maskOptions);

    form.onsubmit = (e) => {
      e.preventDefault();
      if (!nameInput.value) {
        showErrorValidation("Обязательное поле", nameError);
      }
      if (!phoneInput.value) {
        showErrorValidation("Обязательное поле", phoneError);
      }
      if (phoneInput.value && phoneInput.value.length < 18) {
        showErrorValidation("Некорректный номер телефона", phoneError);
      }
      if (nameInput.value && phoneInput.value.length == 18) {
        // Код отправки на сервер
      }
    };
  }
});
