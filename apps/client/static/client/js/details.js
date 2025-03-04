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
      const legalAddressHouseInput = newLegalEntityForm.querySelector(
        ".legal-adress-adress-appartments"
      );
      const legalAddressHouseError = newLegalEntityForm.querySelector(
        ".new_legal_entity_legal_adress_appartments_error"
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
      const bic = newLegalEntityForm.querySelector(".bank-details-input-bik");
      const newLegalEntityBicError = newLegalEntityForm.querySelector(
        ".new_legal_entity_bank_bik_error"
      );
      const bicMaskOptions = {
        mask: "000000000",
      };
      const bicMask = IMask(bic, bicMaskOptions);
      const countryInput = newLegalEntityForm.querySelector(".country_input");
      const provinceInput = newLegalEntityForm.querySelector(".province_input");
      const regionInput = newLegalEntityForm.querySelector(".region_input");
      const cityInput = newLegalEntityForm.querySelector(".city_input");

      const ipSurnameInput =
        newLegalEntityForm.querySelector(".ip_surname_input");
      const ipNameInput = newLegalEntityForm.querySelector(".ip_name_input");
      const ipPatronymicInput = newLegalEntityForm.querySelector(
        ".ip_patronymic_input"
      );
      const emailInput = newLegalEntityForm.querySelector(".email_input");

      const legalEntitiesContainer = newLegalEntityForm.querySelector(
        ".legal_entitis_container"
      );
      const legalEntitiesSearchContainer = legalEntitiesContainer.querySelector(
        ".legal_entitis_search_elems"
      );
      const addNewLegalEntityBtn = legalEntitiesContainer.querySelector(
        ".add_new_legal_entity"
      );

      function enabledInputs() {
        const inputs = newLegalEntityForm.querySelectorAll("input");
        inputs.forEach((el) => {
          el.disabled = false;
        });
      }
      function clearInputs() {
        const inputs = newLegalEntityForm.querySelectorAll("input");
        inputs.forEach((el) => {
          el.value = "";
        });
      }

      innInput.oninput = () => {
        if (innInput.value.length >= 9) {
          const data = JSON.stringify({ inn: innInput.value });
          fetch("/api/v1/requisites/serch-requisites/", {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json(Text))
            .then((response) => {
              console.log("response", response);

              legalEntitiesSearchContainer.innerHTML = "";
              response.forEach((el) => {
                legalEntitiesSearchContainer.innerHTML += `
                <div class="legal_entitis_search_elem">
                  <div class="name">${
                    el["data"]["name"]["short_with_opf"]
                  }</div>
                  <div style="display:none" class="inn">${
                    el["data"]["inn"]
                  }</div>
                  <div style="display:none" class="kpp">${
                    el["data"]["kpp"] ? el["data"]["kpp"] : ""
                  }</div>
                  <div style="display:none" class="orgn">${
                    el["data"]["ogrn"]
                  }</div>
                  <div style="display:none" class="address_postal_code">${
                    el["data"]["address"]["data"]["postal_code"]
                  }</div>
                  <div style="display:none" class="address_city">
                  ${
                    el["data"]["address"]["data"]["region_with_type"]
                      ? el["data"]["address"]["data"]["region_with_type"] + ", "
                      : ""
                  }
                  ${
                    el["data"]["address"]["data"]["city"]
                      ? el["data"]["address"]["data"]["city"]
                      : el["data"]["address"]["data"]["settlement_with_type"]
                      ? el["data"]["address"]["data"]["settlement_with_type"]
                      : ""
                  }
                  </div>
                  <div style="display:none" class="address_street">${
                    el["data"]["address"]["data"]["city"]
                      ? el["data"]["address"]["data"]["settlement_with_type"]
                        ? el["data"]["address"]["data"]["settlement_with_type"]
                        : ""
                      : ""
                  }
                  ${
                    el["data"]["address"]["data"]["street_with_type"]
                      ? el["data"]["address"]["data"]["street_with_type"] + ", "
                      : ""
                  }${
                  el["data"]["address"]["data"]["house_type"]
                    ? el["data"]["address"]["data"]["house_type"] + "."
                    : ""
                }${
                  el["data"]["address"]["data"]["house"]
                    ? el["data"]["address"]["data"]["house"]
                    : ""
                } ${
                  el["data"]["address"]["data"]["block"]
                    ? el["data"]["address"]["data"]["block"]
                    : ""
                }
                  ${
                    el["data"]["address"]["data"]["block_type"]
                      ? el["data"]["address"]["data"]["block_type"]
                      : ""
                  }
                  </div>
                    <div style="display:none" class="address_apartments">${
                      el["data"]["address"]["data"]["flat_type"]
                        ? el["data"]["address"]["data"]["flat_type"]
                        : ""
                    } ${
                  el["data"]["address"]["data"]["flat"]
                    ? el["data"]["address"]["data"]["flat"]
                    : ""
                }
                  ${
                    el["data"]["address"]["data"]["room_type"]
                      ? el["data"]["address"]["data"]["room_type"]
                      : ""
                  }
                  ${
                    el["data"]["address"]["data"]["room"]
                      ? el["data"]["address"]["data"]["room"]
                      : ""
                  }
                  </div>
                  <div style="display:none" class="country">${
                    el["data"]["address"]["data"]["country"]
                  }</div>
                  <div style="display:none" class="region">${
                    el["data"]["address"]["data"]["region_with_type"]
                  }</div>
                  <div style="display:none" class="city">
                      ${
                        el["data"]["address"]["data"]["city"]
                          ? el["data"]["address"]["data"]["city"]
                          : el["data"]["address"]["data"][
                              "settlement_with_type"
                            ]
                          ? el["data"]["address"]["data"][
                              "settlement_with_type"
                            ]
                          : ""
                      }
                  </div>
                  <div style="display:none" class="ip_surname">${
                    el["data"]["fio"] ? el["data"]["fio"]["surname"] : ""
                  }</div>
                  <div style="display:none" class="ip_name">${
                    el["data"]["fio"] ? el["data"]["fio"]["name"] : ""
                  }</div>
                  <div style="display:none" class="ip_patronymic">${
                    el["data"]["fio"] ? el["data"]["fio"]["patronymic"] : ""
                  }</div>
                  <div style="display:none" class="email">${
                    el["data"]["emails"] && el["data"]["emails"].length > 0
                      ? el["data"]["emails"][0]
                      : ""
                  }</div>
                  <div style="display:none" class="phone">
                  ${
                    el["data"]["phones"] && el["data"]["phones"].length > 0
                      ? el["data"]["phones"][0]
                      : ""
                  }
                  </div>
                  <div style="display:none" class="province">
                  ${
                    el["data"]["address"]["data"]["area_with_type"]
                      ? el["data"]["address"]["data"]["area_with_type"]
                      : ""
                  }
                  </div>
                </div>`;
              });

              legalEntitiesContainer.classList.add("show");
              const searchElems = legalEntitiesContainer.querySelectorAll(
                ".legal_entitis_search_elem"
              );
              searchElems.forEach((el) => {
                el.onclick = () => {
                  const name = el.querySelector(".name");
                  const inn = el.querySelector(".inn");
                  const kpp = el.querySelector(".kpp");
                  const orgn = el.querySelector(".orgn");
                  const postalIndex = el.querySelector(".address_postal_code");
                  const leagalCity = el.querySelector(".address_city");
                  const leagalAddressOne = el.querySelector(".address_street");
                  const legalAddressTwo = el.querySelector(
                    ".address_apartments"
                  );
                  const country = el.querySelector(".country");
                  const province = el.querySelector(".province");
                  const region = el.querySelector(".region");
                  const city = el.querySelector(".city");
                  const ipName = el.querySelector(".ip_name");
                  const ipSurname = el.querySelector(".ip_surname");
                  const ipPatronymic = el.querySelector(".ip_patronymic");

                  const email = el.querySelector(".email");
                  const phone = el.querySelector(".phone");

                  const inputs = newLegalEntityForm.querySelectorAll("input");
                  inputs.forEach((el) => {
                    el.value = "";
                  });

                  nameInput.value = name.textContent;
                  innInput.value = inn.textContent;
                  kppInput.value = kpp.textContent;
                  orgnInput.value = orgn.textContent;
                  legalIndexInput.value = postalIndex.textContent;
                  legalCityInput.value = leagalCity.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  legalAdressInput.value = leagalAddressOne.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  legalAddressHouseInput.value = legalAddressTwo.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  countryInput.value = country.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  provinceInput.value = province.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  regionInput.value = region.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  cityInput.value = city.textContent.replace(/ +/g, " ").trim();
                  ipNameInput.value = ipName.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  ipSurnameInput.value = ipSurname.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  ipPatronymicInput.value = ipPatronymic.textContent
                    .replace(/ +/g, " ")
                    .trim();
                  emailInput.value = email.textContent
                    ? email.textContent.replace(/ +/g, " ").trim()
                    : "";
                  phone.textContent.replace(/ +/g, " ").trim()
                    ? (phoneInput.value = phone.textContent)
                    : "";

                  enabledInputs();
                  legalEntitiesContainer.classList.remove("show");
                };
              });
              addNewLegalEntityBtn.onclick = () => {
                enabledInputs();
                let value = innInput.value;
                clearInputs();
                innInput.value = value;
                legalEntitiesContainer.classList.remove("show");
              };
            });
        }
      };

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

        if (innInput.value.length < 12 && !kppInput.value) {
          showErrorValidation("Обязаятельное поле", newLegalEntityKppError);
          validate = false;
        }
        if (
          innInput.value.length < 12 &&
          kppInput.value &&
          kppInput.value.length < 9
        ) {
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
        // if (!legalAdressInput.value) {
        //   showErrorValidation(
        //     "Обязательное поле",
        //     newLegalEntityLegalAdressError
        //   );
        //   validate = false;
        // }
        // if (!legalAddressHouseInput.value) {
        //   showErrorValidation("Обязательное поле", legalAddressHouseError);
        //   validate = false;
        // }
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
        if (!bic.value) {
          showErrorValidation("Обязательное поле", newLegalEntityBicError);
          validate = false;
        }
        if (bic.value && bic.value.length < 9) {
          showErrorValidation(
            "Бик должен состоять из 9 цифр",
            newLegalEntityBicError
          );
          validate = false;
        }
        if (validate) {
          const dataObj = {
            requisites: {
              client: clientId,
              legal_entity: nameInput.value,
              inn: innInput.value,
              surname: ipSurnameInput.value ? ipSurnameInput.value : null,
              name: ipNameInput.value ? ipNameInput.value : null,
              patronymic: ipPatronymicInput.value
                ? ipPatronymicInput.value
                : null,
              phone: phoneInput.value,
              email: emailInput.value ? emailInput.value : null,
            },
            requisitesKpp: {
              kpp: kppInput.value,
              ogrn: orgnInput.value,
            },
            adress: {
              legal_adress: {
                country: countryInput.value ? countryInput.value : null,
                region: regionInput.value ? regionInput.value : null,
                province: provinceInput.value ? provinceInput.value : null,
                post_code: legalIndexInput.value,
                city: cityInput.value ? cityInput.value : null,
                legal_address1: legalAdressInput.value,
                legal_address2: legalAddressHouseInput.value
                  ? legalAddressHouseInput.value
                  : null,
              },
            },
            account_requisites: [
              {
                account_requisites: currentAccount.value,
                bank: bank.value,
                kpp: correspondentAccount.value,
                bic: bic.value,
              },
            ],
          };

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
              console.log("ok");
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
          btn.textContent = "Изменить";
        }
      };
    });
  }
});
