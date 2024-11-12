import { getCurrentPrice, getDigitsNumber } from "/static/core/js/functions.js";

export function editMotrumPrice(container) {
  if (container) {
    const specificationItems = container.querySelectorAll(".item_container");
    specificationItems.forEach((specification) => {
      const priceInput = specification.querySelector(".price-input");
      const motrumPriceContainer = specification.querySelector(".price_motrum");

      if (priceInput) {
        priceInput.value = getCurrentPrice(priceInput.value);

        if (specification.querySelector(".motrum_sale_persent")) {
          const motrumSalePersent = getCurrentPrice(
            specification.querySelector(".motrum_sale_persent").textContent
          );
          motrumPriceContainer.setAttribute(
            "price-motrum",
            (+getCurrentPrice(specification.getAttribute("data-price")) / 100) *
              (100 - +motrumSalePersent)
          );
          priceInput.addEventListener("input", function () {
            if (specification.querySelector(".motrum_sale_persent")) {
              motrumPriceContainer.setAttribute(
                "price-motrum",
                (+priceInput.value / 100) * (100 - +motrumSalePersent)
              );
            } else {
              motrumPriceContainer.setAttribute(
                "price-motrum",
                priceInput.value
              );
            }
          });
        } else {
          motrumPriceContainer.setAttribute("price-motrum", priceInput.value);
        }
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
