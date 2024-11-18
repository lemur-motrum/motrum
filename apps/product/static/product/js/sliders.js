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

  const smallImgSwiperElems = document.querySelectorAll(".small_img");
  if (smallImgSwiperElems.length > 0) {
    smallImgSwiperElems[0].classList.add("active");

    smallImgSwiperElems.forEach((el, i) => {
      el.onclick = () => {
        smallImgSwiperElems.forEach((elem) => {
          elem.classList.remove("active");
        });
        smallImgSwiperElems[i].classList.add("active");
      };
    });
  }
  const productOneSwiper = new Swiper(".small_img_container", {
    slidesPerView: "auto",
  });

  const productOneSwiperBigImg = new Swiper(".big_img", {
    slidesPerView: "auto",
    on: {
      slideChange: function () {
        if (smallImgSwiperElems.length > 0) {
          smallImgSwiperElems.forEach((el) => {
            el.classList.remove("active");
          });
          smallImgSwiperElems[this.realIndex].classList.add("active");
        }
      },
    },
    thumbs: {
      swiper: productOneSwiper,
    },
  });
});
