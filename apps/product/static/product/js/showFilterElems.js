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

    const mobileFilterBtn = wrapper.querySelector(".mobile_filter_button");
    const filtersContainer = wrapper.querySelector(".filter_container");
    const closeBtn = filtersContainer.querySelector(".close_filter_elem_btn");
    const burgerNavMenu = document.querySelector(".burger_menu_nav");
    const supplierContent = filtersContainer.querySelector(".supplier_content");
    const supplierBtn = filtersContainer.querySelector(
      ".suppliers_add_more_btn"
    );

    mobileFilterBtn.onclick = () => {
      document.body.style.overflow = "hidden";
      filtersContainer.classList.add("show");
      burgerNavMenu.style.zIndex = -1;
    };

    closeBtn.onclick = () => {
      filtersContainer.classList.remove("show");
      if (supplierContent) {
        supplierContent.classList.remove("is_open");
      }
      if (supplierBtn) {
        supplierBtn.style.display = "flex";
      }
      document.body.style.overflow = "auto";
      burgerNavMenu.style.zIndex = 1001;
    };
  }
});
