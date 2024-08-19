window.addEventListener("DOMContentLoaded", () => {
  const managerPopUp = document.querySelector(".personal-manager-container");
  if (managerPopUp) {
    window.onload = () => {
      setTimeout(() => {
        managerPopUp.classList.add("visible");
      }, 3000);
    };
    managerPopUp.onmouseenter = () => {
      managerPopUp.classList.add("show");
    };
    managerPopUp.onmouseleave = () => {
      managerPopUp.classList.remove("show");
    };
  }
});
