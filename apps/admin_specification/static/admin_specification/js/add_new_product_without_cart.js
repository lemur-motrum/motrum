import { showErrorValidation, getCookie } from "/static/core/js/functions.js";
import { setErrorModal } from "../js/error_modal.js";
const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const noContentContainer = document.querySelector(".no_content-container");
  if (noContentContainer) {
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
    const openPopupButton =
      noContentContainer.querySelector(".add_new_product");

    let cartId = "";

    openPopupButton.onclick = () => {
      if (!cartId) {
        fetch("/api/v1/cart/add-cart/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((idCart) => {
            if (idCart) {
              overlay.classList.add("show");
              inputValidation(priceInput);
              inputValidationQuantity(quantityInput);
              if (overlay.classList.contains("show")) {
                document.body.style.overflow = "hidden";
              }
              setTimeout(() => {
                overlay.classList.add("visible");
              });
            }
            cartId = getCookie("cart");
          });
      } else {
        overlay.classList.add("show");
        inputValidation(priceInput);
        inputValidationQuantity(quantityInput);
        if (overlay.classList.contains("show")) {
          document.body.style.overflow = "hidden";
        }
        setTimeout(() => {
          overlay.classList.add("visible");
        });
      }
    };

    form.onsubmit = (e) => {
      e.preventDefault();
      if (cartId) {
        if (!nameInput.value) {
          showErrorValidation("Обязательное поле", nameError);
        }
        if (!priceInput.value) {
          showErrorValidation("Обязательное поле", priceError);
        }
        if (!quantityInput.value) {
          showErrorValidation("Обязательное поле", quantityError);
        }
        if (!articleInput.value) {
          showErrorValidation("Обязательное поле", articleError);
        }
        if (
          nameInput.value &&
          priceInput.value &&
          quantityInput.value &&
          articleInput.value
        ) {
          console.log("Ура, товар добавлен в корзину");

          const dataObj = {
            product: null,
            product_new: nameInput.value,
            product_new_article: articleInput.value,
            product_new_price: +priceInput.value,
            cart: +cartId,
            quantity: +quantityInput.value,
          };
          const data = JSON.stringify(dataObj);
          fetch(`/api/v1/cart/${cartId}/save-product-new/`, {
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
                showErrorValidation(
                  "Товар с таким артикулом в корзине уже есть ",
                  articleError
                );
              } else {
                setErrorModal();
                throw new Error("Ошибка");
              }
            })
            .then(
              (response) =>
                (document.querySelector(
                  ".admin_specification_cart_length"
                ).textContent = response.cart_len)
            )
            .catch((error) => {
              setErrorModal();
              console.error(error);
            });
        }
      }
    };

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

export function inputValidation(input) {
  input.addEventListener("input", function (e) {
    const currentValue = this.value
      .replace(",", ".")
      .replace(/[^.\d]+/g, "")
      .replace(/^([^\.]*\.)|\./g, "$1")
      .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
        return a + b + c.slice(0, 2);
      });
    input.value = currentValue;
    if (input.value == ".") {
      e.target.value = "";
    }
    if (input.value == "0") {
      e.target.value = "";
    }
  });
}

export function inputValidationQuantity(input) {
  input.addEventListener("input", function (e) {
    const currentValue = this.value
      .replace(/[^.\d]+/g, "")
      .replace(/(\d+)(\.|,)/g, function (o, a) {
        return a;
      });
    input.value = currentValue;
    if (input.value == ".") {
      e.target.value = "";
    }
    if (input.value == "0") {
      e.target.value = "";
    }
  });
}
