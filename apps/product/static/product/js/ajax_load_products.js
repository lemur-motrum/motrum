import {
  getCookie,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const catalogWrapper = document.querySelector('[catalog-elem="wrapper"]');
  if (catalogWrapper) {
    const category = document
      .querySelector("[data-category-id]")
      .getAttribute("data-category-id");
    const group = document
      .querySelector("[data-group-id]")
      .getAttribute("data-group-id");
    let pageCount = 0;
    let productCount = 0;
    let lastPage = 0;
    let paramsArray = [];

    const loader = catalogWrapper.querySelector(".loader");
    const catalogContainer = catalogWrapper.querySelector(
      '[catalog-elem="container"]'
    );

    const smallLoader = catalogWrapper.querySelector(".small_loader");
    const endContent = catalogWrapper.querySelector(".end_content");
    const catalogButton = endContent.querySelector('[catalog-elem="button"]');
    const pagination = catalogWrapper.querySelector(".pagination");
    const paginationElems = pagination.querySelectorAll(".elem");
    const paginationFirstElem = pagination.querySelector(".first");
    const paginationLastElem = pagination.querySelector(".last");
    const firstDots = pagination.querySelector(".first_dots");
    const lastDots = pagination.querySelector(".last_dots");

    function getActivePaginationElem() {
      for (let i = 0; i < paginationElems.length; i++) {
        if (paginationElems[i].textContent == pageCount + 1) {
          paginationElems[i].classList.add("active");
        } else {
          paginationElems[i].classList.remove("active");
        }
      }
      showFirstPaginationElem();
    }

    function showFirstPaginationElem() {
      if (pageCount >= 2) {
        paginationFirstElem.classList.add("show");
        firstDots.classList.add("show");
      } else {
        paginationFirstElem.classList.remove("show");
        firstDots.classList.remove("show");
      }
      if (pageCount >= 0 && pageCount < 4) {
        if (pageCount >= lastPage - 3) {
          paginationLastElem.classList.remove("show");
          lastDots.classList.remove("show");
          if (pageCount >= lastPage - 1) {
            paginationElems[2].style.display = "none";
            if (paginationElems[1].textContent == "") {
              paginationElems[1].style.display = "none";
            }
          } else {
            paginationElems[2].style.display = "flex";
          }
        } else {
          paginationElems[2].style.display = "flex";
          paginationLastElem.classList.add("show");
          lastDots.classList.add("show");
        }
      } else {
        if (pageCount >= lastPage - 2) {
          paginationLastElem.classList.remove("show");
          lastDots.classList.remove("show");
          if (pageCount >= lastPage - 1) {
            paginationElems[2].style.display = "none";
          } else {
            paginationElems[2].style.display = "flex";
          }
        } else {
          paginationLastElem.classList.add("show");
          lastDots.classList.add("show");
        }
      }
    }

    function loadItems(
      paginationFn = false,
      cleanArray = false,
      vendor = false,
      addMoreBtn = false
    ) {
      let data = {
        count: !paginationFn ? productCount : 10,
        sort: "?",
        page: pageCount,
        category: category,
        group: !group ? "" : group,
        vendor: !vendor ? "" : vendor,
        addMoreBtn: addMoreBtn ? true : false,
      };

      let params = new URLSearchParams(data);

      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/product/load-ajax-product-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then(function (data) {
          lastPage = +data.count;
          const paginationArray = [];
          paginationLastElem.textContent = `${lastPage}`;
          loader.style.display = "none";
          endContent.classList.add("show");
          smallLoader.classList.remove("show");

          for (let i in data.data) {
            addAjaxCatalogItem(data.data[i]);
          }

          if (data.next) {
            catalogButton.disabled = false;
          } else {
            catalogButton.disabled = true;
          }

          for (
            let i = pageCount == 0 ? pageCount : pageCount - 1;
            !data.small
              ? i < pageCount + 3
              : +data.count > 1
              ? i <= pageCount + 1
              : i <= pageCount;
            i++
          ) {
            paginationArray.push(i);
          }
          if (cleanArray) {
            paginationElems.forEach((elem) => {
              elem.textContent = "";
            });
          }
          paginationElems.forEach((el) => (el.textContent = ""));
          paginationArray.forEach((el, i) => {
            if (paginationElems[i]) {
              paginationElems[i].textContent = +el + 1;
            }
          });

          const products = document.querySelectorAll(".product_item");
          products.forEach((productItem) => {
            const priceItem = productItem.querySelector(".price_item");
            if (priceItem) {
              const currentPrice = +getCurrentPrice(priceItem.textContent);
              if (!isNaN(currentPrice)) {
                getDigitsNumber(priceItem, currentPrice);
              }
            }
          });
          getActivePaginationElem();
          urlParams.set("page", pageCount + 1);
          history.pushState({}, "", currentUrl);
        });
    }

    if (urlParams.get("vendor")) {
      const urlsParamArray = urlParams.get("vendor").split(",");
      urlsParamArray.forEach((el) => {
        paramsArray.push(el);
      });
    }

    window.onload = () => {
      const pageGetParam = currentUrl.searchParams.get("page");

      if (pageGetParam) {
        pageCount = +pageGetParam - 1;
        if (paramsArray.length === 0) {
          loadItems(true, false, false, false);
          productCount = pageCount * 10;
        } else {
          loadItems(true, false, paramsArray, false);
          productCount = pageCount * 10;
        }
      } else {
        if (paramsArray.length === 0) {
          loadItems(false, false, false, false);
        } else {
          loadItems(false, false, paramsArray, false);
        }
      }
    };

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      endContent.classList.remove("show");
      catalogContainer.innerHTML = "";
      loader.style.display = "block";

      loadItems(
        true,
        true,
        paramsArray.length > 0 ? paramsArray : false,
        false
      );
      productCount = pageCount * 10;
    };

    paginationElems.forEach((elem) => {
      if (!elem.classList.contains("active")) {
        elem.onclick = () => {
          pageCount = +elem.textContent - 1;
          endContent.classList.remove("show");
          catalogContainer.innerHTML = "";
          loader.style.display = "block";
          loadItems(
            true,
            false,
            paramsArray.length > 0 ? paramsArray : false,
            false
          );
          productCount = pageCount * 10;
        };
      }
    });
    catalogButton.onclick = () => {
      productCount += 10;
      +pageCount++;
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems(
        false,
        false,
        paramsArray.length > 0 ? paramsArray : false,
        true
      );
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      endContent.classList.remove("show");
      catalogContainer.innerHTML = "";
      loader.style.display = "block";
      loadItems(
        true,
        true,
        paramsArray.length > 0 ? paramsArray : false,
        false
      );
      productCount = pageCount * 10;
    };

    function renderCatalogItem(productData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[catalog-elem="product-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, productData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }

    const filters = document.querySelectorAll(".filter_elem");
    filters.forEach((filterElem) => {
      const title = filterElem.querySelector(".filter_title");
      const filterContent = filterElem.querySelector(".filter-wrapper-content");
      const arrow = filterElem.querySelector(".arrow");
      const filterValues = filterElem.querySelectorAll(".filter_elem_content");

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
            const vendorsString = currentUrl.searchParams.get("vendor");
            if (vendorsString) {
              currentUrl.searchParams.set("vendor", paramsArray.join());
              loader.style.display = "block";
              catalogContainer.innerHTML = "";
              endContent.classList.remove("show");
              pageCount = 0;
              loadItems(false, false, paramsArray, false);
            } else {
              currentUrl.searchParams.set("vendor", paramsArray.join(","));
              loader.style.display = "block";
              catalogContainer.innerHTML = "";
              endContent.classList.remove("show");
              pageCount = 0;
              loadItems(false, false, paramsArray, false);
            }
          } else {
            const searchParams = currentUrl.searchParams;
            const filteredParamsArray = paramsArray.filter(
              (el) => el !== vendorParam
            );
            paramsArray = filteredParamsArray;
            searchParams.set("vendor", paramsArray.join());
            loader.style.display = "block";
            catalogContainer.innerHTML = "";
            endContent.classList.remove("show");
            pageCount = 0;

            if (filteredParamsArray.length == 0) {
              searchParams.delete("vendor", paramsArray.join());
              loader.style.display = "block";
              catalogContainer.innerHTML = "";
              endContent.classList.remove("show");
              loadItems(false, false, false, false);
            } else {
              loadItems(false, true, paramsArray, false);
            }
          }
          history.pushState({}, "", currentUrl);
        };
      });
      // title.onclick = () => {
      //   filterContent.classList.toggle("is_open");
      //   arrow.classList.toggle("rotate");
      // };
    });
  }
});
