import { getCookie } from "/static/core/js/functions.js";
let currentUrl = new URL(window.location.href);

window.addEventListener("DOMContentLoaded", () => {
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
    const productCatalogArticles = document.querySelector(
      ".product-catalog-articles"
    );
    if (productCatalogArticles) {
      const arrowPrice = productCatalogArticles.querySelector(".price_arrow");
      let urlsParam;
      const urlParams = new URL(document.location).searchParams;
      if (urlParams.get("price")) {
        urlsParam = urlParams.get("price");
      }
      arrowPrice.onclick = () => {
        if (urlsParam == "down") {
          urlsParam = "up";
        } else if (urlsParam == "up") {
          urlsParam = "down";
        } else {
          urlsParam = "down";
        }
        if (window.location.href.includes("price")) {
          currentUrl.searchParams.set("price", urlsParam);
        }
        currentUrl.searchParams.set("price", urlsParam);
        history.pushState({}, "", currentUrl);
        window.location.reload();
      };
      if (urlsParam == "down") {
        arrowPrice.classList.add("down");
      } else {
        arrowPrice.classList.add("up");
      }
    }
  }
});
