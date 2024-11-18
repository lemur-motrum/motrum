import {
  NumberParser,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

export function getMarginality(wrapper) {
  if (wrapper) {
    const spetificationItems = wrapper.querySelectorAll(".item_container");
    spetificationItems.forEach((item) => {
      const quantityInput = item.querySelector(".input-quantity");
      const discountInput = item.querySelector(".discount-input");
      const priceMotrum = new NumberParser("ru").parse(
        item.querySelector(".price_motrum").textContent
      );
      const priceOne = +getCurrentPrice(item.getAttribute("data-price"));
      let totalCost;
      if (!discountInput) {
        totalCost = +quantityInput.value * priceOne;
      } else {
        totalCost =
          +quantityInput.value *
          ((priceOne / 100) * (100 - discountInput.value));
      }
      const marginalityContainer = item.querySelector(".marginality");
      const motrumSalePersent = item.querySelector(".motrum_sale_persent");
      if (motrumSalePersent) {
        getDigitsNumber(marginalityContainer, totalCost - priceMotrum);
      } else {
        if (discountInput.value) {
          getDigitsNumber(marginalityContainer, totalCost - priceMotrum);
        }
      }
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".spetification_table");
  getMarginality(container);
});
