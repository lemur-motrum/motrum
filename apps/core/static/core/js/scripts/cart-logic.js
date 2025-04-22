import {
  getCookie,
  getDigitsNumber,
  NumberParser,
  showErrorValidation,
  maskOptions,
  deleteCookie,
  setPreloaderInButton,
} from "/static/core/js/functions.js";

import { ItcCustomSelect } from "/static/core/js/customSelect.js";

import { setErrorModal } from "/static/core/js/error_modal.js";
import { successModal } from "/static/core/js/sucessModal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const cartContainer = document.querySelector(".cart_container");

  if (cartContainer) {
    const productContainer = cartContainer.querySelector(".products");
    if (productContainer) {
      const personalDiscount =
        cartContainer.querySelector(".personal_discount");

      let totalSumCart = 0;
      let totalSumSaleCart = 0;
      let totalSalePriceCart = 0;
      let itemNotPrice = 0;
      function getTotalSum() {
        totalSumCart = 0;
        totalSumSaleCart = 0;
        totalSalePriceCart = 0;
        itemNotPrice = 0;
        const productItems = productContainer.querySelectorAll(".product_item");
        productItems.forEach((productItem) => {
          const priceAll = productItem.querySelector(".all_cart_price");
          const priceAllNoSale = productItem.querySelector(
            ".all_cart_no_sale_price"
          );
          if (priceAll) {
            totalSumSaleCart += new NumberParser("ru").parse(
              priceAll.textContent
            );
            if (personalDiscount.dataset.personalDiscount != "0") {
              totalSumCart += new NumberParser("ru").parse(
                priceAllNoSale.textContent
              );
              totalSalePriceCart = totalSumCart - totalSumSaleCart;
            }
          } else {
            itemNotPrice += 1;
          }
        });
      }

      const productItems = productContainer.querySelectorAll(".product_item");

      if (productItems.length == 0) {
        if (globalCountCart.classList.contains("orange")) {
          globalCountCart.classList.add("orange");
        }
      }
      productItems.forEach((productItem) => {
        const productId = productItem.getAttribute("product-id");
        const inputCount = productItem.querySelector(".quantity");
        const plusButton = productItem.querySelector(".plus-button");
        const minusButton = productItem.querySelector(".minus-button");
        const deleteBtn = productItem.querySelector(".delete_cart_button");
        const priceOnce = productItem.querySelector(".cart_price");
        let priceOnceNoSale = productItem.querySelector(
          ".cart_price_one_no_sale"
        );
        priceOnceNoSale = priceOnceNoSale.getAttribute("data-cart-one-no-sale");
        const priceAll = productItem.querySelector(".all_cart_price");
        const priceAllNoSale = productItem.querySelector(
          ".all_cart_no_sale_price"
        );
        if (priceOnce) {
          getDigitsNumber(priceOnce, priceOnce.textContent.replace(",", "."));
        }
        function getAllProductSumm() {
          if (priceOnce) {
            const priceAll = productItem.querySelector(".all_cart_price");
            if (priceAll) {
              priceAll.textContent = (
                +new NumberParser("ru").parse(priceOnce.textContent) *
                +inputCount.value
              ).toFixed(2);
              getDigitsNumber(priceAll, priceAll.textContent);
            }
          } else {
            return;
          }
        }
        getAllProductSumm();

        function getAllProductSummNoSale() {
          if (priceOnce) {
            priceAllNoSale.textContent = (
              +priceOnceNoSale.replace(",", ".") * +inputCount.value
            ).toFixed(2);
            getDigitsNumber(priceAllNoSale, priceAllNoSale.textContent);
          } else {
            return;
          }
        }

        if (personalDiscount.dataset.personalDiscount != "0") {
          getAllProductSummNoSale();
        }

        function updateProduct() {
          addTotalSum();
          setTimeout(() => {
            const dataObj = {
              quantity: +inputCount.value,
            };
            const data = JSON.stringify(dataObj);
            fetch(`/api/v1/cart/${productId}/update-product/`, {
              method: "POST",
              body: data,
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
            }).then((response) => {
              if (response.status >= 200 && response.status < 300) {
                console.log(
                  `Товар с id ${productId}, успешно изменен на количество ${inputCount.value}`
                );
              } else {
                setErrorModal();
              }
            });
          }, 1500);
        }

        let countQuantity = +inputCount.value;

        inputCount.onkeyup = () => {
          countQuantity = +inputCount.value;
          if (countQuantity >= 999) {
            inputCount.value = 999;
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else if (countQuantity <= 1) {
            countQuantity = 1;
            inputCount.value = 1;
            minusButton.disabled = true;
            plusButton.disabled = false;
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          getAllProductSumm();
          if (personalDiscount.dataset.personalDiscount != "0") {
            getAllProductSummNoSale();
          }
          updateProduct();
        };
        plusButton.onclick = () => {
          countQuantity++;
          inputCount.value = +countQuantity;
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
          if (personalDiscount.dataset.personalDiscount != "0") {
            getAllProductSummNoSale();
          }
          updateProduct();
        };
        minusButton.onclick = () => {
          countQuantity--;
          inputCount.value = +countQuantity;
          minusButton.disabled = false;
          if (countQuantity <= 1) {
            countQuantity = 1;
            inputCount.value = 1;
            minusButton.disabled = true;
            plusButton.disabled = false;
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          getAllProductSumm();
          if (personalDiscount.dataset.personalDiscount != "0") {
            getAllProductSummNoSale();
          }
          updateProduct();
        };

        deleteBtn.onclick = () => {
          fetch(`/api/v1/cart/${productId}/delete-product/`, {
            method: "DELETE",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            if (response.status >= 200 && response.status < 300) {
              window.location.reload();
            } else {
              setErrorModal();
            }
          });
        };
      });

      function addTotalSum() {
        getTotalSum();
        const totalSalePriceCartItem =
          cartContainer.querySelector(".cart_total_price");

        getDigitsNumber(totalSalePriceCartItem, totalSumSaleCart);

        if (itemNotPrice > 0) {
          const descriptionContainer = cartContainer.querySelector(
            ".total_sum_container"
          );
          descriptionContainer.classList.add("show");
        }

        if (personalDiscount.dataset.personalDiscount != "0") {
          const totalSumCartItem = cartContainer.querySelector(
            ".cart_total_price_all"
          );
          const totalSumSaleCartItem = cartContainer.querySelector(
            ".cart_total_price_sale"
          );

          getDigitsNumber(totalSumCartItem, totalSumCart);
          getDigitsNumber(totalSumSaleCartItem, totalSalePriceCart);
        }
      }
      addTotalSum();
    }

    const logoutFormContainer =
      cartContainer.querySelector(".logout_container");
    if (logoutFormContainer) {
      const form = logoutFormContainer.querySelector(".autification-form-cart");
      const nameInput = form.querySelector(".name_input");
      const nameError = form.querySelector(".name_error");
      const phoneInput = form.querySelector(".phone_input");
      const phoneError = form.querySelector(".phone_error");
      const pinInput = form.querySelector(".pin_input");
      const pinError = form.querySelector(".pin_error");
      const submitBtn = form.querySelector(".save_cart_button");

      const phoneMask = IMask(phoneInput, maskOptions);

      const maskPinOptions = {
        mask: "0000",
        lazy: false,
        overwrite: "shift",
      };
      const pinMask = IMask(pinInput, maskPinOptions);

      submitBtn.onclick = (e) => {
        e.preventDefault();
        let validate = true;
        if (!nameInput.value) {
          showErrorValidation("Обязательное поле", nameError);
          validate = false;
        }
        if (!phoneInput.value) {
          showErrorValidation("Обязательное поле", phoneError);
          validate = false;
        }
        if (phoneInput.value && phoneInput.value.length < 18) {
          showErrorValidation("Некорректный номер", phoneError);
          validate = false;
        }
        if (validate) {
          const phone = phoneMask.unmaskedValue;
          const name = nameInput.value;
          const dataObj = {
            phone: phone,
            pin: "",
            first_name: name,
          };

          const data = JSON.stringify(dataObj);

          fetch("/api/v1/client/login/", {
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
              }
            })
            .then((response) => {
              submitBtn.classList.add("hide");
              pinInput.oninput = () => {
                const arrayPinInputValue = pinInput.value.split("");
                const validateValue = +arrayPinInputValue[3];
                if (!isNaN(validateValue)) {
                  const dataObj = {
                    phone: phone,
                    pin: pinInput.value,
                    first_name: name,
                  };

                  const data = JSON.stringify(dataObj);
                  fetch("/api/v1/client/login/", {
                    method: "POST",
                    body: data,
                    headers: {
                      "Content-Type": "application/json",
                      "X-CSRFToken": csrfToken,
                    },
                  })
                    .then((response) => {
                      response.json();
                      if (response.status == 201) {
                        console.log("Новый Клиент");
                        window.location.reload();
                      }
                      if (response.status == 200) {
                        console.log("Вы вошли");
                        window.location.reload();
                      }
                      if (response.status == 400) {
                        showErrorValidation("Некорректный Пин-код", pinError);
                      }
                      if (response.status == 403) {
                        console.log("Вы заблокированы");
                      }
                    })
                    .catch((error) => console.error(error));
                }
              };
            });
        }
      };
    }
    const clientOrderDetails = cartContainer.querySelector(
      ".client-order-details"
    );
    if (clientOrderDetails) {
      const selectRequisites = new ItcCustomSelect("#select_requisites");
      const selectDelevery = new ItcCustomSelect("#select_delevery");
      const submitBtn = clientOrderDetails.querySelector(".save_cart_button");

      function showCartButton(select) {
        if (select) {
          select.addEventListener("itc.select.change", () => {
            if (selectDelevery.value && selectRequisites.value) {
              submitBtn.classList.remove("hide");
            } else {
              submitBtn.classList.add("hide");
            }
          });
        }
      }
      showCartButton(document.querySelector("#select_delevery"));
      showCartButton(document.querySelector("#select_requisites"));

      if (submitBtn) {
        const dataInfoValue = submitBtn.getAttribute("data-client-info");
        submitBtn.onclick = () => {
          setPreloaderInButton(submitBtn);
          const cartId = getCookie("cart");
          const clientId = getCookie("client_id");
          let dataObj;
          if (dataInfoValue == "1") {
            const selectRequisitesValuesArray =
              selectRequisites.value.split(",");
            const requisitesKppValue = selectRequisitesValuesArray[0];
            const accountRequisitValue = selectRequisitesValuesArray[1];
            const deleveryIdValue = selectDelevery.value;

            dataObj = {
              all_client_info: 1,
              client: +clientId,
              cart: +cartId,
              requisitesKpp: +requisitesKppValue,
              account_requisites: +accountRequisitValue,
              type_delivery: +deleveryIdValue,
            };
          } else {
            dataObj = {
              all_client_info: 0,
              client: +clientId,
              cart: +cartId,
              requisitesKpp: null,
              account_requisites: null,
              type_delivery: null,
            };
          }

          const data = JSON.stringify(dataObj);

          fetch("/api/v1/order/add_order/", {
            method: "POST",
            body: data,
            headers: {
              "X-CSRFToken": csrfToken,
              "Content-Type": "application/json",
            },
          }).then((response) => {
            if (response.status >= 200 && response.status < 300) {
              ym(37794920, "reachGoal", "add_order_in_site");
              deleteCookie("cart", "/", window.location.hostname);
              successModal(
                "Спасибо за заказ, мы свяжемся с вами в ближайшее время"
              );
              setTimeout(() => {
                window.location.href =
                  window.location.origin + "/lk/my_orders/?page=1";
              }, 200);
            } else {
              setErrorModal();
            }
          });
        };
      }
    }
  }
});
