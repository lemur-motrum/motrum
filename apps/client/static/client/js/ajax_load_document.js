import { getCookie } from "/static/core/js/functions.js";

let currentUrl = new URL(window.location.href);
window.addEventListener("DOMContentLoaded", () => {
  const catalogWrapper = document.querySelector('[document-elem="wrapper"]');
  if (catalogWrapper) {
    let paramsArray = [];
    const btn = catalogWrapper.querySelector(".add_more");
    const catalogContainer = catalogWrapper.querySelector(
      '[document-elem="container"]'
    );
    const loader = catalogWrapper.querySelector(".loader");
    let productCount = 0;

    function loadItems(pagintaionFn = false) {
      let data = {
        count: !pagintaionFn ? productCount : 5,
      };

      let params = new URLSearchParams(data);
      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/order/load-ajax-document-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then(function (data) {
          console.log(data);
          for (let i in data.data) {
            addAjaxCatalogItem(data.data[i]);
          }
          loader.classList.add("hide");
        });
    }

    window.onload = () => {
      loadItems(false, false, false);
    };

    function renderCatalogItem(orderData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[lk-elem="document-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }
  }
});
