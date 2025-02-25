import { getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const currentUrl = new URL(window.location.href);
  const csrfToken = getCookie("csrftoken");
  const urlParams = currentUrl.searchParams;

  const wrapper = document.querySelector(".vacancy_container");
  const catalogContainer = wrapper.querySelector('[project-elem="container"]');

  if (wrapper) {
    const companySliderWrapper = wrapper.querySelector(
      ".vacancy_company_slider"
    );
    const learningSliderWrapper = wrapper.querySelector(".learnig_slider");
    if (companySliderWrapper) {
      const slider = new Swiper(".vacancy_company_slider", {
        slidesPerView: "auto",
      });
    }
    if (learningSliderWrapper) {
      const slider = new Swiper(".learnig_slider", {
        slidesPerView: "auto",
      });
    }

    fetch("/api/v1/vacancy/load-ajax-vacancy-list/", {
      method: "GET",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json(Text))
      .then((response) => {
        if (response.data.length > 0) {
          for (let i in response.data) {
            addAjaxCatalogItem(response.data[i]);
          }
        }
      });
  }

  function renderCatalogItem(orderData) {
    let ajaxTemplateWrapper = document.querySelector(
      '[template-elem="wrapper"]'
    );
    let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
      '[vacancy-elem="vacancy-item"]'
    ).innerText;

    return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
  }

  function addAjaxCatalogItem(ajaxElemData) {
    let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
    catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
  }
});
