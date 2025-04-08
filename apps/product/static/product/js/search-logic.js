import { getCookie } from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".site_search_container");
  if (wrapper) {
    const searchOverlay = wrapper.querySelector(".search_site_overlay");
    const closeBtn = wrapper.querySelector(".close_btn");
    const searchBtn = wrapper.querySelector(".search_btn");
    const searchInput = wrapper.querySelector(".input_text");
    const searchElemWrapper = wrapper.querySelector(".search_elem_wrapper");
    const loader = searchElemWrapper.querySelector(".loader");
    const searchElemContainer = searchElemWrapper.querySelector(
      '[search-elem="container"]'
    );

    searchInput.oninput = () => {
      if (searchInput.value.length > 4) {
        const valueLength = searchInput.value.length;
        setTimeout(() => {
          if (valueLength == searchInput.value.length) {
            const objData = {
              search_text: searchInput.value,
              count: 0,
              count_last: 5,
            };
            const data = JSON.stringify(objData);

            loader.classList.remove("hide");
            openSearchOverlay();

            fetch("/api/v1/product/search-product-web/", {
              method: "POST",
              body: data,
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
            })
              .then((response) => {
                if (response.status === 200) {
                  // searchInput.disabled = false;
                  searchInput.focus();
                  clearTimeout();
                  loader.classList.add("hide");
                  return response.json();
                } else {
                  setErrorModal();
                }
              })
              .then((response) => {
                if (response.data.length > 0) {
                  for (let i in response.data) {
                    addAjaxCatalogItem(response.data[i]);
                  }
                  searchElemsClasses(searchElemContainer);
                } else {
                  searchElemContainer.innerHTML =
                    "<div class='no_search_elems'>Таких товаров нет</div>";
                }
              });
          }
        }, 600);
      } else {
        closeSearchOverlay();
      }
    };

    closeBtn.onclick = () => {
      searchInput.value = "";
      searchInput.blur();
      closeSearchOverlay();
    };
    searchBtn.onclick = () => openSearchPage();

    function showCloseBtn() {
      if (!closeBtn.classList.contains("show")) {
        closeBtn.classList.add("show");
        setTimeout(() => {
          closeBtn.classList.add("visible");
        }, 600);
      }
    }

    function hideCloseBtn() {
      if (closeBtn.classList.contains("show")) {
        closeBtn.classList.remove("visible");
        setTimeout(() => {
          closeBtn.classList.remove("show");
        }, 600);
      }
    }

    function openOverlay() {
      if (!searchOverlay.classList.contains("show")) {
        searchOverlay.classList.add("show");
        setTimeout(() => {
          searchOverlay.classList.add("visible");
        }, 600);
      }
    }

    function closeOverlay() {
      if (searchOverlay.classList.contains("show")) {
        searchOverlay.classList.remove("visible");
        setTimeout(() => {
          searchOverlay.classList.remove("show");
        }, 600);
      }
    }

    function closeSearchElemWrapper() {
      if (searchElemWrapper.classList.contains("show")) {
        searchInput.classList.remove("inputed");
        searchElemWrapper.classList.remove("visible");
        setTimeout(() => {
          searchElemWrapper.classList.remove("show");
        }, 600);
      }
    }

    function openSearchElemWrapper() {
      if (!searchElemWrapper.classList.contains("show")) {
        searchElemWrapper.classList.add("show");
        setTimeout(() => {
          searchInput.classList.add("inputed");
          searchElemWrapper.classList.add("visible");
        }, 600);
      }
    }

    function showSearchBtn() {
      if (!searchBtn.classList.contains("show")) {
        searchBtn.classList.add("show");
        setTimeout(() => {
          searchBtn.classList.add("visible");
        }, 600);
      }
    }

    function hideSearchBtn() {
      if (searchBtn.classList.contains("show")) {
        searchBtn.classList.remove("visible");
        setTimeout(() => {
          searchBtn.classList.remove("show");
        }, 600);
      }
    }

    function closeSearchOverlay() {
      hideCloseBtn();
      hideSearchBtn();
      closeOverlay();
      closeSearchElemWrapper();
      loader.classList.remove("hide");
    }

    function openSearchOverlay() {
      showCloseBtn();
      showSearchBtn();
      openOverlay();
      openSearchElemWrapper();
      searchElemContainer.innerHTML = "";
    }

    function searchElemsClasses(wrapper) {
      const searchElems = wrapper.querySelectorAll(".search_elem");
      searchElems.forEach((searchElem) => {
        searchElem.onmouseover = () => {
          searchElem.classList.add("active");
        };
        searchElem.onmouseout = () => {
          searchElem.classList.remove("active");
        };
      });
      let counterElems = 0;

      document.addEventListener("keyup", function (e) {
        if (e.code == "ArrowDown") {
          searchElems.forEach((el) => {
            el.classList.remove("active");
          });
          if (counterElems > searchElems.length - 1) {
            counterElems = 0;
          } else {
            counterElems += 1;
          }
          if (searchElems[counterElems - 1]) {
            searchElems[counterElems - 1].classList.add("active");
          }
        }
        if (e.code == "ArrowUp") {
          searchElems.forEach((el) => {
            el.classList.remove("active");
          });
          if (counterElems < 1) {
            counterElems = searchElems.length;
          } else {
            counterElems -= 1;
          }
          if (searchElems[counterElems - 1]) {
            searchElems[counterElems - 1].classList.add("active");
          }
        }
        if (e.code == "Enter") {
          let counter = 1;
          let url;
          for (let i = 0; i < searchElems.length; i++) {
            if (searchElems[i].classList.contains("active")) {
              counter = 0;
              url = searchElems[i].getAttribute("data-url");
              break;
            } else {
              counter = +1;
            }
          }

          if (counter == 0) {
            window.location.href = url;
          } else {
            openSearchPage();
          }
        }
      });
    }

    function openSearchPage() {
      window.location.href = `/product/search?page=1&search_text=${searchInput.value}`;
    }

    function renderCatalogItem(productData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[search-elem="search-elem"]'
      ).innerText;
      return nunjucks.renderString(ajaxCatalogElementTemplate, productData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      searchElemContainer.insertAdjacentHTML(
        "beforeend",
        renderCatalogItemHtml
      );
    }
  }
});
