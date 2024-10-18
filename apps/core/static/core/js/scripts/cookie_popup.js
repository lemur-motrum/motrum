window.addEventListener("DOMContentLoaded", () => {
  const cookiePopupContainer = document.querySelector("[window-elem='cookie']");
  if (cookiePopupContainer) {
    const cookiePopupBtn = cookiePopupContainer.querySelector(".cookie_button");
    if (!sessionStorage.getItem("cookieModalVisible")) {
      cookiePopupContainer.style.display = "flex";
      setTimeout(() => {
        cookiePopupContainer.classList.add("visible");
      });
      cookiePopupBtn.onclick = () => {
        sessionStorage.setItem("cookieModalVisible", true);
        cookiePopupContainer.style.opacity = "0";
        setTimeout(() => {
          cookiePopupContainer.classList.remove("visible");
        }, 700);
      };
    } else {
    }
  }
});
