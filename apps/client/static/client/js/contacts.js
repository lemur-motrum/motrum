import {
  isEmailValid,
  showErrorValidation,
  getCookie,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "../../../../core/static/core/js/functions.js";
import { setErrorModal } from "../../../../core/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

const clientId = +getCookie("client_id");

window.addEventListener("DOMContentLoaded", () => {
  const personalAccountContent = document.querySelector(
    ".personal_account_content"
  );
  if (personalAccountContent) {
    const contacts = personalAccountContent.querySelector(".contacts");
    if (contacts) {
      const contactsPerson = contacts.querySelectorAll(".contact_person");
      contactsPerson.forEach((contactPerson) => {
        const changeBtn = contactPerson.querySelector(".change_btn");
        const contactPersonDetails = contactPerson.querySelector(
          ".contact_person_details"
        );

        const changeForm = contactPerson.querySelector(".contact_person_form");
        const changeFormFormSubmitBtn = changeForm.querySelector(".sumbit_btn");
        const inputFirstName = changeForm.querySelector(".surname");
        const inputFirstNameError = changeForm.querySelector(".surname_error");
        const inputName = changeForm.querySelector(".name-input");
        const inputNameError = changeForm.querySelector(".name_error");
        const inputLastName = changeForm.querySelector(".last-name");
        const inputLastNameError = changeForm.querySelector(".last_name_error");
        const inputJobTitle = changeForm.querySelector(".job_title-input");
        const inputJobTitleError = changeForm.querySelector(".job_title_error");
        const inputEmail = changeForm.querySelector(".mail-input");
        const inputEmailError = changeForm.querySelector(".mail_error");
        const extraPhoneInputs =
          changeForm.querySelectorAll(".extra_phone_field");
        const extraPhoneInputErrors = changeForm.querySelectorAll(
          ".extra_phone_field_error"
        );
        const newExtraPointInput = changeForm.querySelector(
          ".new_extra_phone_field"
        );
        const newExtraPointInputError = changeForm.querySelector(
          ".new_extra_phone_field_error"
        );
        const phoneArray = [];

        const mask = IMask(newExtraPointInput, maskOptions);
        extraPhoneInputs.forEach((el) => {
          const mask = IMask(el, maskOptions);
        });

        changeBtn.onclick = () => {
          contactPersonDetails.classList.add("no_visible");
          changeForm.classList.add("show");
        };

        changeFormFormSubmitBtn.onclick = (e) => {
          let validate = true;
          e.preventDefault();
          if (!inputFirstName.value) {
            showErrorValidation("Обязательное поле", inputFirstNameError);
            validate = false;
          }
          if (!inputName.value) {
            showErrorValidation("Обязательное поле", inputNameError);
            validate = false;
          }
          if (!inputLastName.value) {
            showErrorValidation("Обязательное поле", inputLastNameError);
            validate = false;
          }
          if (!isEmailValid(inputEmail.value)) {
            showErrorValidation("Поле заполненно некорректно", inputEmailError);
            validate = false;
          }
          if (!inputEmail.value) {
            showErrorValidation("Обязательное поле", inputEmailError);
            validate = false;
          }
          if (extraPhoneInputs.length > 0) {
            extraPhoneInputs.forEach((el, i) => {
              if (
                extraPhoneInputs[i].value &&
                extraPhoneInputs[i].value.length < 18
              ) {
                showErrorValidation(
                  "Поле заполненно некорректно",
                  extraPhoneInputErrors[i]
                );
                validate = false;
              }
            });
          }
          if (
            newExtraPointInput.value &&
            newExtraPointInput.value.length < 18
          ) {
            showErrorValidation(
              "Поле заполненно некорректно",
              newExtraPointInputError
            );
            validate = false;
          }
          async function sendContactForm() {
            if (extraPhoneInputs.length > 0) {
              extraPhoneInputs.forEach((el) => {
                phoneArray.push(el.value.replace(/\D/g, ""));
              });
            }
            if (newExtraPointInput.value) {
              phoneArray.push(mask.value.replace(/\D/g, ""));
            }

            const dataObj = {
              client: {
                last_name: inputFirstName.value,
                first_name: inputName.value,
                middle_name: inputLastName.value,
                position: inputJobTitle.value ? inputJobTitle.value : "",
                email: inputEmail.value,
              },
              phone: phoneArray[0] == "" ? [] : phoneArray,
            };
            const data = JSON.stringify(dataObj);

            setPreloaderInButton(changeFormFormSubmitBtn);

            const response = await fetch(
              `/api/v1/client/${clientId}/upd-user-lk/`,
              {
                method: "POST",
                body: data,
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken,
                },
              }
            );
            if (response.status >= 200 && response.status < 300) {
              window.location.reload();
              hidePreloaderAndEnabledButton(changeFormFormSubmitBtn);
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          }

          if (validate) {
            sendContactForm();
          }
        };
      });
    }
  }
});
