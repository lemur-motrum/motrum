import { getCookie, getDigitsNumber } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".vacancy_container");

  const csrfToken = getCookie("csrftoken");

  const currentUrl = new URL(window.location.href);
  const urlParams = currentUrl.searchParams;

  if (wrapper) {
    const catalogContainer = wrapper.querySelector(
      '[project-elem="container"]'
    );
    const loader = catalogContainer.querySelector(".loader");

    let filtersParamsArray = [];

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

    loadItems();

    const filtersElems = wrapper.querySelectorAll(".filter_elem");
    filtersElems.forEach((filterElem) => {
      filterElem.onclick = () => {
        const vacancyAttribute = filterElem.getAttribute("slug");
        filterElem.classList.toggle("active");
        if (filterElem.classList.contains("active")) {
          filtersParamsArray.push(vacancyAttribute);
          urlParams.set("vacancy", filtersParamsArray.join(","));
        } else {
          filtersParamsArray = filtersParamsArray.filter(
            (el) => el != vacancyAttribute
          );
          filtersParamsArray.length > 0
            ? urlParams.set("vacancy", filtersParamsArray.join(","))
            : urlParams.delete("vacancy");
        }
        history.pushState({}, "", currentUrl);
      };
    });

    function loadItems() {
      fetch("/api/v1/vacancy/load-ajax-vacancy-list/", {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((response) => {
          loader.classList.add("hide");
          if (response.data.length > 0) {
            for (let i in response.data) {
              addAjaxCatalogItem(response.data[i]);
            }
          } else {
            catalogContainer.innerHTML =
              "<div class='none_content'>Вакансий нет</div>";
          }
        })
        .catch((error) => console.error(error));
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
