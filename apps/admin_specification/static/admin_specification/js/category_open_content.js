window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".categories-container");
  if (wrapper) {
    const elems = wrapper.querySelectorAll(".category");
    const addMoreBtn = wrapper.querySelector(".category_show_container");
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
});
