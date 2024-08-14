import "/static/core/js/slider.js";

//Класс для разделения чила на разряды
class NumberParser {
  constructor(locale) {
    const parts = new Intl.NumberFormat(locale).formatToParts(12345.6);
    const numerals = [
      ...new Intl.NumberFormat(locale, { useGrouping: false }).format(
        9876543210
      ),
    ].reverse();
    const index = new Map(numerals.map((d, i) => [d, i]));
    this._group = new RegExp(
      `[${parts.find((d) => d.type === "group").value}]`,
      "g"
    );
    this._decimal = new RegExp(
      `[${parts.find((d) => d.type === "decimal").value}]`
    );
    this._numeral = new RegExp(`[${numerals.join("")}]`, "g");
    this._index = (d) => index.get(d);
  }
  parse(string) {
    return (string = string
      .trim()
      .replace(this._group, "")
      .replace(this._decimal, ".")
      .replace(this._numeral, this._index))
      ? +string
      : NaN;
  }
}

// const setURLParams = (url, updates, defaults) => {
//   let searchParams = new URL(url).searchParams;

//   // Устанавливаем значения по умолчанию
//   for (let [key, value] of Object.entries(defaults || {})) {
//     if (!searchParams.has(key)) {
//       searchParams.set(key, value);
//     }
//   }

//   // Обновляем остальные параметры
//   for (let [key, value] of Object.entries(updates)) {
//     searchParams.set(key, value);
//   }

//   // Обновляем URL в адресной строке без перезагрузки страницы
//   window.history.replaceState(null, "", "?" + searchParams);
// };

//функция получения куки
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

//функция создания куки
function setCookie(name, value, options = {}) {
  options = {
    ...options,
  };

  if (options.expires instanceof Date) {
    options.expires = options.expires.toUTCString();
  }

  let updatedCookie = name + "=" + value;

  for (let optionKey in options) {
    updatedCookie += "; " + optionKey;
    let optionValue = options[optionKey];
    if (optionValue !== true) {
      updatedCookie += "=" + optionValue;
    }
  }
  document.cookie = updatedCookie;
}

// функция удаления куки
function deleteCookie(name, path, domain) {
  if (getCookie(name)) {
    document.cookie = `${name}=; Path=${path}; Max-Age=-1;`;
    // document.cookie =
    // name + "=; Path=" + path + "; Domain=" + domain + "; Max-Age=-1;";
  }
}
// функция для форматирования цены, если с бэка значения возвращается с запятой по типу 0,000
function getCurrentPrice(p) {
  const price = p.replace(",", ".");
  return price;
}
let productsSpecificationList = [];

let localStorageSpecification = JSON.parse(
  localStorage.getItem("specificationValues")
);

// функция сохранения продукта в localstorage
const saveProduct = (product) => {
  if (localStorageSpecification) {
    localStorageSpecification = localStorageSpecification.filter(
      (item) => item.id !== product.id
    );
    localStorageSpecification.push(product);
    localStorage.setItem(
      "specificationValues",
      JSON.stringify(localStorageSpecification)
    );
    document.cookie = `key=${JSON.stringify(
      localStorageSpecification
    )}; path=/`;
  } else {
    localStorage.setItem(
      "specificationValues",
      JSON.stringify(productsSpecificationList)
    );
    document.cookie = `key=${JSON.stringify(productsSpecificationList)};path=/`;
  }
};

// Проверка есть ли продукт в корзине, если есть, то продукт перезаписывается, если нет, то добавляется новый продукт в корзину
const setProduct = (product) => {
  if (productsSpecificationList.length <= 0) {
    productsSpecificationList.push(product);
  } else {
    productsSpecificationList = productsSpecificationList.filter(
      (item) => item.id !== product.id
    );
    productsSpecificationList.push(product);
  }
  saveProduct(product);
};

// форматирования числового значения с разрядом, для отображения
const getDigitsNumber = (container, value) => {
  container.textContent = new Intl.NumberFormat("ru").format(+value);
};

// получение токена из куки
const csrfToken = getCookie("csrftoken");

// получение полной информации о товаре при наведении мыши
function showInformation(elem) {
  elem.onmouseover = () => {
    elem.classList.add("show");
  };
  elem.onmouseout = () => {
    elem.classList.remove("show");
  };
}

