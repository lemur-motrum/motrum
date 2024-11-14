import { deleteCookie } from "/static/core/js/functions.js";

export function setErrorModal() {
  const overlay = document.querySelector(".error_overlay_modal");
  const btn = overlay.querySelector(".btn");
  overlay.classList.add("show");
  setTimeout(() => {
    overlay.classList.add("visible");
  }, 500);

  btn.onclick = () => {
    btn.textContent = "";
    btn.innerHTML = "<div class='small_loader'></div>";
    localStorage.removeItem("specificationValues");
    deleteCookie("key", "/", window.location.hostname);
    deleteCookie("specificationId", "/", window.location.hostname);
    deleteCookie("cart", "/", window.location.hostname);
    window.location.href = "/admin_specification/";
  };
}
