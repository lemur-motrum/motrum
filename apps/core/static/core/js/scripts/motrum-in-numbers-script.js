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
        const numberPlusContainer = el.querySelector(".plus_block");
        const quantityContainer = el.querySelector(".quantity");
        const currentQuantity = quantityContainer.getAttribute("data-quantity");
        let count = 0;
        const posTop = container.getBoundingClientRect().top;
        const intervalTime = 1500 / +currentQuantity;
        if (
          posTop + container.clientHeight <= window.innerHeight &&
          posTop >= 0
        ) {
          const interval = setInterval(() => {
            quantityContainer.textContent = (+count).toLocaleString("ru");
            if (+currentQuantity > 500) {
              count += Math.ceil(+currentQuantity / 499);
            } else {
              count += 1;
            }
            if (count >= +currentQuantity) {
              quantityContainer.textContent = (+currentQuantity).toLocaleString(
                "ru"
              );
              if (numberPlusContainer) {
                numberPlusContainer.classList.add("show_plus");
              }
              clearInterval(interval);
            }
          }, intervalTime);
          window.removeEventListener("scroll", onScroll);
        }
      });
    }
  }
});
