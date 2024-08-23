import { deleteCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const clientInput = document.querySelector("#client_id");
  if (clientInput) {
    const clientId = clientInput.getAttribute("data-user-id");
    if (clientId) {
      document.cookie = `client_id=${clientId}; path=/`;
    } else {
      deleteCookie("key", "/");
    }
  }
});
