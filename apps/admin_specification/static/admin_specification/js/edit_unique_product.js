import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
import {
  inputValidation,
  inputValidationQuantity,
} from "../js/add_new_product_without_cart.js";

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(".spetification_table");

  if (specificationContainer) {
    const newProducts = specificationContainer.querySelectorAll(
      ".added_item_container"
    );
    newProducts.forEach((newProduct) => {
      const changeBtn = newProduct.querySelector(".change_icon_container");
      const changeFormWrapper = newProduct.querySelector(
        ".change_item_container"
      );
      changeBtn.onclick = () => {
        changeFormWrapper.classList.add("show");
      };
    });
  }
});
