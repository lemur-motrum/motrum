import { getCookie } from "/static/core/js/functions.js";

const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".search-container");
  if (wrapper) {
    const csrfToken = getCookie("csrftoken");
    const searchFormContainer = wrapper.querySelector(".search-form-container");
    const searchInput = wrapper.querySelector(['[name="search_input"]']);
    let searchValue;
    const searchEndpoint = "/admin_specification/search_product/";
    const category = searchFormContainer.getAttribute("category");
    const group = searchFormContainer.getAttribute("group");
    const searchElemsField = searchFormContainer.querySelector(
      ".search-elem-fields"
    );
    const closebtn = searchFormContainer.querySelector(
      ".close-sreach-field-button"
    );
    const overlay = wrapper.querySelector(".search-container-overlay");
    const loader = searchFormContainer.querySelector(".loader");
    if (searchInput.value) {
      closebtn.classList.add("show");
      closebtn.onclick = () => {
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
    }
    function searchProduct(arr) {
      arr.forEach((el) => {
        const name = el.querySelector(".name");
        const btn = el.querySelector(".search_button");
        btn.onclick = () => {
          searchInput.value = name.textContent;
          closeSearchWindow();
          urlParams.set("search_input", searchInput.value);
          history.pushState({}, "", currentUrl);
          setTimeout(() => {
            window.location.reload();
          }, 300);
        };
      });
    }
    function openSearchWindow() {
      searchInput.style.borderBottomLeftRadius = 0;
      searchInput.style.borderBottomRightRadius = 0;
      searchElemsField.classList.add("show");
    }
    function closeSearchWindow() {
      searchElemsField.classList.remove("show");
      searchInput.style.borderBottomLeftRadius = "1.875rem";
      searchInput.style.borderBottomRightRadius = "1.875rem";
    }

    let start = 0;
    let counter = 7;
    const objData = {
      category: category,
      group: group,
      value: searchValue,
      start: start,
      counter: counter,
    };
    searchFormContainer.onsubmit = (e) => {
      e.preventDefault();
    };
    searchInput.addEventListener("input", () => {
      searchValue = searchInput.value;
      objData.value = searchValue.trim();
      objData.value = objData.value.replace(/ {1,}/g, " ");
      objData.start = start;
      objData.counter = counter;

      if (searchInput.value.length > 2) {
        if (
          overlay.classList.contains("show") &&
          overlay.classList.contains("visible")
        ) {
          overlay.classList.add("show");
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
