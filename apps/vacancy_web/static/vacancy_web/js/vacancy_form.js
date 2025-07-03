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
  const wrapper = document.querySelector(".vacancy_container");
  if (wrapper) {
    const vacancyForm = wrapper.querySelector(".vacancies_form_container");
    const nameInput = vacancyForm.querySelector(".name_input");
    const nameError = vacancyForm.querySelector(".name_error");
    const phoneInput = vacancyForm.querySelector(".phone_input");
    const phoneError = vacancyForm.querySelector(".phone_error");
    const textArea = vacancyForm.querySelector(".vacancy_form_textarea");
    const filelabel = vacancyForm.querySelector(".file_label");
    const fileLabelDescription = filelabel.querySelector(".file_description");
    const fileInput = filelabel.querySelector(".file_input");
    const fileError = filelabel.querySelector(".file_error");
    const submitBtn = vacancyForm.querySelector(".submit_btn");

    const mask = IMask(phoneInput, maskOptions);

    function truncate(str, maxlength) {
      return str.length > maxlength
        ? str.slice(0, 3) + "…" + str.slice(maxlength - 4, maxlength - 1)
        : str;
    }

    fileInput.addEventListener("change", function () {
      const file = this.files[0];
      const array = file["name"].split(".");
      const fileName = array[0];
      const fileType = array.at(-1);
      fileLabelDescription.textContent = truncate(fileName, 8) + "." + fileType;
    });

    function clearInputs() {
      const inputs = vacancyForm.querySelectorAll("input");
      inputs.forEach((input) => {
        input.value = "";
      });
      vacancyForm.querySelector("textarea").value = "";
      fileLabelDescription.textContent = "Прикрепить резюме";
    }

    submitBtn.onclick = () => {
      let validate = true;
      if (!nameInput.value) {
        validate = false;
        showErrorValidation("Обязательное поле", nameError);
      }
      if (!phoneInput.value) {
        validate = false;
        showErrorValidation("Обязательное поле", phoneError);
      }
      if (phoneInput.value && phoneInput.value.length < 18) {
        validate = false;
        showErrorValidation("Некорректный номер", phoneError);
      }
      if (!fileInput.value) {
        validate = false;
        showErrorValidation("Файл не прикреплен", fileError);
      }
      if (validate) {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);
        formData.append("name", nameInput.value);
        formData.append("phone", phoneInput.value);
        formData.append("message", textArea.value ? textArea.value : "");
        formData.append("vacancy", "");

        setPreloaderInButton(submitBtn);

        fetch("/api/v1/vacancy/send-vacancy/", {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status >= 200 && response.status < 300) {
              ym(37794920, "reachGoal", "send_vacancy_form");
              clearInputs();
              successModal(
                "Спасибо за отклик, мы рассмотрим Ваше резюме и свяжемся с Вами"
              );
              hidePreloaderAndEnabledButton(submitBtn);
            } else {
              setErrorModal();
            }
          })
          .catch((error) => console.error(error));
      }
    };
  }
});
