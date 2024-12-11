window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".products_wrapper");
  if (wrapper) {
    const filterElemsWrapper = wrapper.querySelector(".supplier_content");
    const showBtn = wrapper.querySelector(".suppliers_add_more_btn");
    if (showBtn) {
      showBtn.onclick = () => {
        filterElemsWrapper.classList.add("is_open");
        showBtn.style.display = "none";
      };
    }
  }
});
