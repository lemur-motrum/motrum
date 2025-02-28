import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

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

    const maskOptions = {
      mask: "+{7} (000) 000-00-00",
      prepare: function (appended, masked) {
        if (appended === "8" && masked.value === "") {
          return "7";
        }
        return appended;
      },
    };

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
      console.log("fileType", fileType);
      fileLabelDescription.textContent = truncate(fileName, 8) + "." + fileType;
    });

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
        const dataObj = {
          name: nameInput.value,
          phone: phoneInput.value,
          message: textArea.value ? textArea.value : "",
          file: fileInput.value,
        };
        const data = JSON.stringify(dataObj);

        fetch("", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((response) => console.log(response))
          .catch((error) => console.error(error));
      }
    };
  }
});
