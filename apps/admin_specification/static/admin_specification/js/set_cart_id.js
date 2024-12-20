import { getCookie, setCookie } from "/static/core/js/functions.js";
import { setErrorModal } from "../js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".okt_cart_container");
  if (wrapper) {
    if (!getCookie("cart")) {
      fetch("/api/v1/cart/add-cart/", {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.status == 200) {
          setCookie("type_save", "new", { path: "/", SameSite:None });
          console.log("ok");
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      });
    }
  }
});
