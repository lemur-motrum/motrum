import { getCookie } from "../../../../core/static/core/js/functions.js";
const currentUrl = new URL(window.location);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const adminSpecificationsFilters = document.querySelector(
    ".admin_specification_filters"
  );
  if (adminSpecificationsFilters) {
    const sliderFilters = new Swiper(".vendor_filters", {
      slidesPerView: "auto",
      navigation: {
        nextEl: ".next_btn_verndor_filter",
      },
    });
    const vendorsFilter =
      adminSpecificationsFilters.querySelector(".vendor_filters");
    const resertBtn =
      adminSpecificationsFilters.querySelector(".resert_filters");
    if (vendorsFilter) {
      const sliderWrapper = vendorsFilter.querySelector(".swiper-wrapper");
      const filterValues = vendorsFilter.querySelectorAll(
        ".filter_elem_content"
      );

      let paramsArray = [];

      if (urlParams.get("vendor")) {
        const urlsParamArray = urlParams.get("vendor").split(",");
        urlsParamArray.forEach((el) => {
          paramsArray.push(el);
        });
      }

      filterValues.forEach((filterValue) => {
        const vendorParam = filterValue.getAttribute("param");
        if (paramsArray.length > 0) {
          paramsArray.forEach((param) => {
            if (vendorParam == param) {
              filterValue.classList.add("active");
              sliderWrapper.prepend(filterValue);
              resertBtn.classList.add("show");
            }
          });
        }
        resertBtn.onclick = () => {
          paramsArray = [];
          filterValue.classList.remove("active");
          urlParams.delete("vendor");
          history.pushState({}, "", currentUrl);
          window.location.reload();
        };

        filterValue.onclick = () => {
          paramsArray.push(vendorParam);
          filterValue.classList.toggle("active");
          if (filterValue.classList.contains("active")) {
            if (urlParams.has("vendor")) {
              urlParams.set("vendor", paramsArray.join());
            } else {
              urlParams.set("vendor", paramsArray.join(","));
            }
          } else {
            const filteredParamsArray = paramsArray.filter(
              (el) => el !== vendorParam
            );
            paramsArray = filteredParamsArray;
            urlParams.set("vendor", paramsArray.join());
            if (filteredParamsArray.length == 0) {
              urlParams.delete("vendor");
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
