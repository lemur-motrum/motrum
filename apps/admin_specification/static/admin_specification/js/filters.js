import { getCookie } from "/static/core/js/functions.js";
let currentUrl = new URL(window.location.href);
const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const searhForm = document.querySelector(".search-form-container");

  const adminSpecificationsFilters = document.querySelector(
    ".admin_specification_filters"
  );
  if (adminSpecificationsFilters) {
    const vendorsFilter =
      adminSpecificationsFilters.querySelector(".vendor_filters");
    if (vendorsFilter) {
      const filterValues = vendorsFilter.querySelectorAll(
        ".filter_elem_content"
      );

      let paramsArray = [];
      const urlParams = new URL(document.location).searchParams;

      if (urlParams.get("vendor")) {
        const urlsParamArray = urlParams.get("vendor").split(",");
        urlsParamArray.forEach((el) => {
          paramsArray.push(el);
        });
      }

      filterValues.forEach((filterValue) => {
        const checkbox = filterValue.querySelector(".checked");
        const vendorParam = filterValue.getAttribute("param");
        if (paramsArray.length > 0) {
          paramsArray.forEach((param) => {
            if (vendorParam == param) {
              checkbox.classList.add("show");
            }
          });
        }
        filterValue.onclick = () => {
          paramsArray.push(vendorParam);
          checkbox.classList.toggle("show");
          if (checkbox.classList.contains("show")) {
            if (window.location.href.includes("?vendor")) {
              currentUrl.searchParams.set("vendor", paramsArray.join());
            } else {
              currentUrl.searchParams.set("vendor", paramsArray.join(","));
            }
          } else {
            const searchParams = currentUrl.searchParams;
            const filteredParamsArray = paramsArray.filter(
              (el) => el !== vendorParam
            );
            paramsArray = filteredParamsArray;
            searchParams.set("vendor", paramsArray.join());
            if (filteredParamsArray.length == 0) {
              searchParams.delete("vendor", paramsArray.join());
            }
          }
          history.pushState({}, "", currentUrl);

          window.location.reload();
        };
      });
    }
    const priceFilters =
      adminSpecificationsFilters.querySelector(".price_filters");
    if (priceFilters) {
      const filterValues = priceFilters.querySelectorAll(
        ".filter_elem_content"
      );
      const urlParams = new URL(document.location).searchParams;
      let urlsParam;
      if (urlParams.get("price")) {
        urlsParam = urlParams.get("price");
      }
      const checkboxes = priceFilters.querySelectorAll(".checked");
      filterValues.forEach((filterValue) => {
        const checkbox = filterValue.querySelector(".checked");
        const priceParam = filterValue.getAttribute("param");
        if (urlsParam) {
          if (priceParam == urlsParam) {
            checkbox.classList.add("show");
          }
        }

        filterValue.onclick = () => {
          if (checkbox.classList.contains("show")) {
            currentUrl.searchParams.delete("price", priceParam);
            checkbox.classList.remove("show");
          } else {
            checkboxes.forEach((el) => el.classList.remove("show"));
            currentUrl.searchParams.set("price", priceParam);
            checkbox.classList.add("show");
          }

          history.pushState({}, "", currentUrl);
          window.location.reload();
        };
      });
    }
  }
});
