import {
  getCookie,
  showErrorValidation,
  getCurrentPrice,
  deleteCookie,
  getDeliveryDate,
} from "/static/core/js/functions.js";
import { setErrorModal } from "/static/core/js/error_modal.js";
import { setCommentProductItem } from "../js/setCommnetToProduct.js";
const csrfToken = getCookie("csrftoken");
// СОХРАНЕНИЯ И СПЕЦИФИКАЦИИ И СЧЕТА
window.addEventListener("DOMContentLoaded", () => {
  const buttonContainer = document.querySelector(
    ".save_invoice_button-wrapper"
  );
  if (buttonContainer) {
    const button = buttonContainer.querySelector(".save_button");
    const specificationId = getCookie("specificationId");
    const adminCreator = document.querySelector("[data-user-id]");
    const adminCreatorId = adminCreator.getAttribute("data-user-id");
    const commentAll = document.querySelector(
      'textarea[name="comment-input-name-all"]'
    );
    const dateDeliveryAll = document.querySelector(
      'textarea[name="delivery-date-all-input-name-all"]'
    );



    const bitrixInput = document.querySelector(".bitrix-input");
    const dateDeliveryInputs = document.querySelectorAll(".delivery_date");

    const specificationWrapepr = document.querySelector(".spetification_table");
    const specificationItems =
      specificationWrapepr.querySelectorAll(".item_container");

    button.onclick = () => {
      console.log("saveSpecification(elems)")
      const products = [];
      let validate = true;
      const marginality =
        document.querySelector(".marginality_value");
      const marginality_sum = marginality.textContent
      const marginalityValue =
        document.querySelector(".marginality_prcent_value");
      const marginality_percent = marginalityValue.textContent

      console.log("marginality_sum", marginality, marginality_sum)
      console.log("marginalityValue", marginalityValue, marginality_percent)

      const clientRequsits = document
        .querySelector("[name='client-requisit']")
        .getAttribute("value");
      const deliveryRequsits = document
        .querySelector("[name='delevery-requisit']")
        .getAttribute("value");
      const motrumRequsits = document
        .querySelector("[name='mortum_req']")
        .getAttribute("value");

      specificationItems.forEach((specificationItem) => {
        const itemQuantity =
          specificationItem.querySelector(".input-quantity").value;
        const itemID = specificationItem.getAttribute("data-product-pk");
        const nameProductNew = specificationItem.getAttribute(
          "data-product-name-new"
        );
        const nameProductNewАrt = specificationItem.getAttribute(
          "data-product-article-new"
        );
        const itemPriceStatus = specificationItem.getAttribute(
          "data-price-exclusive"
        );
        const itemPrice = specificationItem.getAttribute("data-price");
        const extraDiscount =
          specificationItem.querySelector(".discount-input");
        const marjaItem =
          specificationItem.querySelector(".marja-input");
        const productSpecificationId = specificationItem.getAttribute(
          "data-product-specification-id"
        );
        const motrumPrice = specificationItem.getAttribute(
          "data-price-motrum"
        );
        const deliveryDate = specificationItem.querySelector(".delivery_date");

        setCommentProductItem(specificationItem);
        const commentItem = specificationItem.getAttribute("data-comment-item");

        const inputPrice = specificationItem.querySelector(".price-input");
        const textPrice = specificationItem.querySelector(".price_once");
        const saleMotrum = specificationItem.querySelector(
          ".motrum_sale_persent"
        );
        const vendor = specificationItem.getAttribute("data-vendor");
        const supplier = specificationItem.getAttribute("data-supplier");
        const productCartId = specificationItem.getAttribute(
          "data-product-id-cart"
        );

        const createTextDateDelivery = () => {
          const orderData = new Date(deliveryDate.value);
          const today = new Date();
          const delta = orderData.getTime() - today.getTime();
          const dayDifference = +Math.floor(delta / 1000 / 60 / 60 / 24);
          const resultDays = +Math.ceil(dayDifference / 7);

          function num_word(value, words) {
            value = Math.abs(value) % 100;
            var num = value % 10;
            if (value > 10 && value < 20) return words[2];
            if (num > 1 && num < 5) return words[1];
            if (num == 1) return words[0];
            return words[2];
          }
          if (dayDifference > 7) {
            return `${resultDays} ${num_word(resultDays, [
              "неделя",
              "недели",
              "недель",
            ])}`;
          } else {
            return "1 неделя";
          }
        };

        const product = {
          product_id: +itemID,
          quantity: +itemQuantity,
          price_exclusive: +itemPriceStatus,
          price_one: +getCurrentPrice(itemPrice),
          product_specif_id: productSpecificationId
            ? productSpecificationId
            : null,
          extra_discount: extraDiscount.value,
          marja_motrum:  marjaItem.value,
          date_delivery: deliveryDate.value,
          text_delivery: createTextDateDelivery(),
          product_name_new: nameProductNew,
          product_new_article: nameProductNewАrt,
          comment: commentItem ? commentItem : null,
          price_motrum:+getCurrentPrice(motrumPrice),
          sale_motrum: saleMotrum ? saleMotrum.textContent : null,
          
          vendor: vendor ? vendor : null,
          supplier: supplier ? supplier : null,
          id_cart: productCartId,
        };
        if (deliveryDate) {
          if (!deliveryDate.value) {
            validate = false;
            deliveryDate.style.border = "0.063rem solid red";
            deliveryDate.style.borderRadius = "0.625rem";
          }
        }

        if (itemPrice) {
          console.log(itemPrice)
          console.log("inputPrice.value", itemPrice)
          if (!itemPrice || itemPrice == 0.00 || itemPrice == 0.0 || itemPrice == 0 || itemPrice == "0,00" || itemPrice == "0,0"  || itemPrice == "0") {

            console.log(" if inputPrice 22222222222222")
            validate = false;
            textPrice.style.color = "red";
          }
        }
        if (inputPrice) {
          if (!inputPrice.value) {
            validate = false;
            inputPrice.style.border = "0.063rem solid red";
            inputPrice.style.borderRadius = "0.625rem";
          }
        }
        if (validate === true) {
          products.push(product);
        }
      });
      if (bitrixInput) {
        if (!bitrixInput.value) {
          validate = false;
          bitrixInput.style.border = "0.063rem solid red";
        }
      }
      if (!deliveryRequsits || deliveryRequsits == "null") {
        validate = false;
        document.querySelector(".select_delevery").style.border =
          "1px solid red";
      }
      if (!motrumRequsits || motrumRequsits == "null") {
        validate = false;
        document.querySelector(".select_motrum_requisites").style.border =
          "1px solid red";
      }
      if (validate == false) {
        const error = buttonContainer.querySelector(".error");
        showErrorValidation("Заполните все поля", error);
      }
      if (validate == true) {
        button.disabled = true;
        button.textContent = "";
        button.innerHTML = `<div class="small_loader"></div>`;

        const dataObj = {
          id_bitrix: +bitrixInput.value,
          admin_creator_id: adminCreatorId,
          products: products,
          id_specification: specificationId ? specificationId : null,
          id_cart: +getCookie("cart"),
          comment: commentAll.value,
          date_delivery: getDeliveryDate(dateDeliveryInputs),
          motrum_requisites: +motrumRequsits,
          client_requisites: +clientRequsits,
          type_delivery: deliveryRequsits,
          type_save: "bill",
          post_update: false,
          marginality_sum: +getCurrentPrice(marginality_sum),
          marginality: +marginality_percent,
        };

        const data = JSON.stringify(dataObj);
        console.log("add-order-admin", "save without specification")
        fetch("/api/v1/order/add-order-admin/", {
          method: "POST",
          body: data,
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        })
          .then((response) => {
            if (response.status == 200 || response.status == 201) {
              localStorage.removeItem("specificationValues");
              deleteCookie("key", "/", window.location.hostname);
              deleteCookie("specificationId", "/", window.location.hostname);
              deleteCookie("cart", "/", window.location.hostname);
              // document.cookie = `key=; path=/; SameSite=None; Secure; Max-Age=-1;`;
              // document.cookie = `specificationId=; path=/; SameSite=None; Secure; Max-Age=-1;`;
              // document.cookie = `cart=; path=/; SameSite=None; Secure; Max-Age=-1;`;
              // document.cookie = `type_save=; path=/; SameSite=None; Secure; Max-Age=-1;`;
              return response.json();
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          })
          .then((response1) => {
            fetch(
              `/api/v1/order/${response1.specification}/get-specification-product/`,
              {
                method: "GET",
                headers: {
                  "X-CSRFToken": csrfToken,
                  "Content-Type": "application/json",
                },
              }
            )
              .then((response) => {
                if (response.status == 200 || response.status == 201) {
                  return response.json();
                } else {
                  setErrorModal();
                  throw new Error("Ошибка");
                }
              })
              .then((response2) => {
                const dataArr = response2.map((elem) => {
                  const createTextDateDelivery = () => {
                    const orderData = new Date(elem["date_delivery"]);
                    const today = new Date();
                    const delta = orderData.getTime() - today.getTime();
                    const dayDifference = +Math.floor(
                      delta / 1000 / 60 / 60 / 24
                    );
                    const resultDays = +Math.ceil(dayDifference / 7);

                    function num_word(value, words) {
                      value = Math.abs(value) % 100;
                      var num = value % 10;
                      if (value > 10 && value < 20) return words[2];
                      if (num > 1 && num < 5) return words[1];
                      if (num == 1) return words[0];
                      return words[2];
                    }
                    if (dayDifference > 7) {
                      return `${resultDays} ${num_word(resultDays, [
                        "неделя",
                        "недели",
                        "недель",
                      ])}`;
                    } else {
                      return "1 неделя";
                    }
                  };
                  return {
                    id: elem["id"],
                    text_delivery: createTextDateDelivery(),
                  };
                });
                const dataObj = {
                  products: dataArr,
                  post_update: false,
                };
                const data = JSON.stringify(dataObj);

                fetch(
                  `/api/v1/order/${response1.specification}/create-bill-admin/`,
                  {
                    // изменила метод
                    method: "POST",
                    body: data,
                    headers: {
                      "X-CSRFToken": csrfToken,
                      "Content-Type": "application/json",
                    },
                  }
                )
                  .then((response3) => {
                    if (response3.status == 200 || response2.status == 201) {
                      window.location.href =   "/admin_specification/all_specifications/";
                    } else {
                      setErrorModal();
                    }
                  })
                  .catch((error) => console.error(error));
              })
              .catch((error) => console.error(error));
          })
          .catch((error) => console.error(error));
      }
    };
  }
});
