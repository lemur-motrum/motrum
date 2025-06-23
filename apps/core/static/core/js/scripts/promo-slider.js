window.addEventListener("DOMContentLoaded", () => {
  const sliderItemsTwo = document.querySelector(".motrum-promosilder-two");
  if (sliderItemsTwo) {
    const promoSliderLeft = new Swiper(".motrum-promoslider-one", {});
    const promoSliderRigth = new Swiper(".motrum-promosilder-two", {
      navigation: {
        nextEl: ".nav_next",
        prevEl: ".nav_prew",
      },
      thumbs: {
        swiper: promoSliderLeft,
      },
      autoplay: {
        delay: 10000,
      },
      on: {
        slideChange: function (swiper) {
          let activeIndex = swiper.realIndex;
          const videos = sliderItemsTwo.querySelectorAll("video");
          videos.forEach((video, index) => {
            if (index === activeIndex) {
              video.play();
            } else {
              video.pause();
              video.currentTime = 0;
            }
          });
        },
      },
    });
  }
});
