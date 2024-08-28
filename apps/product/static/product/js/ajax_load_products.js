import { getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const catalogWrapper = document.querySelector('[catalog-elem="wrapper"]');
  if (catalogWrapper) {
    const loader = catalogWrapper.querySelector(".loader");
    const btn = catalogWrapper.querySelector(".add_more");
    const catalogContainer = catalogWrapper.querySelector(
      '[catalog-elem="container"]'
    );
    const catalogButton = catalogWrapper.querySelector(
      '[catalog-elem="button"]'
    );
    let productsCount = catalogContainer.querySelectorAll(
      '[catalog-elem="product-item"]'
    ).length;
    // // let productsVendorId = "1";
    const category = document
      .querySelector("[data-category-id]")
      .getAttribute("data-category-id");
    const group = document
      .querySelector("[data-group-id]")
      .getAttribute("data-group-id");

    window.onload = () => {
      let data = {
        count: productsCount,
        sort: "+",
        page: "1",
        category: category,
        group: group,
        // vendor: productsVendorId,
      };
      let params = new URLSearchParams(data);

      console.log(category);
      let csrfToken = getCookie("csrftoken");
      // fetch(`/api/v1/product/${location}load-ajax-product-list/?${params.toString()}`, {
      fetch(`/api/v1/product/load-ajax-product-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then(function (data) {
          console.log(data);
          loader.style.display = "none";

          for (let i in data.data) {
            addAjaxCatalogItem(data.data[i]);
          }
          btn.classList.add("show");
          // addCart();
        });
    };
    function renderCatalogItem(productData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[catalog-elem="product-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, productData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);

      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }
  }
});
