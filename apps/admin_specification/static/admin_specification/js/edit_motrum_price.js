import { getCurrentPrice, getDigitsNumber } from "/static/core/js/functions.js";

export function editMotrumPrice(container) {
  if (container) {
    const specificationItems = container.querySelectorAll(".item_container");
    specificationItems.forEach((specification) => {
      const priceInput = specification.querySelector(".price-input");
      const motrumPriceContainer = specification.querySelector(".price_motrum");
      const motrumSalePersent = getCurrentPrice(
        specification.querySelector(".motrum_sale_persent").textContent
      );

      if (priceInput) {
        priceInput.value = getCurrentPrice(priceInput.value);
        // getDigitsNumber(
        //   productTotalPrice,
        //   +inputPrice.value * +quantity.value
        // );
        if (specification.querySelector(".motrum_sale_persent")) {
          getDigitsNumber(motrumPriceContainer);
          motrumPriceContainer.setAttribute(
            "price-motrum",
            (+priceInput.value / 100) * (100 - +motrumSalePersent)
          );
        } else {
          motrumPriceContainer.setAttribute("price-motrum", priceInput.value);
        }
        priceInput.addEventListener("input", function () {
          if (specification.querySelector(".motrum_sale_persent")) {
            getDigitsNumber(motrumPriceContainer);
            motrumPriceContainer.setAttribute(
              "price-motrum",
              (+priceInput.value / 100) * (100 - +motrumSalePersent)
            );
          } else {
            motrumPriceContainer.setAttribute("price-motrum", priceInput.value);
          }
        });
      }
      const motrumPriceOne = motrumPriceContainer
        ? getCurrentPrice(motrumPriceContainer.getAttribute("price-motrum"))
        : 0;

      const quantityItem = specification.querySelector(".input-quantity").value;
      const currentMotrumPrice = +motrumPriceOne * +quantityItem;

      motrumPriceContainer
        ? getDigitsNumber(motrumPriceContainer, +currentMotrumPrice)
        : "";
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(".spetification_table");
  editMotrumPrice(specificationContainer);
});
