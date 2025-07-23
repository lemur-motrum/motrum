import {
  getCookie,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

import { setErrorModal } from "/static/core/js/error_modal.js";

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
    let maxValue;
    let minValue;
    let searchText = urlParams.get("search_text");
    let priceInputsArray = [0, 0];

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

    const priceFilterElemWrapper = document.querySelector(".price_filter_elem");
    const minInputPrice =
      priceFilterElemWrapper.querySelector(".small_price_input");
    const maxInputPrice =
      priceFilterElemWrapper.querySelector(".big_price_input");

    const offsetTop =
      document.querySelector(".bread_crumbs").getBoundingClientRect().top +
      window.scrollY;

    const charBlocksFalseDiaposon = document.querySelectorAll(
      ".char_block_false_diapason"
    );

    const filterContainer = document.querySelector(".filter_container");

    const noManagerContainer = document.querySelector(
      ".personal-manager-container"
    );

    const submitFiltersContainer = document.querySelector(
      ".submit_filter_container"
    );
    const submitButtonContainer =
      submitFiltersContainer.querySelector(".submit");

    const submitButtonContainerButtonLoader =
      submitFiltersContainer.querySelector(".small_loader");

    const filterButton = submitButtonContainer.querySelector(
      ".submit_button_name"
    );
    const cancelFilterButton =
      submitFiltersContainer.querySelector(".canceled");

    if (filterContainer) {
      noManagerContainer.classList.add("right");
    }

    const priceOneFilterContent = priceFilterElemWrapper.querySelector(
      ".price_checkbox_content"
    );
    const checkboxZone = priceOneFilterContent.querySelector(".checkbox");

    let charactiristics = [];

    const charsContent = document.querySelector(".chars_content");
    if (charsContent) {
      new Accordion(".chars_content", {
        elementClass: "char_values_long",
        triggerClass: "add_more_btn",
        panelClass: "char_values",
        showMultiple: true,
      });

      new Accordion(".chars_content", {
        elementClass: "accordion_head",
        triggerClass: "filter_arrow_title",
        panelClass: "char_values",
        showMultiple: false,
      });
    }

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

    function num_word(value, words) {
      value = Math.abs(value) % 100;
      var num = value % 10;
      if (value > 10 && value < 20) return words[2];
      if (num > 1 && num < 5) return words[1];
      if (num == 1) return words[0];
      return words[2];
    }

    function test_serch_chars() {
      let data = {
        count: productCount,
        sort: sort ? sort : "?",
        page: pageCount,
        category: category,
        group: !group ? "" : group,
        vendor: paramsArray.length > 0 ? paramsArray : "",
        pricefrom: priceFrom ? priceFrom : 0,
        priceto: priceTo ? priceTo : 0,
        pricenone: pricenone,
        search_text: searchText ? searchText : "",
        chars:
          charactiristics.length > 0 ? JSON.stringify(charactiristics) : [],
      };
      let csrfToken = getCookie("csrftoken");
      let params = new URLSearchParams(data);

      filterButton.classList.add("hide");
      submitButtonContainerButtonLoader.classList.add("show");
      submitButtonContainer.disabled = true;

      fetch(`/api/v1/product/search-filters-product/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => {
          if (response.status >= 200 && response.status < 300) {
            filterButton.classList.remove("hide");
            submitButtonContainerButtonLoader.classList.remove("show");
            return response.json();
          } else {
            setErrorModal();
          }
        })
        .then((response) => {
          if (response["count_product"] > 999) {
            submitButtonContainer.disabled = false;
            filterButton.textContent = "Найдено больше 1тыс. товаров";
          } else if (response["count_product"] == 0) {
            submitButtonContainer.disabled = true;
            filterButton.textContent = "Ничего не найдено";
          } else {
            submitButtonContainer.disabled = false;
            filterButton.textContent = `Найдено ${
              response["count_product"]
            } ${num_word(response["count_product"], [
              "товар",
              "товара",
              "товаров",
            ])}`;
          }
        });
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
        search_text: searchText ? searchText : "",
        chars:
          charactiristics.length > 0 ? JSON.stringify(charactiristics) : [],
      };

      let params = new URLSearchParams(data);

      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/product/load-ajax-product-list/?${params.toString()}`, {
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
          loader.style.display = "none";
          if (data.data.length == 0) {
            noneContentText.classList.add("show");
          } else {
            lastPage = +data.count;
            const paginationArray = [];
            paginationLastElem.textContent = `${lastPage}`;
            if (data.count > 1) {
              endContent.classList.add("show");
            }
            smallLoader.classList.remove("show");
            maxValue = !priceTo ? +data["price_max"] : maxValue;
            minValue = !priceFrom ? +data["price_min"] : minValue;
            priceInputsArray = [minValue, maxValue];

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
            test_serch_chars();
            addPlaceholderValue(maxInputPrice, true);
            addPlaceholderValue(minInputPrice);
          }
          history.pushState({}, "", currentUrl);
        })
        .catch((error) => console.error(error));
    }

    if (urlParams.get("vendor")) {
      const urlsParamArray = urlParams.get("vendor").split(",");
      urlsParamArray.forEach((el) => {
        paramsArray.push(el);
      });
    }

    inputValidate(minInputPrice, false, maxInputPrice);
    inputValidate(maxInputPrice, true, minInputPrice);

    window.onload = () => {
      const pageGetParam = urlParams.get("page");
      const priceGetParam = urlParams.get("price");

      const slugsElems = document.querySelectorAll("[data-chars-slug]");
      slugsElems.forEach((slugElem) => {
        if (slugElem.classList.contains("char_block_false_diapason")) {
          const slug = slugElem.getAttribute("data-chars-slug");
          const charsGetParam = urlParams.get(`${slug}`);
          if (charsGetParam) {
            const dataIdChars = slugElem.getAttribute("data-id-chars");
            const values = charsGetParam.split(",");
            const charValues = slugElem.querySelectorAll(".char_value");
            values.forEach((valueID) => {
              charValues.forEach((charValue) => {
                if (charValue.getAttribute("data-id-value-chars") == valueID) {
                  charValue.classList.add("checked");
                  charValue.parentNode.prepend(charValue);
                }
              });
            });

            charactiristics.push({
              id: dataIdChars,
              values: values,
              is_diapason: false,
              min_value: 0,
              max_value: 0,
            });
          }
        }
        if (slugElem.classList.contains("char_block_true_diapason")) {
          const slug = slugElem.getAttribute("data-chars-slug");

          const charsGetParam = urlParams.get(`${slug}`);
          if (charsGetParam) {
            const minInput = slugElem.querySelector(
              ".range_chars_value_small_input"
            );
            const maxInput = slugElem.querySelector(
              ".range_chars_value_big_input"
            );
            const dataIdChars = slugElem.getAttribute("data-id-chars");
            const values = charsGetParam.split(",");

            minInput.value = values[0];
            maxInput.value = values[1];

            charactiristics.push({
              id: dataIdChars,
              values: null,
              is_diapason: true,
              min_value: values[0],
              max_value: values[1],
            });
          }
        }

        if (slugElem.classList.contains("accordion_head")) {
          const countQuantityPush = slugElem.querySelector(".count_quantity");
          let countQuantity = 0;
          slugElem.setAttribute("data-quantity", countQuantity);
          const charValues = slugElem.querySelectorAll(".char_value");
          charValues.forEach((el) => {
            if (el.classList.contains("checked")) {
              countQuantity += 1;
            }
          });
          slugElem.setAttribute("data-quantity", countQuantity);

          countQuantityPush.textContent = countQuantity;
          if (countQuantity > 0) {
            countQuantityPush.classList.add("show");
          } else {
            countQuantityPush.classList.remove("show");
          }
        }
      });

      if (pageGetParam) {
        pageCount = +pageGetParam - 1;
        productCount = 10;
      }
      if (priceGetParam) {
        sort = priceGetParam == "up" ? "ASC" : "DESC";
        priceGetParam == "up"
          ? upPriceBtn.classList.add("active")
          : downPriceBtn.classList.add("active");
      }

      if (currentUrl.searchParams.get("priceDiapazon")) {
        const paramsString = currentUrl.searchParams.get("priceDiapazon");
        const paramsArray = paramsString.split("-");
        priceFrom = paramsArray[0];
        priceTo = paramsArray[1];

        document.querySelector(".small_price_input").value = priceFrom;
        document.querySelector(".big_price_input").value = priceTo;
      }

      if (currentUrl.searchParams.get("pricenone")) {
        pricenone = true;
        checkboxZone.classList.add("checked");
      }

      loadItems();
    };

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      preLoaderLogic();
      productCount = 10;
    };

    paginationElems.forEach((elem) => {
      if (!elem.classList.contains("active")) {
        elem.onclick = () => {
          pageCount = +elem.textContent - 1;
          productCount = 10;
          preLoaderLogic();
        };
      }
    });
    catalogButton.onclick = () => {
      productCount = 10;
      +pageCount++;
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems();
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      productCount = 10;
      preLoaderLogic();
    };

    const filters = document.querySelectorAll(".filter_elem");
    const supplierNameContainer = document.querySelector(
      ".suppliers_max_height_container"
    );

    function closeFilterElems() {
      const filterContent = document.querySelector(".filter_container");
      if (filterContent.classList.contains("show")) {
        const supplierContent =
          filterContent.querySelector(".supplier_content");
        const supplierBtn = filterContent.querySelector(
          ".suppliers_add_more_btn"
        );
        const burger_nav_menu = document.querySelector(".burger_menu_nav");
        filterContent.classList.remove("show");
        supplierContent.classList.remove("is_open");
        if (supplierBtn) {
          supplierBtn.style.display = "flex";
        }
        document.body.style.overflow = "auto";
        burger_nav_menu.style.zIndex = 1001;
      }
    }

    charBlocksFalseDiaposon.forEach((charBlock) => {
      const slug = charBlock.getAttribute("data-chars-slug");
      const charValues = charBlock.querySelectorAll(".char_value");
      const dataIdChars = charBlock.getAttribute("data-id-chars");
      const charValuesContainer = charBlock.querySelector(".char_values");
      const countQuantityPush = charBlock.querySelector(".count_quantity");

      charValues.forEach((charValue) => {
        let originalPosition = +charValue.getAttribute("data-position");
        charValue.onclick = () => {
          let countQuantity = +charBlock.getAttribute("data-quantity");
          const dataIdValueChars = charValue.getAttribute(
            "data-id-value-chars"
          );
          charValue.classList.toggle("checked");
          let validate = false;
          if (charValue.classList.contains("checked")) {
            countQuantity += 1;
            console.log(countQuantity);
            charValue.parentNode.prepend(charValue);
            if (charactiristics.length > 0) {
              for (let i = 0; i < charactiristics.length; i++) {
                if (charactiristics[i]["id"] == dataIdChars) {
                  charactiristics[i]["values"].push(dataIdValueChars);
                  validate = true;
                  currentUrl.searchParams.set(
                    `${slug}`,
                    charactiristics
                      .filter((el) => el["id"] == dataIdChars)[0]
                      ["values"].join(",")
                  );
                  break;
                }
              }
              if (!validate) {
                charactiristics.push({
                  id: dataIdChars,
                  values: [dataIdValueChars],
                  is_diapason: false,
                  min_value: 0,
                  max_value: 0,
                });
                validate = false;
                currentUrl.searchParams.set(
                  `${slug}`,
                  charactiristics
                    .filter((el) => el["id"] == dataIdChars)[0]
                    ["values"].join(",")
                );
              }
            } else {
              charactiristics.push({
                id: dataIdChars,
                values: [dataIdValueChars],
                is_diapason: false,
                min_value: 0,
                max_value: 0,
              });

              currentUrl.searchParams.set(
                `${slug}`,
                charactiristics
                  .filter((el) => el["id"] == dataIdChars)[0]
                  ["values"].join()
              );
            }
          } else {
            countQuantity -= 1;
            const siblings = charValuesContainer.children;
            charValuesContainer.insertBefore(
              charValue,
              siblings[originalPosition + 1]
            );

            if (charactiristics.length > 0) {
              for (let i = 0; i < charactiristics.length; i++) {
                if (charactiristics[i]["id"] == dataIdChars) {
                  if (charactiristics[i]["values"].length > 1) {
                    charactiristics[i]["values"] = charactiristics[i][
                      "values"
                    ].filter((el) => el !== dataIdValueChars);
                    currentUrl.searchParams.set(
                      `${slug}`,
                      charactiristics
                        .filter((el) => el["id"] == dataIdChars)[0]
                        ["values"].join(",")
                    );
                    break;
                  } else {
                    charactiristics = charactiristics.filter(
                      (el) => el["id"] !== dataIdChars
                    );
                    currentUrl.searchParams.delete(`${slug}`);
                    filterButton.textContent = "применить фильтры";
                    break;
                  }
                }
              }
            }
          }
          if (charBlock.classList.contains("accordion_head")) {
            charBlock.setAttribute("data-quantity", countQuantity);
            countQuantityPush.textContent = countQuantity;
            if (countQuantity > 0) {
              countQuantityPush.classList.add("show");
            } else {
              countQuantityPush.classList.remove("show");
            }
          }
          history.pushState({}, "", currentUrl);
          test_serch_chars();
        };
      });
    });

    const charBlocksTrueDiaposon = document.querySelectorAll(
      ".char_block_true_diapason"
    );

    charBlocksTrueDiaposon.forEach((charBlock) => {
      const charValueContainer = charBlock.querySelector(".range_chars_value");
      const slug = charBlock.getAttribute("data-chars-slug");
      const charBlockDataId = charBlock.getAttribute("data-id-chars");

      const minValueInput = charValueContainer.querySelector(
        ".range_chars_value_small_input"
      );
      const maxValueInput = charValueContainer.querySelector(
        ".range_chars_value_big_input"
      );

      const minValue = getCurrentPrice(
        charValueContainer.getAttribute("data-min-value")
      );

      const maxValue = getCurrentPrice(
        charValueContainer.getAttribute("data-max-value")
      );

      setupInputHandler(minValueInput, 0, maxValue);
      setupInputHandler(maxValueInput, 0, maxValue);

      function setupInputHandler(input, min, max) {
        input.addEventListener("input", (e) => {
          let value = e.target.value;

          function formatInput(value) {
            let newValue = value;
            newValue = newValue.replace(/,/g, ".");
            newValue = newValue.replace(/[^\d.]/g, "");
            newValue = newValue.replace(/\.+/g, ".");
            if (newValue.startsWith(".")) {
              newValue = newValue.substring(1);
            }
            newValue = newValue.replace(/\.(?=.*\.)/g, "");
            if (newValue.includes(".")) {
              const [integerPart, decimalPart] = newValue.split(".");
              newValue = integerPart + "." + decimalPart.slice(0, 2);
            }

            if (+newValue < min) {
              return min;
            } else if (+newValue > max) {
              return max;
            } else {
              return newValue;
            }
          }
          value = formatInput(value);
          input.value = value;

          let validate = false;

          const minMaxArrray = [];

          if (minValueInput.value || minValueInput.value) {
            if (charactiristics.length > 0) {
              for (let i = 0; i < charactiristics.length; i++) {
                if (charactiristics[i]["id"] == charBlockDataId) {
                  charactiristics[i]["min_value"] = minValueInput.value
                    ? minValueInput.value
                    : minValue;
                  charactiristics[i]["max_value"] = maxValueInput.value
                    ? maxValueInput.value
                    : maxValue;
                  validate = true;

                  minMaxArrray.push(charactiristics[i]["min_value"]);
                  minMaxArrray.push(charactiristics[i]["max_value"]);

                  currentUrl.searchParams.set(
                    `${slug}`,
                    minMaxArrray.join(",")
                  );

                  break;
                }
              }
              if (!validate) {
                charactiristics.push({
                  id: charBlockDataId,
                  values: null,
                  is_diapason: true,
                  min_value: minValueInput.value
                    ? minValueInput.value
                    : minValue,
                  max_value: maxValueInput.value
                    ? maxValueInput.value
                    : maxValue,
                });

                const char = charactiristics.filter(
                  (el) => el["id"] == charBlockDataId
                )[0];

                minMaxArrray.push(char["min_value"]);
                minMaxArrray.push(char["max_value"]);
                currentUrl.searchParams.set(`${slug}`, minMaxArrray.join(","));
              }
            } else {
              charactiristics.push({
                id: charBlockDataId,
                values: null,
                is_diapason: true,
                min_value: minValueInput.value ? minValueInput.value : minValue,
                max_value: maxValueInput.value ? maxValueInput.value : maxValue,
              });

              const char = charactiristics.filter(
                (el) => el["id"] == charBlockDataId
              )[0];

              minMaxArrray.push(char["min_value"]);
              minMaxArrray.push(char["max_value"]);
              currentUrl.searchParams.set(`${slug}`, minMaxArrray.join(","));
            }
          } else {
            charactiristics = charactiristics.filter(
              (el) => el["id"] !== charBlockDataId
            );
            currentUrl.searchParams.delete(`${slug}`);
          }
          history.pushState({}, "", currentUrl);
          test_serch_chars();
        });
      }
    });

    filters.forEach((filterElem) => {
      const filterValues = filterElem.querySelectorAll(".suplier_elem_content");
      filterValues.forEach((filterValue) => {
        let dataPosition = +filterValue.getAttribute("data-position");
        const vendorParam = filterValue.getAttribute("param");
        if (paramsArray.length > 0) {
          paramsArray.forEach((param) => {
            if (vendorParam == param) {
              filterValue.classList.add("show");
              supplierNameContainer.prepend(filterValue);
            }
          });
        }
        filterValue.onclick = () => {
          paramsArray.push(vendorParam);
          filterValue.classList.toggle("show");
          closeFilterElems();

          if (filterValue.classList.contains("show")) {
            supplierNameContainer.prepend(filterValue);
            const vendorsString = currentUrl.searchParams.get("vendor");
            if (vendorsString) {
              currentUrl.searchParams.set("vendor", paramsArray.join());
            } else {
              currentUrl.searchParams.set("vendor", paramsArray.join(","));
            }
            pageCount = 0;
          } else {
            const siblings = document.querySelector(
              ".suppliers_max_height_container"
            ).children;
            document
              .querySelector(".suppliers_max_height_container")
              .insertBefore(filterValue, siblings[dataPosition + 1]);

            const activeSupplierElems =
              supplierNameContainer.querySelectorAll(".show");
            if (activeSupplierElems[activeSupplierElems.length - 1]) {
              activeSupplierElems[activeSupplierElems.length - 1].after(
                filterValue
              );
            }
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
          }
          test_serch_chars();
          history.pushState({}, "", currentUrl);
        };
      });
    });

    priceOneFilterContent.onclick = () => {
      checkboxZone.classList.toggle("checked");
      if (checkboxZone.classList.contains("checked")) {
        pricenone = true;
        currentUrl.searchParams.set("pricenone", true);
        test_serch_chars();
      } else {
        pricenone = false;
        currentUrl.searchParams.delete("pricenone");
        test_serch_chars();
      }

      history.pushState({}, "", currentUrl);
    };

    submitButtonContainer.onclick = () => {
      priceFrom = minInputPrice.value ? +minInputPrice.value : "";
      priceTo = maxInputPrice.value ? +maxInputPrice.value : "";
      pageCount = 0;
      closeFilterElems();
      scrollToTop(offsetTop);
      preLoaderLogic();
    };

    cancelFilterButton.onclick = () => {
      const filterValues = document.querySelectorAll(".suplier_elem_content");
      filterValues.forEach((el) => {
        el.classList.remove("show");
      });
      priceFrom = "";
      priceTo = "";
      charactiristics = [];
      document.querySelectorAll(".char_value").forEach((el) => {
        if (el.classList.contains("checked")) {
          el.classList.remove("checked");
        }
      });

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
      urlParams.delete("priceDiapazon");
      checkboxZone.classList.remove("checked");
      const slugsElems = document.querySelectorAll("[data-chars-slug]");
      slugsElems.forEach((slugElem) => {
        const slug = slugElem.getAttribute("data-chars-slug");
        urlParams.delete(`${slug}`);
        if (slugElem.classList.contains("accordion_head")) {
          slugElem.setAttribute("data-quantity", 0);
          slugElem.querySelector(".count_quantity").classList.remove("show");
        }
      });
      closeFilterElems();
      scrollToTop(offsetTop);
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

    function scrollToTop(arhor) {
      window.scrollTo({
        top: arhor,
        behavior: "smooth",
      });
    }

    function inputValidate(input, max = false, anotherInput) {
      const intervalMaxValue = setInterval(() => {
        if (maxValue && minValue) {
          clearInterval(intervalMaxValue);
          addPlaceholderValue(input, max);
        }
      }, 5);
      let validate = true;

      input.addEventListener("input", function (e) {
        validate = true;
        console.log(minValue, maxValue);
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });

        input.value = currentValue;

        if (input.value == ".") {
          validate = false;
          e.target.value = "";
        }
        if (input.value == "0") {
          validate = false;
          e.target.value = "";
        }

        if (maxValue) {
          if (+input.value >= +maxValue) {
            e.target.value = maxValue;
          }
        }

        const inputValue = input.value;

        if (max) {
          priceTo = e.target.value;
          if (e.target.value == "") {
            priceTo = 0;
          }

          if (anotherInput.value == "") {
            priceFrom = 0;
          }
          priceInputsArray[0] = priceFrom;
          priceInputsArray[1] = priceTo;
          currentUrl.searchParams.set(
            "priceDiapazon",
            priceInputsArray.join("-")
          );
        } else {
          priceFrom = e.target.value;
          if (input.value == "") {
            priceFrom = 0;
          }

          if (anotherInput.value == "") {
            priceTo = 0;
          }

          priceInputsArray[0] = priceFrom;
          priceInputsArray[1] = priceTo;

          currentUrl.searchParams.set(
            "priceDiapazon",
            priceInputsArray.join("-")
          );
        }
        if (priceInputsArray[0] == "" && priceInputsArray[1] == "") {
          currentUrl.searchParams.delete("priceDiapazon");
          priceFrom = 0;
          priceTo = 0;
        }

        setTimeout(() => {
          if (e.target.value == inputValue) {
            if (validate) {
              console.log("Запрос");
              test_serch_chars();
              validate = false;
            }
          } else {
            validate = true;
          }
        }, 600);
        history.pushState({}, "", currentUrl);
      });
    }

    function addPlaceholderValue(input, max = false) {
      if (max) {
        input.placeholder = `до ${maxValue}`;
      } else {
        input.placeholder = `от ${minValue}`;
      }
    }
  }
});
