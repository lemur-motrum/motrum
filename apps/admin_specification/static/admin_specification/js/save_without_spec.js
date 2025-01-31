import {
  getCookie,
  deleteCookie,
  getCurrentPrice,
} from "/static/core/js/functions.js";

import { setErrorModal } from "../js/error_modal.js";

window.addEventListener("DOMContentLoaded", () => {
  const cartWrapper = document.querySelector(".spetification_table");
  if (cartWrapper) {
    const csrfToken = getCookie("csrftoken");
    const specificationId = getCookie("specificationId");
    const adminCreator = document.querySelector("[data-user-id]");
    const adminCreatorId = adminCreator.getAttribute("data-user-id");
    const products = [];
    const saveWithoutSpecificationButton =
      cartWrapper.querySelector(".save_order_button");
    const cartItems = cartWrapper.querySelectorAll(".item_container");
    cartItems.forEach((item) => {
      const itemQuantity = item.querySelector(".input-quantity").value;
      const itemID = item.getAttribute("data-product-pk");
      const nameProductNew = item.getAttribute("data-product-name-new");
      const itemPriceStatus = item.getAttribute("data-price-exclusive");
      const itemPrice = item.getAttribute("data-price");
      const extraDiscount = item.querySelector(".discount-input");
      const productSpecificationId = item.getAttribute(
        "data-product-specification-id"
      );
      const vendor = item.getAttribute("data-vendor");
      const deliveryDate = item.querySelector(".delivery_date")
        ? item.querySelector(".delivery_date").value
        : item.querySelector(".invoice-data-input").value;
      const commentItem = item.querySelector(
        'textarea[name="comment-input-name"]'
      ).value;
      const productCartId = item.getAttribute("data-product-id-cart");

      const product = {
        product_id: +itemID,
        quantity: +itemQuantity,
        price_exclusive: +itemPriceStatus,
        price_one: +getCurrentPrice(itemPrice),
        product_specif_id: productSpecificationId
          ? productSpecificationId
          : null,
        extra_discount: extraDiscount.value,
        date_delivery: deliveryDate,
        product_name_new: nameProductNew,
        product_new_article: nameProductNew,
        comment: commentItem ? commentItem : null,
        vendor: vendor ? vendor : null,
        id_cart: productCartId,
      };

      products.push(product);
    });

    if (saveWithoutSpecificationButton) {
      saveWithoutSpecificationButton.onclick = () => {
        const bitrixInput = cartWrapper.querySelector(".bitrix-input");
        const motrumRequsits = cartWrapper
          .querySelector("[name='mortum_req']")
          .getAttribute("value");
        const clientRequsits = document
          .querySelector("[name='client-requisit']")
          .getAttribute("value");
        const commentAll = cartWrapper.querySelector(
          'textarea[name="comment-input-name-all"]'
        ).value;
        const dateDeliveryAll = cartWrapper.querySelector(
          'textarea[name="delivery-date-all-input-name-all"]'
        ).value;
        const deliveryRequsits = document.querySelector(
          "[name='delevery-requisit']"
        );

        saveWithoutSpecificationButton.disabled = true;
        saveWithoutSpecificationButton.textContent = "";
        saveWithoutSpecificationButton.innerHTML = `<div class="small_loader"></div>`;
        const dataObj = {
          id_bitrix: bitrixInput.value ? +bitrixInput.value : null,
          admin_creator_id: adminCreatorId ? adminCreatorId : null,
          products: products,
          id_specification: specificationId ? specificationId : null,
          id_cart: +getCookie("cart"),
          comment: commentAll ? commentAll : null,
          date_delivery: dateDeliveryAll ? dateDeliveryAll : null,
          motrum_requisites: motrumRequsits ? +motrumRequsits : null,
          client_requisites: clientRequsits ? +clientRequsits : null,
          type_delivery: deliveryRequsits
            ? deliveryRequsits.getAttribute("value")
            : null,
          type_save: "bill",
          post_update: false,
        };
        const data = JSON.stringify(dataObj);

        fetch("/api/v1/order/add-order-no-spec-admin/", {
          method: "POST",
          body: data,
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        }).then((response) => {
          if (response.status == 200) {
            document.cookie = `key=; path=/; SameSite=None; Secure; Max-Age=-1;`;
            document.cookie = `specificationId=; path=/; SameSite=None; Secure; Max-Age=-1;`;
            document.cookie = `cart=; path=/; SameSite=None; Secure; Max-Age=-1;`;
            document.cookie = `type_save=; path=/; SameSite=None; Secure; Max-Age=-1;`;
            
            // deleteCookie("key", "/", window.location.hostname);
            // deleteCookie("specificationId", "/", window.location.hostname);
            // deleteCookie("cart", "/", window.location.hostname);
            window.location.href = "/admin_specification/all_specifications/";
          } else {
            setErrorModal();
            throw new Error("Ошибка");
          }
        });
      };
    }
  }
});
