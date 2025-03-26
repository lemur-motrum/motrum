window.addEventListener("DOMContentLoaded", () => {
  const markingContentElem = document.querySelector(".marking_content_elem");
  if (markingContentElem) {
    const leftVector = markingContentElem.querySelector(".left");
    const rightVector = markingContentElem.querySelector(".rigth");

    markingContentElem.onmouseover = () => {
      leftVector.classList.add("animate");
      rightVector.classList.add("animate");
    };

    markingContentElem.onmouseout = () => {
      leftVector.classList.remove("animate");
      rightVector.classList.remove("animate");
    };
  }
});
