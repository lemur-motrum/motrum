window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".solution_one_container");
  if (wrapper) {
    const overlay = wrapper.querySelector(".anchor_overlay");
    const form = wrapper.querySelector(".demo-form-container");
    const anchorButtons = wrapper.querySelectorAll(".anchor_link");
    const formHeight = form.clientHeight;
    const initPosition = form.offsetTop;

    anchorButtons.forEach((anchorButton) => {
      anchorButton.onclick = () => showOverlay();
    });

    document.onscroll = () => {
      if (overlay.classList.contains("show")) {
        const formPosition = form.getBoundingClientRect().top;
        if (
          formPosition - initPosition >= -formHeight * 2 ||
          formPosition <= -formHeight / 2
        ) {
          closeOverlay();
        }
      }
    };

    function showOverlay() {
      overlay.classList.add("show");
      setTimeout(() => {
        overlay.classList.add("visible");
      });
    }

    function closeOverlay() {
      overlay.classList.remove("visible");
      setTimeout(() => {
        overlay.classList.remove("show");
      });
    }
  }
});
