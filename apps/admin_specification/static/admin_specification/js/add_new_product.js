import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const specificationTable = document.querySelector(".spetification_table");
  if (specificationTable) {
    const csrfToken = getCookie("csrftoken");
    const addNewProductBtn =
      specificationTable.querySelector(".add_new_product");
    const overlay = document.querySelector(
      ".overlay_new_product_in_specification"
    );
    const modalWindow = overlay.querySelector(".modal_window");
    const form = modalWindow.querySelector("form");
    const nameInput = modalWindow.querySelector(".name");
    const nameInputError = modalWindow.querySelector(".name-error");
    const articleInput = modalWindow.querySelector(".article");
    const articleInputError = modalWindow.querySelector(".article-error");
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
      if (!articleInput.value) {
        showErrorValidation("Обязательное поле", articleInputError);
      }
      if (nameInput.value && priceInput.value && quantityInput.value) {
        console.log("Ура, товар добавлен в корзину");
        const cart_id = getCookie("cart");
        const dataObj = {
          product: null,
          product_new: nameInput.value,
          product_new_article: articleInput.value,
          product_new_price: +priceInput.value,
          cart: +cart_id,
          quantity: +quantityInput.value,
        };

        const data = JSON.stringify(dataObj);
        
        fetch(`/api/v1/cart/${cart_id}/save-product-new/`, {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status == 200) {
              location.reload();
              return response.json();
            }
            if (response.status == 409) {
              showErrorValidation("Товар с таким артикулом в корзине уже есть ", articleInputError);
              nameInput.style.border = "1px solid red";
            }
            else {
              throw new Error("Ошибка");
            }
          })
          .then(
            (response) =>
              (document.querySelector(
                ".admin_specification_cart_length"
              ).textContent = response.cart_len)
          )
          .catch((error) => console.error(error));
      }
    };
  }
});
