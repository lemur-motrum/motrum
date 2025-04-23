import {
  showErrorValidation,
  getCookie,
  getDigitsNumber,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";
import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

function addNewProductLogic(container) {
  if (container) {
    const addNewProductContainer = container.querySelector(
      ".add_new_product_container"
    );
    const searchInput = addNewProductContainer.querySelector(".search_input");
    const searchElemsContainer =
      addNewProductContainer.querySelector(".search_container");

    const searchElemsContainerWrapper = searchElemsContainer.querySelector(
      ".search_elems_contaner"
    );
    const addProductContainer = addNewProductContainer.querySelector(
      ".add_product_container"
    );
    const error = addNewProductContainer.querySelector(".add_product_error");

    const addProductButton =
      addNewProductContainer.querySelector(".add_product");
    const addNewProductButton =
      addNewProductContainer.querySelector(".add_new_product");
    const deleteSearchButton = addNewProductContainer.querySelector(
      ".delete_search_details_btn"
    );
    const loader = searchElemsContainer.querySelector(".loader");
    const smallLoader = searchElemsContainer.querySelector(".small_loader");

    let count = 0;
    let countLast = 9;
    let finish = false;

    function getProducts() {
      const objData = {
        search_text: searchInput.value,
        count: count,
        count_last: countLast,
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
            loader.classList.add("hide");

            return response.json();
          } else {
            setErrorModal();
            throw new Error("Ошибка");
          }
        })
        .then((response) => {
          if (response.data.length >= 9) {
            smallLoader.classList.remove("show");
            response.data.forEach((el) => {
              searchElemsContainerWrapper.innerHTML += `<div product-id="${el.id}" class="product_search_item"><span class="name">${el.name}</span><span class="search_button">Добавить</span></div>`;
            });
          } else if (response.data.length > 0 && response.data.length < 9) {
            smallLoader.classList.remove("show");
            response.data.forEach((el) => {
              searchElemsContainerWrapper.innerHTML += `<div product-id="${el.id}" class="product_search_item"><span class="name">${el.name}</span><span class="search_button">Добавить</span></div>`;
            });
          } else {
            if (count == 0 && countLast == 9) {
              smallLoader.classList.remove("show");
              searchElemsContainerWrapper.innerHTML += `<div class="product_search_item_none">Таких товаров нет, попробуйте добавить новый товар</div>`;
            } else {
              smallLoader.classList.remove("show");
              finish = true;
              return;
            }
          }
          count += 9;
          countLast += 9;
          searchProductLogic(searchElemsContainer);
        });
    }

    searchElemsContainer.addEventListener("scroll", function () {
      if (this.scrollHeight >= this.scrollTop + this.clientHeight) {
        console.log("ff ff ff");
        if (!finish) {
          if (
            !smallLoader.classList.contains("show") &&
            count != 0 &&
            countLast != 9
          ) {
            getProducts();
            smallLoader.classList.add("show");
          }
        }
      }
    });

    function closeSearchWindow() {
      searchElemsContainer.classList.remove("show");
      deleteSearchButton.classList.remove("show");
      addProductContainer.classList.remove("show");
      searchInput.classList.remove("bordering");
    }
    function openSearchWindow() {
      searchElemsContainer.classList.add("show");
      deleteSearchButton.classList.add("show");
      searchInput.classList.add("bordering");
    }

    searchInput.oninput = () => {
      count = 0;
      countLast = 9;
      finish = false;
      if (searchInput.value.length >= 3) {
        const currentValue = searchInput.value;
        searchElemsContainerWrapper.innerHTML = "";
        loader.classList.remove("hide");
        openSearchWindow();

        setTimeout(() => {
          if (currentValue == searchInput.value) {
            getProducts();
          }
        }, 600);
      } else {
        closeSearchWindow();
      }
    };
    deleteSearchButton.onclick = () => {
      searchInput.value = "";
      closeSearchWindow();
    };
    addNewProductButton.onclick = () => {
      document
        .querySelector(".new_item_container_wrapper")
        .classList.toggle("is_open");

      if (
        document
          .querySelector(".new_item_container_wrapper")
          .classList.contains("is_open")
      ) {
        addNewProductButton.textContent = "Скрыть";
      } else {
        addNewProductButton.textContent = "Добавить новый товар";
      }
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
      // addProductButton.innerHTML = "<div class='small_loader'></div>";
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
        } else if (response.status == 409) {
          addProductButton.innerHTML = "";
          addProductButton.textContent = "Добавить этот товар";
          showErrorValidation("Этот товар уже в корзине", error);
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      });
    };

    const newItemContainer = container.querySelector(".new_item_container");
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
      const newProductError = newItemContainer.querySelector(
        ".add_new_item_in_cart_container_error"
      );
      const vendorSelect = newItemContainer.querySelector(".vendor_select");
      const vendorSelectToggle = vendorSelect.querySelector(
        ".vendor_select__toggle"
      );
      const supplierSelect = newItemContainer.querySelector(".supplier_select");
      const supplierSelectToggle = supplierSelect.querySelector(
        ".supplier_select__toggle"
      );

      const addNewItemInCartButton = newItemContainer.querySelector(
        ".add_new_item_in_cart"
      );
      const newItemContainerTotalCost = newItemContainer.querySelector(
        ".new_item_container_value_total_cost"
      );
      const motrumPrice = newItemContainer.querySelector(
        ".new_item_container_value_motrum_price"
      );
      const changeMotrumPriceInput = newItemContainer.querySelector(
        ".new_item_change_price_motrum"
      );
      const deliveryDate = newItemContainer.querySelector(".new_item_container_calendar")
      const discountInput = newItemContainer.querySelector(".add_sale")


      function closeSelectDropdown(select) {
        const options = select.querySelectorAll(".itc-select__options");

        options.forEach((el) => {
          el.onclick = () => {
            setTimeout(() => {
              select.classList.remove("itc-select_show");
            });
          };
        });
      }
      closeSelectDropdown(supplierSelect);
      closeSelectDropdown(vendorSelect);

      function changePercent() {
        if (priceOnceInput.value && quantityInput.value) {
          getDigitsNumber(
            motrumPrice,
            (priceOnceInput.value / 100) *
            (100 - persentSaleInput.value) *
            quantityInput.value
          );
        }
      }
      discountInput.addEventListener("input", function () {
        console.log("discountInput")
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
        discountInput.value = currentValue;
        if (discountInput.value == ".") {
          e.target.value = "";
        }
        if (discountInput.value == "0") {
          e.target.value = "";
        }
      })
      changeMotrumPriceInput.addEventListener("input", function () {
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
          changeMotrumPriceInput.value = currentValue;
        if (changeMotrumPriceInput.value == ".") {
          e.target.value = "";
        }
        if (changeMotrumPriceInput.value == "0") {
          e.target.value = "";
        }
      })

      persentSaleInput.addEventListener("input", function () {
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d.-]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
        persentSaleInput.value = currentValue;
        if (+persentSaleInput.value > 99.99) {
          persentSaleInput.value = 99.99;
        }
        if (+persentSaleInput.value < -99.99) {
          persentSaleInput.value = -99.99;
        }
        if (
          persentSaleInput.value.length > 1 &&
          persentSaleInput.value.at(-1) === "-"
        ) {
          persentSaleInput.target.value = persentSaleInput.value.slice(0, -1);
        }
        if (persentSaleInput.value == ".") {
          persentSaleInput.target.value = "";
        }
        if (persentSaleInput.value == "0") {
          persentSaleInput.target.value = "";
        }
        changePercent();
      });

      function changeTotalCost(input1, input2) {
        input1.addEventListener("input", function (e) {
          const currentValue = this.value
            .replace(",", ".")
            .replace(/[^.\d.-]+/g, "")
            .replace(/^([^\.]*\.)|\./g, "$1")
            .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
              return a + b + c.slice(0, 2);
            });
          input1.value = currentValue;
          if (input2.value) {
            getDigitsNumber(
              newItemContainerTotalCost,
              +input1.value * +input2.value
            );
          }
          changePercent();
        });
      }
      changeTotalCost(priceOnceInput, quantityInput);
      changeTotalCost(quantityInput, priceOnceInput);
      let validate = true;

      addNewItemInCartButton.onclick = () => {
        setPreloaderInButton(addNewItemInCartButton);
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

        if (!vendorSelectToggle.getAttribute("value")) {
          validate = false;
          vendorSelectToggle.style.borderColor = "red";
        } else {
          validate = true;
        }

        if (!supplierSelectToggle.getAttribute("value")) {
          validate = false;
          supplierSelectToggle.style.borderColor = "red";
        } else {
          validate = true;
        }

        if (
          nameInput.value &&
          articleInput.value &&
          priceOnceInput.value &&
          quantityInput.value &&
          vendorSelect.getAttribute("value")
        ) {
          validate = true;
        }
        if (validate == false) {
          addNewItemInCartButton.disabled = false;
          addNewItemInCartButton.innerHTML = "";
          addNewItemInCartButton.textContent = "Добавить товар";
        }

        if (validate === true) {
          const cartId = getCookie("cart");
          const dataObjNewProduct = {
            product: null,
            product_new: nameInput.value,
            product_new_article: articleInput.value,
            product_new_price: +priceOnceInput.value,
            cart: +cartId,
            quantity: +quantityInput.value,
            product_new_sale_motrum: persentSaleInput.value
              ? persentSaleInput.value
              : null,
            product_new_sale: addPersentSaleInput.value
              ? addPersentSaleInput.value
              : null,
            vendor: vendorSelectToggle.getAttribute("value"),
            supplier: supplierSelectToggle.getAttribute("value"),
            date_delivery: deliveryDate.value,
            sale_client: discountInput.value,
            product_price_motrum: changeMotrumPriceInput.value
          };
          const data = JSON.stringify(dataObjNewProduct);

          fetch(`/api/v1/cart/${cartId}/save-product-new/`, {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status === 200 || response.status === 201) {
                window.location.reload();
              } else if (response.status === 409) {
                return response.json();
              } else {
                setErrorModal();
                throw new Error("Ошибка");
              }
            })
            .then((response) => {
              if (response.status == "product_in_okt") {
                hidePreloaderAndEnabledButton(addNewItemInCartButton);
                showErrorValidation(
                  "Данный товар уже есть в ОКТ",
                  newProductError
                );
              } else if (response.status == "product_in_cart") {
                hidePreloaderAndEnabledButton(addNewItemInCartButton);
                showErrorValidation(
                  "Товар с таким артикулом уже есть в корзине",
                  newProductError
                );
              }
            });
        }
      };
    }

    function searchProductLogic(cont) {
      const searchProductItems = cont.querySelectorAll(".product_search_item");

      let counterElems = 0;
      searchProductItems.forEach((searchProductItem, i) => {
        searchProductItem.onmouseover = () => {
          searchProductItems.forEach((el) => el.classList.remove("active"));
          searchProductItem.classList.add("active");
          counterElems = i + 1;
        };
        searchProductItem.onmouseout = () => {
          searchProductItem.classList.remove("active");
          counterElems = 0;
        };
        const searchButton = searchProductItem.querySelector(".search_button");
        const productId = searchProductItem.getAttribute("product-id");

        // document.addEventListener("keyup", function (e) {
        //   console.log(counterElems);
        //   if (e.code == "ArrowUp") {
        //     searchProductItems.forEach((el) => {
        //       el.classList.remove("active");
        //     });
        //     if (counterElems > searchProductItems.length - 1) {
        //       counterElems = 0;
        //     } else {
        //       counterElems += 1;
        //     }
        //     if (searchProductItems[counterElems - 1]) {
        //       searchProductItems[counterElems - 1].classList.add("active");
        //       const name =
        //         searchProductItems[counterElems - 1].querySelector(".name");
        //       searchInput.value = name.textContent;
        //     }
        //   }
        //   if (e.code == "ArrowDown") {
        //     searchProductItems.forEach((el) => {
        //       el.classList.remove("active");
        //     });
        //     if (counterElems < 1) {
        //       counterElems = searchProductItems.length;
        //     } else {
        //       counterElems -= 1;
        //     }
        //     if (searchProductItems[counterElems - 1]) {
        //       searchProductItems[counterElems - 1].classList.add("active");
        //       const name =
        //         searchProductItems[counterElems - 1].querySelector(".name");
        //       searchInput.value = name.textContent;
        //     }
        //   }
        //   if (e.code == "Enter") {
        //     if (searchInput.value) {
        //       const productId = document
        //         .querySelector(".search_container")
        //         .querySelector(".active")
        //         .getAttribute("product-id");
        //       closeSearchWindow();
        //       cont.classList.remove("show");
        //       searchInput.classList.remove("bordering");
        //       const cartId = getCookie("cart");
        //       const objData = {
        //         cart: cartId,
        //         product: productId,
        //         quantity: 1,
        //       };
        //       const data = JSON.stringify(objData);
        //       fetch(`/api/v1/cart/${cartId}/save-product/`, {
        //         method: "POST",
        //         body: data,
        //         headers: {
        //           "Content-Type": "application/json",
        //           "X-CSRFToken": csrfToken,
        //         },
        //       }).then((response) => {
        //         if (response.status == 200) {
        //           window.location.reload();
        //         } else if (response.status == 409) {
        //           addProductButton.innerHTML = "";
        //           addProductButton.textContent = "Добавить этот товар";
        //           showErrorValidation("Этот товар уже в корзине", error);
        //         } else {
        //           setErrorModal();
        //           throw new Error("Ошибка");
        //         }
        //       });
        //     }
        //   }
        // });

        searchProductItem.onclick = () => {
          cont.classList.remove("show");
          searchInput.classList.remove("bordering");
          const cartId = getCookie("cart");
          const objData = {
            cart: cartId,
            product: productId,
            quantity: 1,
          };
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
            } else if (response.status == 409) {
              addProductButton.innerHTML = "";
              addProductButton.textContent = "Добавить этот товар";
              showErrorValidation("Этот товар уже в корзине", error);
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          });
        };
      });
    }
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const globalCartWrapper = document.querySelector(".spetification_table");
  if (globalCartWrapper) {
    addNewProductLogic(globalCartWrapper);
  }
  const noContentContainer = document.querySelector(".no_content_container");
  if (noContentContainer) {
    addNewProductLogic(noContentContainer);
  }
});
