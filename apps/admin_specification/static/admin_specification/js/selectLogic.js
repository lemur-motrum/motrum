import { version } from "/static/core/js/scripts/version.js";

const { ItcCustomSelect } = await import(
  `/static/core/js/customSelect.js?ver=${version}`
);

window.addEventListener("DOMContentLoaded", () => {
  const select1 = new ItcCustomSelect("#select-1");
  const select2 = new ItcCustomSelect("#select-2");
  const select3 = new ItcCustomSelect("#select-3");
});
