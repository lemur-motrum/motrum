import { version } from "/static/core/js/scripts/version.js";

const { getCookie } = await import(
  `/static/core/js/functions.js?ver=${version}`
);
const { setErrorModal } = await import(
  `/static/core/js/error_modal.js?ver=${version}`
);

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".okt_cart_container");
  if (wrapper) {
    if (!getCookie("cart")) {
      let objData = {
        iframe: false,
      };
      const isInIframe = window.self !== window.top;

      if (isInIframe) {
        objData = {
          iframe: isInIframe,
        };
      }
      const data = JSON.stringify(objData);
      fetch("/api/v1/cart/add-cart/", {
        method: "POST",
        body: data,
        headers: {
          "Content-Type": "application/json; charset=UTF-8",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.status == 200) {
          // document.cookie = `type_save=new; path=/; SameSite=None; Secure`;
          // setCookie("type_save", "new", { path: "/",});

          console.log("ok");
          document.location.reload();
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      });
    }
  }
});
