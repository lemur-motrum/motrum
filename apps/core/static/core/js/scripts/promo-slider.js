window.addEventListener("DOMContentLoaded", () => {
  const promoSliderLeft = new Swiper(".motrum-promoslider-one", {
    // slidesPerView: "auto",
  });

  const promoSliderRigth = new Swiper(".motrum-promosilder-two", {
    navigation: {
      nextEl: ".nav_next",
      prevEl: ".nav_prew",
    },
    thumbs: {
      swiper: promoSliderLeft,
    },
  });
});
