import {
  getCookie,
  getDigitsNumber,
  showErrorValidation,
  maskOptions,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";
import { successModal } from "/static/core/js/sucessModal.js";

const csrfToken = getCookie("csrftoken");
const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".vacancy_container");

  if (wrapper) {
    const loader = wrapper.querySelector(".loader");
    const noneContent = wrapper.querySelector(".none_content");
    const catalogContainer = wrapper.querySelector(
      '[project-elem="container"]'
    );
    const filtersElems = wrapper.querySelectorAll(".filter_elem");
    const canceledBtn = wrapper.querySelector(".canceled_btn");

    let filtersParamsArray = [];

    const vacancyGetParam = urlParams.get("vacancy_category");

    function truncate(str, maxlength) {
      return str.length > maxlength
        ? str.slice(0, 3) + "…" + str.slice(maxlength - 4, maxlength - 1)
        : str;
    }

    if (vacancyGetParam) {
      filtersParamsArray = vacancyGetParam.split(",");
      filtersParamsArray.forEach((param) => {
        if (filtersParamsArray.length > 0) {
          for (let i = 0; i < filtersElems.length; i++) {
            if (filtersElems[i].getAttribute("slug") == param) {
              console.log("Есть такое");
              filtersElems[i].classList.add("active");
            }
          }
        }
      });
    }
    const filterButton = wrapper.querySelector(".mobile_filter_button");
    const filterContainer = wrapper.querySelector(".filter_container");
    filterButton.onclick = () => {
      filterContainer.classList.add("show");
    };
    const closeBtn = filterContainer.querySelector(".close_btn");
    closeBtn.onclick = () => {
      filterContainer.classList.remove("show");
    };

    loadItems();

    filtersElems.forEach((filterElem) => {
      filterElem.onclick = () => {
        catalogContainer.innerHTML = "";
        noneContent.classList.remove("show");
        loader.classList.remove("hide");
        const vacancyAttribute = filterElem.getAttribute("slug");
        filterElem.classList.toggle("active");
        if (filterElem.classList.contains("active")) {
          filtersParamsArray.push(vacancyAttribute);
          urlParams.set("vacancy_category", filtersParamsArray.join(","));
        } else {
          filtersParamsArray = filtersParamsArray.filter(
            (el) => el != vacancyAttribute
          );
          filtersParamsArray.length > 0
            ? urlParams.set("vacancy_category", filtersParamsArray.join(","))
            : urlParams.delete("vacancy_category");
        }
        if (filterContainer.classList.contains("show")) {
          filterContainer.classList.remove("show");
        }
        filtersElems.forEach((el) => (el.disabled = true));
        loadItems();
        // filterContainer.classList.add("show");
      };
    });

    canceledBtn.onclick = () => {
      catalogContainer.innerHTML = "";
      noneContent.classList.remove("show");
      loader.classList.remove("hide");
      filtersElems.forEach((el) => el.classList.remove("active"));
      filtersParamsArray = [];
      urlParams.delete("vacancy_category");
      filtersElems.forEach((el) => (el.disabled = true));
      if (filterContainer.classList.contains("show")) {
        filterContainer.classList.remove("show");
      }
      loadItems();
    };

    function getVacancies() {
      const interval = setInterval(() => {
        const vacancyItems = wrapper.querySelectorAll(".vacancy_item");
        if (vacancyItems.length > 0) {
          clearInterval(interval);
        }
        vacancyItems.forEach((vacancyItem) => {
          const showContentBtn = vacancyItem.querySelector(".show_btn");
          const prices = vacancyItem.querySelectorAll(".price");
          prices.forEach((price) => {
            getDigitsNumber(price, price.textContent);
          });

          showContentBtn.onclick = () => {
            vacancyItem.classList.toggle("is_open");
            if (vacancyItem.classList.contains("is_open")) {
              showContentBtn.textContent = "скрыть";
            } else {
              showContentBtn.textContent = "подробнее";
            }
          };
          overlayLogic(vacancyItem);
        });
      }, 1);
    }

    function loadItems() {
      const data = {
        vacancy_category:
          filtersParamsArray.length > 0 ? filtersParamsArray : "",
      };

      const params = new URLSearchParams(data);

      fetch(`/api/v1/vacancy/load-ajax-vacancy-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((response) => {
          loader.classList.add("hide");
          filtersElems.forEach((el) => (el.disabled = false));
          if (response.data.length > 0) {
            if (response.data.length > 6) {
              filterContainer.classList.add("show");
            }
            catalogContainer.innerHTML = "";
            for (let i in response.data) {
              addAjaxCatalogItem(response.data[i]);
            }
            getVacancies();
          } else {
            catalogContainer.innerHTML = "";
            noneContent.classList.add("show");
          }
        })
        .catch((error) => console.error(error));
      history.pushState({}, "", currentUrl);
    }

    function renderCatalogItem(orderData) {
      const ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      const ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[vacancy-elem="vacancy-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      const renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }

    function resetInputs(form, descr) {
      const inputs = form.querySelectorAll("input");
      const textArea = form.querySelector("textarea");
      inputs.forEach((el) => {
        el.value = "";
      });
      textArea.value = "";
      descr.textContent = "Прикрепить резюме";
    }

    function overlayLogic(container) {
      const submitBtn = container.querySelector(".submit_btn");
      const overlay = container.querySelector(".overlay_vacancy");
      const closeBtn = overlay.querySelector(".close_btn");
      const formContainer = overlay.querySelector(".vacancy_modal_form");
      const vacancyName = formContainer.getAttribute("vacancy-name");
      const nameInput = formContainer.querySelector(".name_input");
      const nameError = formContainer.querySelector(".name_error");
      const phoneInput = formContainer.querySelector(".phone_input");
      const phoneError = formContainer.querySelector(".phone_error");
      const filelabel = overlay.querySelector(".file_label");
      const fileLabelDescription = filelabel.querySelector(".file_description");
      const fileInput = filelabel.querySelector(".file_input");
      const fileError = filelabel.querySelector(".file_error");
      const vacancyTextArea = formContainer.querySelector(".vacancy_textarea");
      const formSubmitBtn = formContainer.querySelector(".submit_btn");

      const mask = IMask(phoneInput, maskOptions);

      function closeOverlay() {
        overlay.classList.remove("visible");
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
        document.body.style.overflowY = "auto";
        resetInputs(formContainer, fileLabelDescription);
      }

      submitBtn.onclick = () => {
        ym(37794920, "reachGoal", "open_vacancy_popup");
        overlay.classList.add("show");
        setTimeout(() => {
          overlay.classList.add("visible");
        }, 600);
        document.body.style.overflowY = "hidden";
      };

      closeBtn.onclick = () => closeOverlay();

      fileInput.addEventListener("change", function () {
        const file = this.files[0];
        const array = file["name"].split(".");
        const fileName = array[0];
        const fileType = array.at(-1);
        fileLabelDescription.textContent =
          truncate(fileName, 8) + "." + fileType;
      });

      formSubmitBtn.onclick = () => {
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
        if (!fileInput.value) {
          validate = false;
          showErrorValidation("Файл не прикреплен", fileError);
        }
        if (validate) {
          const file = fileInput.files[0];

          const formData = new FormData();
          formData.append("file", file);
          formData.append("name", nameInput.value);
          formData.append("phone", phoneInput.value);
          formData.append("message", vacancyTextArea.value);
          formData.append("vacancy", vacancyName);

          setPreloaderInButton(formSubmitBtn);

          fetch("/api/v1/vacancy/send-vacancy/", {
            method: "POST",
            body: formData,
            headers: {
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            if (response.status >= 200 && response.status < 300) {
              ym(37794920, "reachGoal", "send_current_vacancy_form");
              closeOverlay();
              successModal(
                `Спасибо за отклик, мы рассмотрим Ваше резюме и вернемся с обратной связью`
              );
              hidePreloaderAndEnabledButton(formSubmitBtn);
            } else {
              setErrorModal();
            }
          });
        }
      };
    }
  }
});
