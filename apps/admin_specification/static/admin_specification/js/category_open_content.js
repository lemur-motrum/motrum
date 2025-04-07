window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".categories-container");
  const groupWrapper = document.querySelector(".group-container");
  openContentLogic(wrapper);
  openContentLogic(groupWrapper);
  function openContentLogic(wrapper) {
    if (wrapper) {
      const elems = wrapper.querySelectorAll(".elem-container");
      const addMoreBtn = wrapper.querySelector(".add_more_elems_btn");
      if (addMoreBtn) {
        addMoreBtn.onclick = () => {
          addMoreBtn.classList.toggle("show");
          if (!addMoreBtn.classList.contains("show")) {
            let i = 0;
            const interval = setInterval(() => {
              i += 1;
              elems[i].style.display = "flex";
              if (i == elems.length - 1) {
                clearInterval(interval);
              }
            }, 25);
          } else {
            let i = elems.length;
            const interval = setInterval(() => {
              i -= 1;
              elems[i].style.display = "none";
              if (i == 5) {
                clearInterval(interval);
              }
            }, 25);
          }
        };
      }
    }
  }
});
