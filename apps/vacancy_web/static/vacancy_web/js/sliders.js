window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".vacancy_container");
  if (wrapper) {
    const companySliderWrapper = wrapper.querySelector(
      ".vacancy_company_slider"
    );
    if (companySliderWrapper) {
      const slider = new Swiper(".vacancy_company_slider", {
        slidesPerView: "auto",
      });
    }
  }
});
