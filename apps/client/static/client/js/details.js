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
      const newLegalEntityContainerWrapper = detailsContainer.querySelector(
        ".new_legal_entity_wrapper"
      );
      const addLegalEntity =
        detailsContainer.querySelector(".add_legal_entity");
      addLegalEntity.onclick = () => {
        newLegalEntityContainerWrapper.classList.toggle("show");
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
        mask: "000000000000",
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
        mask: "000000000000000",
      };
      const ogrnMask = IMask(orgnInput, ogrnMaskOptions);

      const phoneInput = newLegalEntityForm.querySelector(".phone");
      const phoneError = newLegalEntityForm.querySelector(".phone_error");

      const phoneMaskOptions = {
        mask: "+{7} (000) 000-00-00",
        prepare: function (appended, masked) {
          if (appended === "8" && masked.value === "") {
            return "7";
          }
          return appended;
        },
      };
      const phoneMask = IMask(phoneInput, phoneMaskOptions);
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
        let validate = true;
        if (!nameInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityNameError);
          validate = false;
        }
        if (!innInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityInnError);
          validate = false;
        }

        if (
          innInput.value.length !== 10 &&
          innInput.value &&
          innInput.value.length !== 12 &&
          innInput.value &&
          innInput.value.length !== 13 &&
          innInput.value
        ) {
          showErrorValidation(
            "ИНН должен состоять из 10 или 12 цифр",
            newLegalEntityInnError
          );
          validate = false;
        }

        if (!kppInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityKppError);
          validate = false;
        }
        if (kppInput.value && kppInput.value.length < 9) {
          showErrorValidation(
            "КПП должен состоять из 9 цифр",
            newLegalEntityKppError
          );
          validate = false;
        }
        if (!orgnInput.value) {
          showErrorValidation("Обязательное поле", newLegalEntityOgrnError);
          validate = false;
        }
        if (
          orgnInput.value &&
          orgnInput.value.length != 13 &&
          orgnInput.value &&
          orgnInput.value.length != 15 &&
          orgnInput.value &&
          orgnInput.value.length != 16
        ) {
          showErrorValidation(
            "ОГРН должен состоять из 13 или 15 цифр",
            newLegalEntityOgrnError
          );
          validate = false;
        }
        if (!phoneInput.value) {
          showErrorValidation("Обязательное поле", phoneError);
          validate = false;
        }

        if (phoneInput.value && phoneInput.value.length < 18) {
          showErrorValidation("Некорректный номер телефона", phoneError);
          validate = false;
        }

        if (!legalIndexInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalIndexError
          );
          validate = false;
        }
        if (legalIndexInput.value && legalIndexInput.value.length < 6) {
          showErrorValidation("Неверный индекс", newLegalEntityLegalIndexError);
          validate = false;
        }
        if (!legalCityInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalCityError
          );
          validate = false;
        }
        if (!legalAdressInput.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityLegalAdressError
          );
          validate = false;
        }
        if (!currentAccount.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityCurrentAccountError
          );
          validate = false;
        }
        if (currentAccount.value && currentAccount.value.length < 20) {
          showErrorValidation(
            "Cчет должен состоять из 20 цифр",
            newLegalEntityCurrentAccountError
          );
          validate = false;
        }
        if (!bank.value) {
          showErrorValidation("Обязательное поле", newLegalEntityBankError);
          validate = false;
        }
        if (!correspondentAccount.value) {
          showErrorValidation(
            "Обязательное поле",
            newLegalEntityCorrespondentAvvountError
          );
          validate = false;
        }
        if (
          correspondentAccount.value &&
          correspondentAccount.value.length < 20
        ) {
          showErrorValidation(
            "Cчет должен состоять из 20 цифр",
            newLegalEntityCorrespondentAvvountError
          );
          validate = false;
        }
        if (!bik.value) {
          showErrorValidation("Обязательное поле", newLegalEntityBicError);
          validate = false;
        }
        if (bik.value.length < 9) {
          showErrorValidation(
            "Бик должен состоять из 9 цифр",
            newLegalEntityBicError
          );
          validate = false;
        }
        if (validate) {
          const dataObj = [
            {
              requisites: {
                legal_entity: nameInput.value,
                inn: innInput.value,
                kpp: kppInput.value,
                ogrn: orgnInput.value,
                legal_post_code: legalIndexInput.value,
                legal_city: legalCityInput.value,
                legal_address: legalAdressInput.value,
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
              // window.location.reload();
            }
            if (response.status == 400) {
              console.log("Ошибка");
            }
          });
        }
      };
    }

    const legalEntities = personalAccountContent.querySelectorAll(
      ".legal_entity_wrapper"
    );

    legalEntities.forEach((legalEntity) => {
      const countContainer = legalEntity.querySelector(
        ".new_bank_detail_counter"
      );
      const bankDetails = legalEntity.querySelectorAll(".bank_detail");

      // countContainer.textContent = bankDetails.length + 1;

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
