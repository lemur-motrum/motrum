import {
  showErrorValidation,
  getCookie,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "../functions.js";

import { setErrorModal } from "../error_modal.js";
import { successModal } from "../sucessModal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".contacts-wrapper");
  if (wrapper) {
    ymaps.ready(function () {
      const myMap = new ymaps.Map(
          "map",
          {
            center:
              window.innerWidth > 576
                ? [53.234504811961656, 50.19189402114864]
                : [53.236397293742286, 50.19255920898432],
            zoom: 16,
          },
          {
            searchControlProvider: "yandex#search",
          }
        ),
        myPlacemark = new ymaps.Placemark(
          [53.23432457121684, 50.19386812698358],
          myMap.getCenter(),
          {
            iconLayout: "default#imageWithContent",
            iconImageHref: "../../../../static/core/images/map-bullet.png",
            iconImageSize: [50.5, 79],
            iconImageOffset: [-21, -79],
          }
        );

      myMap.behaviors.disable("scrollZoom");
      myMap.controls.remove("geolocationControl");
      myMap.controls.remove("routeButtonControl");
      myMap.controls.remove("trafficControl");
      myMap.controls.remove("searchControl");
      myMap.controls.remove("typeSelector");
      myMap.controls.remove("fullscreenControl");
      myMap.controls.remove("taxiControl");
      myMap.controls.remove("rulerControl");
      myMap.geoObjects.add(myPlacemark);
    });

    const contactsWrapper = wrapper.querySelector(".contacts-block");
    const contactsWrapperBtn = contactsWrapper.querySelector(".contacts-btn");
    const contactsFormOverlay = contactsWrapper.querySelector(
      ".contact_page_overlay"
    );
    const closeBtn = contactsFormOverlay.querySelector(".close_btn");
    const modalWindow = contactsFormOverlay.querySelector(".modal_window");
    const nameInput = modalWindow.querySelector(".name_input");
    const nameError = modalWindow.querySelector(".name_error");
    const phoneInput = modalWindow.querySelector(".phone_input");
    const phoneError = modalWindow.querySelector(".phone_error");
    const textArea = modalWindow.querySelector(".modal_textarea");
    const submitBtn = modalWindow.querySelector(".submit_btn");

    const mask = IMask(phoneInput, maskOptions);

    function resetInputs(container) {
      const inputs = container.querySelectorAll("input");
      const textArea = container.querySelector("textarea");
      inputs.forEach((input) => {
        input.value = "";
      });
      textArea.value = "";
    }

    contactsWrapperBtn.onclick = () => {
      ym(37794920, "reachGoal", "open_contacts_overlay");
      contactsFormOverlay.classList.add("show");
      setTimeout(() => {
        contactsFormOverlay.classList.add("visible");
      }, 600);
      document.body.style.overflowY = "hidden";
    };

    closeBtn.onclick = () => hideOverlay();

    function hideOverlay() {
      contactsFormOverlay.classList.remove("visible");
      setTimeout(() => {
        contactsFormOverlay.classList.remove("show");
      }, 600);
      resetInputs(modalWindow);

      document.body.style.overflowY = "auto";
    }

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
          phone: mask.unmaskedValue,
          message: textArea.value ? textArea.value : "",
          url: window.location.href,
        };
        const data = JSON.stringify(dataObj);

        setPreloaderInButton(submitBtn);

        fetch("/api/v1/core/forms/send-form-contact-us/", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status >= 200 && response.status < 300) {
              ym(37794920, "reachGoal", "send_contact_form");
              hidePreloaderAndEnabledButton(submitBtn);
              hideOverlay();
              successModal(
                "Спасибо за обращение, мы свяжемся с вами в ближайшее время"
              );
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          })
          .catch((error) => console.error(error));
      }
    };
  }
});
