import { setCookie, getCookie } from "/static/core/js/functions.js";

let csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const cartContainer = document.querySelector(".cart_container");
  if (cartContainer) {
    const productContainer = cartContainer.querySelector(".products");
    if (productContainer) {
      const productItems = productContainer.querySelectorAll(".product_item");
      productItems.forEach((productItem) => {
        const productId = productItem.getAttribute("product-id");
        const inputCount = productItem.querySelector("input");
        const plusButton = productItem.querySelector(".plus-button");
        const minusButton = productItem.querySelector(".minus-button");
        const deleteBtn = productItem.querySelector(".delete_cart_button");
        const priceOnce = productItem.querySelector(".cart_price");
        function getAllProductSumm() {
          if (priceOnce) {
            const priceAll = productItem.querySelector(".all_cart_price");
            priceAll.textContent = (
              +priceOnce.textContent.replace(",", ".") * +inputCount.value
            ).toFixed(2);
          } else {
            return;
          }
        }
        getAllProductSumm();

        function updateProduct() {
          setTimeout(() => {
            const dataObj = {
              quantity: +inputCount.value,
            };
            const data = JSON.stringify(dataObj);
            fetch(`/api/v1/cart/${productId}/update-product/`, {
              method: "UPDATE",
              body: data,
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
            })
              .then((response) => {
                if (response.status == 200) {
                  console.log(
                    `Товар с id ${productId}, успешно изменен на количество ${inputCount.value}`
                  );
                }
              })
              .catch((error) => console.error(error));
          }, 1500);
        }

        let countQuantity = inputCount.value;

        inputCount.onkeyup = () => {
          countQuantity = inputCount.value;
          if (countQuantity >= 999) {
            inputCount.value = 999;
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else if (countQuantity <= 1) {
            inputCount.value = 1;
            plusButton.disabled = false;
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          getAllProductSumm();
          updateProduct();
        };
        plusButton.onclick = () => {
          countQuantity++;
          inputCount.value = countQuantity;
          minusButton.disabled = false;
          if (countQuantity >= 999) {
            inputCount.value = 999;
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else {
            plusButton.disabled = false;
            minusButton.disabled = false;
          }
          getAllProductSumm();
          updateProduct();
        };
        minusButton.onclick = () => {
          countQuantity--;
          inputCount.value = countQuantity;
          minusButton.disabled = false;
          if (countQuantity == 1) {
            inputCount.value = 1;
            minusButton.disabled = true;
            plusButton.disabled = false;
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          getAllProductSumm();
          updateProduct();
        };

        deleteBtn.onclick = () => {
          fetch(`/api/v1/cart/${productId}/delete-product/`, {
            method: "DELETE",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status == 200) {
                window.location.reload();
              }
            })
            .catch((error) => console.error(error));
        };
      });
    }
  }
});
