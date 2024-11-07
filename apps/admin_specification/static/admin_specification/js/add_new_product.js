import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
import {
  inputValidation,
  inputValidationQuantity,
} from "../js/add_new_product_without_cart.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const globalCartWrapper = document.querySelector(".spetification_table");
  if (globalCartWrapper) {
    const addNewProductContainer = globalCartWrapper.querySelector(
      ".add_new_product_container"
    );
    const searchInput = addNewProductContainer.querySelector(".search_input");
    const searchElemsContainer =
      addNewProductContainer.querySelector(".search_container");
    const addProductButton =
      addNewProductContainer.querySelector(".add_product");
    const addNewProductButton =
      addNewProductContainer.querySelector(".add_new_product");
    const deleteSearchButton = addNewProductContainer.querySelector(
      ".delete_search_details_btn"
    );

    searchInput.oninput = () => {
      if (searchInput.value.length >= 3) {
        searchElemsContainer.classList.add("show");
        deleteSearchButton.classList.add("show");
        searchElemsContainer.innerHTML = "<div class='small_loader'></div>";
        const objData = {
          search_text: searchInput.value,
          count: 0,
          count_last: 9,
        };
        const data = JSON.stringify(objData);
        fetch("/api/v1/product/search-product/", {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status === 200) {
              return response.json();
            } else {
              throw new Error("Ошибка");
            }
          })
          .then((response) => {
            searchElemsContainer.innerHTML = "";
            if (response.data.length >= 9) {
              response.data.forEach((el) => {
                searchElemsContainer.innerHTML += `<div product-id="${el.id}" class="product_search_item">${el.name}</div>`;
              });
              searchElemsContainer.innerHTML += `<div class="small_loader search"></div>`;
            } else if (response.data.length > 0 && response.data.length < 9) {
              response.data.forEach((el) => {
                searchElemsContainer.innerHTML += `<div product-id="${el.id}" class="product_search_item">${el.name}</div>`;
              });
            } else {
              searchElemsContainer.innerHTML += `<div class="product_search_item_none">Таких товаров нет, попробуйте добавить новый товар</div>`;
            }
            searchElemsContainer.onscroll = () => {
              if (
                searchElemsContainer.scrollHeight -
                  searchElemsContainer.scrollTop <=
                searchElemsContainer.offsetHeight
              ) {
                objData["count"] += 10;
                objData["count_last"] += 10;
                const data = JSON.stringify(objData);
                fetch("/api/v1/product/search-product/", {
                  method: "POST",
                  body: data,
                  headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                  },
                })
                  .then((response) => {
                    if (response.status === 200) {
                      return response.json();
                    } else {
                      throw new Error("Ошибка");
                    }
                  })
                  .then((response) => {
                    if (searchElemsContainer.querySelector(".small_loader")) {
                      searchElemsContainer
                        .querySelector(".small_loader")
                        .remove();
                    }
                    if (response.data.length >= 9) {
                      response.data.forEach((el) => {
                        searchElemsContainer.innerHTML += `<div product-id="${el.id}" class="product_search_item">${el.name}</div>`;
                      });
                      searchElemsContainer.innerHTML += `<div class="small_loader search"></div>`;
                    } else {
                      response.data.forEach((el) => {
                        searchElemsContainer.innerHTML += `<div product-id="${el.id}" class="product_search_item">${el.name}</div>`;
                      });
                    }
                    searchProductLogic(searchElemsContainer);
                  });
              }
            };
            searchProductLogic(searchElemsContainer);
          });
      } else {
        searchElemsContainer.innerHTML = "";
        searchElemsContainer.classList.remove("show");
        deleteSearchButton.classList.remove("show");
        addProductButton.classList.remove("show");
      }
    };
    deleteSearchButton.onclick = () => {
      searchInput.value = "";
      searchElemsContainer.classList.remove("show");
      if (addProductButton.getAttribute("product-id")) {
        addProductButton.setAttribute("product-id", "");
      }
      addProductButton.classList.remove("show");
      deleteSearchButton.classList.remove("show");
    };

    addProductButton.onclick = () => {
      const cartId = getCookie("cart");
      const productId = addProductButton.getAttribute("product-id");
      const objData = {
        cart: cartId,
        product: productId,
        quantity: 1,
      };
      addProductButton.textContent = "";
      addProductButton.innerHTML = "<div class='small_loader'></div>";
      const data = JSON.stringify(objData);
      fetch(`/api/v1/cart/${cartId}/save-product/`, {
        method: "POST",
        body: data,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.status == 200) {
          window.location.reload();
        } else {
          throw new Error("Ошибка");
        }
      });
    };

    const newItemContainer = globalCartWrapper.querySelector(
      ".new_item_container"
    );
    if (newItemContainer) {
      const nameInput = newItemContainer.querySelector(
        ".new_item_container_name_input"
      );
      const articleInput = newItemContainer.querySelector(
        ".new_item_container_article_input"
      );
      const priceOnceInput = newItemContainer.querySelector(".price_input");
      const quantityInput = newItemContainer.querySelector(".quantity_input");
      const persentSaleInput = newItemContainer.querySelector(".persent_sale");
      const addPersentSaleInput = newItemContainer.querySelector(".add_sale");
      const calendarInput = newItemContainer.querySelector(
        ".new_item_container_calendar"
      );
      const addNewItemInCartButton = newItemContainer.querySelector(
        ".add_new_item_in_cart"
      );
      let validate = true;
      addNewItemInCartButton.onclick = () => {
        function inputValidate(input) {
          if (!input.value) {
            validate = false;
            input.style.border = "1px solid red";
          }
        }
        inputValidate(nameInput);
        inputValidate(articleInput);
        inputValidate(priceOnceInput);
        inputValidate(quantityInput);
        inputValidate(persentSaleInput);
        inputValidate(addPersentSaleInput);
        inputValidate(calendarInput);
      };
      // if (validate === ) {
      //   fetch("");
      // }
    }

    function searchProductLogic(container) {
      const searchProductItems = container.querySelectorAll(
        ".product_search_item"
      );
      searchProductItems.forEach((searchProductItem) => {
        searchProductItem.onclick = () => {
          searchInput.value = searchProductItem.textContent;
          container.classList.remove("show");
          addProductButton.setAttribute(
            "product-id",
            searchProductItem.getAttribute("product-id")
          );
          addProductButton.classList.add("show");
        };
      });
    }
  }
});
