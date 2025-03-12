import { version } from "/static/core/js/scripts/version.js";

const { getCookie } = await import(
  `/static/core/js/functions.js?ver=${version}`
);
const { setErrorModal } = await import(
  `/static/core/js/error_modal.js?ver=${version}`
);
const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const productFile = document.querySelector(".add_product_file");
  if (productFile) {
    productFile.onclick = () => {
      const cartId = getCookie("cart");
      const dataObj = {
        cart: +cartId,
        // file: null,
      };
      const data = JSON.stringify(dataObj);

      fetch("/api/v1/cart/cart-file-download/", {
        method: "POST",
        body: data,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.status == 200) {
          console.log("STOP");
          location.reload();
        } else {
          setErrorModal();
          throw new Error("Ошибка");
        }
      });
    };
  }
});
