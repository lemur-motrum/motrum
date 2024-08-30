window.addEventListener("DOMContentLoaded", () => {
  const managerPopUp = document.querySelector(".personal-manager-container");
  if (managerPopUp) {
    setTimeout(() => {
      managerPopUp.classList.add("visible");
    }, 5000);
    managerPopUp.onmouseenter = () => {
      managerPopUp.classList.add("show");
    };
    managerPopUp.onmouseleave = () => {
      managerPopUp.classList.remove("show");
    };
  }
});
