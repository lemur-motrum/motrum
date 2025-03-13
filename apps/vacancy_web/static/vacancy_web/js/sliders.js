window.addEventListener("DOMContentLoaded", () => {
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

      const slider1 = new Swiper(".vacancy_company_slider_overlay_slider", {
        slidesPerView: "auto",
      });

      const sliderElems = companySliderWrapper.querySelectorAll(".photo-slide");

      const overlay = companySliderWrapper.querySelector(
        ".vacancy_company_slider_overlay"
      );

      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        if (window.innerWidth > 576) {
          el.onclick = () => {
            overlay.classList.add("show");
            setTimeout(() => {
              overlay.classList.add("visible");
            }, 600);
            slider1.activeIndex = i;
            document.body.style.overflowY = "hidden";
          };
        }
      });

      closeBtn.onclick = () => {
        overlay.classList.remove("visible");
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
        document.body.style.overflowY = "scroll";
      };
    }
    if (learningSliderWrapper) {
      const slider = new Swiper(".learnig_slider", {
        slidesPerView: "auto",
      });

      const slider1 = new Swiper(".learning_slider_overlay_slider", {
        slidesPerView: "auto",
      });
      const sliderElems = learningSliderWrapper.querySelectorAll(
        ".photo_education_elem_img_container"
      );

      const overlay = learningSliderWrapper.querySelector(
        ".learning_slider_overlay"
      );
      const closeBtn = overlay.querySelector(".close_btn");

      sliderElems.forEach((el, i) => {
        if (window.innerWidth > 576) {
          el.onclick = () => {
            overlay.classList.add("show");
            setTimeout(() => {
              overlay.classList.add("visible");
            }, 600);
            slider1.activeIndex = i;
            document.body.style.overflowY = "hidden";
          };
        }
      });

      closeBtn.onclick = () => {
        overlay.classList.remove("visible");
        setTimeout(() => {
          overlay.classList.remove("show");
        }, 600);
        document.body.style.overflowY = "scroll";
      };
    }
  }
});
