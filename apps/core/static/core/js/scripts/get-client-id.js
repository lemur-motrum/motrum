import { version } from "/static/core/js/scripts/version.js";
const { deleteCookie } = await import(
  `/static/core/js/functions.js?ver=${version}`
);

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
