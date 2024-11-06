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

    searchInput.oninput = () => {
      if (searchInput.value.length >= 3) {
        searchElemsContainer.classList.add("show");
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
                searchElemsContainer.innerHTML += `<div class="product_search_item">${el.name}</div>`;
              });
              searchElemsContainer.innerHTML += `<div class="small_loader"></div>`;
            } else if (response.data.length > 0 && response.data.length < 9) {
              response.data.forEach((el) => {
                searchElemsContainer.innerHTML += `<div class="product_search_item">${el.name}</div>`;
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
                        searchElemsContainer.innerHTML += `<div class="product_search_item">${el.name}</div>`;
                      });
                      searchElemsContainer.innerHTML += `<div class="small_loader"></div>`;
                    } else {
                      response.data.forEach((el) => {
                        searchElemsContainer.innerHTML += `<div class="product_search_item">${el.name}</div>`;
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
      }
    };
    function searchProductLogic(container) {
      const searchProductItems = container.querySelectorAll(
        ".product_search_item"
      );
      searchProductItems.forEach((searchProductItem) => {
        searchProductItem.onclick = () => {
          searchInput.value = searchProductItem.textContent;
          container.classList.remove("show");
        };
      });
    }
  }
});
