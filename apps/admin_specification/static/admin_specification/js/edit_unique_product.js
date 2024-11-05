import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
import {
  inputValidation,
  inputValidationQuantity,
} from "../js/add_new_product_without_cart.js";

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(".spetification_table");

  if (specificationContainer) {
    const overlay = document.querySelector(
      ".overlay_new_product_in_specification"
    );
    const modalWindow = overlay.querySelector(".modal_window");
    const form = modalWindow.querySelector("form");
    const nameInput = form.querySelector(".name");
    const nameError = form.querySelector(".name-error");
    const articleInput = form.querySelector(".article");
    const articleError = form.querySelector(".article-error");
    const priceInput = form.querySelector(".price");
    const priceError = form.querySelector(".price-error");
    const quantityInput = form.querySelector(".quantity");
    const quantityError = form.querySelector(".quantity-error");
    const closeBtn = modalWindow.querySelector(".close-btn");

    const specificationsItems =
      specificationContainer.querySelectorAll(".item_container");

    specificationsItems.forEach((specification) => {
      const editSpecificationButton = specification.querySelector(
        ".change_icon_container"
      );
      if (editSpecificationButton) {
        editSpecificationButton.onclick = () => {
          overlay.classList.add("show");
          inputValidation(priceInput);
          inputValidationQuantity(quantityInput);
          if (overlay.classList.contains("show")) {
            document.body.style.overflow = "hidden";
          }
          setTimeout(() => {
            overlay.classList.add("visible");
          });
        };
      }
    });
    closeBtn.onclick = () => {
      overlay.classList.remove("visible");
      if (overlay.classList.contains("show")) {
        document.body.style.overflowY = "scroll";
      }
      setTimeout(() => {
        overlay.classList.remove("show");
      }, 600);
      form.reset();
    };
  }
});
