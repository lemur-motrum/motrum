import { showErrorValidation } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".solution_one_container");
  if (wrapper) {
    const slider = new Swiper(".solution_one_slider", {
      slidesPerView: "auto",
    });

    const formContainer = wrapper.querySelector(".demo-form-container");
    if (formContainer) {
      const nameInput = formContainer.querySelector(".name_input");
      const nameError = formContainer.querySelector(".name_error");
      const phoneInput = formContainer.querySelector(".phone_input");
      const phoneError = formContainer.querySelector(".phone_error");
      const submitBtn = formContainer.querySelector(".btn");

      const maskPhoneOptions = {
        mask: "+{7} (000) 000-00-00",
        prepare: function (appended, masked) {
          if (appended === "8" && masked.value === "") {
            return "7";
          }
          return appended;
        },
      };

      const phoneMask = IMask(phoneInput, maskPhoneOptions);

      submitBtn.onclick = () => {
        if (!nameInput.value) {
          showErrorValidation("Обязательное поле", nameError);
        }
        if (!phoneInput.value) {
          showErrorValidation("Обязательное поле", phoneError);
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          showErrorValidation("Некорректный номер телефона", phoneError);
        }
      };
    }

    const palettScrollZoneContainer = wrapper.querySelector(
      ".palett_description"
    );

    if (palettScrollZoneContainer) {
      window.onscroll = () => {
        let scrollPosY = palettScrollZoneContainer.getBoundingClientRect().top;
      };
    }
  }
});
