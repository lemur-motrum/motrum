window.addEventListener("DOMContentLoaded", () => {
  const indexPageContainer = document.querySelector(".head-page-container");
  if (indexPageContainer) {
    const projectsSlider = indexPageContainer.querySelector(".projects-slider");
    if (projectsSlider) {
      const swiper = new Swiper(".projects-slider", {
        loop: true,
        slidesPerView: "auto",
        navigation: {
          nextEl: ".swiper-button-next",
          prevEl: ".swiper-button-prev",
        },
      });
    }
  }
});
