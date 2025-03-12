window.addEventListener("load", () => {
  const headerWrapper = document.querySelector(".header");
  if (headerWrapper) {
    const burgerMenuNav = headerWrapper.querySelector(".burger_menu_nav");
    const navigation = headerWrapper.querySelector(".user-navigation");
    burgerMenuNav.onclick = () => {
      burgerMenuNav.classList.toggle("checked");
      if (burgerMenuNav.classList.contains("checked")) {
        navigation.classList.add("show");
        document.body.style.overflow = "hidden";
      } else {
        navigation.classList.remove("show");
        document.body.style.overflow = "auto";
      }
    };
  }
});
