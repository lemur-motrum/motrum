window.addEventListener("DOMContentLoaded", () => {
  const categorySwiper = new Swiper(".site_categories_container", {
    slidesPerView: "auto",
    navigation: {
      nextEl: ".slider-arrow",
    },
  });

  const groupSwiper = new Swiper(".site_groups_container", {
    slidesPerView: "auto",
    navigation: {
      nextEl: ".slider-arrow",
    },
  });
});
