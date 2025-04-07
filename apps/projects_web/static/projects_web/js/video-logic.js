window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".project_one_wrapper");
  if (wrapper) {
    const videoWrappers = wrapper.querySelectorAll(".project_video_elem");
    if (videoWrappers.length > 0) {
      videoWrappers.forEach((videoWrapper) => {
        const video = videoWrapper.querySelector("video");

        video.addEventListener("mouseover", function () {
          this.play();
        });
        video.addEventListener("mouseout", function () {
          this.pause();
          this.currentTime = 0;
        });
      });
    }
  }
});
