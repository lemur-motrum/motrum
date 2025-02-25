window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".about_container");
  if (wrapper) {
    const clientSliderContainer = wrapper.querySelector(
      ".company_photo_client_swiper"
    );
    const companySliderContainer = wrapper.querySelector(
      ".employees_photo_swiper"
    );

    if (clientSliderContainer) {
      const slider = new Swiper(".company_photo_client_swiper", {
        slidesPerView: "auto",
      });
      const slider2 = new Swiper(
        ".company_photo_client_swiper_overlay_slider",
        {}
      );

      const sliderElems = document.querySelectorAll(
        ".company_photo_client_swiper_slide"
      );

      const overlay = clientSliderContainer.querySelector(
        ".company_photo_client_swiper_overlay"
      );
      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        el.onclick = () => {
          overlay.classList.add("show");
          setTimeout(() => {
            overlay.classList.add("visible");
          }, 600);
          slider2.activeIndex = i;
          document.body.style.overflowY = "hidden";
        };

        closeBtn.onclick = () => {
          overlay.classList.remove("visible");
          setTimeout(() => {
            overlay.classList.remove("show");
          }, 600);
          document.body.style.overflowY = "scroll";
        };
      });
    }

    if (companySliderContainer) {
      const slider = new Swiper(".employees_photo_swiper", {
        slidesPerView: "auto",
      });
      const slider1 = new Swiper(".employees_photo_swiper_overlay_slider", {});

      const sliderElems = document.querySelectorAll(
        ".employees_photo_swiper_slide"
      );

      const overlay = companySliderContainer.querySelector(
        ".employees_photo_swiper_overlay"
      );
      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        el.onclick = () => {
          overlay.classList.add("show");
          setTimeout(() => {
            overlay.classList.add("visible");
          }, 600);
          slider1.activeIndex = i;
          document.body.style.overflowY = "hidden";
        };

        closeBtn.onclick = () => {
          overlay.classList.remove("visible");
          setTimeout(() => {
            overlay.classList.remove("show");
          }, 600);
          document.body.style.overflowY = "scroll";
        };
      });
    }
  }
});
