window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const map = document.querySelector("#map");
  if (header) {
    if (!map) {
      const headerHeigth = header.scrollHeight;
      console.log(headerHeigth);
      window.onscroll = () => {
        let windowScrollY = window.scrollY;
        if (windowScrollY > headerHeigth * 7) {
          header.classList.add("fixed");
        } else {
          header.classList.remove("fixed");
        }
      };
    }
  }
});
