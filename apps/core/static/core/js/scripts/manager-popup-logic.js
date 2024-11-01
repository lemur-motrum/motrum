window.addEventListener("DOMContentLoaded", () => {
  const managerPopUp = document.querySelector(".personal-manager-container");
  if (managerPopUp) {
    setTimeout(() => {
      managerPopUp.classList.add("visible");
    }, 3000);
  }
});
