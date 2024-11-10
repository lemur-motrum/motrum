import { getCookie } from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".otk_description_content");
  if (wrapper) {
    const cartLink = wrapper.querySelector(".basket_cart_link");
    if (cartLink) {
      cartLink.onclick = () => {
        if (!getCookie("cart")) {
          fetch("/api/v1/cart/add-cart/", {
            method: "GET",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            if (response.status == 200) {
              console.log("ok");
            } else {
              throw new Error("Ошибка");
            }
          });
        }
      };
    }
  }
});
