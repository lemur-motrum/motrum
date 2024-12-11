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
    let pricenone = false;
    let priceFrom;
    let priceTo;
    let sort;

    const loader = catalogWrapper.querySelector(".loader");
    const catalogContainer = catalogWrapper.querySelector(
      '[catalog-elem="container"]'
    );

    const smallLoader = catalogWrapper.querySelector(".small_loader");
    const endContent = catalogWrapper.querySelector(".end_content");
    const noneContentText = catalogWrapper.querySelector(".none_content_data");
    const catalogButton = endContent.querySelector('[catalog-elem="button"]');
    const pagination = catalogWrapper.querySelector(".pagination");
    const paginationElems = pagination.querySelectorAll(".elem");
    const paginationFirstElem = pagination.querySelector(".first");
    const paginationLastElem = pagination.querySelector(".last");
    const firstDots = pagination.querySelector(".first_dots");
    const lastDots = pagination.querySelector(".last_dots");

    const producsPriceSortingWrapper =
      document.querySelector(".catalog_sorting");
    const sortingElems = producsPriceSortingWrapper.querySelectorAll(
      ".catalog_sorting_elem"
    );
    const upPriceBtn =
      producsPriceSortingWrapper.querySelector(".up_price_sorting");
    const downPriceBtn = producsPriceSortingWrapper.querySelector(
      ".down_price_sorting"
    );

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
            if (paginationElems[2].textContent == "") {
              paginationElems[2].style.display = "none";
            } else {
              paginationElems[2].style.display = "flex";
            }
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

    function loadItems(addMoreBtn = false) {
      let data = {
        count: productCount,
        sort: sort ? sort : "?",
        page: pageCount,
        category: category,
        group: !group ? "" : group,
        vendor: paramsArray.length > 0 ? paramsArray : "",
        addMoreBtn: addMoreBtn ? true : false,
        pricefrom: priceFrom ? priceFrom : 0,
        priceto: priceTo ? priceTo : 0,
        pricenone: pricenone,
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
          loader.style.display = "none";
          if (data.data.length == 0) {
            noneContentText.classList.add("show");
          } else {
            lastPage = +data.count;
            const paginationArray = [];
            paginationLastElem.textContent = `${lastPage}`;
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
          }
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
      const pageGetParam = urlParams.get("page");
      const priceGetParam = urlParams.get("price");
      if (pageGetParam) {
        pageCount = +pageGetParam - 1;
        productCount = pageCount * 10;
      }
      if (priceGetParam) {
        sort = priceGetParam == "up" ? "ASC" : "DESC";
        priceGetParam == "up"
          ? upPriceBtn.classList.add("active")
          : downPriceBtn.classList.add("active");
      }

      loadItems();
    };

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      preLoaderLogic();
      productCount = pageCount * 10;
    };

    paginationElems.forEach((elem) => {
      if (!elem.classList.contains("active")) {
        elem.onclick = () => {
          pageCount = +elem.textContent - 1;
          preLoaderLogic();
          productCount = pageCount * 10;
        };
      }
    });
    catalogButton.onclick = () => {
      productCount += 10;
      +pageCount++;
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems();
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      preLoaderLogic();
      productCount = pageCount * 10;
    };

    const filters = document.querySelectorAll(".filter_elem");
    const supplierNameContainer = document.querySelector(
      ".suppliers_max_height_container"
    );
    filters.forEach((filterElem) => {
      const filterValues = filterElem.querySelectorAll(".suplier_elem_content");

      filterValues.forEach((filterValue) => {
        const nameContainer = filterValue.querySelector(
          ".suplier_elem_content_name"
        );
        const vendorParam = filterValue.getAttribute("param");
        if (paramsArray.length > 0) {
          paramsArray.forEach((param) => {
            if (vendorParam == param) {
              nameContainer.classList.add("show");
            }
          });
        }
        filterValue.onclick = () => {
          paramsArray.push(vendorParam);
          nameContainer.classList.toggle("show");
          if (nameContainer.classList.contains("show")) {
            const vendorsString = currentUrl.searchParams.get("vendor");
            if (vendorsString) {
              currentUrl.searchParams.set("vendor", paramsArray.join());
            } else {
              currentUrl.searchParams.set("vendor", paramsArray.join(","));
            }
            pageCount = 0;
            preLoaderLogic();
          } else {
            const searchParams = currentUrl.searchParams;
            const filteredParamsArray = paramsArray.filter(
              (el) => el !== vendorParam
            );
            paramsArray = filteredParamsArray;
            if (filteredParamsArray.length == 0) {
              searchParams.delete("vendor");
            } else {
              searchParams.set("vendor", paramsArray.join());
            }
            preLoaderLogic();
          }
          history.pushState({}, "", currentUrl);
        };
      });
    });

    const priceFilterElemWrapper = document.querySelector(".price_filter_elem");
    const minInputPrice =
      priceFilterElemWrapper.querySelector(".small_price_input");
    const maxInputPrice =
      priceFilterElemWrapper.querySelector(".big_price_input");
    inputValidate(minInputPrice);
    inputValidate(maxInputPrice);

    const priceOneFilterContent = priceFilterElemWrapper.querySelector(
      ".price_checkbox_content"
    );
    const checkboxZone = priceOneFilterContent.querySelector(".checkbox");
    priceOneFilterContent.onclick = () => {
      checkboxZone.classList.toggle("checked");
      if (checkboxZone.classList.contains("checked")) {
        pricenone = true;
      } else {
        pricenone = false;
      }
    };

    const submitFiltersContainer = document.querySelector(
      ".submit_filter_container"
    );

    const filterButton = submitFiltersContainer.querySelector(".submit");
    const cancelFilterButton =
      submitFiltersContainer.querySelector(".canceled");

    filterButton.onclick = () => {
      priceFrom = minInputPrice.value ? +minInputPrice.value : "";
      priceTo = maxInputPrice.value ? +maxInputPrice.value : "";
      pageCount = 0;
      preLoaderLogic();
    };

    cancelFilterButton.onclick = () => {
      const filterValues = document.querySelectorAll(".suplier_elem_content");
      filterValues.forEach((el) => {
        const nameSupplier = el.querySelector(".suplier_elem_content_name");
        nameSupplier.classList.remove("show");
      });
      priceFrom = "";
      priceTo = "";
      maxInputPrice.value = "";
      minInputPrice.value = "";
      pageCount = 0;
      paramsArray = [];
      pricenone = false;
      sort = "";
      sortingElems.forEach((el) => {
        el.classList.remove("active");
      });
      urlParams.delete("price");
      urlParams.delete("vendor");
      checkboxZone.classList.remove("checked");
      preLoaderLogic();
    };

    sortingByPrice(upPriceBtn);
    sortingByPrice(downPriceBtn, false);

    function sortingByPrice(btn, up = true) {
      btn.onclick = () => {
        if (!btn.classList.contains("active")) {
          sortingElems.forEach((el) => {
            el.classList.remove("active");
          });
          btn.classList.add("active");
          urlParams.set("price", up ? "up" : "down");
          sort = up ? "ASC" : "DESC";
        } else {
          btn.classList.remove("active");
          urlParams.delete("price");
          sort = "";
        }
        preLoaderLogic();
      };
    }

    function preLoaderLogic() {
      noneContentText.classList.remove("show");
      endContent.classList.remove("show");
      catalogContainer.innerHTML = "";
      loader.style.display = "block";
      loadItems();
    }

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

    function inputValidate(input) {
      input.addEventListener("input", function (e) {
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d.-]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
        input.value = currentValue;
        if (input.value == ".") {
          e.target.value = "";
        }
        if (input.value == "0") {
          e.target.value = "";
        }
      });
    }
  }
});
