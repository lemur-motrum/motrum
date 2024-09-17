import { setCookie, getCookie } from "/static/core/js/functions.js";

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
          if (buttonContainer) {
            const minusButton = buttonContainer.querySelector(".minus-button");
            const plusButton = buttonContainer.querySelector(".plus-button");
            const countInput = buttonContainer.querySelector("input");
            const cartButton = buttonContainer.querySelector(
              ".add-specification-button"
            );

            let countQuantity = countInput.value;

            countInput.onkeyup = () => {
              countQuantity = countInput.value;
              if (countQuantity >= 999) {
                countInput.value = 999;
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
            };

            plusButton.onclick = () => {
              countQuantity++;
              countInput.value = countQuantity;
              minusButton.disabled = false;
              cartButton.disabled = false;
              if (countQuantity >= 999) {
                countInput.value = 999;
                minusButton.disabled = false;
                plusButton.disabled = true;
              } else {
                plusButton.disabled = false;
                minusButton.disabled = false;
              }
            };
            minusButton.onclick = () => {
              countQuantity--;
              countInput.value = countQuantity;
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
            };
            cartButton.onclick = () => {
              console.log(getCookie("cart"))
              if (!getCookie("cart")) {
                console.log(111)
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
                console.log(22)
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
    if (buttonContainer) {
      const minusButton = buttonContainer.querySelector(".minus-button");
      const plusButton = buttonContainer.querySelector(".plus-button");
      const countInput = buttonContainer.querySelector("input");
      const cartButton = buttonContainer.querySelector(
        ".add-specification-button"
      );
      let countQuantity = countInput.value;

      countInput.onkeyup = () => {
        countQuantity = countInput.value;
        if (countQuantity >= 999) {
          countInput.value = 999;
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
      };

      plusButton.onclick = () => {
        countQuantity++;
        countInput.value = countQuantity;
        minusButton.disabled = false;
        cartButton.disabled = false;
        if (countQuantity >= 999) {
          countInput.value = 999;
          minusButton.disabled = false;
          plusButton.disabled = true;
        } else {
          plusButton.disabled = false;
          minusButton.disabled = false;
        }
      };
      minusButton.onclick = () => {
        countQuantity--;
        countInput.value = countQuantity;
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
      };

      cartButton.onclick = () => {
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
      };
    }
  }
});
