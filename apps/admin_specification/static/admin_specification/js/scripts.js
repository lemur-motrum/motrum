import "/static/core/js/slider.js";
import {
  NumberParser,
  getCookie,
  deleteCookie,
  getClosestInteger,
  getDigitsNumber,
  showErrorValidation,
  getCurrentPrice,
} from "/static/core/js/functions.js";

import { setErrorModal } from "../js/error_modal.js";
import { changeDateInOrder } from "../js/change_date_in_order.js";
import { editMotrumPrice } from "../js/edit_motrum_price.js";

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
function catalogLogic(elems) {
  elems.forEach((catalogItem) => {
    showInformation(catalogItem);

    const productId = catalogItem.getAttribute("data-id");
    const buttonContainer = catalogItem.querySelector(".quantity-buttons");

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
        countQuantity = +val;
      } else {
        countQuantity = +countQuantityZone.value;
      }

      if (countQuantity >= 99999) {
        countQuantityZone.value = productMultiplicityQuantity
          ? getClosestInteger(99999, +productMultiplicityQuantity)
          : 99999;
        minusButton.disabled = false;
        plusButton.disabled = true;
        addSpecificationButton.disabled = false;
      } else if (countQuantity <= 0) {
        countQuantityZone.value = 0;
        plusButton.disabled = false;
        addSpecificationButton.disabled = true;
      } else {
        minusButton.disabled = false;
        plusButton.disabled = false;
        addSpecificationButton.disabled = false;
      }
    });

    plusButton.onclick = () => {
      if (productMultiplicityQuantity) {
        countQuantity += +productMultiplicityQuantity;
      } else {
        countQuantity++;
      }
      countQuantityZone.value = +countQuantity;
      minusButton.disabled = false;
      addSpecificationButton.disabled = false;
      if (countQuantity >= 99999) {
        countQuantityZone.value = productMultiplicityQuantity
          ? getClosestInteger(99999, +productMultiplicityQuantity)
          : 99999;
        plusButton.disabled = true;
        minusButton.disabled = false;
      } else {
        plusButton.disabled = false;
        minusButton.disabled = false;
      }
    };
    minusButton.onclick = () => {
      if (productMultiplicityQuantity) {
        countQuantity -= +productMultiplicityQuantity;
      } else {
        countQuantity--;
      }
      countQuantityZone.value = countQuantity;
      minusButton.disabled = false;
      if (countQuantity <= 0) {
        countQuantityZone.value = 0;
        minusButton.disabled = true;
        plusButton.disabled = false;
        addSpecificationButton.disabled = true;
      } else {
        minusButton.disabled = false;
        plusButton.disabled = false;
        addSpecificationButton.disabled = false;
      }
    };
    addSpecificationButton.onclick = () => {
      if (!getCookie("cart")) {
        fetch("/api/v1/cart/add-cart/", {
          method: "GET",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((cart_id) => {
            if (cart_id) {
              const dataObj = {
                product: +productId,
                cart: +cart_id,
                quantity: countQuantityZone.value,
              };

              const data = JSON.stringify(dataObj);
              fetch(`/api/v1/cart/${cart_id}/save-product/`, {
                method: "POST",
                body: data,
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken,
                },
              })
                .then((response) => {
                  if (response.status == 200) {
                    return response.json();
                  } else {
                    setErrorModal();
                    throw new Error("Ошибка");
                  }
                })
                .then(
                  (response) =>
                    (document.querySelector(
                      ".admin_specification_cart_length"
                    ).textContent = response.cart_len)
                )
                .catch((error) => {
                  setErrorModal();
                  console.error(error);
                });
            }
          })
          .catch((error) => {
            setErrorModal();
            console.error(error);
          });
      } else {
        const cart_id = getCookie("cart");
        const dataObj = {
          product: +productId,
          cart: +cart_id,
          quantity: +countQuantityZone.value,
        };

        const data = JSON.stringify(dataObj);
        fetch(`/api/v1/cart/${cart_id}/save-product/`, {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.status == 200) {
              return response.json();
            } else {
              setErrorModal();
              throw new Error("Ошибка");
            }
          })
          .then(
            (response) =>
              (document.querySelector(
                ".admin_specification_cart_length"
              ).textContent = response.cart_len)
          )
          .catch((error) => {
            setErrorModal();
            console.error(error);
          });
      }
    };
  });
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
    const catalog = catalogContainer.querySelector(
      ".spetification-product-catalog"
    );
    if (catalog) {
      const catalogItems = catalog.querySelectorAll(".catalog-item");
      catalogLogic(catalogItems);

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

        const urlParams = new URL(document.location).searchParams;
        const urlParamasArray = urlParams.get("vendor")
          ? urlParams.get("vendor").split(",")
          : null;
        const priceUrl = urlParams.get("price") ? urlParams.get("price") : null;
        const objData = {
          group: group,
          category: category,
          pageNum: pageNum,
          urlParams: urlParamasArray,
          priceUrl: priceUrl,
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
                catalogLogic(catalogItems);
                setCurrentPriceCataloItem(catalogItems);
              }
            });
        };
      }

      setCurrentPriceCataloItem(catalogItems);
    }
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
        const specificationId = getCookie("specificationId");
        const adminCreator = document.querySelector("[data-user-id]");
        const adminCreatorId = adminCreator.getAttribute("data-user-id");
        const commentAll = document.querySelector(
          'textarea[name="comment-input-name-all"]'
        ).value;
        const dateDeliveryAll = document.querySelector(
          'textarea[name="delivery-date-all-input-name-all"]'
        ).value;
        let validate = true;
        const products = [];
        const motrumRequsits = document
          .querySelector("[name='mortum_req']")
          .getAttribute("value");
        const clientRequsits = document
          .querySelector("[name='client-requisit']")
          .getAttribute("value");
        const deliveryRequsits = document
          .querySelector("[name='delevery-requisit']")
          .getAttribute("value");
        const bitrixInput = document.querySelector(".bitrix-input");
        elems.forEach((item, i) => {
          const itemQuantity = item.querySelector(".input-quantity").value;
          const itemID = item.getAttribute("data-product-pk");
          const nameProductNew = item.getAttribute("data-product-name-new");
          const itemPriceStatus = item.getAttribute("data-price-exclusive");
          const itemPrice = item.getAttribute("data-price");

          const extraDiscount = item.querySelector(".discount-input");
          const productSpecificationId = item.getAttribute(
            "data-product-specification-id"
          );
          const vendor = item.getAttribute("data-vendor");
          const deliveryDate = item.querySelector(".delivery_date");
          const commentItem = item.querySelector(
            'textarea[name="comment-input-name"]'
          ).value;
          const inputPrice = item.querySelector(".price-input");
          const saleMotrum = item.querySelector(".motrum_sale_persent");
          const productCartId = item.getAttribute("data-product-id-cart");

          const createTextDateDelivery = () => {
            const orderData = new Date(deliveryDate.value);
            const today = new Date();
            const delta = orderData.getTime() - today.getTime();
            const dayDifference = +Math.floor(delta / 1000 / 60 / 60 / 24);
            const resultDays = +Math.ceil(dayDifference / 7);

            function num_word(value, words) {
              value = Math.abs(value) % 100;
              var num = value % 10;
              if (value > 10 && value < 20) return words[2];
              if (num > 1 && num < 5) return words[1];
              if (num == 1) return words[0];
              return words[2];
            }
            if (dayDifference > 7) {
              return `${resultDays} ${num_word(resultDays, [
                "неделя",
                "недели",
                "недель",
              ])}`;
            } else {
              return "1 неделя";
            }
          };
          const product = {
            product_id: +itemID,
            quantity: +itemQuantity,
            price_exclusive: +itemPriceStatus,
            price_one: +getCurrentPrice(itemPrice),
            product_specif_id: productSpecificationId
              ? productSpecificationId
              : null,
            extra_discount: extraDiscount.value,
            date_delivery: deliveryDate.value,
            text_delivery: createTextDateDelivery(),
            product_name_new: nameProductNew,
            product_new_article: nameProductNew,
            comment: commentItem ? commentItem : null,
            sale_motrum: saleMotrum ? saleMotrum.textContent : null,
            vendor: vendor ? vendor : null,
            id_cart: productCartId,
          };

          if (
            inputPrice
              ? !inputPrice.value || !deliveryDate.value
              : !deliveryDate.value
          ) {
            validate = false;
            if (!deliveryDate.value) {
              deliveryDate.style.border = "1px solid red";
              deliveryDate.style.borderRadius = "10px";
            }
            if (inputPrice && !inputPrice.value) {
              inputPrice.style.border = "1px solid red";
              inputPrice.style.borderRadius = "10px";
            }
          } else {
            if (deliveryDate) {
              deliveryDate.style.border = "1px solid black";
            }
            if (inputPrice) {
              inputPrice.style.border = "1px solid black";
            }
            products.push(product);
          }
        });

        if (bitrixInput) {
          if (!bitrixInput.value) {
            validate = false;
            bitrixInput.style.border = "1px solid red";
            bitrixInput.style.borderRadius = "10px";
          }
        }
        if (validate == false) {
          const saveButtonContainer = document.querySelector(
            ".save_button-wrapper"
          );
          const error = saveButtonContainer.querySelector(".error");
          showErrorValidation("Заполните все поля", error);
        }

        if (validate == true) {
          saveButton.disabled = true;
          saveButton.textContent = "";
          saveButton.innerHTML = `<div class="small_loader"></div>`;

          const dataObj = {
            id_bitrix: +bitrixInput.value,
            admin_creator_id: adminCreatorId,
            products: products,
            id_specification: specificationId ? specificationId : null,
            id_cart: +getCookie("cart"),
            comment: commentAll ? commentAll : null,
            date_delivery: dateDeliveryAll ? dateDeliveryAll : null,
            motrum_requisites: +motrumRequsits,
            client_requisites: +clientRequsits,
            type_delivery: deliveryRequsits,
            type_save: "specification",
            post_update: false,
          };

          const data = JSON.stringify(dataObj);
          let endpoint = "/api/v1/order/add-order-admin/";
          fetch(endpoint, {
            method: "POST",
            body: data,
            headers: {
              "X-CSRFToken": csrfToken,
              "Content-Type": "application/json",
            },
          })
            .then((response) => response.json())
            .then((response) => {
              localStorage.removeItem("specificationValues");
              deleteCookie("key", "/", window.location.hostname);
              deleteCookie("specificationId", "/", window.location.hostname);
              deleteCookie("cart", "/", window.location.hostname);

              window.location.href = "/admin_specification/all_specifications/";
            })
            .catch((error) => {
              setErrorModal();
              console.error(error);
            });
        }
      }
      function exitSpecification(elems) {
        const endpoint = `/api/v1/order/exit-order-admin/`;
        fetch(endpoint, {
          method: "UPDATE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((response) => {
            deleteCookie("specificationId", "/", window.location.hostname);
            deleteCookie("cart", "/", window.location.hostname);
            window.location.href = "/admin_specification/all_specifications/";
          });
      }

      productItems.forEach((item, i) => {
        const deleteItemBtn = item.querySelector(".item_conainer-delete_btn");
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
        const productID = item.getAttribute("data-id");
        const productCartID = item.getAttribute("data-product-id-cart");

        if (discountInput) {
          discountInput.value = getCurrentPrice(discountInput.value);
        }
        if (inputPrice) {
          getDigitsNumber(
            productTotalPrice,
            +inputPrice.value * +quantity.value
          );
        }
        if (itemPriceOnce) {
          if (discountInput) {
            getDigitsNumber(
              itemPriceOnce,
              (+getCurrentPrice(productPrice) * (100 - +discountInput.value)) /
                100
            );
          } else {
            const currnetPriceOne = +getCurrentPrice(itemPriceOnce.textContent);
            getDigitsNumber(itemPriceOnce, currnetPriceOne);
          }
          const currentPrice = +getCurrentPrice(productPrice) * +quantity.value;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
        }

        function updateProduct() {
          setTimeout(() => {
            const dataObj = {
              quantity: +quantity.value,
            };
            const data = JSON.stringify(dataObj);
            fetch(`/api/v1/cart/${productID}/update-product/`, {
              method: "UPDATE",
              body: data,
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
            })
              .then((response) => {
                if (response.status == 200) {
                  console.log(
                    `Товар с id ${productID}, успешно изменен на количество ${quantity.value}`
                  );
                }
              })
              .catch((error) => {
                setErrorModal();
                console.error(error);
              });
          }, 1500);
        }

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
            countQuantity = +val;
          } else {
            countQuantity = +quantity.value;
          }
          if (countQuantity >= 99999) {
            quantity.value = 99999;
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else if (countQuantity <= 1) {
            quantity.value = 1;
            plusButton.disabled = false;
          } else {
            minusButton.disabled = false;
            plusButton.disabled = false;
          }
          if (itemPriceOnce) {
            const currentPrice = !discountInput.value
              ? +getCurrentPrice(item.getAttribute("data-price")) *
                +quantity.value
              : (+getCurrentPrice(item.getAttribute("data-price")) *
                  +quantity.value *
                  (100 - +discountInput.value)) /
                100;

            getDigitsNumber(productTotalPrice, currentPrice);
            editMotrumPrice(spetificationTable);
            changeDateInOrder(spetificationTable);
            getResult();
            updateProduct();
          }
        });

        plusButton.onclick = () => {
          if (multiplicity) {
            countQuantity += +multiplicity;
          } else {
            countQuantity++;
          }
          quantity.value = +countQuantity;
          const currentPrice = !discountInput.value
            ? +getCurrentPrice(item.getAttribute("data-price")) *
              +quantity.value
            : (+getCurrentPrice(item.getAttribute("data-price")) *
                +quantity.value *
                (100 - +discountInput.value)) /
              100;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
          if (countQuantity >= 99999) {
            minusButton.disabled = false;
            plusButton.disabled = true;
          }
          if (countQuantity > 0) {
            minusButton.disabled = false;
          } else {
            minusButton.disabled = true;
          }
          editMotrumPrice(spetificationTable);
          changeDateInOrder(spetificationTable);
          updateProduct();
        };

        minusButton.onclick = () => {
          if (multiplicity) {
            countQuantity -= +multiplicity;
          } else {
            countQuantity--;
          }
          quantity.value = +countQuantity;
          if (quantity.value <= 1) {
            quantity.value = 1;
          }
          const currentPrice = !discountInput.value
            ? +getCurrentPrice(item.getAttribute("data-price")) *
              +quantity.value
            : (+getCurrentPrice(item.getAttribute("data-price")) *
                +quantity.value *
                (100 - +discountInput.value)) /
              100;
          getDigitsNumber(productTotalPrice, currentPrice);
          getResult();
          if (countQuantity >= 99999) {
            minusButton.disabled = false;
            plusButton.disabled = true;
          } else {
            plusButton.disabled = false;
          }
          if (countQuantity <= 1) {
            minusButton.disabled = true;
          } else {
            minusButton.disabled = false;
          }
          editMotrumPrice(spetificationTable);
          changeDateInOrder(spetificationTable);
          updateProduct();
        };

        if (inputPrice) {
          const totalPrice = item.querySelector(".input_totla-cost");
          const quantity = item.querySelector(".input-quantity");

          quantity.onkeyup = () => {
            countQuantity = +quantity.value;
            const currentPrice = !discountInput.value
              ? new NumberParser("ru").parse(inputPrice.value) * +quantity.value
              : (new NumberParser("ru").parse(inputPrice.value) *
                  +quantity.value *
                  (100 - +discountInput.value)) /
                100;
            getDigitsNumber(productTotalPrice, currentPrice);
            let price = +inputPrice.value * quantity.value;
            getDigitsNumber(totalPrice, price);
            getResult();
            editMotrumPrice(spetificationTable);
            changeDateInOrder(spetificationTable);
          };

          plusButton.onclick = () => {
            const currentPrice = !discountInput.value
              ? +item.getAttribute("data-price") * +quantity.value
              : (+item.getAttribute("data-price") *
                  +quantity.value *
                  (100 - +discountInput.value)) /
                100;
            getDigitsNumber(productTotalPrice, currentPrice);
            if (multiplicity) {
              countQuantity += +multiplicity;
            } else {
              countQuantity++;
            }
            quantity.value = +countQuantity;
            minusButton.disabled = false;
            if (countQuantity >= 99999) {
              quantity.value = multiplicity
                ? getClosestInteger(99999, +multiplicity)
                : 99999;
              plusButton.disabled = true;
              minusButton.disabled = false;
            } else {
              plusButton.disabled = false;
              minusButton.disabled = false;
            }
            editMotrumPrice(spetificationTable);
            changeDateInOrder(spetificationTable);
            updateProduct();
            let price = +inputPrice.value * quantity.value;
            getDigitsNumber(totalPrice, price);
            getResult();
          };

          minusButton.onclick = () => {
            const currentPrice = !discountInput.value
              ? +item.getAttribute("data-price") * +quantity.value
              : (+item.getAttribute("data-price") *
                  +quantity.value *
                  (100 - +discountInput.value)) /
                100;
            getDigitsNumber(productTotalPrice, currentPrice);

            if (multiplicity) {
              countQuantity -= +multiplicity;
            } else {
              countQuantity--;
            }
            quantity.value = countQuantity;
            minusButton.disabled = false;
            if (countQuantity <= 1) {
              quantity.value = 1;
              minusButton.disabled = true;
              plusButton.disabled = false;
            } else {
              minusButton.disabled = false;
              plusButton.disabled = false;
            }
            editMotrumPrice(spetificationTable);
            updateProduct();
            changeDateInOrder(spetificationTable);
            let price = +inputPrice.value * quantity.value;
            getDigitsNumber(totalPrice, price);
            getResult();
          };

          inputPrice.addEventListener("input", function (e) {
            const currentValue = this.value
              .replace(",", ".")
              .replace(/[^.\d]+/g, "")
              .replace(/^([^\.]*\.)|\./g, "$1")
              .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
                return a + b + c.slice(0, 2);
              });
            inputPrice.value = currentValue;
            if (inputPrice.value == ".") {
              e.target.value = "";
            }
            if (inputPrice.value == "0") {
              e.target.value = "";
            }
            let price = !discountInput.value
              ? +inputPrice.value * quantity.value
              : (+inputPrice.value *
                  quantity.value *
                  (100 - +discountInput.value)) /
                100;
            getDigitsNumber(totalPrice, price);
            if (!discountInput.value) {
              item.setAttribute("data-price", +inputPrice.value);
            } else {
              item.setAttribute(
                "data-price",
                (+inputPrice.value * 100) / (100 - +discountInput.value)
              );
            }
            if (!inputPrice.value) {
              totalPrice.textContent = 0;
            }
            editMotrumPrice(spetificationTable);
            updateProduct();
            // changeDateInOrder(spetificationTable);
            getResult();
            const allPrice = inputPrice.value * countQuantity;
            getDigitsNumber(productTotalPrice, allPrice);
          });

          const allPrice = inputPrice.value * countQuantity;
          getDigitsNumber(productTotalPrice, allPrice.toFixed(2));
          discountInput.onkeyup = () => {
            if (discountInput.value >= 100) {
              discountInput.value == 100;
            }
            const curentPrice =
              (+getCurrentPrice(item.getAttribute("data-price")) *
                (100 - +discountInput.value)) /
              100;

            inputPrice.value = curentPrice.toFixed(2);
            const allPrice = inputPrice.value * countQuantity;
            getDigitsNumber(productTotalPrice, allPrice);
            getResult();
          };
          if (saveButton) {
            saveButton.onclick = () => saveSpecification();
          }
        } else {
          getResult();
          discountInput.onkeyup = () => {
            if (discountInput.value >= 100) {
              discountInput.value == 100;
            }
            const curentPrice =
              (+getCurrentPrice(productPrice) * (100 - +discountInput.value)) /
              100;
            getDigitsNumber(productPriceContainer, curentPrice);
            const allPrice = (curentPrice * countQuantity).toFixed(2);
            getDigitsNumber(productTotalPrice, allPrice);
            getResult();
          };
          if (saveButton) {
            saveButton.onclick = () => saveSpecification(productItems);
          }
        }

        deleteItemBtn.onclick = () => {
          fetch(`/api/v1/cart/${+productCartID}/delete-product/`, {
            method: "delete",
            headers: {
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => {
              if (response.status == 200) {
                window.location.reload();
              }
            })
            .catch((error) => {
              setErrorModal();
              console.error(error);
            });
        };
      });
      getResult();
      if (saveButton) {
        saveButton.onclick = () => saveSpecification(productItems);
      }
      exitButton.onclick = () => exitSpecification(productItems);
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
      const link = item.querySelector("a");
      const specificationId = +link.textContent;
      const cartId = +link.dataset.cartId;

      changeButton.onclick = () => {
        document.cookie = `cart=${cartId};path=/`;
        document.cookie = `specificationId=${specificationId};path=/`;
        const endpoint = `/api/v1/order/${cartId}/update-order-admin/`;
        fetch(endpoint, {
          method: "UPDATE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((response) => {
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

    //добавление счета

    currentSpecificatons.forEach((item) => {
      const changeButton = item.querySelector(".create-bill-button");
      const link = item.querySelector("a");
      const specificationId = +link.textContent;

      changeButton.onclick = () => {
        const endpoint = `/api/v1/order/${specificationId}/create-bill-admin/`;
        fetch(endpoint, {
          method: "UPDATE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        }).then((response) => {
          if (response.status == 200) {
            window.location.reload();
          } else {
            setErrorModal();
          }
        });
      };
    });
    overdueSpecifications.forEach((item) => {
      const updatingBtn = item.querySelector(".uptate-specification-button");

      const specificationId =
        +item.querySelectorAll(".table_item_value")[0].textContent;
      let cartId = item.querySelectorAll(".table_item_value")[0];

      updatingBtn.onclick = () => {
        cartId = cartId.getAttribute("data-cart-id");

        document.cookie = `cart=${cartId};path=/`;
        document.cookie = `specificationId=${specificationId};path=/`;
        const endpoint = `/api/v1/order/${cartId}/update-order-admin/`;
        fetch(endpoint, {
          method: "UPDATE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((response) => {
            window.location.href =
              "/admin_specification/current_specification/";
          });
      };
    });
    //
  }

  const priceDiscountInput = document.querySelectorAll(
    '[name="price-input-discount"]'
  );
  if (priceDiscountInput) {
    priceDiscountInput.forEach((el) => {
      el.addEventListener("input", function (e) {
        const currentValue = this.value
          .replace(",", ".")
          .replace(/[^.\d.-]+/g, "")
          .replace(/^([^\.]*\.)|\./g, "$1")
          .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
            return a + b + c.slice(0, 2);
          });
        el.value = currentValue;
        if (+el.value > 99.99) {
          el.value = 99.99;
        }
        if (+el.value < -99.99) {
          el.value = -99.99;
        }
        if (el.value.length > 1 && el.value.at(-1) === "-") {
          e.target.value = el.value.slice(0, -1);
        }
        if (el.value == ".") {
          e.target.value = "";
        }
        if (el.value == "0") {
          e.target.value = "";
        }
      });
    });
  }
  // поиск клиентов по инн имени в корзине
  const searhClientForm = document.querySelector(".serch-client");
  if (searhClientForm) {
    const searchClientInput = searhClientForm.querySelector([
      '[name="serch-client_input"]',
    ]);
    const clientsContainer = searhClientForm.querySelector(".clients");
    const clientRequsitsSelectLabel = searhClientForm.querySelector(
      ".select-client-requsits_label"
    );
    const specificationContainer = document.querySelector(
      ".specification-container"
    );
    if (specificationContainer) {
      const orderStatus = specificationContainer.getAttribute("order");
      if (orderStatus) {
        if (orderStatus !== "None") {
          clientRequsitsSelectLabel.classList.add("show");
        }
      }
    }
    const clientRequsitsSelect = clientRequsitsSelectLabel.querySelector(
      ".select-client-requsits"
    );
    const selectDelevery = searhClientForm.querySelector(".select_delevery");
    changeSelect(selectDelevery);

    const motrumRequsits = document.querySelector(".select_motrum_requisites");
    const clientOptions = motrumRequsits.querySelectorAll("option");
    motrumRequsits.setAttribute(
      "value",
      clientOptions[0].getAttribute("data-account-requisites-id")
    );
    clientOptions.forEach((el) => {
      motrumRequsits.addEventListener("change", function () {
        if (el.selected) {
          motrumRequsits.setAttribute("value", el.getAttribute("value"));
        }
      });
    });
    const clientInfo = searhClientForm.querySelector(".client-info");
    const searchEndpoint = "/api/v1/client/get-client-requisites/";
    const saveButtonContainer = document.querySelector(".save_button-wrapper");
    const saveInvoiceButtonContainer = document.querySelector(
      ".save_invoice_button-wrapper"
    );

    window.onload = () => {
      if (searchClientInput.value) {
        if (saveButtonContainer) {
          saveButtonContainer.classList.add("show");
        }
        if (saveInvoiceButtonContainer) {
          saveInvoiceButtonContainer.classList.add("show");
        }
        if (clientRequsitsSelect) {
          const clientOptions = clientRequsitsSelect.querySelectorAll("option");
          clientRequsitsSelect.setAttribute(
            "value",
            clientOptions[0].getAttribute("value")
          );
          clientOptions.forEach((el) => {
            clientRequsitsSelect.addEventListener("change", function () {
              if (el.selected) {
                clientRequsitsSelect.setAttribute(
                  "value",
                  el.getAttribute("value")
                );
              }
            });
          });
        }
      }
    };
    searchClientInput.onkeyup = () => {
      const objData = {
        client: searchClientInput.value,
      };
      if (searchClientInput.value.length > 2) {
        clientsContainer.classList.add("show");
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
          .then((data) => {
            if (data.length > 0) {
              clientsContainer.innerHTML = "";
              data.forEach((el) => {
                clientsContainer.innerHTML += `<div data-client-id="${el.id}" class="client">${el.legal_entity}</div>`;
                const clients = clientsContainer.querySelectorAll(".client");
                clients.forEach((client) => {
                  if (client) {
                    client.onmouseover = () => {
                      client.classList.add("active");
                    };
                    client.onmouseout = () => {
                      client.classList.remove("active");
                    };
                    client.onclick = () => {
                      clientInfo.innerHTML = "";
                      searchClientInput.value = client.textContent;
                      searchClientInput.setAttribute(
                        "client-id",
                        client.getAttribute("data-client-id")
                      );
                      if (el.accountrequisites_set.length > 0) {
                        clientRequsitsSelect.innerHTML = "";
                        el.accountrequisites_set.forEach((elem) => {
                          if (
                            +searchClientInput.getAttribute("client-id") ===
                            +elem.requisites
                          ) {
                            clientRequsitsSelectLabel.classList.add("show");
                            clientRequsitsSelect.innerHTML += `<option class="client-option" value="${elem.id}">${elem.account_requisites}</option>`;
                          }
                        });

                        if (clientRequsitsSelect) {
                          changeSelect(clientRequsitsSelect);
                        }
                      } else {
                        clientRequsitsSelect.innerHTML = "";
                      }
                      clientInfo.innerHTML = `
                             <div>Предоплата: ${el.prepay_persent}%</div>
                             <div>Доставка: <select class="select_delevery" name='delevery-requisit'><option value="pickup">Самовывоз</option><option value="paid_delivery">Доставка до терминала за счет покупателя</option></select></div>
                             `;
                      const selectDelevery =
                        searhClientForm.querySelector(".select_delevery");
                      changeSelect(selectDelevery);
                      clientsContainer.classList.remove("show");
                      saveButtonContainer.classList.add("show");
                      saveInvoiceButtonContainer.classList.add("show");
                    };
                  }
                });
              });
            } else {
              clientsContainer.innerHTML =
                "<div class='none'>Клинтов нет</div>";
              searchClientInput.setAttribute("client-id", "");
            }
          });
      } else {
        clientsContainer.classList.remove("show");
        saveButtonContainer.classList.remove("show");
        saveInvoiceButtonContainer.classList.remove("show");
        searchClientInput.setAttribute("client-id", "");
      }
    };
  }
});

function changeSelect(select) {
  if (select) {
    const clientOptions = select.querySelectorAll("option");
    select.setAttribute("value", clientOptions[0].getAttribute("value"));
    clientOptions.forEach((el) => {
      select.addEventListener("change", function () {
        if (el.selected) {
          select.setAttribute("value", el.getAttribute("value"));
        }
      });
    });
  }
}
