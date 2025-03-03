window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const map = document.querySelector("#map");
  const headerWrapper = document.querySelector(".header_wrapper124");
  if (header) {
    const orderCounts = header.querySelectorAll(".order_count");
    orderCounts.forEach((orderCount) => {
      if (+orderCount.textContent.trim() > 0) {
        orderCount.classList.add("blue");
      }
    });

    if (!map) {
      const headerHeigth = header.scrollHeight;
      window.onscroll = () => {
        let windowScrollY = window.scrollY;
        if (windowScrollY > headerHeigth * 10) {
          headerWrapper.style.height = headerHeigth * 1.3 + "px";
          header.classList.add("fixed");
        } else {
          headerWrapper.style.height = "0px";
          header.classList.remove("fixed");
        }
      };
    }
  }
});
