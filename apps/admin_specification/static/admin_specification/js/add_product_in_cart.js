import { getCookie, getClosestInteger } from "/static/core/js/functions.js";

import { setErrorModal } from "../js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  cartItemsQuantity();
  const catalogWrapper = document.querySelector(".all-products");
  buttonsLogic(catalogWrapper);
});
export function buttonsLogic(wrapper) {
  if (wrapper) {
    const products = wrapper.querySelectorAll(".catalog-item");
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
          hiddenProductButtonsForCart.querySelector(".plus-button");

        if (productMultiplicityQuantity) {
          quantityInput.value = +productMultiplicityQuantity;
        }

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
            addProductInCartBtn.classList.remove("hide");
            hiddenProductButtonsForCart.classList.remove("show");
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          addProductInCartMoreQuantity();
        });

        plusButton.onclick = () => {
          if (productMultiplicityQuantity) {
            countQuantity += +productMultiplicityQuantity;
          } else {
            countQuantity++;
          }
          quantityInput.value = +countQuantity;
          minusButton.disabled = false;
          if (countQuantity >= 99999) {
            quantityInput.value = productMultiplicityQuantity
              ? getClosestInteger(99999, +productMultiplicityQuantity)
              : 99999;
            plusButton.disabled = true;
            minusButton.disabled = false;
          } else {
            plusButton.disabled = false;
            minusButton.disabled = false;
          }
          addProductInCartMoreQuantity();
        };
        minusButton.onclick = () => {
          if (productMultiplicityQuantity) {
            countQuantity -= +productMultiplicityQuantity;
          } else {
            countQuantity--;
          }
          quantityInput.value = countQuantity;
          minusButton.disabled = false;

          if (countQuantity <= 0) {
            quantityInput.value = 0;
            minusButton.disabled = true;
            plusButton.disabled = false;
            addProductInCartBtn.classList.remove("hide");
            hiddenProductButtonsForCart.classList.remove("show");
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          addProductInCartMoreQuantity();
        };
        function addProductInCartMoreQuantity() {
          if (quantityInput.value > 0) {
            const cart_id = getCookie("cart");
            const dataObj = {
              product: +productId,
              cart: +cart_id,
              quantity: +quantityInput.value,
            };
            const data = JSON.stringify(dataObj);
            addProductInCart(cart_id, data, product);
          } else {
            deleteProductInCart(product);
          }
        }
      }
    });
  }
}

function deleteProductInCart(product) {
  const productDataCartId = product.getAttribute("data-cart-product");
  fetch(`/api/v1/cart/${+productDataCartId}/delete-product/`, {
    method: "delete",
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => {
      if (response.status == 200) {
        if (
          document.querySelector(".admin_specification_cart_length")
            .textContent != 0
        ) {
          document.querySelector(
            ".admin_specification_cart_length"
          ).textContent =
            +document.querySelector(".admin_specification_cart_length")
              .textContent - 1;
        }
        cartItemsQuantity();
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
    .then((response) => {
      product.setAttribute("data-cart-product", response.cart_prod);
      document.querySelector(".admin_specification_cart_length").textContent =
        response.cart_len;
      cartItemsQuantity();
    })
    .catch((error) => {
      setErrorModal();
      console.error(error);
    });
}

function cartItemsQuantity() {
  const cartItemsQuantity = document.querySelector(
    ".admin_specification_cart_length"
  );
  if (cartItemsQuantity) {
    if (cartItemsQuantity.textContent != 0) {
      cartItemsQuantity.classList.add("orange");
    }
  } else {
    return;
  }
}
