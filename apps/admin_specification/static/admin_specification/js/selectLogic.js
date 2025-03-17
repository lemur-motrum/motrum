import { ItcCustomSelect } from "/static/core/js/customSelect.js";

window.addEventListener("DOMContentLoaded", () => {
  if (document.querySelector("#select-1")) {
    const select1 = new ItcCustomSelect("#select-1");
  }
  if (document.querySelector("#select-2")) {
    const select2 = new ItcCustomSelect("#select-2");
  }
  if (document.querySelector("#select-3")) {
    const select3 = new ItcCustomSelect("#select-3");
  }
});
