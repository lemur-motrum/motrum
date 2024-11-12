import {
  getCookie,
  showErrorValidation,
  getCurrentPrice,
  deleteCookie,
} from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const buttonContainer = document.querySelector(
    ".button_specification-wrapper"
  );
  if (buttonContainer) {
    const button = buttonContainer.querySelector(".save_upd_bill");
    if (button) {
      const specificationId = getCookie("specificationId");
      const adminCreator = document.querySelector("[data-user-id]");
      const adminCreatorId = adminCreator.getAttribute("data-user-id");
      const commentAll = document.querySelector(
        'textarea[name="comment-input-name-all"]'
      ).value;
      const dateDeliveryAll = document.querySelector(
        'textarea[name="delivery-date-all-input-name-all"]'
      ).value;

      const products = [];
      const motrumRequsits = document
        .querySelector("[name='mortum_req']")
        .getAttribute("value");

      const bitrixInput = document.querySelector(".bitrix-input");
      const specificationWrapepr = document.querySelector(
        ".spetification_table"
      );
      const specificationItems =
        specificationWrapepr.querySelectorAll(".item_container");

      button.onclick = () => {
        let validate = true;
        const clientRequsits = document
          .querySelector("[name='client-requisit']")
          .getAttribute("value");
        const deliveryRequsits = document
          .querySelector("[name='delevery-requisit']")
          .getAttribute("value");
        specificationItems.forEach((specificationItem) => {
          const itemQuantity =
            specificationItem.querySelector(".input-quantity").value;
          const itemID = specificationItem.getAttribute("data-product-pk");
          const nameProductNew = specificationItem.getAttribute(
            "data-product-name-new"
          );
          const itemPriceStatus = specificationItem.getAttribute(
            "data-price-exclusive"
          );
          const itemPrice = specificationItem.getAttribute("data-price");
          const extraDiscount =
            specificationItem.querySelector(".discount-input");
          const productSpecificationId = specificationItem.getAttribute(
            "data-product-specification-id"
          );
          const deliveryDate = specificationItem.querySelector(
            ".invoice-data-input"
          );
          const commentItem = specificationItem.querySelector(
            'textarea[name="comment-input-name"]'
          ).value;
          const inputPrice = specificationItem.querySelector(".price-input");
          const saleMotrum = specificationItem.querySelector(
            ".motrum_sale_persent"
          );
          const vendor = specificationItem.getAttribute("data-vendor");

          const product = {
            product_id: +itemID,
            quantity: +itemQuantity,
            price_exclusive: +itemPriceStatus,
            price_one: +getCurrentPrice(itemPrice),
            product_specif_id: productSpecificationId
              ? productSpecificationId
              : null,
            extra_discount: extraDiscount.value,
            date_delivery: null,
            text_delivery: deliveryDate.value,
            product_name_new: nameProductNew,
            product_new_article: nameProductNew,
            comment: commentItem ? commentItem : null,
            sale_motrum: saleMotrum ? saleMotrum.textContent : null,
            vendor: vendor ? vendor : null,
          };

          if (deliveryDate) {
            if (!deliveryDate.value) {
              validate = false;
              deliveryDate.style.border = "1px solid red";
              deliveryDate.style.borderRadius = "10px";
            }
          }

          if (inputPrice) {
            if (!inputPrice.value) {
              validate = false;
              inputPrice.style.border = "1px solid red";
              inputPrice.style.borderRadius = "10px";
            }
          }
          if (validate === true) {
            products.push(product);
          }
        });

        if (bitrixInput) {
          if (!bitrixInput.value) {
            validate = false;
            bitrixInput.style.border = "1px solid red";
            bitrixInput.style.borderRadius = "10px";
          }
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
            comment: commentAll ? commentAll : null,
            date_delivery: dateDeliveryAll ? dateDeliveryAll : null,
            motrum_requisites: +motrumRequsits,
            client_requisites: +clientRequsits,
            type_delivery: deliveryRequsits,
            type_save: "bill",
            post_update: true,
          };

          const data = JSON.stringify(dataObj);

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
                return response.json();
              } else {
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
                    throw new Error("Ошибка");
                  }
                })
                .then((response2) => {
                  const dataArr = response2.map((elem) => {
                    return {
                      id: elem["id"],
                      text_delivery: elem["text_delivery"],
                    };
                  });
                  const dataObj = { products: dataArr, post_update: true };
                  const data = JSON.stringify(dataObj);
                  fetch(
                    `/api/v1/order/${response1.specification}/create-bill-admin/`,
                    {
                      method: "UPDATE",
                      body: data,
                      headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/json",
                      },
                    }
                  ).then((response3) => {
                    if (response3.status == 200 || response2.status == 201) {
                      window.location.href =
                        "/admin_specification/all_specifications/";
                    }
                  });
                });
            });
        }
      };
    }
  }
});
