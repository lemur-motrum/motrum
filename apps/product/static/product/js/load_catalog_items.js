import { version } from "/static/core/js/scripts/version.js";

const { getCookie } = await import(
  `/static/core/js/functions.js?ver=${version}`
);
