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
    document.cookie = `key=${JSON.stringify(localStorageSpecification)}`;
  } else {
    localStorage.setItem(
      "specificationValues",
      JSON.stringify(productsSpecificationList)
    );
    document.cookie = `key=${JSON.stringify(productsSpecificationList)}`;
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
        const countQuantityZone = buttonContainer.querySelector("span");

        let countQuantity = +countQuantityZone.textContent;

        plusButton.onclick = () => {
          countQuantity++;
          countQuantityZone.textContent = countQuantity;
          minusButton.disabled = false;
          addSpecificationButton.disabled = false;

          if (countQuantityZone.textContent.length > 1) {
            countQuantityZone.style.left = "40.5%";
          }
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
        };

        minusButton.onclick = () => {
          countQuantity--;
          countQuantityZone.textContent = countQuantity;

          if (countQuantity <= 0) {
            minusButton.disabled = true;
            addSpecificationButton.disabled = true;
          } else {
            minusButton.disabled = false;
            addSpecificationButton.disabled = false;
          }
          if (countQuantityZone.textContent.length <= 1) {
            countQuantityZone.style.left = "45.5%";
          }
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
      const totalPraiceValueContainer =
        spetificationTable.querySelector(".price_description");
      const valueContainer = totalPraiceValueContainer.querySelector(".price");

      function getResult() {
        let sum = 0;
        const allElems = spetificationTable.querySelectorAll(".total_cost");
        for (let i = 0; i < allElems.length; i++) {
          sum += new NumberParser("ru").parse(allElems[i].textContent);
        }
        valueContainer.textContent = new Intl.NumberFormat("ru").format(+sum);
      }
      productItems.forEach((item) => {
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

        const csrfToken = getCookie("csrftoken");
        const endpoint = "/admin_specification/save_specification_view_admin/";

        const dataObj = {
          id_bitrix: 22,
          admin_creator_id: 1,
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
              console.log(data);
            }
          })
          .catch((error) => console.error(error));
      };
    }
  }
});
