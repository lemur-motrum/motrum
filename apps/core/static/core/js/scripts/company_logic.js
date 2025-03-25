import {
  showErrorValidation,
  getCookie,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".about_container");
  if (wrapper) {
    const clientSliderContainer = wrapper.querySelector(
      ".company_photo_client_swiper"
    );
    const companySliderContainer = wrapper.querySelector(
      ".employees_photo_swiper"
    );

    if (clientSliderContainer) {
      const slider = new Swiper(".company_photo_client_swiper", {
        slidesPerView: "auto",
      });
      const slider2 = new Swiper(
        ".company_photo_client_swiper_overlay_slider",
        {}
      );

      const sliderElems = document.querySelectorAll(
        ".company_photo_client_swiper_slide"
      );

      const overlay = clientSliderContainer.querySelector(
        ".company_photo_client_swiper_overlay"
      );
      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        if (window.innerWidth > 576) {
          el.onclick = () => {
            overlay.classList.add("show");
            setTimeout(() => {
              overlay.classList.add("visible");
            }, 600);
            slider2.activeIndex = i;
            if (window.innerWidth > 576) {
              document.body.style.overflowY = "hidden";
            }
          };
        }

        closeBtn.onclick = () => {
          overlay.classList.remove("visible");
          setTimeout(() => {
            overlay.classList.remove("show");
          }, 600);
          document.body.style.overflowY = "scroll";
        };
      });
    }

    if (companySliderContainer) {
      const slider = new Swiper(".employees_photo_swiper", {
        slidesPerView: "auto",
      });
      const slider1 = new Swiper(".employees_photo_swiper_overlay_slider", {});

      const sliderElems = document.querySelectorAll(
        ".employees_photo_swiper_slide"
      );

      const overlay = companySliderContainer.querySelector(
        ".employees_photo_swiper_overlay"
      );
      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        if (window.innerWidth > 576) {
          el.onclick = () => {
            overlay.classList.add("show");
            setTimeout(() => {
              overlay.classList.add("visible");
            }, 600);
            slider1.activeIndex = i;
            if (window.innerWidth > 576) {
              document.body.style.overflowY = "hidden";
            }
          };
        }

        closeBtn.onclick = () => {
          overlay.classList.remove("visible");
          setTimeout(() => {
            overlay.classList.remove("show");
          }, 600);
          document.body.style.overflowY = "scroll";
        };
      });
    }

    const companyForm = wrapper.querySelector(".company_form_container");
    if (companyForm) {
      const form = companyForm.querySelector(".form");
      const nameInput = form.querySelector(".name_input");
      const nameError = form.querySelector(".name_error");
      const phoneInput = form.querySelector(".phone_input");
      const phoneError = form.querySelector(".phone_error");
      const submitBtn = form.querySelector(".submit_btn");

      const mask = IMask(phoneInput, maskOptions);

      submitBtn.onclick = () => {
        let validate = true;
        if (!nameInput.value) {
          showErrorValidation("Обязательное поле", nameError);
          validate = false;
        }
        if (!phoneInput.value) {
          showErrorValidation("Обязательное поле", phoneError);
          validate = false;
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          showErrorValidation("Некорректный номер", phoneError);
          validate = false;
        }
        if (validate) {
          const dataObj = {
            name: nameInput.value,
            phone: phoneInput.value,
          };

          const data = JSON.stringify(dataObj);
          setPreloaderInButton(submitBtn);

          fetch("", {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            if (response.status >= 200 && response.status < 300) {
              // window.location.reload();
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          });
        }
      };
    }
  }
});
