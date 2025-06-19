import { ItcCustomSelect } from "/static/core/js/customSelect.js";

window.addEventListener("DOMContentLoaded", () => {
  if (document.querySelector("#select-1")) {
    const select1 = new ItcCustomSelect("#select-1");
  }
  if (document.querySelector("#select-1-second")) {
    const select1Second = new ItcCustomSelect("#select-1-second");
  }
  if (document.querySelector("#select-2")) {
    const select2 = new ItcCustomSelect("#select-2");
  }
  if (document.querySelector("#select-4")) {
    const select4 = new ItcCustomSelect("#select-4");
  }

  const select3 = new ItcCustomSelect("#select-3");

  const toggleSelects = document.querySelectorAll(
    ".vendor_select__toggle_change"
  );
  if (toggleSelects.length > 0) {
    toggleSelects.forEach((el, i) => {
      const select = new ItcCustomSelect(`#vendor_toggle_select-${i + 1}`);
    });
  }
  
});
