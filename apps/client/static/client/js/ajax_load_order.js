import { version } from "/static/core/js/scripts/version.js";

const { getCookie, getDigitsNumber } = await import(
  `/static/core/js/functions.js?ver=${version}`
);
const { setErrorModal } = await import(
  `/static/core/js/error_modal.js?ver=${version}`
);

const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const catalogWrapper = document.querySelector('[order-elem="wrapper"]');
  if (catalogWrapper) {
    let paramsArray = [];

    const catalogContainer = catalogWrapper.querySelector(
      '[order-elem="container"]'
    );
    const loader = catalogWrapper.querySelector(".loader");
    const smallLoader = catalogWrapper.querySelector(".small_loader");
    const endContent = catalogWrapper.querySelector(".end_content");
    const catalogButton = endContent.querySelector('[catalog-elem="button"]');
    const pagination = catalogWrapper.querySelector(".pagination");
    const paginationElems = pagination.querySelectorAll(".elem");
    const paginationFirstElem = pagination.querySelector(".first");
    const paginationLastElem = pagination.querySelector(".last");
    const firstDots = pagination.querySelector(".first_dots");
    const lastDots = pagination.querySelector(".last_dots");

    let pageCount = 0;
    let productCount = 0;
    let lastPage = 0;

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
          console.log(`pageCount - ${pageCount}, delta - ${lastPage - 2}`);
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
          console.log(`pageCount - ${pageCount}, delta - ${lastPage - 2}`);
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
        page: pageCount,
        addMoreBtn: addMoreBtn ? true : false,
      };

      let params = new URLSearchParams(data);
      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/order/load-ajax-order-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => {
          if (response.status >= 200 && response.status < 300) {
            return response.json();
          } else {
            setErrorModal();
          }
        })
        .then(function (data) {
          endContent.classList.add("show");
          smallLoader.classList.remove("show");
          lastPage = +data.count;
          console.log(lastPage);
          const paginationArray = [];
          paginationLastElem.textContent = `${lastPage}`;

          for (let i in data.data) {
            // data.data[i]["bill_sum"] = data.data[i]["bill_sum"].toFixed(2);
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
          getActivePaginationElem();
          loader.classList.add("hide");
          const prices = document.querySelectorAll(".price");
          prices.forEach((price) => {
            if (!isNaN(+price.textContent)) {
              getDigitsNumber(price, price.textContent);
            }
          });
          urlParams.set("page", pageCount + 1);
          history.pushState({}, "", currentUrl);
        });
    }

    window.onload = () => {
      const pageGetParam = currentUrl.searchParams.get("page");
      if (pageGetParam) {
        pageCount = +pageGetParam - 1;
        productCount = pageCount * 5;
        loadItems();
      } else {
        loadItems();
      }
    };

    paginationElems.forEach((elem) => {
      if (!elem.classList.contains("active")) {
        elem.onclick = () => {
          pageCount = +elem.textContent - 1;
          productCount = pageCount * 5;
          endContent.classList.remove("show");
          catalogContainer.innerHTML = "";
          loader.classList.remove("hide");
          loadItems(true);
        };
      }
    });

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      productCount = 0;
      endContent.classList.remove("show");
      catalogContainer.innerHTML = "";
      loader.classList.remove("hide");
      loadItems(true);
    };

    catalogButton.onclick = () => {
      productCount += 5;
      +pageCount++;
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems(true);
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      productCount = pageCount * 5;
      endContent.classList.remove("show");
      catalogContainer.innerHTML = "";
      loader.classList.remove("hide");
      loadItems(true);
    };

    function renderCatalogItem(orderData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[lk-elem="order-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }
  }
});
