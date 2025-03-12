import { version } from "/static/core/js/scripts/version.js";

const { showErrorValidation, maskOptions, getCookie } = await import(
  `/static/core/js/functions.js?ver=${version}`
);
const { setErrorModal } = await import(
  `/static/core/js/error_modal.js?ver=${version}`
);

const csrfToken = getCookie("csrftoken");

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
      let validate = true;
      e.preventDefault();
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
      if (validate) {
        const dataObj = {
          name: nameInput.value,
          phone: phoneInput.value,
        };
        const data = JSON.stringify(dataObj);

        fetch("", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        }).then((response) => {
          if (response.status >= 200 && response.status < 300) {
          } else {
            setErrorModal();
          }
        });
      }
    };
  }
});
