import { getCookie, getDigitsNumber } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".vacancy_container");

  const csrfToken = getCookie("csrftoken");

  const currentUrl = new URL(window.location.href);
  const urlParams = currentUrl.searchParams;

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
        filtersElems.forEach((el) => (el.disabled = true));
        loadItems();
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
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[vacancy-elem="vacancy-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }
  }
});
