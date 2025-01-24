import { getCookie, setCookie } from "/static/core/js/functions.js";
import { setErrorModal } from "../js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".okt_cart_container");
  if (wrapper) {
    if (!getCookie("cart")) {
      let isInIframe;
      const objData = null
      try {
        isInIframe = window.self !== window.top;
      } catch (e) {
        isInIframe = true;
      }
      if (isInIframe) {
        const objData = {
          iframe: isInIframe,
        };
      }
      
      const data = JSON.stringify(objData);
      fetch("/api/v1/cart/add-cart/", {
        method: "POST",
        body: data,
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.status == 200) {
          // document.cookie = `type_save=new; path=/; SameSite=None; Secure`;
          // setCookie("type_save", "new", { path: "/",});
          console.log("ok");
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      });
    }
  }
});
