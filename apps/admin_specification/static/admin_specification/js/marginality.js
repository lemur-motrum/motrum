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
      const marginalityPercentContainer = item.querySelector(
        ".marginality-persent"
      );
      const clientPrice = new NumberParser("ru").parse(
        item.querySelector(".total_cost").textContent
      );

      let marginalityPercentValue;
      let totalCost;
      if (!discountInput.value) {
        totalCost = +quantityInput.value * priceOne;
        marginalityPercentValue =
          ((clientPrice - priceMotrum) / clientPrice) * 100;
      } else {
        if (discountInput.value == "-") {
          totalCost = +quantityInput.value * priceOne;
          marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
        } else {
          totalCost =
            +quantityInput.value *
            ((priceOne / 100) * (100 - discountInput.value)).toFixed(2);
          marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
        }
      }
      const marginalityContainer = item.querySelector(".marginality");
      const marginality = totalCost - priceMotrum;

      marginalityPercentContainer.textContent = isNaN(marginalityPercentValue)
        ? "0,00"
        : marginalityPercentValue.toFixed(2);
      getDigitsNumber(marginalityContainer, marginality);
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".spetification_table");
  getMarginality(container);
});
