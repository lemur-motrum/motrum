import {
  getCookie,
  deleteCookie,
  getDigitsNumber,
} from "/static/core/js/functions.js";

let csrfToken = getCookie("csrftoken");

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

        function getAllProductSumm() {
          if (priceOnce) {
            const priceAll = productItem.querySelector(".all_cart_price");
            priceAll.textContent = (
              +priceOnce.textContent.replace(",", ".") * +inputCount.value
            ).toFixed(2);
            getDigitsNumber(priceAll, priceAll.textContent);
          } else {
            return;
          }
        }
        getAllProductSumm();

        function getAllProductSummNoSale() {
          if (priceOnce) {
            priceAllNoSale.textContent = (+priceOnceNoSale.replace(
              ",",
              "."
            )).toFixed(2);
            getDigitsNumber(priceAllNoSale, priceAllNoSale.textContent);
          } else {
            return;
          }
        }

        if (personalDiscount.dataset.personalDiscount != "0") {
          getAllProductSummNoSale();
        }

        function getTotalSum() {
          if (priceAll) {
            totalSumSaleCart += Number.parseFloat(priceAll.textContent);
            if (personalDiscount.dataset.personalDiscount != "0") {
              totalSumCart += Number.parseFloat(+priceAllNoSale.textContent);
              totalSalePriceCart = totalSumCart - totalSumSaleCart;
            }
          } else {
            itemNotPrice += 1;
          }
        }
        getTotalSum();

        function updateProduct() {
          setTimeout(() => {
            const dataObj = {
              quantity: +inputCount.value,
            };
            const data = JSON.stringify(dataObj);
            fetch(`/api/v1/cart/${productId}/update-product/`, {
              // изменила метод
              method: "POST",
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
          })
            .then((response) => {
              if (response.status == 200) {
                window.location.reload();
              }
            })
            .catch((error) => console.error(error));
        };
      });

      function addTotalSum() {
        let totalSalePriceCartItem =
          cartContainer.querySelector(".cart_total_price");
        totalSalePriceCartItem.textContent = totalSumSaleCart.toFixed(2);

        if (itemNotPrice > 0) {
          let totalSumItem = cartContainer.querySelector(".total_sum_all");

          let div_message_price = document.createElement("div");
          div_message_price.className = "alert_total_sum_all";
          div_message_price.innerHTML = `<span>${itemNotPrice} товара с ценой по запросу</span>`;
          // html_message_no_price_item = `<span>${itemNotPrice} товара с ценой по запросу</span>`;
          totalSumItem.append(div_message_price);
        }

        if (personalDiscount.dataset.personalDiscount != "0") {
          let totalSumCartItem = cartContainer.querySelector(
            ".cart_total_price_all"
          );
          let totalSumSaleCartItem = cartContainer.querySelector(
            ".cart_total_price_sale"
          );
          totalSumCartItem.textContent = totalSumCart.toFixed(2);
          totalSumSaleCartItem.textContent = totalSalePriceCart.toFixed(2);
        }
      }
      addTotalSum();
    }
  }

  // сохранение корзины сайт
  const saveCartBtn = document.querySelector(".save_cart_button");
  if (saveCartBtn) {
    const user = document
      .querySelector("#client_id")
      .getAttribute("data-user-id");
    saveCartBtn.onclick = () => {
      saveCartBtn.disabled = true;
      saveCartBtn.textContent = "";
      saveCartBtn.innerHTML = "<div class='btn_loader'></div>";
      if (user == "None") {
        saveCartNoAuthentication();
      } else {
        saveCart();
      }
    };
  }
});

function saveCart() {
  let validate = true;
  const products = [];
  const cart_id = getCookie("cart");

  if (validate == true) {
    // const select = document.querySelector(".select_account_requisites");
    // const selected = select.options[select.selectedIndex];
    // const requisites = selected.getAttribute("data-requisites-id");
    // const account_requisites_name = selected.getAttribute(
    //   "data-account-requisites-id"
    // );

    const dataObj = {
      cart: +cart_id,
      // requisites: +requisites,
      // account_requisites: +account_requisites_name,
    };

    const data = JSON.stringify(dataObj);
    let endpoint = "/api/v1/order/add_order/";
    fetch(endpoint, {
      method: "POST",
      body: data,
      headers: {
        "X-CSRFToken": csrfToken,
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((response) => {
        // deleteCookie("cart", "/", window.location.hostname);
        // window.location.href = "/lk/my_orders";
      })
      .catch((error) => console.error(error));
  }
}

function saveCartNoAuthentication() {
  let validate = true;
  const products = [];
  const cart_id = getCookie("cart");

  if (validate == true) {
    const select = document.querySelector(".select_account_requisites");

    const dataObj = {
      cart: +cart_id,
    };
    const dataArr = {
      phone: phone,
      pin: "",
    };

    // const data = JSON.stringify(dataObj);
    // let endpoint = "/api/v1/order/add_order/";
    // fetch(endpoint, {
    //   method: "POST",
    //   body: data,
    //   headers: {
    //     "X-CSRFToken": csrfToken,
    //     "Content-Type": "application/json",
    //   },
    // })
    //   .then((response) => response.json())
    //   .then((response) => {
    //     deleteCookie("cart", "/", window.location.hostname);

    //     // window.location.href =
    //     //   "/lk/my_orders";
    //   })
    //   .catch((error) => console.error(error));
  }
}
