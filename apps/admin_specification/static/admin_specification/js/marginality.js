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
        if (discountInput.value == "-") {
          totalCost = +quantityInput.value * priceOne;
        } else {
          totalCost =
            +quantityInput.value *
            ((priceOne / 100) * (100 - discountInput.value)).toFixed(2);
        }
      }
      const marginalityContainer = item.querySelector(".marginality");
      const marginality = totalCost - priceMotrum;

      getDigitsNumber(marginalityContainer, marginality);
      // if ((marginalityContainer.textContent = "-0,00")) {
      //   marginalityContainer.textContent = "0,00";
      // }
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".spetification_table");
  getMarginality(container);
});
