window.addEventListener("DOMContentLoaded", () => {
  const managerPopUp = document.querySelector(".personal-manager-container");
  if (managerPopUp) {
    const overlay = managerPopUp.querySelector(".manager_callback_overlay");
    const openOverlayBtn = managerPopUp.querySelector(".open_overlay_btn");
    const closeOverlayBtn = overlay.querySelector(".close_btn");

    setTimeout(() => {
      managerPopUp.classList.add("visible");
    }, 3000);

    function openOverlay() {
      overlay.classList.add("show");
      setTimeout(() => {
        overlay.classList.add("visible");
      });
    }

    function closeOverlay() {
      overlay.classList.remove("visible");
      setTimeout(() => {
        overlay.classList.remove("show");
      }, 600);
    }

    openOverlayBtn.onclick = () => openOverlay();
    closeOverlayBtn.onclick = () => closeOverlay();
  }
});
