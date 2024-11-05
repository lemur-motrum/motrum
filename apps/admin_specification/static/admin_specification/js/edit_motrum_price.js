import { getCurrentPrice, getDigitsNumber } from "/static/core/js/functions.js";

export function editMotrumPrice(container) {
  if (container) {
    const specificationItems = container.querySelectorAll(".item_container");
    specificationItems.forEach((specification) => {
      const priceInput = specification.querySelector(".price-input");
      const motrumPriceContainer = specification.querySelector(".price_motrum");
      if (priceInput) {
        priceInput.oninput = () => {
          motrumPriceContainer.setAttribute("price-motrum", priceInput.value);
        };
      }
      const motrumPriceOne = getCurrentPrice(
        motrumPriceContainer.getAttribute("price-motrum")
      );

      const quantityItem = specification.querySelector(".input-quantity").value;
      const currentMotrumPrice = +motrumPriceOne * +quantityItem;
      console.log("currentMotrumPrice", currentMotrumPrice);

      getDigitsNumber(motrumPriceContainer, currentMotrumPrice);
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(".spetification_table");
  editMotrumPrice(specificationContainer);
});
