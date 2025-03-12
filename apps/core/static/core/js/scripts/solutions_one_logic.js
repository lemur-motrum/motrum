import { showErrorValidation, maskOptions } from "/static/core/js/functions.js";

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

      const phoneMask = IMask(phoneInput, maskOptions);

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

    // анимация при скролле
    // if (palettScrollZoneContainer) {
    //   const tab = document.querySelector(".chars_table");
    //   const palettAnimateElem = palettScrollZoneContainer.querySelector(
    //     ".palett_animate_scroll_up"
    //   );
    //   let deltaY = 0;
    //   let lastKnownScrollPosition = 0;
    //   let rotationValue = 0;
    //   document.onscroll = () => {
    //     let ticking = false;
    //     if (!ticking) {
    //       window.requestAnimationFrame(() => {
    //         deltaY = window.scrollY - lastKnownScrollPosition;
    //         lastKnownScrollPosition = window.scrollY;
    //         ticking = false;
    //       });
    //       ticking = true;
    //     }

    //     let charsScrollTop = tab.getBoundingClientRect().top;
    //     let scrollPosY = palettScrollZoneContainer.getBoundingClientRect().top;

    //     // let translateValue = -deltaY * -5;

    //     if (deltaY > 0) {
    //       rotationValue += -deltaY * 5;
    //       if (rotationValue <= -45) {
    //         rotationValue = -45;
    //       } else {
    //         if (rotationValue >= 0) {
    //           rotationValue = 0;
    //         }
    //       }
    //     } else {
    //       rotationValue -= deltaY * 5;
    //       if (rotationValue <= -45) {
    //         rotationValue = -45;
    //       } else {
    //         if (rotationValue >= 0) {
    //           rotationValue = 0;
    //         }
    //       }
    //     }

    //     if (scrollPosY < 200) {
    //       palettAnimateElem.style.transform = `rotate(${rotationValue}deg)`;
    //     }
    //   };
    // }
  }
});
