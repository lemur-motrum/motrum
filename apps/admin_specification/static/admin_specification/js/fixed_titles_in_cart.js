window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".spetification_table");
  if (wrapper) {
    const specificationTitlesWrapper = wrapper.querySelector(
      ".spetification_titles"
    );
    let deltaY;
    window.addEventListener("scroll", function () {
      deltaY = specificationTitlesWrapper.getBoundingClientRect().top;
      if (deltaY <= 0) {
        specificationTitlesWrapper.classList.add("fixed");
      }
      if (deltaY > 0) {
        specificationTitlesWrapper.classList.remove("fixed");
      }
    });
  }
});
