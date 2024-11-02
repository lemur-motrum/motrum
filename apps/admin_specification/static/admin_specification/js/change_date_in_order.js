export function changeDateInOrder(container) {
  if (container) {
    const specificationItems = container.querySelectorAll(".item_container");
    specificationItems.forEach((specificationItem) => {
      const quantityInput = specificationItem.querySelector(".input-quantity");
      const supplierUnit = specificationItem.querySelector(".supplier_unit");
      const motrumUnit = specificationItem.querySelector(".motrum_unit");
      const calendar = specificationItem.querySelector(".delivery_date");
      const minusButton = specificationItem.querySelector(".minus-button");
      const plusButton = specificationItem.querySelector(".plus-button");

      const setCalendarValue = (day) => {
        const currentDate = new Date();
        currentDate.setDate(currentDate.getDate() + day);
        const date = currentDate.toISOString().slice(0, 10);
        console.log(date);
        return date;
      };
      const getDateInCalendar = () => {
        if (+quantityInput.value <= +motrumUnit.textContent) {
          calendar.value = setCalendarValue(7);
        } else if (
          +quantityInput.value > +motrumUnit.textContent &&
          +quantityInput.value <= +supplierUnit.textContent
        ) {
          calendar.value = setCalendarValue(14);
        } else {
          calendar.value = "";
        }
      };
      getDateInCalendar();
    });
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const specificationItemsWrapper = document.querySelector(
    ".spetification_table"
  );
  changeDateInOrder(specificationItemsWrapper);
});
