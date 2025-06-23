import { getCookie } from "/static/core/js/functions.js";
import { setErrorModal } from "/static/core/js/error_modal.js"

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
      finish = true;
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
        } else {
          overlay.classList.add("show");
          overlay.classList.add("visible");
        }
        openSearchWindow();
        closebtn.classList.add("show");
        const data = JSON.stringify(objData);
        fetch(searchEndpoint, {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((response) => {
            if (response.status == "ok") {
              loader.classList.add("remove");
              const products = JSON.parse(response.products);
              searchElemsField.innerHTML = "";
              products.forEach((product) => {
                searchElemsField.innerHTML += `<div class="product">
                          <span class="name">${product.fields.name}</span>
                          <span class="search_button">Найти</span>
                          </div>`;
              });
              const searchProducts =
                searchElemsField.querySelectorAll(".product");
              if (searchProducts.length > 0) {
                searchProduct(searchProducts);
                if (products.length == 0) {
                  searchElemsField.innerHTML = "<div>Таких товаров нет</div>";
                } else {
                  let counterElems = 0;
                  searchProducts.forEach((el, i) => {
                    el.onmouseover = () => {
                      searchProducts.forEach((el) =>
                        el.classList.remove("active")
                      );
                      el.classList.add("active");
                      counterElems = i + 1;
                    };
                    el.onmouseout = () => {
                      el.classList.remove("active");
                      counterElems = 0;
                    };
                  });

                  document.addEventListener("keyup", function (e) {
                    console.log(counterElems);
                    if (e.code == "ArrowDown") {
                      searchProducts.forEach((el) => {
                        el.classList.remove("active");
                      });
                      if (counterElems > searchProducts.length - 1) {
                        counterElems = 0;
                      } else {
                        counterElems += 1;
                      }
                      if (searchProducts[counterElems - 1]) {
                        searchProducts[counterElems - 1].classList.add(
                          "active"
                        );
                        const name =
                          searchProducts[counterElems - 1].querySelector(
                            ".name"
                          );
                        searchInput.value = name.textContent;
                      }
                    }
                    if (e.code == "ArrowUp") {
                      searchProducts.forEach((el) => {
                        el.classList.remove("active");
                      });
                      if (counterElems < 1) {
                        counterElems = searchProducts.length;
                      } else {
                        counterElems -= 1;
                      }
                      if (searchProducts[counterElems - 1]) {
                        searchProducts[counterElems - 1].classList.add(
                          "active"
                        );
                        const name =
                          searchProducts[counterElems - 1].querySelector(
                            ".name"
                          );
                        searchInput.value = name.textContent;
                      }
                    }
                    if (e.code == "Enter") {
                      if (searchInput.value) {
                        closeSearchWindow();
                        urlParams.set("search_input", searchInput.value.trim());
                        history.pushState({}, "", currentUrl);
                        setTimeout(() => {
                          window.location.reload();
                        }, 300);
                      }
                    }
                  });
                }
              } else {
                searchElemsField.innerHTML = "<div>Таких товаров нет</div>";
              }
            }
          })
          .catch((error) => console.error(error));
      } else {
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 200);
        overlay.classList.remove("visible");
        closebtn.classList.remove("show");
        start = 0;
        counter = 7;
        objData.start = start;
        objData.counter = counter;
        closeSearchWindow();
      }
      closebtn.onclick = () => {
        closeSearchWindow();
        closebtn.classList.remove("show");
        urlParams.delete("search_input");
        searchInput.value = "";
        start = 0;
        counter = 7;
        objData.start = start;
        objData.counter = counter;
        history.pushState({}, "", currentUrl);
        window.location.reload();
      };
    });
  }
});
