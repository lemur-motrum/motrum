import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const legalEntityContainer = document.querySelector(".legal_entitis");
  if (legalEntityContainer) {
    const legalEntitis = legalEntityContainer.querySelectorAll(".legal_entity");
    legalEntitis.forEach((legalEntity) => {
      const legalAdressForm = legalEntity.querySelector(".legal_adress_form");
      const postAdressForm = legalEntity.querySelector(".post_adress_form");
      const bankDetails = legalEntity.querySelectorAll(".bank_detail");
      const newBankDetailForm = legalEntity.querySelector(".new_bank_detail");
      const detailsId = legalEntity.getAttribute("legal-entity-adress");

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
        const cityInputError = legalAdressForm.querySelector(
          ".current_legal_adress_city_error"
        );
        const addressInput = legalAdressForm.querySelector(
          ".current_legal_adress_adress"
        );
        const addressError = legalAdressForm.querySelector(
          ".current_legal_adress_adress_error"
        );
        const updateBtn = legalAdressForm.querySelector(
          ".change-legal-adress-button"
        );

        updateBtn.onclick = (e) => {
          e.preventDefault();
          if (!indexInput.value) {
            showErrorValidation("Обязательное поле", indexInputError);
          }
          if (indexInput.value.length !== 6) {
            showErrorValidation("индекс состоит из 6 цифр", indexInputError);
          }
          if (!cityInput.value) {
            showErrorValidation("Обязательное поле", cityInputError);
          }
          if (!addressInput.value) {
            showErrorValidation("Обязательное поле", addressError);
          }
          if (
            indexInput.value.length == 6 &&
            cityInput.value &&
            addressInput.value
          ) {
            const dataObj = [
              {
                requisites: {
                  legal_post_code: indexInput.value,
                  legal_city: cityInput.value,
                  legal_address: addressInput.value,
                },
              },
            ];
            const data = JSON.stringify(dataObj);

            fetch(`/api/v1/requisites/${detailsId}/update/`, {
              method: "UPDATE",
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
      if (postAdressForm) {
        const indexInput = postAdressForm.querySelector(
          ".current_post_adress_index"
        );
        const indexInputError = postAdressForm.querySelector(
          ".current_post_adress_index_error"
        );
        const cityInput = postAdressForm.querySelector(
          ".current_post_adress_city"
        );
        const cityInputError = postAdressForm.querySelector(
          ".current_post_adress_error"
        );
        const addressInput = postAdressForm.querySelector(
          ".current_post_adress_adress"
        );
        const addressError = postAdressForm.querySelector(
          ".current_post_adress_adress_error"
        );
        const updateBtn = legalAdressForm.querySelector(
          ".change-post-adress-button"
        );

        updateBtn.onclick = (e) => {
          e.preventDefault();
          if (!indexInput.value) {
            showErrorValidation("Обязательное поле", indexInputError);
          }
          if (indexInput.value.length !== 6) {
            showErrorValidation("индекс состоит из 6 цифр", indexInputError);
          }
          if (!cityInput.value) {
            showErrorValidation("Обязательное поле", cityInputError);
          }
          if (!addressInput.value) {
            showErrorValidation("Обязательное поле", addressError);
          }
          if (
            indexInput.value.length == 6 &&
            cityInput.value &&
            addressInput.value
          ) {
            const dataObj = [
              {
                requisites: {
                  postal_post_code: indexInput.value,
                  postal_city: cityInput.value,
                  postal_address: addressInput.value,
                },
              },
            ];
            const data = JSON.stringify(dataObj);

            fetch(`/api/v1/requisites/${detailsId}/update/`, {
              method: "UPDATE",
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

        bankDetails.forEach((bankDetail) => {
          if (bankDetail) {
            const bankDetailId = bankDetail.getAttribute("bank-details-id");
            const currentAccount = bankDetail.querySelector(
              ".bank_detail-current_account"
            );
            const currentAccountError = bankDetail.querySelector(
              ".bank_detail-current_account_error"
            );
            const bankName = bankDetail.querySelector(".bank_detail-bank");
            const bankNameError = bankDetail.querySelector(
              ".bank_detail-bank_error"
            );
            const correspondentAccount = bankDetail.querySelector(
              ".bank_detail-correspondent_account"
            );
            const correspondentAccountError = bankDetail.querySelector(
              ".bank_detail-correspondent_account_error"
            );
            const bic = bankDetail.querySelector(".bank_detail-bic");
            const bickError = bankDetail.querySelector(
              ".bank_detail-bic_error"
            );
            const changeBtn = bankDetail.querySelector(".bank-detail-button");

            changeBtn.onclick = (e) => {
              e.preventDefault();
              if (!currentAccount.value) {
                showErrorValidation("Обязательное поле", currentAccountError);
              }
              if (currentAccount.value.length != 20) {
                showErrorValidation(
                  "Cчет должен состоять из 20 цифр",
                  currentAccountError
                );
              }
              if (!bankName.value) {
                showErrorValidation("Обязательное поле", bankNameError);
              }
              if (!correspondentAccount.value) {
                showErrorValidation(
                  "Обязательное поле",
                  correspondentAccountError
                );
              }
              if (correspondentAccount.value.length != 20) {
                showErrorValidation(
                  "Cчет должен состоять из 20 цифр",
                  correspondentAccountError
                );
              }
              if (!bic.value) {
                showErrorValidation("Обязательное поле", bickError);
              }
              if (bic.value.length != 9) {
                showErrorValidation("Бик должен состоять из 9 цифр", bickError);
              }
              if (
                currentAccount.value.length == 20 &&
                bankName.value &&
                correspondentAccount.value.length == 20 &&
                bic.value == 9
              ) {
                const dataObj = [
                  {
                    account_requisites: {
                      account_requisites: currentAccount.value,
                      bank: bankName.value,
                      kpp: correspondentAccount.value,
                      bic: bic.value,
                      id: bankDetailId,
                    },
                  },
                ];
                const data = JSON.stringify(dataObj);

                fetch(`/api/v1/requisites/${detailsId}/update/`, {
                  method: "UPDATE",
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
        });
        if (newBankDetailForm) {
          const currentAccount = newBankDetailForm.querySelector(
            ".bank_detail-current_account"
          );
          const currentAccountError = newBankDetailForm.querySelector(
            ".bank_detail-current_account_error"
          );
          const bankName = newBankDetailForm.querySelector(".bank_detail-bank");
          const bankNameError = newBankDetailForm.querySelector(
            ".bank_detail-bank_error"
          );
          const correspondentAccount = newBankDetailForm.querySelector(
            ".bank_detail-correspondent_account"
          );
          const correspondentAccountError = newBankDetailForm.querySelector(
            ".bank_detail-correspondent_account_error"
          );
          const bic = newBankDetailForm.querySelector(".bank_detail-bic");
          const bickError = newBankDetailForm.querySelector(
            ".bank_detail-bic_error"
          );
          const changeBtn = newBankDetailForm.querySelector(
            ".bank-detail-button"
          );
          changeBtn.onclick = (e) => {
            e.preventDefault();
            if (!currentAccount.value) {
              showErrorValidation("Обязательное поле", currentAccountError);
            }
            if (currentAccount.value.length != 20) {
              showErrorValidation(
                "Cчет должен состоять из 20 цифр",
                currentAccountError
              );
            }
            if (!bankName.value) {
              showErrorValidation("Обязательное поле", bankNameError);
            }
            if (!correspondentAccount.value) {
              showErrorValidation(
                "Обязательное поле",
                correspondentAccountError
              );
            }
            if (correspondentAccount.value.length != 20) {
              showErrorValidation(
                "Cчет должен состоять из 20 цифр",
                correspondentAccountError
              );
            }
            if (!bic.value) {
              showErrorValidation("Обязательное поле", bickError);
            }
            if (bic.value.length != 9) {
              showErrorValidation("Бик должен состоять из 9 цифр", bickError);
            }
            if (
              currentAccount.value.length == 20 &&
              bankName.value &&
              correspondentAccount.value.length == 20 &&
              bic.value == 9
            ) {
              const dataObj = [
                {
                  account_requisites: {
                    account_requisites: currentAccount.value,
                    bank: bankName.value,
                    kpp: correspondentAccount.value,
                    bic: bic.value,
                  },
                },
              ];
              const data = JSON.stringify(dataObj);
              fetch(`/api/v1/requisites/${detailsId}/update/`, {
                method: "UPDATE",
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
  }
});
