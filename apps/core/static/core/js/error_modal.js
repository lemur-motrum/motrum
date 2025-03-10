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
    window.location.reload();
  };
}
