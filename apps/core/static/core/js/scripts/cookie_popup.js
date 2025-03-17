window.addEventListener("DOMContentLoaded", () => {
  const cookiePopupContainer = document.querySelector("[window-elem='cookie']");
  if (cookiePopupContainer) {
    const cookiePopupBtn = cookiePopupContainer.querySelector(".cookie_button");
    if (!localStorage.getItem("cookieModalVisible")) {
      setTimeout(() => {
        cookiePopupContainer.classList.add("visible");
      });
      cookiePopupBtn.onclick = () => {
        localStorage.setItem("cookieModalVisible", true);
        cookiePopupContainer.style.opacity = "0";
        setTimeout(() => {
          cookiePopupContainer.classList.remove("visible");
        }, 700);
      };
    }

    const footer = document.querySelector(".footer");
  }
});
