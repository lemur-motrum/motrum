import {
  setCookie,
  getCookie,
  getClosestInteger,
  NumberParser,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

let csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const filtersAndProductContainer = document.querySelector(
    ".filters_and_products_container"
  );

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
              console.log(getCookie("cart"));
              if (!getCookie("cart")) {
                console.log(111);
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
                          if (response.status == 200) {
                            return response.json();
                          } else {
                            throw new Error("Ошибка");
                          }
                        })
                        .then(
                          (response) =>
                            (document.querySelector(
                              ".global_cart_count"
                            ).textContent = response.cart_len)
                        )
                        .catch((error) => console.error(error));
                    }
                  })
                  .catch((error) => console.error(error));
              } else {
                console.log(22);
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
                    if (response.status == 200) {
                      return response.json();
                    } else {
                      throw new Error("Ошибка");
                    }
                  })
                  .then(
                    (response) =>
                      (document.querySelector(
                        ".global_cart_count"
                      ).textContent = response.cart_len)
                  )
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
      getDigitsNumber(price, getCurrentPrice(price.textContent));

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
            .then((response) => response.json())
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
                    if (response.status == 200) {
                      return response.json();
                    } else {
                      throw new Error("Ошибка");
                    }
                  })
                  .then(
                    (response) =>
                      (document.querySelector(
                        ".global_cart_count"
                      ).textContent = response.cart_len)
                  )
                  .catch((error) => console.error(error));
              }
            })
            .catch((error) => console.error(error));
        } else {
          const cart_id = setCookie("cart");
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
              if (response.status == 200) {
                return response.json();
              } else {
                throw new Error("Ошибка");
              }
            })
            .then(
              (response) =>
                (document.querySelector(".global_cart_count").textContent =
                  response.cart_len)
            )
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

  const cartContainer = document.querySelector(".cart_container");
  if (cartContainer) {
    const allPriceContainer = cartContainer.querySelector(".cart_total_price");
    const cartTotalPriceAll = cartContainer.querySelector(
      ".cart_total_price_all"
    );
    const cartTotalPriceSale = cartContainer.querySelector(
      ".cart_total_price_sale"
    );
    const products = cartContainer.querySelectorAll(".product_item");
    let allPriceWithoutDiscount = 0;
    let allPrice = 0;
    const personalDiscountInput =
      cartContainer.querySelector(".personal_discount");
    const personalDiscount = +getCurrentPrice(
      personalDiscountInput.getAttribute("data-personal-discount")
    );
    products.forEach((product) => {
      const priceOne = product.querySelector(".cart_price");
      const productMultiplicity = +product.getAttribute("order-multiplicity");
      const cartMinusButton = product.querySelector(".minus-button");
      const cartPlusButton = product.querySelector(".plus-button");
      const cartCountInput = product.querySelector(".quantity");
      let cartCountQuantity = +cartCountInput.value;
      const priceQuantity = product.querySelector(".all_cart_price");
      const priceWithoutDiscontContainer = product.querySelector(
        ".all_cart_no_sale_price"
      );

      getDigitsNumber(priceOne, getCurrentPrice(priceOne.textContent));

      setInterval(() => {
        if (!+new NumberParser("ru").parse(priceQuantity.textContent)) {
          allPriceWithoutDiscount = 0;
          allPrice = 0;
          getDigitsNumber(
            priceQuantity,
            new NumberParser("ru").parse(priceOne.textContent) *
              +cartCountInput.value
          );
          if (priceWithoutDiscontContainer) {
            getDigitsNumber(
              priceWithoutDiscontContainer,
              (new NumberParser("ru").parse(priceOne.textContent) *
                (100 + personalDiscount)) /
                100
            );
          }
          for (
            let i = 0;
            i < cartContainer.querySelectorAll(".all_cart_price").length;
            i++
          ) {
            allPrice += new NumberParser("ru").parse(
              cartContainer.querySelectorAll(".all_cart_price")[i].textContent
            );
          }
          if (allPriceContainer) {
            getDigitsNumber(allPriceContainer, allPrice);
          }

          for (
            let i = 0;
            i <
            cartContainer.querySelectorAll(".all_cart_no_sale_price").length;
            i++
          ) {
            allPriceWithoutDiscount += new NumberParser("ru").parse(
              cartContainer.querySelectorAll(".all_cart_no_sale_price")[i]
                .textContent
            );
          }
          if (cartTotalPriceAll) {
            getDigitsNumber(cartTotalPriceAll, allPriceWithoutDiscount);
          }

          if (cartTotalPriceSale) {
            getDigitsNumber(
              cartTotalPriceSale,
              new NumberParser("ru").parse(cartTotalPriceAll.textContent) -
                new NumberParser("ru").parse(allPriceContainer.textContent)
            );
          }
        } else {
          clearInterval();
        }
      });

      cartCountInput.addEventListener("keyup", function () {
        allPrice = 0;
        allPriceWithoutDiscount = 0;
        if (productMultiplicity) {
          let val = parseInt(this.value) || 0;
          while (val % +productMultiplicity) {
            val++;
            if (val % +productMultiplicity == 0) {
              break;
            }
          }
          this.value = val;
          cartCountQuantity = +val;
        } else {
          cartCountQuantity = +cartCountInput.value;
        }

        cartCountQuantity = +cartCountInput.value;
        if (cartCountQuantity >= 999) {
          cartCountInput.value = productMultiplicity
            ? getClosestInteger(999, +productMultiplicity)
            : 999;
          cartMinusButton.disabled = false;
          cartPlusButton.disabled = true;
        } else if (cartCountQuantity <= 0) {
          cartCountInput.value = 0;
          cartPlusButton.disabled = false;
        } else {
          cartMinusButton.disabled = false;
          cartPlusButton.disabled = false;
        }
      });

      cartPlusButton.onclick = () => {
        allPrice = 0;
        allPriceWithoutDiscount = 0;
        if (productMultiplicity) {
          cartCountQuantity += +productMultiplicity;
        } else {
          cartCountQuantity++;
        }
        cartCountInput.value = +cartCountQuantity;
        cartMinusButton.disabled = false;

        if (cartCountQuantity >= 999) {
          cartCountInput.value = productMultiplicity
            ? getClosestInteger(999, +productMultiplicity)
            : 999;
          cartMinusButton.disabled = false;
          cartPlusButton.disabled = true;
        } else {
          cartPlusButton.disabled = false;
          cartMinusButton.disabled = false;
        }
      };
      cartMinusButton.onclick = () => {
        allPrice = 0;
        allPriceWithoutDiscount = 0;
        if (productMultiplicity) {
          cartCountQuantity -= +productMultiplicity;
        } else {
          cartCountQuantity--;
        }
        cartCountInput.value = +cartCountQuantity;
        cartMinusButton.disabled = false;
        if (cartCountQuantity <= 0) {
          cartCountInput.value = 0;
          cartMinusButton.disabled = true;
          cartPlusButton.disabled = false;
        } else {
          cartMinusButton.disabled = false;
          cartPlusButton.disabled = false;
        }
      };
    });
  }
});
