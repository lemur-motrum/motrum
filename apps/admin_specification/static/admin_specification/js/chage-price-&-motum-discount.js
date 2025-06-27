import { getCookie } from "../../../../core/static/core/js/functions.js";
import { setErrorModal } from "../../../../core/static/core/js/error_modal.js";

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".spetification_table");
  if (wrapper) {
    const productItems = wrapper.querySelectorAll(
      ".data-base-product-container"
    );
    productItems.forEach((productItem) => {
      const productCartId = productItem.getAttribute("data-product-id-cart");
      const productId = productItem.getAttribute("data-product-pk");
      const changeBtn = productItem.querySelector(".change_icon_container");
      const priceInput = productItem.querySelector(".price-input");
      const saveBtn = productItem.querySelector(".save_icon_container");
      const priceContainer = productItem.querySelector(".price_once");
      const motrumSaleContainer = productItem.querySelector(
        ".motrum_sale_persent"
      );
      const changePriceInput = productItem.querySelector(".change_input_price");
      const changeMotrumSaleInput = productItem.querySelector(
        ".change-input-sale-percent-motrum"
      );
      const changeMotrumSaleInputWithoutSale = productItem.querySelector(
        ".change-motrum-sale-percent-without-sale"
      );

      changeBtn.onclick = () => {
        changeBtn.style.display = "none";
        saveBtn.classList.add("show");
        if (changePriceInput) {
          changePriceInput.value = getReplacedInputValue(changePriceInput);
          priceContainer.style.display = "none";
          changePriceInput.classList.add("show");
          inputLogic(changePriceInput);
        }
        changeMotrumSaleInput.value = getReplacedInputValue(
          changeMotrumSaleInput
        );
        inputLogic(changeMotrumSaleInput);
        if (motrumSaleContainer) {
          motrumSaleContainer.style.display = "none";
          changeMotrumSaleInput.classList.add("show");
        } else {
          changeMotrumSaleInputWithoutSale.classList.add("show");
          changeMotrumSaleInput.classList.add("show");
        }
      };

      saveBtn.onclick = () => {
        const cartId = getCookie("cart");
        const csrfToken = getCookie("csrftoken");

        const dataObj = {
          product: productId,
          product_price: changePriceInput
            ? changePriceInput.value
            : priceInput.value,
          cart: cartId,
          product_sale_motrum: changeMotrumSaleInput.value,
        };
        const data = JSON.stringify(dataObj);

        fetch(`/api/v1/cart/${productCartId}/upd-product-cart/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: data,
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
      };
    });
  }
});

function inputLogic(input) {
  input.addEventListener("input", function (e) {
    input.value = getReplacedInputValue(input);
    if (input.value == ".") {
      e.target.value = "";
    }
    if (input.value == "0") {
      e.target.value = "";
    }
  });
}

function getReplacedInputValue(input) {
  const currentValue = input.value
    .replace(",", ".")
    .replace(/[^.\d]+/g, "")
    .replace(/^([^\.]*\.)|\./g, "$1")
    .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
      return a + b + c.slice(0, 2);
    });
  return currentValue;
}
