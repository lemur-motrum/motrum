window.addEventListener("DOMContentLoaded", () => {
  const categorySlider = new Swiper(".category_projects", {
    slidesPerView: "auto",
  });
  const projectOneSlider = new Swiper(".project_one_image_wrapper", {
    slidesPerView: "auto",
  });

  const projectOneSliderGallery = new Swiper(
    ".procject_one_image_wrapper_galery",
    {
      navigation: {
        nextEl: ".next_btn",
        prevEl: ".prev_btn",
      },
      loop: true,
    }
  );

  const productOneWrapper = document.querySelector(".project_one_wrapper");
  if (productOneWrapper) {
    const productOneSwiperItems = productOneWrapper.querySelectorAll(
      ".product_one_slider_elem"
    );
    const galleryWrapper = productOneWrapper.querySelector(
      ".procject_one_image_wrapper_galery_overlay"
    );
    const closeBtn = galleryWrapper.querySelector(".close_btn");

    productOneSwiperItems.forEach((el, i) => {
      el.onclick = () => {
        galleryWrapper.classList.add("show");
        setTimeout(() => {
          galleryWrapper.classList.add("visible");
        }, 600);
        if (window.innerWidth > 576) {
          document.body.style.overflowY = "hidden";
        }
        projectOneSliderGallery.realIndex = i;
      };
    });
    closeBtn.onclick = () => {
      galleryWrapper.classList.remove("visible");
      setTimeout(() => {
        galleryWrapper.classList.remove("show");
      }, 600);
      if (window.innerWidth > 576) {
        document.body.style.overflowY = "scroll";
      }
    };
  }
});
