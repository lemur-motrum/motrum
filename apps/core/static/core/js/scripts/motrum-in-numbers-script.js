window.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".motrum_in_numbers-container");
  if (container) {
    const dynamicContentContainer = container.querySelector(
      ".dynamics_content-container"
    );
    const dynamicsElems = dynamicContentContainer.querySelectorAll(
      ".dynamics_content-elem"
    );
    window.addEventListener("scroll", onScroll);

    function onScroll() {
      dynamicsElems.forEach((el) => {
        const quantityContainer = el.querySelector(".quantity");
        const currentQuantity = quantityContainer.getAttribute("data-quantity");
        let count = 0;
        const posTop = container.getBoundingClientRect().top;
        if (
          posTop + container.clientHeight <= window.innerHeight &&
          posTop >= 0
        ) {
          const interval = setInterval(() => {
            quantityContainer.textContent = +count;
            count += 1;
            if (count == +currentQuantity) {
              quantityContainer.textContent = +count;
              clearInterval(interval);
            }
          }, 0.5);
          window.removeEventListener("scroll", onScroll);
        }
      });
    }
  }
});
