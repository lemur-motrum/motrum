import {
  NumberParser,
  getDigitsNumber,
  getCurrentPrice,
} from "/static/core/js/functions.js";

// ставит маржинальность в конкретных товарх корзина окт
export function getMarginality(wrapper) {
  if (wrapper) {
    const spetificationItems = wrapper.querySelectorAll(".item_container");
    spetificationItems.forEach((item) => {
      const quantityInput = item.querySelector(".input-quantity");
      const discountInput = item.querySelector(".discount-input");
      const marjinInput = item.querySelector(".marja-input");
      const priceMotrum = new NumberParser("ru").parse(
        item.querySelector(".price_motrum").textContent
      );
      const priceOne = +getCurrentPrice(item.getAttribute("data-price"));
      const priceOneMotrum = +getCurrentPrice(item.getAttribute("data-price-motrum"));
      const marginalityPercentContainer = item.querySelector(
        ".marginality-persent"
      );
      const clientPrice = new NumberParser("ru").parse(
        item.querySelector(".total_cost").textContent
      );
      console.log("clientPrice26",clientPrice)

      let marginalityPercentValue;
      let totalCost;
      console.log("++++++++++++++++++++++++++++++++++++++++") 
      console.log(item.querySelector(".price_once").textContent) 
      if (!discountInput.value & !marjinInput.value) {
        console.log("!discountInput.value & !marjinInput.value")
        totalCost = +quantityInput.value * priceOne;
        marginalityPercentValue =
          ((clientPrice - priceMotrum) / clientPrice) * 100;
      } else {
        if (discountInput.value == "-") {
          console.log("discountInput.value == ")
          totalCost = +quantityInput.value * priceOne;
          marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
          // (100 * clientPrice * +quantityInput.value) /
          //   (+quantityInput.value * priceMotrum) -
          // 100;
        } 
        else if(discountInput.value != 0 & discountInput.value != ""){
          console.log("discountInput.value != 0 & discountInput.value !=")
          console.log(+quantityInput.value)
          console.log( discountInput.value)
          console.log(clientPrice)
          console.log(priceMotrum)
          totalCost =
            +quantityInput.value *
            ((priceOne / 100) * (100 - discountInput.value)).toFixed(2);
            console.log(totalCost)
          marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
            console.log("marginalityPercentValue discountInput",marginalityPercentValue)
            console.log("totalCost discountInput",totalCost)
          // (clientPrice * +quantityInput.value * 100) /
          //   (+quantityInput.value * priceMotrum) -
          // 100;
        }
        else if(marjinInput.value != 0 & marjinInput.value != ""){
          console.log("marjinInput.value != 0 & marjinInput.value != ")
          const marjinValue = +marjinInput.value;
          let oneProduct = (priceOneMotrum/ ((100 - +marjinInput.value)/100))
          totalCost = (+quantityInput.value *oneProduct).toFixed(2);
          marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
            
        }
        else {
         console.log("============================") 
         totalCost = +quantityInput.value * priceOne;
         marginalityPercentValue =
            ((clientPrice - priceMotrum) / clientPrice) * 100;
        }
      }
      const marginalityContainer = item.querySelector(".marginality");
      const marginality = totalCost - priceMotrum;

      console.log("clientPrice",clientPrice)
      console.log("totalCost",totalCost)
      console.log("priceMotrum",priceMotrum)
      console.log("marginality",marginality)
      console.log("marginalityPercentValue",marginalityPercentValue)

      marginalityPercentContainer.textContent = isNaN(marginalityPercentValue)
        ? "0,00"
        : marginalityPercentValue.toFixed(2);
       getDigitsNumber(marginalityContainer, marginality);
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  console.log("window.addEventListener(DOMContentLoadedspetificationTable)")
  const container = document.querySelector(".spetification_table");
  getMarginality(container);
});
