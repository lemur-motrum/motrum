window.addEventListener("DOMContentLoaded", () => {
  const btn1 = document.querySelector(".all-brands-btn");
  const btns2 = document.querySelectorAll(".title-link");
  const btn3 = document.querySelector(".suppliers_add_more_btn");
  const btns4 = document.querySelectorAll(".filters_add_more_btn");
  buttonArrowLogic(btn1);
  btns2.forEach((el) => {
    buttonArrowLogic(el);
  });
  buttonArrowLogic(btn3);
  btns4.forEach((el) => {
    buttonArrowLogic(el);
  });
});

function buttonArrowLogic(buttonWrapper) {
  if (buttonWrapper) {
    const arrow = buttonWrapper.querySelector(".arrow-container");
    buttonWrapper.onmouseover = () => {
      arrow.classList.add("swipe");
    };

    buttonWrapper.onmouseout = () => {
      if (arrow.classList.contains("swipe")) {
        arrow.classList.remove("swipe");
      }
    };
  }
}
