import {
  getClosestInteger,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

export function getMarginality(wrapper) {
  if (wrapper) {
    const spetificationItems = wrapper.querySelectorAll(".item_container");
    spetificationItems.forEach((item) => {
      const quantityInput = item.querySelector(".input-quantity");
      const discountInput = item.querySelector(".discount-input");

      const priceOne = +getCurrentPrice(item.getAttribute("data-price"));
      let totalCost;
      if (!discountInput) {
        totalCost = +quantityInput.value * priceOne;
      } else {
        totalCost =
          ((+quantityInput.value * priceOne) / 100) *
          (100 - discountInput.value);
      }
      const marginalityContainer = item.querySelector(".marginality");
      const motrumSalePersent = item.querySelector(".motrum_sale_persent");
      if (motrumSalePersent) {
        const marginality =
          (totalCost / 100) * +getCurrentPrice(motrumSalePersent.textContent);
        getDigitsNumber(marginalityContainer, marginality);
      }
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".spetification_table");
  getMarginality(container);
});
