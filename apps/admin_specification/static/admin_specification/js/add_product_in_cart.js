import { getCookie, getClosestInteger } from "/static/core/js/functions.js";

import { setErrorModal } from "../js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const catalogWrapper = document.querySelector(".all-products");
  if (catalogWrapper) {
    const products = catalogWrapper.querySelectorAll(".catalog-item");
    products.forEach((product) => {
      const addProductInCartBtn = product.querySelector(
        ".first_display_button"
      );
      const hiddenProductButtonsForCart =
        product.querySelector(".quantity-buttons");
      const productId = product.getAttribute("data-id");
      const productMultiplicityQuantity = product.getAttribute(
        "data-order-multiplicity"
      );
      const productDataCartId = product.getAttribute("data-cart-product");

      addProductInCartBtn.onclick = () => {
        addProductInCartBtn.classList.add("hide");
        hiddenProductButtonsForCart.classList.add("show");
        if (!getCookie("cart")) {
          fetch("/api/v1/cart/add-cart/", {
            method: "GET",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((cart_id) => {
              if (cart_id) {
                const dataObj = {
                  product: +productId,
                  cart: +cart_id,
                  quantity: +productMultiplicityQuantity,
                };
                const data = JSON.stringify(dataObj);
                addProductInCart(cart_id, data, product);
              }
            })
            .catch((error) => {
              setErrorModal();
              console.error(error);
            });
        } else {
          const cart_id = getCookie("cart");
          const dataObj = {
            product: +productId,
            cart: +cart_id,
            quantity: +productMultiplicityQuantity,
          };
          const data = JSON.stringify(dataObj);
          addProductInCart(cart_id, data, product);
        }
      };

      if (hiddenProductButtonsForCart) {
        const minusButton =
          hiddenProductButtonsForCart.querySelector(".minus-button");
        const quantityInput =
          hiddenProductButtonsForCart.querySelector(".quantity_input");
        const plusButton =
          hiddenProductButtonsForCart.querySelector(".minus-button");

        let countQuantity = +quantityInput.value;

        quantityInput.addEventListener("input", function () {
          if (productMultiplicityQuantity) {
            let val = parseInt(this.value) || 0;
            while (val % +productMultiplicityQuantity) {
              val++;
              if (val % +productMultiplicityQuantity == 0) {
                break;
              }
            }
            this.value = val;
            countQuantity = +val;
          } else {
            countQuantity = +quantityInput.value;
          }

          if (countQuantity >= 99999) {
            quantityInput.value = productMultiplicityQuantity
              ? getClosestInteger(99999, +productMultiplicityQuantity)
              : 99999;
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else if (countQuantity <= 0) {
            quantityInput.value = 0;
            plusButton.disabled = false;
            deleteProductInCart(productDataCartId);
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
        });
      }
    });
  }

  function deleteProductInCart(product_cart_id) {
    fetch(`/api/v1/cart/${+product_cart_id}/delete-product/`, {
      method: "delete",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => {
        if (response.status == 200) {
          window.location.reload();
        }
      })
      .catch((error) => {
        setErrorModal();
        console.error(error);
      });
  }

  function addProductInCart(cart_id, data, product) {
    fetch(`/api/v1/cart/${cart_id}/save-product/`, {
      method: "POST",
      body: data,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => {
        if (response.status == 200) {
          return response.json();
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      })
      .then(
        (response) => {
          product.setAttribute("data-cart-product", response.cart_prod);
        }
        // (document.querySelector(
        //   ".admin_specification_cart_length"
        // ).textContent = response.cart_len)
      )
      .catch((error) => {
        setErrorModal();
        console.error(error);
      });
  }
});
