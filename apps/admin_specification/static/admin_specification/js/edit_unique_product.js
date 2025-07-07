import {
  showErrorValidation,
  getCookie,
  getDigitsNumber,
  getCurrentPrice,
  setPreloaderInButton,
  hidePreloaderAndEnabledButton,
} from "/static/core/js/functions.js";

import {
  inputValidation,
  inputValidationQuantity,
} from "../js/add_new_product_without_cart.js";
import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(".spetification_table");

  if (specificationContainer) {
    const newProducts = specificationContainer.querySelectorAll(
      ".added_item_container"
    );
    newProducts.forEach((newProduct) => {
      const productId = newProduct.getAttribute("data-product-id-cart");
      const changeBtn = newProduct.querySelector(".change_icon_container");
      const closeBtn = newProduct.querySelector(".close-btn");
      const changeFormWrapper = newProduct.querySelector(
        ".change_item_container"
      );
      const nameInput = changeFormWrapper.querySelector(
        ".new_item_container_name_input"
      );
      const articleInput = changeFormWrapper.querySelector(
        ".new_item_container_article_input"
      );
      const select = changeFormWrapper.querySelector(".vendor_select");
      const supplierSelect = select.querySelector(
        ".vendor_select__toggle_change"
      );

      const options = select.querySelectorAll(".itc-select__options");

      options.forEach((el) => {
        el.onclick = () => {
          setTimeout(() => {
            select.classList.remove("itc-select_show");
          });
        };
      });

      const priceOneInput = changeFormWrapper.querySelector(".price_input");
      priceOneInput.value = getCurrentPrice(priceOneInput.value);
      const quantityInput = changeFormWrapper.querySelector(".quantity_input");
      const totalCostValue = changeFormWrapper.querySelector(
        ".change_item_container_value_total_cost"
      );
      getDigitsNumber(
        totalCostValue,
        priceOneInput.value * quantityInput.value
      );
      const saleValue = changeFormWrapper.querySelector(
        ".change_item_container_value_motrum_price"
      );
      const salePersentInput = changeFormWrapper.querySelector(".persent_sale");
      salePersentInput.value = salePersentInput.value
        ? getCurrentPrice(salePersentInput.value)
        : "";
      const changeButton = changeFormWrapper.querySelector(
        ".add_new_item_in_cart"
      );

      changeBtn.onclick = () => {
        changeFormWrapper.classList.add("show");
        setTimeout(() => {
          changeFormWrapper.classList.add("visible");
        }, 600);
      };
      closeBtn.onclick = () => {
        changeFormWrapper.classList.remove("visible");
        setTimeout(() => {
          changeFormWrapper.classList.remove("show");
        }, 600);
      };
      inputValidation(priceOneInput);
      inputValidationQuantity(quantityInput);

      function changePercent() {
        if (priceOneInput.value && quantityInput.value) {
          getDigitsNumber(
            saleValue,
            (priceOneInput.value / 100) *
              (100 - salePersentInput.value) *
              quantityInput.value
          );
        }
      }
      changePercent();
      salePersentInput.addEventListener("input", function () {
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d.-]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
        salePersentInput.value = currentValue;
        if (+salePersentInput.value > 99.99) {
          salePersentInput.value = 99.99;
        }
        if (+salePersentInput.value < -99.99) {
          salePersentInput.value = -99.99;
        }
        if (
          salePersentInput.value.length > 1 &&
          salePersentInput.value.at(-1) === "-"
        ) {
          salePersentInput.target.value = salePersentInput.value.slice(0, -1);
        }
        if (salePersentInput.value == ".") {
          salePersentInput.target.value = "";
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
            getDigitsNumber(totalCostValue, +input1.value * +input2.value);
          }
          changePercent();
        });
      }
      changeTotalCost(priceOneInput, quantityInput);
      changeTotalCost(quantityInput, priceOneInput);

      changeButton.onclick = () => {
        setPreloaderInButton(changeButton);
        function validate(input) {
          if (!input.value || input.value.trim().length === 0) {
            input.style.border = "0.063rem solid red";
            hidePreloaderAndEnabledButton(changeButton);
          }
        }
        validate(nameInput);
        validate(articleInput);
        validate(priceOneInput);
        validate(quantityInput);
        if (!supplierSelect.getAttribute("value")) {
          setPreloaderInButton(changeButton);
          supplierSelect.style.border = "0.063rem solid red";
        }
        if (
          nameInput.value &&
          articleInput.value &&
          priceOneInput.value &&
          quantityInput.value &&
          supplierSelect.getAttribute("value")
        ) {
          const cartId = getCookie("cart");
          const objData = {
            product: null,
            product_new: nameInput.value,
            product_new_article: articleInput.value,
            product_new_price: +priceOneInput.value,
            cart: +cartId,
            quantity: +quantityInput.value,
            product_new_sale_motrum: salePersentInput.value
              ? salePersentInput.value
              : null,
            vendor: supplierSelect.getAttribute("value"),
          };
          const data = JSON.stringify(objData);
          fetch(`/api/v1/cart/${productId}/upd-product-new/`, {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status == 200) {
                window.location.reload();
              } else {
                setErrorModal();
                throw new Error("Ошибка");
              }
            })
            .catch((error) => console.error(error));
        }
      };
    });
  }
});
