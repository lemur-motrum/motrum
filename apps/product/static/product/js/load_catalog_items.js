import { getCookie } from "/static/core/js/functions.js";

// ЮРИНА ФУНКЦИЯ ДЛЯ АДЖАКС ЗАГРУЗКИ АЙТЕМОВ ТОВАРОВ
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
    let category = document
      .querySelector("[data-category-id]")
      .getAttribute("data-category-id");
    let group = document
      .querySelector("[data-group-id]")
      .getAttribute("data-group-id");

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
        for (let i in data.data) {
          addAjaxCatalogItem(data.data[i]);
        }
        addCart();
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

// ФУНКЦИЯ ДОБАВИТЬ В КОРЗИНУ ТЕСТ ТУТ И ДОБАВЛЯЕТ И КОРЗИНУ И ДОБАВЛЯЕТ ПРОДУКТЫ
function addCart() {
  const clientAdd = document.querySelectorAll(".add-cart-button");
  if (clientAdd) {
    clientAdd.forEach((element) => {
      element.addEventListener("click", () => {
        let el = element.getAttribute("data-id-product");
        console.log(el);
        let cart = getCookie("cart");
        console.log(cart);
        let csrfToken = getCookie("csrftoken");

        if (!cart) {
          let dataArr = {};

          let data = JSON.stringify(dataArr);
          let csrfToken = getCookie("csrftoken");
          let endpoint = "/api/v1/cart/add-cart/";
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
        } else {
          cart = getCookie("cart");
          let dataArr = {
            cart: cart,
            product: el,
            quantity: 1,
          };

          let data = JSON.stringify(dataArr);
          let csrfToken = getCookie("csrftoken");

          let endpoint = `/api/v1/cart/${cart}/save-product/`;
          fetch(endpoint, {
            method: "POST",
            body: data,
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
      });
    });
  }
}

// ФУНКЦИЯ ИЗМЕНИТЬ КОЛИЧЕСТВО ТОВАР В КОРЗИНЕ ТЕСТ
function UpdateProductCart() {
  const clientAdd = document.querySelectorAll(".button-cart-update");
  if (clientAdd) {
    clientAdd.forEach((element) => {
      element.addEventListener("click", () => {
        let el = element.getAttribute("data-id-cart-product");
        console.log(el);
        let cart = getCookie("cart");
        console.log(cart);
        let csrfToken = getCookie("csrftoken");

        cart = getCookie("cart");
        let dataArr = {
          quantity: 4,
        };

        let data = JSON.stringify(dataArr);

        let endpoint = `/api/v1/cart/${el}/update-product/`;
        fetch(endpoint, {
          method: "UPDATE",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
          });
      });
    });
  }
}
UpdateProductCart();
// ФУНКЦИЯ УДАЛИТЬ ТОВАР В КОРЗИНЕ ТЕСТ
function DelProductCart() {
  const clientAdd = document.querySelectorAll(".button-cart-delite");
  if (clientAdd) {
    clientAdd.forEach((element) => {
      element.addEventListener("click", () => {
        let el = element.getAttribute("data-id-cart-product");
        console.log(el);
        let cart = getCookie("cart");
        console.log(cart);
        let csrfToken = getCookie("csrftoken");

        let endpoint = `/api/v1/cart/${el}/delete-product/`;
        fetch(endpoint, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
          });
      });
    });
  }
}
DelProductCart();


// ФУНКЦИЯ ДОБАВИТЬ ЗАКАЗ пользователем ТЕСТ
function addOrder() {
  const clientAdd = document.querySelectorAll(".button-cart-save-user");
  
  if (clientAdd) {
    clientAdd.forEach((element) => {
      element.addEventListener("click", () => {
        let el = element.getAttribute("data-id-cart-product");
        console.log(el);
        let cart = getCookie("cart");
        console.log(cart);
        let csrfToken = getCookie("csrftoken");
        let dataArr = 
          {
            cart: cart,
            requisites: 32,
            account_requisites: 1,
          }
        
        let data = JSON.stringify(dataArr);
        let endpoint = `/api/v1/order/add_order/`;
        fetch(endpoint, {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
          });
      });
    });
  }
}
addOrder();
