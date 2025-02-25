import { getCookie } from "/static/core/js/functions.js";

window.addEventListener("DOMContentLoaded", () => {
  const currentUrl = new URL(window.location.href);
  const csrfToken = getCookie("csrftoken");
  const urlParams = currentUrl.searchParams;

  const wrapper = document.querySelector(".vacancy_container");
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

    fetch("/api/v1/project/load-ajax-vacancy-list/", {
      method: "GET",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((response) => console.log(response));
  }
});
