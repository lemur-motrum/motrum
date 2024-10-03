import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const legalEntityContainer = document.querySelector(".legal_entitis");
  if (legalEntityContainer) {
    const legalEntitis = legalEntityContainer.querySelectorAll(".legal_entity");
    legalEntitis.forEach((legalEntity) => {
      const legalAdressForm = legalEntity.querySelector(".legal_adress_form");
      const postAdressForm = legalEntity.querySelector(".post_adress_form");
      const bankDetails = legalEntity.querySelectorAll(".bank_detail");
      const newBankDetailForm = legalEntity.querySelector(".new_bank_detail");

      if (legalAdressForm) {
        const indexInput = legalAdressForm.querySelector(
          ".current_legal_adress_index"
        );
        const indexInputError = legalAdressForm.querySelector(
          ".current_legal_adress_index_error"
        );
        const cityInput = legalAdressForm.querySelector(
          ".current_legal_adress_city"
        );
        const addresInput = legalAdressForm.querySelector(
          ".current_legal_adress_city"
        );
        const updateBtn = legalAdressForm.querySelector(
          ".change-legal-adress-button"
        );

        updateBtn.onclick = (e) => {
          e.preventDefault();
          if (!indexInput.value) {
            showErrorValidation("Обязательное поле", indexInputError);
          }
        };
      }
    });
  }
});
