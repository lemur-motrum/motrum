window.addEventListener("DOMContentLoaded", () => {
  const markingContentElem = document.querySelector(".marking_content_elem");
  const cobotsContentElem = document.querySelector(".cobots_content_elem");

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

  if (cobotsContentElem) {
    const downVector = cobotsContentElem.querySelector(".down");

    cobotsContentElem.onmouseover = () => {
      downVector.classList.add("animate");
    };

    cobotsContentElem.onmouseout = () => {
      downVector.classList.remove("animate");
    };
  }
});
