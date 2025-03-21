window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".solution_one_container");
  if (wrapper) {
    const overlay = wrapper.querySelector(".anchor_overlay");
    const form = wrapper.querySelector(".demo-form-container");

    const anchorButtons = wrapper.querySelectorAll(".title-link");
    anchorButtons.forEach((anchorButton) => {
      anchorButton.onclick = () => showOverlay();
    });

    const formHeight = form.clientHeight;
    const initPosition = form.offsetTop;

    console.log("formHeight", formHeight);
    console.log("initPosition", initPosition);

    function showOverlay() {
      overlay.classList.add("show");
      setTimeout(() => {
        overlay.classList.add("visible");
      });
    }

    document.onscroll = () => {
      if (overlay.classList.contains("show")) {
        const formPosition = form.getBoundingClientRect().top;
        console.log("formPosition", formPosition);

        console.log("result", -(initPosition + formHeight / 2));
        if (
          formPosition - initPosition >= -formHeight * 2 ||
          formPosition <= -formHeight / 2
        ) {
          closeOverlay();
        }
      }
    };

    function closeOverlay() {
      overlay.classList.remove("visible");
      setTimeout(() => {
        overlay.classList.remove("show");
      });
    }
  }
});
