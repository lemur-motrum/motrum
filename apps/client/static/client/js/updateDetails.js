import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const legalEntityContainer = document.querySelector(".legal_entitis");
  if (legalEntityContainer) {
    const legalEntityElems =
      legalEntityContainer.querySelectorAll(".legal_entity");
    legalEntityElems.forEach((legalEntityElem) => {
      const addressForms =
        legalEntityElem.querySelectorAll(".legal_adress_form");
      addressForms.forEach((form) => {
        const indexInput = form.querySelector(".current_legal_adress_index");
        const indexError = form.querySelector(
          ".current_legal_adress_index_error"
        );
        const regionInput = form.querySelector(".current_legal_adress_region");
        const regionError = form.querySelector(
          ".current_legal_adress_region_error"
        );
        const cityInput = form.querySelector(".current_legal_adress_city");
        const cityError = form.querySelector(
          ".current_legal_adress_city_error"
        );
        const addresOneInput = form.querySelector(
          ".current_legal_adress_adress_one"
        );
        const addressOneError = form.querySelector(
          ".current_legal_adress_adress_one_error"
        );
        const addressTwoInput = form.querySelector(
          ".current_legal_adress_adress_two"
        );
        const addressTwoError = form.querySelector(
          ".current_legal_adress_adress_two_error"
        );
        const addressCountry = form.getAttribute("data-country");
        const addressId = form.getAttribute("data-address-id");

        const submitBtn = form.querySelector(".change-legal-adress-button");

        submitBtn.onclick = (e) => {
          e.preventDefault();
          let validate = true;
          if (!indexInput.value) {
            showErrorValidation("Обязательное поле", indexError);
            validate = false;
          }
          if (!regionInput.value) {
            showErrorValidation("Обязательное поле", regionError);
            validate = false;
          }
          if (!addresOneInput.value) {
            showErrorValidation("Обязательное поле", addressOneError);
            validate = false;
          }
          if (validate) {
            const dataObj = {
              country: addressCountry ? addressCountry : null,
              region: regionInput.value,
              province: null,
              post_code: indexInput.value,
              city: cityInput.value ? cityInput.value : null,
              legal_address1: addresOneInput.value,
              legal_address2: addressTwoInput.value
                ? addressTwoInput.value
                : null,
            };
            const data = JSON.stringify(dataObj);

            fetch(`/api/v1/adress_requisites/${addressId}/`, {
              method: "PATCH",
              body: data,
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
            }).then((response) => {
              if (response.status == 200) {
                window.location.reload();
              }
            });
          }
        };
      });
    });
  }
});
