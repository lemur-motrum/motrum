import { getCookie } from "/static/core/js/functions.js";

let catalogWrapper = document.querySelector('[catalog-elem="wrapper"]');
if (catalogWrapper) {
  let catalogContainer = catalogWrapper.querySelector(
    '[catalog-elem="container"]'
  );
  let catalogButton = catalogWrapper.querySelector('[catalog-elem="button"]');

  catalogButton.addEventListener("click", function (event) {
    let productsCount = catalogContainer.querySelectorAll(
      '[catalog-elem="product-item"]'
    ).length;
    let productsVendorId = "1";
    let data = {
      count: productsCount,
      vendor: productsVendorId,
      // "page": 3
    };

    let params = new URLSearchParams(data);

    let csrfToken = getCookie("csrftoken");

    fetch(`/api/v1/product/load-ajax-product-list/?${params.toString()}`, {
      method: "GET",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then(function (data) {
        console.log(data);
        for (let i in data.data) {
          console.log(data.data[i]);
          addAjaxCatalogItem(data.data[i]);
          console.log(data.next);
        }
      });
  });

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
