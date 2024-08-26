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
      const newLegalEntityNameError = newLegalEntityForm.querySelector(
        ".new_legal_entity_name_error"
      );
      const innInput = newLegalEntityForm.querySelector(".inn");
      const newLegalEntityInnError = newLegalEntityForm.querySelector(
        ".new_legal_entity_inn_error"
      );
      const innMaskOptions = {
        mask: "0000000000",
      };
      const innMask = IMask(innInput, innMaskOptions);
      const kppInput = newLegalEntityForm.querySelector(".kpp");
      const newLegalEntityKppError = newLegalEntityForm.querySelector(
        ".new_legal_entity_kpp_error"
      );
      const kppMaskOptions = {
        mask: "000000000",
      };
      const kppMask = IMask(kppInput, kppMaskOptions);

      const orgnInput = newLegalEntityForm.querySelector(".ogrn");
      const newLegalEntityOgrnError = newLegalEntityForm.querySelector(
        ".new_legal_entity_ogrn_error"
      );

      const ogrnMaskOptions = {
        mask: "0000000000000",
      };
      const ogrnMask = IMask(orgnInput, ogrnMaskOptions);
      const contractInput = newLegalEntityForm.querySelector(".contract");
      const newLegalEntityContractError = newLegalEntityForm.querySelector(
        ".new_legal_entity_contract_error"
      );
      const legalIndexInput = newLegalEntityForm.querySelector(
        ".legal-adress-index"
      );
      const newLegalEntityLegalIndexError = newLegalEntityForm.querySelector(
        ".new_legal_entity_legal_adress_index_error"
      );
      const indexMaskOptions = {
        mask: "000000",
      };
      const legalIndexMask = IMask(legalIndexInput, indexMaskOptions);
      const legalCityInput =
        newLegalEntityForm.querySelector(".legal-adress-city");
      const newLegalEntityLegalCityError = newLegalEntityForm.querySelector(
        ".new_legal_entity_legal_adress_city_error"
      );
      const legalAdressInput = newLegalEntityForm.querySelector(
        ".legal-adress-adress"
      );
      const newLegalEntityLegalAdressError = newLegalEntityForm.querySelector(
        ".new_legal_entity_legal_adress_adress_error"
      );
      const postIndexInput =
        newLegalEntityForm.querySelector(".post-adress-index");
      const newLegalEntityPostalIndexError = newLegalEntityForm.querySelector(
        ".new_legal_entity_post_adress_index_error"
      );
      const postIndexMask = IMask(postIndexInput, indexMaskOptions);
      const postCityInput =
        newLegalEntityForm.querySelector(".post-adress-city");
      const newLegalEntityPostalCityError = newLegalEntityForm.querySelector(
        ".new_legal_entity_post_adress_city_error"
      );
      const postAdressInput = newLegalEntityForm.querySelector(
        ".post-adress-adress"
      );
      const newLegalEntityPostalAddresError = newLegalEntityForm.querySelector(
        ".new_legal_entity_post_adress_adress_error"
      );
      const currentAccount = newLegalEntityForm.querySelector(
        ".bank-details-input-current-account"
      );
      const newLegalEntityCurrentAccountError =
        newLegalEntityForm.querySelector(
          ".new_legal_entity_bank_current_account_error"
        );
      const accountMaskOptions = {
        mask: "00000000000000000000",
      };
      const currentAccountMask = IMask(currentAccount, accountMaskOptions);
      const bank = newLegalEntityForm.querySelector(".bank-details-input-bank");
      const newLegalEntityBankError = newLegalEntityForm.querySelector(
        ".new_legal_entity_bank_error"
      );
      const correspondentAccount = newLegalEntityForm.querySelector(
        ".bank-details-input-correspondent-account"
      );
      const newLegalEntityCorrespondentAvvountError =
        newLegalEntityForm.querySelector(
          ".new_legal_entity_bank_correspondent_account_error"
        );
      const correspondentAccountMask = IMask(
        correspondentAccount,
        accountMaskOptions
      );
      const bik = newLegalEntityForm.querySelector(".bank-details-input-bik");
      const newLegalEntityBicError = newLegalEntityForm.querySelector(
        ".new_legal_entity_bank_bik_error"
      );
      const bicMaskOptions = {
        mask: "000000000",
      };
      const bicMask = IMask(bik, bicMaskOptions);

      newLegalEntityForm.onsubmit = (e) => {
        e.preventDefault();
        if (!nameInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityNameError);
        }
        if (!innInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityInnError);
        }
        if (innInput.value && innInput.value.length < 10) {
          showErrorValidation(
            "ИНН должен состоять из 10 цифр",
            newLegalEntityInnError
          );
        }
        if (!kppInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityKppError);
        }
        if (kppInput.value && kppInput.value.length < 9) {
          showErrorValidation(
            "КПП должен состоять из 9 цифр",
            newLegalEntityKppError
          );
        }
        if (!orgnInput.value) {
          showErrorValidation("Обязательное поле", newLegalEntityOgrnError);
        }
        if (orgnInput.value && orgnInput.value.length < 13) {
          showErrorValidation(
            "ОГРН должен состоять из 9 цифр",
            newLegalEntityOgrnError
          );
        }
        if (!contractInput.value) {
          showErrorValidation("Обязательное поле", newLegalEntityContractError);
        }
        if (!legalIndexInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalIndexError
          );
        }
        if (legalIndexInput.value && legalIndexInput.value.length < 6) {
          showErrorValidation("Неверный индекс", newLegalEntityLegalIndexError);
        }
        if (!legalCityInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalCityError
          );
        }
        if (!legalAdressInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalAdressError
          );
        }
        if (!postIndexInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityPostalIndexError
          );
        }
        if (postIndexInput.value && postIndexInput.value.length < 6) {
          showErrorValidation(
            "Неверный индекс",
            newLegalEntityPostalIndexError
          );
        }
        if (!legalCityInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityPostalCityError
          );
        }
        if (!postAdressInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityPostalAddresError
          );
        }
        if (!currentAccount.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityCurrentAccountError
          );
        }
        if (currentAccount.value && currentAccount.value.length < 20) {
          showErrorValidation(
            "Cчет должен состоять из 20 цифр",
            newLegalEntityCurrentAccountError
          );
        }
        if (!bank.value) {
          showErrorValidation("Обязательное поле", newLegalEntityBankError);
        }
        if (!correspondentAccount.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityCorrespondentAvvountError
          );
        }
        if (
          correspondentAccount.value &&
          correspondentAccount.value.length < 20
        ) {
          showErrorValidation(
            "Cчет должен состоять из 20 цифр",
            newLegalEntityCorrespondentAvvountError
          );
        }
        if (!bik.value) {
          showErrorValidation("Обязательное поле", newLegalEntityBicError);
        }
        if (bik.value.length < 9) {
          showErrorValidation(
            "Бик должен состоять из 9 цифр",
            newLegalEntityBicError
          );
        }
        if (
          nameInput.value &&
          innInput.value.length == 10 &&
          kppInput.value.length == 9 &&
          orgnInput.value.length == 13 &&
          contractInput.value &&
          legalIndexInput.value.length == 6 &&
          legalCityInput.value &&
          legalAdressInput.value &&
          postIndexInput.value.length == 6 &&
          postCityInput.value &&
          postAdressInput.value &&
          currentAccount.value.length == 20 &&
          bank.value &&
          correspondentAccount.value.length == 20 &&
          bik.value.length == 9
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

    const legalEntities =
      personalAccountContent.querySelectorAll(".legal_entity");

    legalEntities.forEach((legalEntity) => {
      const countContainer = legalEntity.querySelector(
        ".new_bank_detail_counter"
      );
      const bankDetails = legalEntity.querySelectorAll(".bank_detail");

      countContainer.textContent = bankDetails.length + 1;

      const btn = legalEntity.querySelector(".change_button");
      legalEntity.onmouseover = () => {
        btn.classList.add("show");
      };
      legalEntity.onmouseout = () => {
        btn.classList.remove("show");
      };
      btn.onclick = () => {
        legalEntity.classList.toggle("show");
        if (legalEntity.classList.contains("show")) {
          btn.textContent = "Скрыть";
        } else {
          btn.textContent = "Редактировать";
        }
      };
    });
  }
});
