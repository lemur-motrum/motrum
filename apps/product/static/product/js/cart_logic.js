import {
  getCookie,
  getClosestInteger,
  NumberParser,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const filtersAndProductContainer = document.querySelector(
    ".filters_and_products_container"
  );
  const globalCountCart = document.querySelector(".global_cart_count");

  if (globalCountCart) {
    if (
      +globalCountCart.textContent.trim() > 0 &&
      !globalCountCart.classList.contains("orange")
    ) {
      globalCountCart.classList.add("orange");
    }
  }

  if (filtersAndProductContainer) {
    const productContainer = filtersAndProductContainer.querySelector(
      ".site_catalog_container"
    );

    setInterval(() => {
      if (productContainer) {
        const products = document.querySelectorAll(".product_item");
        products.forEach((procductItem) => {
          const product_id = procductItem.getAttribute("product-id");
          const buttonContainer = procductItem.querySelector(
            ".item-buttons_container"
          );

          const productMultiplicity =
            +procductItem.getAttribute("order-multiplicity");
          if (buttonContainer) {
            const inputButtonsContainer =
              buttonContainer.querySelector(".quantity-buttons");
            const minusButton =
              inputButtonsContainer.querySelector(".minus-button");
            const plusButton =
              inputButtonsContainer.querySelector(".plus-button");
            const countInput = inputButtonsContainer.querySelector("input");
            const cartButton = buttonContainer.querySelector(
              ".add-specification-button"
            );

            let countQuantity = +countInput.value;

            countInput.addEventListener("keyup", function () {
              if (productMultiplicity) {
                let val = parseInt(this.value) || 0;
                while (val % +productMultiplicity) {
                  val++;
                  if (val % +productMultiplicity == 0) {
                    break;
                  }
                }
                this.value = val;
                countQuantity = +val;
              } else {
                countQuantity = +countInput.value;
              }

              countQuantity = +countInput.value;
              if (countQuantity >= 999) {
                countInput.value = productMultiplicity
                  ? getClosestInteger(999, +productMultiplicity)
                  : 999;
                minusButton.disabled = false;
                plusButton.disabled = true;
                cartButton.disabled = false;
              } else if (countQuantity <= 0) {
                countInput.value = 0;
                plusButton.disabled = false;
                cartButton.disabled = true;
              } else {
                minusButton.disabled = false;
                plusButton.disabled = false;
                cartButton.disabled = false;
              }
              saveProductInCart();
            });

            plusButton.onclick = () => {
              if (productMultiplicity) {
                countQuantity += +productMultiplicity;
              } else {
                countQuantity++;
              }
              countInput.value = +countQuantity;
              minusButton.disabled = false;
              cartButton.disabled = false;
              if (countQuantity >= 999) {
                countInput.value = productMultiplicity
                  ? getClosestInteger(999, +productMultiplicity)
                  : 999;
                minusButton.disabled = false;
                plusButton.disabled = true;
              } else {
                plusButton.disabled = false;
                minusButton.disabled = false;
              }
              saveProductInCart();
            };
            minusButton.onclick = () => {
              if (productMultiplicity) {
                countQuantity -= +productMultiplicity;
              } else {
                countQuantity--;
              }
              countInput.value = +countQuantity;
              minusButton.disabled = false;
              if (countQuantity <= 1) {
                countInput.value = 1;
                minusButton.disabled = true;
                plusButton.disabled = false;
                cartButton.disabled = true;
              } else {
                minusButton.disabled = false;
                plusButton.disabled = false;
              }
              saveProductInCart();
            };
            function saveProductInCart() {
              if (!getCookie("cart")) {
                fetch("/api/v1/cart/add-cart/", {
                  method: "GET",
                  headers: {
                    "X-CSRFToken": csrfToken,
                  },
                })
                  .then((response) => {
                    if (response.status >= 200 && response.status < 300) {
                      return response.json();
                    } else {
                      setErrorModal();
                    }
                  })
                  .then((cart_id) => {
                    if (cart_id) {
                      const dataObj = {
                        product: product_id,
                        cart: cart_id,
                        quantity: countInput.value,
                      };
                      const data = JSON.stringify(dataObj);
                      fetch(`/api/v1/cart/${cart_id}/save-product/`, {
                        method: "POST",
                        body: data,
                        headers: {
                          "Content-Type": "application/json",
                          "X-CSRFToken": csrfToken,
                        },
                      })
                        .then((response) => {
                          if (response.status >= 200 && response.status < 300) {
                            return response.json();
                          } else {
                            setErrorModal();
                            throw new Error("Ошибка");
                          }
                        })
                        .then((response) => {
                          globalCountCart.textContent = response.cart_len;
                          if (!globalCountCart.classList.contains("orange")) {
                            globalCountCart.classList.add("orange");
                          }
                        })
                        .catch((error) => console.error(error));
                    }
                  })
                  .catch((error) => console.error(error));
              } else {
                const cart_id = getCookie("cart");
                const dataObj = {
                  product: product_id,
                  cart: cart_id,
                  quantity: countInput.value,
                };

                const data = JSON.stringify(dataObj);
                fetch(`/api/v1/cart/${cart_id}/save-product/`, {
                  method: "POST",
                  body: data,
                  headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                  },
                })
                  .then((response) => {
                    if (response.status >= 200 && response.status < 300) {
                      return response.json();
                    } else {
                      setErrorModal();
                      throw new Error("Ошибка");
                    }
                  })
                  .then((response) => {
                    globalCountCart.textContent = response.cart_len;
                    if (!globalCountCart.classList.contains("orange")) {
                      globalCountCart.classList.add("orange");
                    }
                  })
                  .catch((error) => console.error(error));
              }
            }

            cartButton.onclick = () => {
              saveProductInCart();
              cartButton.style.display = "none";
              inputButtonsContainer.style.zIndex = 1;
            };
          }
        });
      }
    }, 1000);
  }

  const productOneContainer = document.querySelector(".product_one_container");
  if (productOneContainer) {
    const buttonContainer = productOneContainer.querySelector(
      ".item-buttons_container"
    );
    const productId = productOneContainer.getAttribute("product-id");
    const productMultiplicity =
      +productOneContainer.getAttribute("order-multiplicity");
    if (buttonContainer) {
      const inputButtonsContainer =
        buttonContainer.querySelector(".quantity-buttons");
      const minusButton = inputButtonsContainer.querySelector(".minus-button");
      const plusButton = inputButtonsContainer.querySelector(".plus-button");
      const countInput = inputButtonsContainer.querySelector("input");
      const cartButton = buttonContainer.querySelector(
        ".add-specification-button"
      );

      let countQuantity = +countInput.value;
      const price = productOneContainer.querySelector(".price");
      if (price) {
        getDigitsNumber(price, getCurrentPrice(price.textContent));
      }

      countInput.addEventListener("keyup", function () {
        if (productMultiplicity) {
          let val = parseInt(this.value) || 0;
          while (val % +productMultiplicity) {
            val++;
            if (val % +productMultiplicity == 0) {
              break;
            }
          }
          this.value = val;
          countQuantity = val;
        } else {
          countQuantity = +countInput.value;
        }

        countQuantity = +countInput.value;
        if (countQuantity >= 999) {
          countInput.value = productMultiplicity
            ? getClosestInteger(999, +productMultiplicity)
            : 999;
          minusButton.disabled = false;
          plusButton.disabled = true;
          cartButton.disabled = false;
        } else if (countQuantity <= 0) {
          countInput.value = 0;
          plusButton.disabled = false;
          cartButton.disabled = true;
        } else {
          minusButton.disabled = false;
          plusButton.disabled = false;
          cartButton.disabled = false;
        }
        saveProductInCart();
      });

      plusButton.onclick = () => {
        if (productMultiplicity) {
          countQuantity += +productMultiplicity;
        } else {
          countQuantity++;
        }
        countInput.value = +countQuantity;
        minusButton.disabled = false;
        cartButton.disabled = false;
        if (countQuantity >= 999) {
          countInput.value = productMultiplicity
            ? getClosestInteger(999, +productMultiplicity)
            : 999;
          minusButton.disabled = false;
          plusButton.disabled = true;
        } else {
          plusButton.disabled = false;
          minusButton.disabled = false;
        }
        saveProductInCart();
      };
      minusButton.onclick = () => {
        if (productMultiplicity) {
          countQuantity -= +productMultiplicity;
        } else {
          countQuantity--;
        }
        countInput.value = +countQuantity;
        minusButton.disabled = false;
        if (countQuantity <= 0) {
          countInput.value = 0;
          minusButton.disabled = true;
          plusButton.disabled = false;
          cartButton.disabled = true;
        } else {
          minusButton.disabled = false;
          plusButton.disabled = false;
        }
        saveProductInCart();
      };

      function saveProductInCart() {
        if (!getCookie("cart")) {
          fetch("/api/v1/cart/add-cart/", {
            method: "GET",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status >= 200 && response.status < 300) {
                return response.json();
              } else {
                setErrorModal();
              }
            })
            .then((cart_id) => {
              if (cart_id) {
                const dataObj = {
                  product: productId,
                  cart: cart_id,
                  quantity: countInput.value,
                };

                const data = JSON.stringify(dataObj);

                fetch(`/api/v1/cart/${cart_id}/save-product/`, {
                  method: "POST",
                  body: data,
                  headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                  },
                })
                  .then((response) => {
                    if (response.status >= 200 && response.status < 300) {
                      return response.json();
                    } else {
                      setErrorModal();
                      throw new Error("Ошибка");
                    }
                  })
                  .then((response) => {
                    globalCountCart.textContent = response.cart_len;
                    if (!globalCountCart.classList.contains("orange")) {
                      globalCountCart.classList.add("orange");
                    }
                  })
                  .catch((error) => console.error(error));
              }
            })
            .catch((error) => console.error(error));
        } else {
          const cart_id = getCookie("cart");
          const dataObj = {
            product: productId,
            cart: cart_id,
            quantity: countInput.value,
          };

          const data = JSON.stringify(dataObj);
          fetch(`/api/v1/cart/${cart_id}/save-product/`, {
            method: "POST",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status >= 200 && response.status < 300) {
                return response.json();
              } else {
                setErrorModal();
                throw new Error("Ошибка");
              }
            })
            .then((response) => {
              globalCountCart.textContent = response.cart_len;
              if (!globalCountCart.classList.contains("orange")) {
                globalCountCart.classList.add("orange");
              }
            })
            .catch((error) => console.error(error));
        }
      }

      cartButton.onclick = () => {
        saveProductInCart();
        cartButton.style.display = "none";
        inputButtonsContainer.style.zIndex = 1;
      };
    }
  }
});
