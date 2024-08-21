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
    // let productsVendorId = "1";
    let data = {
      count: productsCount,
      sort: "+",
      page: "1",
      // vendor: productsVendorId,

    };

    let params = new URLSearchParams(data);
    let location = window.location.pathname
    let csrfToken = getCookie("csrftoken");
    // fetch(`/api/v1/product/${location}load-ajax-product-list/?${params.toString()}`, {
    fetch(`/api/v1${location}/load-ajax-product-list/?${params.toString()}`, {
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
        addCart()
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

function addCart() {
  const clientAdd = document.querySelectorAll(".add-cart-button");
  if (clientAdd) {
    clientAdd.forEach((element) => {
      element.addEventListener("click", () => {

        let el = element.getAttribute("data-id-product");
        console.log(el)
        let cart = getCookie("cart");
        console.log(cart)
        let csrfToken = getCookie("csrftoken");

        if (!cart) {
          let dataArr = {
          };

          let data = JSON.stringify(dataArr);
          let csrfToken = getCookie("csrftoken");
          let endpoint = "/api/v1/cart/add-cart/"
          fetch(endpoint, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              console.log(data);
            });
          
        }
        else{
          cart = getCookie("cart");
          let dataArr = {
            "cart": cart,
            "product":el,
            "quantity":1,
          };
          
          let data = JSON.stringify(dataArr);
          let csrfToken = getCookie("csrftoken");

          let endpoint = `/api/v1/cart/${cart}/save-product/`
          fetch(endpoint, {
            method: "POST",
            body:data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              console.log(data);
              cart = getCookie("cart");
            });
          
        }

  
      })
    })
  }
}
