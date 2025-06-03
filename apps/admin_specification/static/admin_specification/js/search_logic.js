import { getCookie } from "/static/core/js/functions.js";

const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".search-container");
  if (wrapper) {
    const csrfToken = getCookie("csrftoken");

    const searchFormContainer = wrapper.querySelector(".search-form-container");
    const searchInput = wrapper.querySelector(['[name="search_input"]']);
    const category = searchFormContainer.getAttribute("category");
    const group = searchFormContainer.getAttribute("group");
    const searchElemsBlockWrapper = wrapper.querySelector(
      ".search_elems_block_wrapper"
    );
    const searchElemsField = searchFormContainer.querySelector(
      ".search-elem-fields"
    );
    const closebtn = searchFormContainer.querySelector(
      ".close-sreach-field-button"
    );
    const overlay = wrapper.querySelector(".search-container-overlay");
    const loader = searchFormContainer.querySelector(".loader");
    const smallLoader = searchFormContainer.querySelector(".small_loader");
    const searchElemContainer = wrapper.querySelector(
      '[okt-search-elem="container"]'
    );

    let count = 0;
    let countLast = 9;
    let finish = false;

    if (searchInput.value) {
      closebtn.classList.add("show");
    }

    searchInput.oninput = () => {
      if (searchInput.value.length > 3) {
        const valueLength = searchInput.value.length;

        setTimeout(() => {
          count = 0;
          countLast = 9;
          finish = false;
          if (valueLength == searchInput.value.length) {
            // smallLoader.classList.remove("show");
            loader.classList.remove("remove");
            openSearchOverlay();
            getProducts();
          }
        }, 600);
      } else {
        closeSearchOverlay();
      }
    };

    searchElemsField.addEventListener("scroll", function () {
      if (this.scrollHeight >= this.scrollTop + this.clientHeight) {
        if (!finish) {
          if (
            !smallLoader.classList.contains("show") &&
            count != 0 &&
            countLast != 9
          ) {
            getProducts();
            smallLoader.classList.add("show");
          }
        }
      }
    });

    closebtn.onclick = () => {
      const param = new URLSearchParams(window.location.search).get(
        "search_input"
      );
      if (param) {
        window.location.href = window.location.pathname;
      } else {
        searchInput.value = "";
        closeSearchOverlay();
      }
    };

    function openSearchElemWrapper() {
      if (!searchElemsBlockWrapper.classList.contains("show")) {
        searchElemsBlockWrapper.classList.add("show");
        searchElemsField.classList.add("show");
        setTimeout(() => {
          searchInput.classList.add("inputed");
          searchElemsBlockWrapper.classList.add("visible");
          searchElemsField.classList.add("visible");
        }, 600);
      }
    }

    function closeSearchElemWrapper() {
      if (searchElemsBlockWrapper.classList.contains("show")) {
        searchInput.classList.remove("inputed");
        searchElemsBlockWrapper.classList.remove("visible");
        searchElemsField.classList.remove("visible");
        setTimeout(() => {
          searchElemsBlockWrapper.classList.remove("show");
          searchElemsField.classList.remove("show");
        }, 600);
      }
    }

    function openSearchOverlay() {
      openOverlay();
      openSearchElemWrapper();
      closebtn.classList.add("show");
      searchElemContainer.innerHTML = "";
    }

    function openOverlay() {
      if (!overlay.classList.contains("show")) {
        overlay.classList.add("show");
        setTimeout(() => {
          overlay.classList.add("visible");
        }, 600);
      }
    }

    function closeOverlay() {
      if (overlay.classList.contains("show")) {
        overlay.classList.remove("visible");
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
      }
    }

    function closeSearchOverlay() {
      closeOverlay();
      closeSearchElemWrapper();
      closebtn.classList.remove("show");
      loader.classList.remove("remove");
    }

    function getProducts() {
      const data = {
        search_text: searchInput.value,
        count: count,
        count_last: countLast,
        cat: category ? category : "",
        gr: group ? group : "",
      };
      fetch("/api/v1/product/search-product-okt-categ/", {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => {
          if (response.status === 200) {
            smallLoader.classList.remove("show");
            loader.classList.add("remove");
            console.log(finish);
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
            count += 9;
            countLast += 9;
            clickOnTheProduct(
              wrapper.querySelector(".search_elem_fields_container")
            );
          } else {
            if (count == 0 && countLast == 9) {
              searchElemContainer.innerHTML =
                "<div class='no_search_elems'>Таких товаров нет</div>";
            } else {
              finish = true;
              return;
            }
          }
        });
    }

    function clickOnTheProduct(block) {
      const searchElems = block.querySelectorAll(".product");
      searchElems.forEach((searchElem) => {
        const name = searchElem.querySelector(".name");
        searchElem.onclick = () => {
          window.location.href = `?search_input=${name.textContent}`;
        };
      });
    }

    function renderCatalogItem(productData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[okt-search-elem="okt-search-elem"]'
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
