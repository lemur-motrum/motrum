import { getCookie } from "/static/core/js/functions.js";

let currentUrl = new URL(window.location.href);

window.addEventListener("DOMContentLoaded", () => {
  const filters = document.querySelectorAll(".filter_elem");
  filters.forEach((filterElem) => {
    const title = filterElem.querySelector(".filter_title");
    const filterContent = filterElem.querySelector(".filter-wrapper-content");
    const arrow = filterElem.querySelector(".arrow");
    const filterValues = filterElem.querySelectorAll(".filter_elem_content");
    filterValues.forEach((filterValue) => {
      const checkbox = filterValue.querySelector(".checked");
      const vendorParam = filterValue.getAttribute("param");
      filterValue.onclick = () => {
        checkbox.classList.toggle("show");
        if (checkbox.classList.contains("show")) {
          if (window.location.href.includes("?")) {
            currentUrl.searchParams.append("vendor", vendorParam);
          } else {
            currentUrl.searchParams.set("vendor", vendorParam);
          }
        } else {
          const searchParams = currentUrl.searchParams;
          searchParams.delete("vendor", vendorParam);
        }
        history.pushState({}, "", currentUrl);
      };
    });
    title.onclick = () => {
      filterContent.classList.toggle("is_open");
      arrow.classList.toggle("rotate");
    };
  });
});
