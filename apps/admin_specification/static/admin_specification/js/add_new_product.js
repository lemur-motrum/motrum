import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const specificationTable = document.querySelector(".spetification_table");
  if (specificationTable) {
    const addNewProductBtn =
      specificationTable.querySelector(".add_new_product");
    const overlay = document.querySelector(
      ".overlay_new_product_in_specification"
    );
    const modalWindow = overlay.querySelector(".modal_window");
    const form = modalWindow.querySelector("form");
    const nameInput = modalWindow.querySelector(".name");
    const nameInputError = modalWindow.querySelector(".name-error");
    const priceInput = modalWindow.querySelector(".price");
    const priceInputError = modalWindow.querySelector(".price-error");
    const quantityInput = modalWindow.querySelector(".quantity");
    const quantityInputError = modalWindow.querySelector(".quantity-error");

    addNewProductBtn.onclick = () => {
      overlay.classList.add("show");
      if (overlay.classList.contains("show")) {
        document.body.style.overflow = "hidden";
      }
      setTimeout(() => {
        overlay.classList.add("visible");
      });

      overlay.onclick = () => {
        overlay.classList.remove("visible");
        if (overlay.classList.contains("show")) {
          document.body.style.overflowY = "scroll";
        }
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
        form.reset();
      };
    };
    modalWindow.onclick = (e) => {
      e.stopPropagation();
    };

    form.onsubmit = (e) => {
      e.preventDefault();
      if (!nameInput.value) {
        showErrorValidation("Обязательное поле", nameInputError);
      }
      if (!priceInput.value) {
        showErrorValidation("Обязательное поле", priceInputError);
      }
      if (!quantityInput.value) {
        showErrorValidation("Обязательное поле", quantityInputError);
      }
      if (nameInput.value && priceInput.value && quantityInput.value) {
        console.log("Ура, товар добавлен в корзину");
      }
    };
  }
});
