export function successModal(mes) {
  const overlay = document.querySelector(".overlay_success_modal");
  const modalWindow = overlay.querySelector(".modal_window");
  const message = modalWindow.querySelector(".message");
  message.textContent = mes;

  overlay.classList.add("show");
  setTimeout(() => {
    overlay.classList.add("visible");
  }, 600);

  setTimeout(() => {
    overlay.classList.remove("visible");
    setTimeout(() => {
      overlay.classList.remove("show");
    }, 700);
  }, 3000);
}