// добавление продукта в корзину
function addProductInSpecification(
  btn,
  id,
  name,
  price,
  motrumId,
  salerId,
  quantity,
  discount,
  valueContainer,
  multiplicity
) {
  if (btn.disabled == false) {
    btn.style.cursor = "pointer";
  } else {
    btn.style.cursor = "default";
  }
  if (btn.disabled == false) {
    const product = {
      id: +id,
      name: name,
      price: getCurrentPrice(price),
      idMotrum: motrumId,
      idSaler: salerId,
      quantity: quantity,
      totalCost: (getCurrentPrice(price) * quantity).toFixed(2),
      discount: discount,
      productSpecificationId: null,
      multiplicity: multiplicity,
    };
    btn.onclick = () => {
      setProduct(product);
      if (localStorageSpecification) {
        valueContainer.textContent = localStorageSpecification.length;
      } else {
        valueContainer.textContent = productsSpecificationList.length;
      }
    };
  }
}
// Изменить значение товаров на фронте
function showQuantityCart(value) {
  if (localStorageSpecification) {
    value.textContent = localStorageSpecification.length;
  } else {
    value.textContent = 0;
  }
}
//рендеринг цен
function setCurrentPriceCataloItem(elems) {
  elems.forEach((el) => {
    const priceContainer = el.querySelector(".price");
    const price = priceContainer.querySelector(".price-count");
    const supplerPriceContainer = el.querySelector(".suppler-price");
    const supplerPrice = supplerPriceContainer.querySelector(
      ".price-suppler-count"
    );

    if (price) {
      const priceValue = new NumberParser("ru").parse(price.textContent);
      getDigitsNumber(price, priceValue);
    }
    if (supplerPrice) {
      const priceValue = new NumberParser("ru").parse(supplerPrice.textContent);
      getDigitsNumber(supplerPrice, priceValue);
    }
  });
}
//логика страницы каталога
function catalogLogic(elems, val) {
  elems.forEach((catalogItem) => {
    showInformation(catalogItem);
    showQuantityCart(val);

    const productId = catalogItem.getAttribute("data-id");
    const productName = catalogItem.querySelector(".name").textContent;
    const productPrice = catalogItem.getAttribute("data-price");
    const productMotrumId = catalogItem.getAttribute("data-motrum-id");
    const productSalerId = catalogItem.getAttribute("data-saler-id");
    const buttonContainer = catalogItem.querySelector(".quantity-buttons");
    const productDiscount = getCurrentPrice(
      catalogItem.getAttribute("data-discoutnt")
    );
    const plusButton = buttonContainer.querySelector(".plus-button");
    const minusButton = buttonContainer.querySelector(".minus-button");
    const addSpecificationButton = catalogItem.querySelector(
      ".add-specification-button"
    );
    const countQuantityZone = buttonContainer.querySelector("input");
    const productMultiplicityQuantity = catalogItem.getAttribute(
      "data-order-multiplicity"
    );

    let countQuantity = +countQuantityZone.value;

    countQuantityZone.addEventListener("keyup", function () {
      if (productMultiplicityQuantity) {
        let val = parseInt(this.value) || 0;
        while (val % +productMultiplicityQuantity) {
          val++;
          if (val % +productMultiplicityQuantity == 0) {
            break;
          }
        }
        this.value = val;
        countQuantity = val;
      } else {
        countQuantity = +countQuantityZone.value;
      }
      if (countQuantity > 0) {
        addSpecificationButton.disabled = false;
        addProductInSpecification(
          addSpecificationButton,
          productId,
          productName,
          productPrice,
          productMotrumId,
          productSalerId,
          countQuantity,
          productDiscount,
          val,
          productMultiplicityQuantity
        );
      }
    });

    plusButton.onclick = () => {
      if (productMultiplicityQuantity) {
        countQuantity += +productMultiplicityQuantity;
      } else {
        countQuantity++;
      }
      countQuantityZone.value = countQuantity;
      minusButton.disabled = false;
      addSpecificationButton.disabled = false;

      if (countQuantity >= 999) {
        minusButton.disabled = false;
        plusButton.disabled = true;
      }
      addProductInSpecification(
        addSpecificationButton,
        productId,
        productName,
        productPrice,
        productMotrumId,
        productSalerId,
        countQuantity,
        productDiscount,
        val,
        productMultiplicityQuantity
      );
    };

    minusButton.onclick = () => {
      if (productMultiplicityQuantity) {
        countQuantity -= +productMultiplicityQuantity;
      } else {
        countQuantity--;
      }
      countQuantityZone.value = countQuantity;
      if (countQuantityZone.value <= 0) {
        countQuantityZone.value = 0;
      }

      if (countQuantity >= 999) {
        minusButton.disabled = false;
        plusButton.disabled = true;
      } else {
        plusButton.disabled = false;
      }

      if (countQuantity <= 0) {
        minusButton.disabled = true;
        addSpecificationButton.disabled = true;
      } else {
        minusButton.disabled = false;
        addSpecificationButton.disabled = false;
      }
      addProductInSpecification(
        addSpecificationButton,
        productId,
        productName,
        productPrice,
        productMotrumId,
        productSalerId,
        countQuantity,
        productDiscount,
        val,
        productMultiplicityQuantity
      );
    };
  });
}
//логика пояаления кнопок "Актуализировать" и "Редактирорвать" на странице всех спецификаций
function showButton(container, button) {
  container.onmouseover = () => {
    button.classList.add("show");
  };
  container.onmouseout = () => {
    button.classList.remove("show");
  };
}
function backendDataFormat(string) {
  const dateArray = string.split("-");
  const year = dateArray[0];
  const mounth = dateArray[1];
  const day = dateArray[2];
  const result = `${day}.${mounth}.${year}`;
  return result;
}

