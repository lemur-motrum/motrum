import { setPreloaderInButton } from "/static/core/js/functions.js";

export function setErrorModal() {
  const overlay = document.querySelector(".error_overlay_modal");
  const btn = overlay.querySelector(".btn");
  overlay.classList.add("show");

  requestAnimationFrame(() => {
    overlay.classList.add("visible");
  });

  btn.onclick = () => {
    setPreloaderInButton(btn);
    setTimeout(() => {
      window.location.reload();
    }, 300);
  };
}
