import {
  isEmailValid,
  showErrorValidation,
  getCookie,
} from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

const clientId = +getCookie("client_id");

window.addEventListener("DOMContentLoaded", () => {
  const personalAccountContent = document.querySelector(
    ".personal_account_content"
  );
  if (personalAccountContent) {
    const contacts = personalAccountContent.querySelector(".contacts");
    if (contacts) {
      const form = contacts.querySelector(".contact-form");
      const nameInput = form.querySelector(".name-input");
      const nameError = form.querySelector(".name_error");
      const phoneInput = form.querySelector(".phone-input");
      const phoneError = form.querySelector(".phone_error");
      const mailInput = form.querySelector(".mail-input");
      const mailError = form.querySelector(".mail_error");

      const maskOptions = {
        mask: "+{7} (000) 000-00-00",
      };

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
        if (!mailInput.value) {
          showErrorValidation("Обязательное поле", mailError);
        }
        if (mailInput.value && !isEmailValid(mailInput.value)) {
          showErrorValidation("Некорректный Email", mailError);
        }
        if (
          nameInput.value &&
          phoneInput.value.length == 18 &&
          isEmailValid(mailInput.value)
        ) {
          const phone = mask.unmaskedValue;

          const dataObj = {
            contact_name: nameInput.value,
            phone: phone,
            email: mailInput.value,
            username: phone,
            password: "",
          };
          const data = JSON.stringify(dataObj);

          fetch(`/api/v1/client/${clientId}/`, {
            // изменила метод 
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            response.json();
            if (response.status == 200) {
              console.log("Данные изменены");
              window.location.reload();
            }
            if (response.status == 400) {
              console.log("Ошибка");
            }
          });
        }
      };
    }
  }
});
