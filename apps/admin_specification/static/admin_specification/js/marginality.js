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
      const priceOne = +getCurrentPrice(item.getAttribute("data-price"));
      const totalCost = +quantityInput.value * priceOne;
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
