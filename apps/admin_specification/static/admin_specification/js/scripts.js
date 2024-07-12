import "/static/core/js/slider.js";

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

function deleteCookie() {
  var cookies = document.cookie.split("; ");
  for (var c = 0; c < cookies.length; c++) {
    var d = window.location.hostname.split(".");
    while (d.length > 0) {
      var cookieBase =
        encodeURIComponent(cookies[c].split(";")[0].split("=")[0]) +
        "=; expires=Thu, 01-Jan-1970 00:00:01 GMT; domain=" +
        d.join(".") +
        " ;path=";
      var p = location.pathname.split("/");
      document.cookie = cookieBase + "/";
      while (p.length > 0) {
        document.cookie = cookieBase + p.join("/");
        p.pop();
      }
      d.shift();
    }
  }
}

function getCurrentPrice(p) {
  const price = p.replace(",", ".");
  return price;
}
let productsSpecificationList = [];

let localStorageSpecification = JSON.parse(
  localStorage.getItem("specificationValues")
);
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

const getDigitsNumber = (container, value) => {
  container.textContent = new Intl.NumberFormat("ru").format(+value);
};

const csrfToken = getCookie("csrftoken");

window.addEventListener("DOMContentLoaded", () => {
  const specificationContent = document.querySelector(".specification-content");
  if (specificationContent) {
    const specificationLinkContainer = specificationContent.querySelector(
      ".specification-link-container"
    );
    const specificationLinkContainerProductValue =
      specificationLinkContainer.querySelector("span");
    if (localStorageSpecification) {
      specificationLinkContainerProductValue.textContent =
        localStorageSpecification.length;
    } else {
      specificationLinkContainerProductValue.textContent = 0;
    }

    const catalog = specificationContent.querySelector(
      ".spetification-product-catalog"
    );
    if (catalog) {
      const catalogItems = catalog.querySelectorAll(".catalog-item");
      catalogItems.forEach((catalogItem) => {
        const productId = catalogItem.getAttribute("data-id");
        const productName = catalogItem.querySelector(".name").textContent;
        const productPrice = catalogItem.getAttribute("data-price");
        const productMotrumId = catalogItem.getAttribute("data-motrum-id");
        const productSalerId = catalogItem.getAttribute("data-saler-id");
        const buttonContainer = catalogItem.querySelector(".quantity-buttons");
        const plusButton = buttonContainer.querySelector(".plus-button");
        const minusButton = buttonContainer.querySelector(".minus-button");
        const addSpecificationButton = catalogItem.querySelector(
          ".add-specification-button"
        );
        const countQuantityZone = buttonContainer.querySelector("input");

        let countQuantity = +countQuantityZone.value;

        function addProductInSpecification() {
          if (addSpecificationButton.disabled == false) {
            addSpecificationButton.style.cursor = "pointer";
          } else {
            addSpecificationButton.style.cursor = "default";
          }
          if (addSpecificationButton.disabled == false) {
            const product = {
              id: +productId,
              name: productName,
              price: getCurrentPrice(productPrice),
              idMotrum: productMotrumId,
              idSaler: productSalerId,
              quantity: countQuantity,
              totalCost: (
                getCurrentPrice(productPrice) * countQuantity
              ).toFixed(2),
            };
            addSpecificationButton.onclick = () => {
              setProduct(product);
              if (localStorageSpecification) {
                specificationLinkContainerProductValue.textContent =
                  localStorageSpecification.length;
              } else {
                specificationLinkContainerProductValue.textContent =
                  productsSpecificationList.length;
              }
            };
          }
        }

        countQuantityZone.onkeyup = () => {
          countQuantity = +countQuantityZone.value;
          if (countQuantity > 0) {
            addSpecificationButton.disabled = false;
            addProductInSpecification();
          }
        };

        plusButton.onclick = () => {
          countQuantity++;
          countQuantityZone.value = countQuantity;
          minusButton.disabled = false;
          addSpecificationButton.disabled = false;

          if (countQuantity >= 999) {
            minusButton.disabled = false;
            plusButton.disabled = true;
          }
          addProductInSpecification();
        };

        minusButton.onclick = () => {
          countQuantity--;
          countQuantityZone.value = countQuantity;

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
          addProductInSpecification();
        };

        const priceContainer = catalogItem.querySelector(".price");
        const price = priceContainer.querySelector(".price-count");

        if (price) {
          const priceNumberValue = getCurrentPrice(price.textContent);
          getDigitsNumber(price, priceNumberValue);
        }
      });
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

      function getResult() {
        let sum = 0;
        const allElems = spetificationTable.querySelectorAll(".total_cost");
        for (let i = 0; i < allElems.length; i++) {
          sum += new NumberParser("ru").parse(allElems[i].textContent);
        }
        getDigitsNumber(valueContainer, +sum);
      }
      productItems.forEach((item, i) => {
        const deleteItemBtn = item.querySelector(".item_conainer-delete_btn");
        const itemPrices = item.querySelectorAll(".price");
        const inputPrice = item.querySelector("input");
        if (inputPrice) {
          const totalPrice = item.querySelector(".input_totla-cost");
          const quantity = +item.querySelector(".input_quantity").textContent;
          inputPrice.onkeyup = () => {
            let price = +inputPrice.value * quantity;
            totalPrice.textContent = price.toFixed(2);
            if (!inputPrice.value) {
              totalPrice.textContent = 0;
            }
            getResult();
            itemPrices.forEach((itemPrice) => {
              getDigitsNumber(itemPrice, itemPrice.textContent);
            });
          };
        } else {
          getResult();
          itemPrices.forEach((itemPrice) => {
            getDigitsNumber(itemPrice, itemPrice.textContent);
          });
        }

        deleteItemBtn.onclick = () => {
          const specificationArray = JSON.parse(
            localStorage.getItem("specificationValues")
          );
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

      const saveButton = spetificationTable.querySelector(".save_button");

      saveButton.onclick = (e) => {
        e.preventDefault();

        const products = [];
        productItems.forEach((item) => {
          let price;
          const itemPrice = item.querySelector(".price_once");
          if (itemPrice) {
            price = new NumberParser("ru").parse(itemPrice.textContent);
          } else {
            const inputPrice = item.querySelector("input");
            price = +inputPrice.value;
          }
          const itemQuantity = item.querySelector(".quantity").textContent;
          const itemID = item.getAttribute("data-id");
          const itemPriceStatus = item.getAttribute("data-price-exclusive");

          const product = {
            product_id: +itemID,
            quantity: +itemQuantity,
            price_exclusive: +itemPriceStatus,
            price_one: price,
          };
          products.push(product);
        });

        const endpoint = "/admin_specification/save_specification_view_admin/";

        const dataObj = {
          id_bitrix: 22,
          admin_creator_id: 2,
          products: products,
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
              deleteCookie();
              window.location.href =
                "/admin_specification/all_specifications/";
            }
          })
          .catch((error) => console.error(error));
      };
    }
  }
  const categorySwiper = new Swiper(".categories_container", {
    slidesPerView: "auto",
  });

  const groupSwiper = new Swiper(".group-slider", {
    slidesPerView: "auto",
  });

  const allSpecifications = document.querySelector(".all_specifications_table");
  if (allSpecifications) {
    const prices = allSpecifications.querySelectorAll(".price");
    prices.forEach((price) => {
      const priceValue = getCurrentPrice(price.textContent);
      getDigitsNumber(price, priceValue);
    });
  }

  //выпадающий поиск
  const searhForm = document.querySelector(".search-form-container");
  if (searhForm) {
    const searchInput = searhForm.querySelector(['[name="search_input"]']);
    const searchEndpoint = "/admin_specification/search_product/";
    let searchValue;
    const category = searhForm.getAttribute("category");
    const group = searhForm.getAttribute("group");
    const searchDescriptionField = searhForm.querySelector(
      ".search-elems-field"
    );
    searchInput.onkeyup = () => {
      if (searchInput.value.length >= 3) {
        searchValue = searchInput.value;
        const objData = {
          category: category,
          group: group,
          value: searchValue,
        };
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
              const products = JSON.parse(response.products);
              searchDescriptionField.style.display = "block";
              // searchDescriptionField.style.heigth = "7rem";
              setTimeout(() => {
                searchDescriptionField.style.opacity = 1;
              }, 600);
              searchDescriptionField.innerHTML = "";
              products.forEach((product) => {
                searchDescriptionField.innerHTML += `<div class="product">${product.fields.name}</div>`;
              });
              if (products.length == 0) {
                searchDescriptionField.innerHTML =
                  "<div>Таких товаров нет</div>";
              }
            }
          })
        );
      } else {
        searchDescriptionField.style.heigth = "1rem";
        searchDescriptionField.style.opacity = 0;
        setTimeout(() => {
          searchDescriptionField.style.display = "none";
        }, 600);
        searchDescriptionField.innerHTML = "";
      }

      searchDescriptionField.onmouseleave = () => {
        searchDescriptionField.style.opacity = 0;
        setTimeout(() => {
          searchDescriptionField.style.display = "none";
        }, 600);
        searchDescriptionField.innerHTML = "";
      };
    };
  }

  //
});
