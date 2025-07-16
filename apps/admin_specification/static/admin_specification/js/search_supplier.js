import { getCookie, showErrorValidation } from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".okt_cart_container");
  if (wrapper) {
    const vendorLabels = wrapper.querySelectorAll(".vendor_label");

    vendorLabels.forEach((vendorLabel) => {
      const vendorSearchInput = vendorLabel.querySelector(".vendor_input");
      const vendorSearchElemsContainerWrapper = vendorLabel.querySelector(
        ".vendor_input_elems_container_wrapper"
      );
      const vendorSearchElemsContainer = vendorLabel.querySelector(
        ".vendor_input_elems_container"
      );
      const loader = vendorSearchElemsContainer.querySelector(".loader");
      const smallLoader =
        vendorSearchElemsContainer.querySelector(".small_loader");
      const searchElemsContainer =
        vendorSearchElemsContainer.querySelector(".search_elems");
      const noneContent =
        vendorSearchElemsContainer.querySelector(".none_content");

      const searchElemContainer = vendorLabel.querySelector(
        "[search-supplier-elem='container']"
      );

      let count = 0;
      let countLast = 5;
      let finish = false;

      vendorSearchInput.oninput = () => {
        const inputedvalue = vendorSearchInput.value;
        searchElemsContainer.innerHTML = "";
        vendorSearchInput.setAttribute("vendor_value", "");
        loader.classList.remove("hide");
        noneContent.classList.remove("show");
        if (vendorSearchInput) {
          vendorSearchInput.classList.add("inputed");
          vendorSearchElemsContainerWrapper.classList.add("show");
          vendorSearchElemsContainer.classList.add("show");
          setTimeout(() => {
            count = 0;
            countLast = 5;
            finish = false;
            if (inputedvalue == vendorSearchInput.value) {
              getSearchElems();
            }
          }, 600);
        } else {
          vendorSearchElemsContainerWrapper.classList.remove("show");
          vendorSearchElemsContainer.classList.remove("show");
          vendorSearchInput.classList.remove("inputed");
        }
      };

      // Для срабатыванию по простому клику
      function showVendorSearch() {
        const inputedvalue = vendorSearchInput.value;
        searchElemsContainer.innerHTML = "";
        vendorSearchInput.setAttribute("vendor_value", "");
        loader.classList.remove("hide");
        noneContent.classList.remove("show");
        if (vendorSearchInput.value == "") {
          vendorSearchInput.classList.add("inputed");
          vendorSearchElemsContainerWrapper.classList.add("show");
          vendorSearchElemsContainer.classList.add("show");
          
            count = 0;
            countLast = 5;
            finish = false;
            if (inputedvalue == vendorSearchInput.value) {
              getSearchElems();
            }
          
        } else {
          vendorSearchElemsContainerWrapper.classList.remove("show");
          vendorSearchElemsContainer.classList.remove("show");
          vendorSearchInput.classList.remove("inputed");
        }
      }
      vendorSearchInput.addEventListener("click", showVendorSearch);


      vendorSearchElemsContainer.addEventListener("scroll", function () {
        console.log(
          `${this.scrollHeight} >= ${this.scrollTop + this.clientHeight}`
        );
        if (this.scrollHeight >= this.scrollTop + this.clientHeight) {
          if (!finish) {
            if (
              !smallLoader.classList.contains("show") &&
              count != 0 &&
              countLast != 5
            ) {
              getSearchElems();
              smallLoader.classList.add("show");
            }
          }
        }
      });

      function renderCatalogItem(orderData) {
        const ajaxTemplateWrapper = document.querySelector(
          '[template-elem="wrapper"]'
        );
        const ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
          '[search-supplier-elem="search-supplier-item"]'
        ).innerText;

        return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
      }

      function addAjaxCatalogItem(ajaxElemData) {
        const renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
        searchElemContainer.insertAdjacentHTML(
          "beforeend",
          renderCatalogItemHtml
        );
      }

      function searchElemsLogic(elems) {
        elems.forEach((el) => {
          el.onclick = () => {
            vendorSearchInput.value = el.textContent;
            vendorSearchInput.setAttribute(
              "vendor_value",
              el.getAttribute("search-supplier-id")
            );
            vendorSearchElemsContainer.classList.remove("show");
            vendorSearchInput.classList.remove("inputed");
          };
        });
      }

      function getSearchElems() {
        const data = {
          search_text: vendorSearchInput.value,
          count: count,
          count_last: countLast,
        };

        fetch("/api/v1/product/search-vendor/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: JSON.stringify(data),
        })
          .then((response) => {
            if (response.status == 200) {
              return response.json();
            }
          })
          .then((response) => {
            loader.classList.add("hide");
            smallLoader.classList.remove("show");
            if (response.data.length > 0) {
              for (let i in response.data) {
                addAjaxCatalogItem(response.data[i]);
              }
              const searchElems = searchElemsContainer.querySelectorAll(
                ".search_supplier_elem"
              );
              searchElemsLogic(searchElems);
              count += 5;
              countLast += 5;
            } else {
              if (count == 0 && countLast == 5) {
                noneContent.classList.add("show");
              } else {
                finish = true;
                return;
              }
            }
          });
      }
    });
  }
});