window.addEventListener("DOMContentLoaded", () => {
  const catalogContainer = document.querySelector(".catalog_container");
  if (catalogContainer) {
    const specificationLinkContainer = document.querySelector(
      ".specification-link-container"
    );
    const specificationLinkContainerProductValue =
      specificationLinkContainer.querySelector("span");
    showQuantityCart(specificationLinkContainerProductValue);
    const catalog = catalogContainer.querySelector(
      ".spetification-product-catalog"
    );
    if (catalog) {
      const catalogItems = catalog.querySelectorAll(".catalog-item");
      catalogLogic(catalogItems, specificationLinkContainerProductValue);

      const endContent = catalog.querySelector(".products-end-content");
      //Пагинация и аякс загрузка
      if (endContent) {
        const loadMoreBtn = endContent.querySelector(".load-more-btn");
        const searhForm = document.querySelector(".search-form-container");
        const category = searhForm.getAttribute("category");
        const group = searhForm.getAttribute("group");
        const allProducts = catalog.querySelector(".all-products");
        const loader = catalog.querySelector(".loader");
        const params = new URLSearchParams(window.location.search);
        let pageNum = params.get("page");
        if (pageNum == 1 || !pageNum) {
          pageNum = "";
        }
        const endpoint = "/admin_specification/load_products/";

        const objData = {
          group: group,
          category: category,

          pageNum: pageNum,
        };
        let data = JSON.stringify(objData);

        loadMoreBtn.onclick = () => {
          loader.classList.add("show");
          fetch(endpoint, {
            method: "Post",
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((response) => {
              if (response.status == "ok") {
                loader.classList.remove("show");
                if (!pageNum) {
                  pageNum = 2;
                } else {
                  pageNum = +pageNum + 1;
                }
                objData.pageNum = pageNum;
                data = JSON.stringify(objData);
                const products = JSON.parse(response.products);
                products.forEach((product) => {
                  allProducts.innerHTML += `<div class="catalog-item" data-id=${
                    product.pk
                  }  data-price=${
                    !product.price ? 0 : product.price
                  }  data-motrum-id=${product.article} data-saler-id=${
                    product.saler_article
                  } data-discoutnt=${
                    product.discount
                  } data-order-multiplicity=${product.multiplicity}> 
                        <div class="hidden-description">
                            <div class="descripton">
                                <div class="name">${
                                  product.supplier != product.vendor &&
                                  product.vendor != null
                                    ? product.supplier +
                                      " " +
                                      product.vendor +
                                      " " +
                                      product.name
                                    : product.supplier + " " + product.name
                                }</div>
                                <div class="article-motrum">${
                                  product.article
                                }</div>
                                <div class="charactiristics">
                                    ${
                                      product.chars.length == 0
                                        ? "-"
                                        : product.chars.join(" ")
                                    }
                                </div>
                                <div class="stock">
                                ${
                                  product.stock
                                    ? `<div class="stock_item">
                                    ${
                                      product.stock_to_order
                                        ? " Поставщик:<br>Под заказ"
                                        : `${
                                            product.stock_supplier
                                              ? `Поставщик: ${product.stock_supplier}`
                                              : "Поставщик: -"
                                          }`
                                    }
                                        </div>
                                        <div class="stock_item">Motrum:${
                                          product.stock_motrum
                                        }</div>
                                        <span class="span-transit">${backendDataFormat(
                                          product.data_update
                                        )}</span>
                                        <br>
                                        <span class="span-transit">
                                        ${
                                          product.transit_count
                                            ? `Ближайшая поставка: ${backendDataFormat(
                                                product.data_transit
                                              )} - ${product.transit_count} шт.`
                                            : ""
                                        }
                                        </span>`
                                    : `${
                                        product.stok_to_order ? "Под заказ" : ""
                                      } Неизвестно`
                                }
                                </div>
                                <div class="lot">
                                ${
                                  product.stock
                                    ? `${
                                        product.multiplicity != 1 &&
                                        !product.is_one_sale
                                          ? `<span class="span-min">Минимальный заказ ${
                                              product.multiplicity +
                                              " " +
                                              product.lot
                                            }
                                           </span>`
                                          : ""
                                      }${
                                        product.lot_complect != 1
                                          ? `${
                                              product.lot +
                                              "." +
                                              product.lot_complect +
                                              "ед."
                                            }`
                                          : `${
                                              product.lot_complect +
                                              " " +
                                              product.lot +
                                              "."
                                            }`
                                      }
                                        `
                                    : "-"
                                }
                                </div>
                                 <div class="suppler-price">
                                 ${
                                   product.price_suppler &&
                                   product.price_suppler != 0
                                     ? `<span class="price-suppler-count">${product.price_suppler}</span> ₽`
                                     : "<span>По запросу</span>"
                                 }
                                </div>
                                <div class="price">
                                ${
                                  product.price && product.price != 0
                                    ? `<span class="span-update">${backendDataFormat(
                                        product.data_update
                                      )}</span>
                                        <span class="price-count">${
                                          product.price
                                        }</span> ₽`
                                    : `<span>По запросу</span>`
                                }
                                </div>
                            </div>
                            <div class="item-buttons_container">
                                <div class="quantity-buttons">
                                    <button disabled class="minus-button">-</button>
                                    <input type="number"
                                           value="0"
                                           oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);"
                                           maxlength="3"
                                           onkeypress='validate(event)'>
                                    <button class="plus-button">+</button>
                                </div>
                                <button disabled class="add-specification-button">В корзину</button>
                            </div>
                        </div>
                    </div>`;
                });
                const catalogItems =
                  allProducts.querySelectorAll(".catalog-item");
                catalogLogic(
                  catalogItems,
                  specificationLinkContainerProductValue
                );
                setCurrentPriceCataloItem(catalogItems);
              }
            });
          // .catch((error) => console.error(error));
        };
      }
      //
      setCurrentPriceCataloItem(catalogItems);
    }
    // //Фильтры
    // const filtersContainer = specificationContent.querySelector(".filters");
    // const filters = filtersContainer.querySelectorAll(".filter-elem");
    // filters.forEach((filter) => {
    //   const tilte = filter.querySelector(".title-container");
    //   const arrow = tilte.querySelector("span");
    //   const content = filter.querySelector(".filter-content");

    //   tilte.onclick = () => {
    //     content.classList.toggle("show");
    //     arrow.classList.toggle("rotate");

    //     const checkboxes = content.querySelectorAll(".suppler-chekbox");
    //     checkboxes.forEach((checkboxElem) => {
    //       const checkBoxTitle = checkboxElem.querySelector("span").textContent;
    //       const square = filter.querySelectorAll(".chekbox");

    //       checkboxElem.addEventListener("click", function () {
    //         const currentSquare = this.querySelector(".chekbox");
    //         if (currentSquare.classList.contains("checked")) {
    //           currentSquare.classList.remove("checked");
    //         } else {
    //           square.forEach((el) => el.classList.remove("checked"));
    //           currentSquare.classList.toggle("checked");
    //         }
    //         const squareChecked = checkboxElem.querySelector(".checked");
    //         if (squareChecked) {
    //           setURLParams(location.href, { suppler: checkBoxTitle });
    //         } else {
    //           setURLParams(location.href, { suppler: "" });
    //         }
    //       });
    //     });
    //   };
    // });
    // //
  }

  const specificationContainer = document.querySelector(
    ".specification-container"
  );

  if (specificationContainer) {
    const spetificationTable = specificationContainer.querySelector(
      ".spetification_table"
    );
    if (spetificationTable) {
      const productItems =
        spetificationTable.querySelectorAll(".item_container");
      const totalPriceValueContainer =
        spetificationTable.querySelector(".price_description");
      const valueContainer = totalPriceValueContainer.querySelector(".price");
      const saveButton = spetificationTable.querySelector(".save_button");
      const exitButton = spetificationTable.querySelector(".exit_button");

      function getResult() {
        let sum = 0;
        const allElems = spetificationTable.querySelectorAll(".total_cost");
        for (let i = 0; i < allElems.length; i++) {
          sum += new NumberParser("ru").parse(allElems[i].textContent);
        }
        getDigitsNumber(valueContainer, +sum);
      }

      function saveSpecification(elems) {
        console.log(elems);
        const products = [];
        const checkbox = document.querySelector("#prepayment-checkbox");
        const specificationId = getCookie("specificationId");
        const adminCreator = document.querySelector("[data-user-id]");
        const adminCreatorId = adminCreator.getAttribute("data-user-id");
        let validate = true;

        elems.forEach((item, i) => {
          const itemQuantity = item.querySelector(".input-quantity").value;
          const itemID = item.getAttribute("data-id");
          const itemPriceStatus = item.getAttribute("data-price-exclusive");
          const itemPrice = item.querySelector(".price_once");
          const extraDiscount = item.querySelector(".discount-input");
          const productSpecificationId = item.getAttribute(
            "data-product-specification-id"
          );
          console.log(itemID);
          console.log(itemPrice);

          const inputPrice = item.querySelector(".price-input");

          const product = {
            product_id: +itemID,
            quantity: +itemQuantity,
            price_exclusive: +itemPriceStatus,
            price_one: !itemPrice
              ? +inputPrice.value
              : new NumberParser("ru").parse(
                  JSON.parse(getCookie("key"))[i].price
                ),
            product_specif_id: productSpecificationId
              ? productSpecificationId
              : null,
            extra_discount: extraDiscount.value,
          };
          if (product.price_one == 0) {
            validate = false;
            inputPrice.style.border = "1px solid red";
            inputPrice.style.borderRadius = "10px";
          } else {
            products.push(product);
          }
        });
        console.log(products);
        if (validate == true) {
          const endpoint =
            "/admin_specification/save_specification_view_admin/";
          const dataObj = {
            id_bitrix: 22,
            admin_creator_id: adminCreatorId,
            products: products,
            is_pre_sale: checkbox.checked ? true : false,
            id_specification: specificationId ? specificationId : null,
          };

          const data = JSON.stringify(dataObj);
          fetch(endpoint, {
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
                localStorage.removeItem("specificationValues");
                deleteCookie("key", "/", window.location.hostname);
                deleteCookie("specificationId", "/", window.location.hostname);
                window.location.href =
                  "/admin_specification/all_specifications/";
              }
            })
            .catch((error) => console.error(error));
        }
      }
      function exitSpecification(elems) {
        localStorage.removeItem("specificationValues");
        console.log(window.location.hostname);
        deleteCookie("key", "/", window.location.hostname);
        deleteCookie("specificationId", "/", window.location.hostname);
        window.location.href = "/admin_specification/all_specifications/";
      }

      productItems.forEach((item, i) => {
        const deleteItemBtn = item.querySelector(".item_conainer-delete_btn");
        const itemPrices = item.querySelectorAll(".price");
        const inputPrice = item.querySelector(".price-input");
        const discountInput = item.querySelector(".discount-input");
        const productPrice = item.getAttribute("data-price");
        const productPriceContainer = item.querySelector(".price_once");
        const productTotalPrice = item.querySelector(".total_cost");
        const itemPriceOnce = item.querySelector(".price_once");
        const plusButton = item.querySelector(".plus-button");
        const minusButton = item.querySelector(".minus-button");
        const quantity = item.querySelector(".input-quantity");
        let countQuantity = +quantity.value;

        const multiplicity = item.getAttribute("data-multiplicity");

        quantity.addEventListener("keyup", function () {
          if (multiplicity) {
            let val = parseInt(this.value) || 0;
            while (val % +multiplicity) {
              val++;
              if (val % +multiplicity == 0) {
                break;
              }
            }
            this.value = val;
            countQuantity = val;
          } else {
            countQuantity = +quantity.value;
          }
          const currentPrice =
            new NumberParser("ru").parse(itemPriceOnce.textContent) *
            +quantity.value;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
        });

        plusButton.onclick = () => {
          if (multiplicity) {
            countQuantity += +multiplicity;
          } else {
            countQuantity++;
          }

          quantity.value = countQuantity;
          const currentPrice =
            new NumberParser("ru").parse(itemPriceOnce.textContent) *
            +quantity.value;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
          if (countQuantity >= 999) {
            minusButton.disabled = false;
            plusButton.disabled = true;
          }
          if (countQuantity > 0) {
            minusButton.disabled = false;
          } else {
            minusButton.disabled = true;
          }
        };

        minusButton.onclick = () => {
          if (multiplicity) {
            countQuantity -= +multiplicity;
          } else {
            countQuantity--;
          }

          quantity.value = countQuantity;
          if (quantity.value <= 0) {
            quantity.value = 0;
          }
          const currentPrice =
            new NumberParser("ru").parse(itemPriceOnce.textContent) *
            +quantity.value;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
          if (countQuantity >= 999) {
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else {
            plusButton.disabled = false;
          }
          if (countQuantity <= 0) {
            minusButton.disabled = true;
          } else {
            minusButton.disabled = false;
          }
        };

        if (inputPrice) {
          const totalPrice = item.querySelector(".input_totla-cost");
          const quantity = item.querySelector(".input-quantity");

          quantity.onkeyup = () => {
            countQuantity = quantity.value;
            const currentPrice =
              new NumberParser("ru").parse(inputPrice.value) * +quantity.value;

            getDigitsNumber(productTotalPrice, currentPrice);
            getResult();
          };

          plusButton.onclick = () => {
            countQuantity++;
            quantity.value = countQuantity;
            const currentPrice =
              new NumberParser("ru").parse(inputPrice.value) * +quantity.value;
            getDigitsNumber(productTotalPrice, currentPrice);
            getResult();
            if (countQuantity >= 999) {
              minusButton.disabled = false;
              plusButton.disabled = true;
            }
          };

          minusButton.onclick = () => {
            countQuantity--;
            quantity.value = countQuantity;
            const currentPrice =
              new NumberParser("ru").parse(inputPrice.value) * +quantity.value;
            getDigitsNumber(productTotalPrice, currentPrice);
            getResult();
            if (countQuantity >= 999) {
              minusButton.disabled = false;
              plusButton.disabled = true;
            } else {
              plusButton.disabled = false;
            }

            if (countQuantity <= 0) {
              minusButton.disabled = true;
            } else {
              minusButton.disabled = false;
            }
          };

          inputPrice.onkeyup = () => {
            let price = +inputPrice.value * quantity.value;
            totalPrice.textContent = price.toFixed(2);
            item.setAttribute("data-price", inputPrice.value);
            if (!inputPrice.value) {
              totalPrice.textContent = 0;
            }
            getResult();
            itemPrices.forEach((itemPrice) => {
              getDigitsNumber(itemPrice, itemPrice.textContent);
            });
          };
          discountInput.onkeyup = () => {
            const curentPrice =
              (+item.getAttribute("data-price") *
                (100 - +discountInput.value)) /
              100;
            inputPrice.value = curentPrice.toFixed(2);
            const allPrice = curentPrice * countQuantity;
            getDigitsNumber(productTotalPrice, allPrice);
            getResult();
          };
          saveButton.onclick = () => saveSpecification();
        } else {
          getResult();
          itemPrices.forEach((itemPrice) => {
            getDigitsNumber(itemPrice, itemPrice.textContent);
          });
          discountInput.onkeyup = () => {
            const curentPrice =
              (+productPrice * (100 - +discountInput.value)) / 100;
            getDigitsNumber(productPriceContainer, curentPrice);

            const allPrice = curentPrice * countQuantity;
            getDigitsNumber(productTotalPrice, allPrice);
            getResult();
          };
          saveButton.onclick = () => saveSpecification(productItems);
        }

        deleteItemBtn.onclick = () => {
          const specificationArray = JSON.parse(
            localStorage.getItem("specificationValues")
          );
          console.log(specificationArray);
          specificationArray.splice(i, 1);
          const result = JSON.stringify(specificationArray);

          localStorage.setItem("specificationValues", result);

          setCookie("key", result, {
            path: "/",
            domain: window.location.hostname,
          });
          window.location.reload();
        };
      });

      saveButton.onclick = () => saveSpecification(productItems);
      exitButton.onclick = () => exitSpecification(productItems);

      // saveButton.onclick = (e) => {
      //   e.preventDefault();
      //   const products = [];
      //   productItems.forEach((item) => {
      //     let price;
      //     if (!itemPrice) {
      //       const inputPrice = item.querySelector("input");
      //       price = +inputPrice.value;
      //     } else {
      //       price = new NumberParser("ru").parse(itemPrice.textContent);
      //     }
      //     const itemQuantity = item.querySelector(".quantity").textContent;
      //     const itemID = item.getAttribute("data-id");
      //     const itemPriceStatus = item.getAttribute("data-price-exclusive");

      //     const product = {
      //       product_id: +itemID,
      //       quantity: +itemQuantity,
      //       price_exclusive: +itemPriceStatus,
      //       price_one: itemPrice,
      //     };
      //     products.push(product);
      //   });

      //   const endpoint = "/admin_specification/save_specification_view_admin/";

      //   const dataObj = {
      //     id_bitrix: 22,
      //     admin_creator_id: 2,
      //     products: products,
      //   };

      //   const data = JSON.stringify(dataObj);
      //   fetch(endpoint, {
      //     method: "POST",
      //     body: data,
      //     headers: {
      //       "Content-Type": "application/json",
      //       "X-CSRFToken": csrfToken,
      //     },
      //   })
      //     .then((response) => response.json())
      //     .then((response) => {
      //       if (response.status == "ok") {
      //         localStorage.removeItem("specificationValues");
      //         deleteCookie();
      //         window.location.href = "/admin_specification/all_specifications/";
      //       }
      //     })
      //     .catch((error) => console.error(error));
      // };
    }
  }

  //Слайдеры

  const categorySwiper = new Swiper(".categories_container", {
    slidesPerView: "auto",
    navigation: {
      nextEl: ".slider-arrow",
    },
  });

  const groupSwiper = new Swiper(".group-slider", {
    slidesPerView: "auto",
  });
  //

  //выпадающий поиск
  const searhForm = document.querySelector(".search-form-container");
  if (searhForm) {
    const searchInput = searhForm.querySelector(['[name="search_input"]']);
    const searchEndpoint = "/admin_specification/search_product/";
    let searchValue;
    const category = searhForm.getAttribute("category");
    const group = searhForm.getAttribute("group");
    const searchDescriptionField = searhForm.querySelector(
      ".search-elem-fields"
    );
    const closebtn = searhForm.querySelector(".close-sreach-field-button");
    const loader = searhForm.querySelector(".loader");

    function searchProduct(arr) {
      arr.forEach((el) => {
        el.onclick = () => {
          searchInput.value = el.textContent;
          closeSearchWindow();
        };
      });
    }
    function openSearchWindow() {
      searchDescriptionField.style.display = "flex";
      searchDescriptionField.style.opacity = "1";
    }
    function closeSearchWindow() {
      searchDescriptionField.style.opacity = 0;
      setTimeout(() => {
        searchDescriptionField.style.display = "none";
      }, 600);
      searchDescriptionField.innerHTML = "<div class='loader'>loading</div>";
    }

    let start = 0;
    let counter = 10;
    const objData = {
      category: category,
      group: group,
      value: searchValue,
      start: start,
      counter: counter,
    };

    function getNewSearchValues() {
      start += 10;
      counter += 10;
      objData.start = start;
      objData.counter = counter;
    }
    searchInput.onkeyup = () => {
      searchValue = searchInput.value;
      objData.value = searchValue.trim();
      objData.value = objData.value.replace(/ {1,}/g, " ");
      objData.start = start;
      objData.counter = counter;
      if (searchInput.value.length > 2) {
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
        }).then((response) =>
          response.json().then((response) => {
            if (response.status == "ok") {
              loader.classList.add("remove");
              start = 0;
              counter = 10;
              objData.start = start;
              objData.counter = counter;
              const products = JSON.parse(response.products);
              searchDescriptionField.innerHTML = "";
              products.forEach((product) => {
                searchDescriptionField.innerHTML += `<div class="product">${product.fields.name}</div>`;
              });
              const searchProducts =
                searchDescriptionField.querySelectorAll(".product");
              if (searchProducts) {
                searchProduct(searchProducts);
                searchDescriptionField.onscroll = () => {
                  if (
                    searchDescriptionField.scrollHeight -
                      searchDescriptionField.scrollTop <=
                    searchDescriptionField.offsetHeight
                  ) {
                    const data = JSON.stringify(objData);
                    fetch(searchEndpoint, {
                      method: "POST",
                      body: data,
                      headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                      },
                    }).then((response) =>
                      response.json().then((response) => {
                        if (response.status == "ok") {
                          getNewSearchValues();
                          const products = JSON.parse(response.products);
                          products.forEach((product) => {
                            searchDescriptionField.innerHTML += `<div class="product">${product.fields.name}</div>`;
                          });
                          const searchProducts =
                            searchDescriptionField.querySelectorAll(".product");
                          if (searchProducts) {
                            searchProduct(searchProducts);
                          }
                        }
                      })
                    );
                  }
                };
                if (products.length == 0) {
                  searchDescriptionField.innerHTML =
                    "<div>Таких товаров нет</div>";
                }
              }
            }
          })
        );
      }
      closebtn.onclick = () => {
        closeSearchWindow();
        closebtn.classList.remove("show");
        searchInput.value = "";
        start = 0;
        counter = 10;
        objData.start = start;
        objData.counter = counter;
      };
    };
  }
  //
  const allSpecifications = document.querySelector(".all_specifications_table");
  if (allSpecifications) {
    const prices = allSpecifications.querySelectorAll(".price");
    prices.forEach((price) => {
      const priceValue = getCurrentPrice(price.textContent);
      getDigitsNumber(price, priceValue);
    });

    //редактирование спецификации
    const currentSpecificatons = allSpecifications.querySelectorAll(
      "div[data-status='True']"
    );
    currentSpecificatons.forEach((item) => {
      const changeButton = item.querySelector(".change-specification-button");
      showButton(item, changeButton);
      const specificationId = +item.querySelector("a").textContent;

      changeButton.onclick = () => {
        const objData = {
          specification_id: specificationId,
        };
        const data = JSON.stringify(objData);
        fetch("/admin_specification/update_specification/", {
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
              const products = JSON.parse(response.products);
              localStorage.setItem(
                "specificationValues",
                JSON.stringify(products)
              );
              document.cookie = `key=${JSON.stringify(products)};path=/`;

              products.forEach((product) => {
                document.cookie = `specificationId=${JSON.stringify(
                  product.specificationId
                )}; path=/`;
              });
            }
            window.location.href =
              "/admin_specification/current_specification/";
          });
      };
    });
    //

    //актуализация спецификации
    const overdueSpecifications = allSpecifications.querySelectorAll(
      "div[data-status='False']"
    );
    overdueSpecifications.forEach((item) => {
      const updatingBtn = item.querySelector(".uptate-specification-button");
      showButton(item, updatingBtn);
      const specificationId =
        +item.querySelectorAll(".table_item_value")[0].textContent;
      updatingBtn.onclick = () => {
        const objData = {
          specification_id: specificationId,
        };
        const data = JSON.stringify(objData);
        fetch("/admin_specification/update_specification/", {
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
              const products = JSON.parse(response.products);
              localStorage.setItem(
                "specificationValues",
                JSON.stringify(products)
              );
              document.cookie = `key=${JSON.stringify(products)};path=/`;
              products.forEach((product) => {
                document.cookie = `specificationId=${JSON.stringify(
                  product.specificationId
                )}; path=/`;
              });
            }
            window.location.href =
              "/admin_specification/current_specification/";
          });
      };
    });
    //
  }
});
