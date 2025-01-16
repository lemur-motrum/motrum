window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const map = document.querySelector("#map");
  const headerWrapper = document.querySelector(".header_wrapper124");
  if (header) {
    if (!map) {
      const headerHeigth = header.scrollHeight;
      console.log(headerHeigth);
      window.onscroll = () => {
        let windowScrollY = window.scrollY;
        if (windowScrollY > headerHeigth * 10) {
          console.log("headerHeigth", headerHeigth);
          headerWrapper.style.height = headerHeigth + "px";
          header.classList.add("fixed");
        } else {
          headerWrapper.style.height = "0px";
          header.classList.remove("fixed");
        }
      };
    }
  }
});
