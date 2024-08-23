import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");
const clientId = +getCookie("client_id");

window.addEventListener("DOMContentLoaded", () => {
  const personalAccountContent = document.querySelector(
    ".personal_account_content"
  );
  if (personalAccountContent) {
    const detailsContainer = document.querySelector(".details");
    if (detailsContainer) {
      const newLegalEntityContainer =
        detailsContainer.querySelector(".new_legal_entity");
      const addLegalEntity =
        detailsContainer.querySelector(".add_legal_entity");
      addLegalEntity.onclick = () => {
        newLegalEntityContainer.classList.add("show");
      };
      const newLegalEntityForm =
        newLegalEntityContainer.querySelector(".legal_entity_form");

      const nameInput = newLegalEntityForm.querySelector(".name");
      const innInput = newLegalEntityForm.querySelector(".inn");
      const kppInput = newLegalEntityForm.querySelector(".kpp");
      const orgnInput = newLegalEntityForm.querySelector(".ogrn");
      const contractInput = newLegalEntityForm.querySelector(".contract");
      const legalIndexInput = newLegalEntityForm.querySelector(
        ".legal-adress-index"
      );
      const legalCityInput =
        newLegalEntityForm.querySelector(".legal-adress-city");
      const legalAdressInput = newLegalEntityForm.querySelector(
        ".legal-adress-adress"
      );
      const postIndexInput =
        newLegalEntityForm.querySelector(".post-adress-index");
      const postCityInput =
        newLegalEntityForm.querySelector(".post-adress-city");
      const postAdressInput = newLegalEntityForm.querySelector(
        ".post-adress-adress"
      );
      const currentAccount = newLegalEntityForm.querySelector(
        ".bank-details-input-current-account"
      );
      const bank = newLegalEntityForm.querySelector(".bank-details-input-bank");
      const correspondentAccount = newLegalEntityForm.querySelector(
        ".bank-details-input-correspondent-account"
      );
      const bik = newLegalEntityForm.querySelector(".bank-details-input-bik");

      newLegalEntityForm.onsubmit = (e) => {
        e.preventDefault();
        if (
          nameInput.value &&
          innInput.value &&
          kppInput.value &&
          orgnInput.value &&
          contractInput.value &&
          legalIndexInput.value &&
          legalCityInput.value &&
          legalAdressInput.value &&
          postIndexInput.value &&
          postCityInput.value &&
          postAdressInput.value &&
          currentAccount.value &&
          bank.value &&
          correspondentAccount.value &&
          bik.value
        ) {
          const dataObj = [
            {
              requisites: {
                contract: contractInput.value,
                legal_entity: nameInput.value,
                inn: innInput.value,
                kpp: kppInput.value,
                ogrn: orgnInput.value,
                legal_post_code: legalIndexInput.value,
                legal_city: legalCityInput.value,
                legal_address: legalAdressInput.value,
                postal_post_code: postIndexInput.value,
                postal_city: postCityInput.value,
                postal_address: postAdressInput.value,
                client: clientId,
              },
              account_requisites: [
                {
                  account_requisites: currentAccount.value,
                  bank: bank.value,
                  kpp: correspondentAccount.value,
                  bic: bik.value,
                  requisites: null,
                },
              ],
            },
          ];

          const data = JSON.stringify(dataObj);

          fetch(`/api/v1/requisites/add/`, {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            response.json();
            if (response.status == 200) {
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
