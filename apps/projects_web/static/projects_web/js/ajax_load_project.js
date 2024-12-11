import { getCookie } from "/static/core/js/functions.js";

const currentUrl = new URL(window.location.href);
const urlParams = currentUrl.searchParams;

window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".projects_wrapper");
  if (wrapper) {
    const loader = wrapper.querySelector(".loader");
    const smallLoader = wrapper.querySelector(".small_loader");
    const endContent = wrapper.querySelector(".end_content");
    const noneContentText = wrapper.querySelector(".none_content_data");
    const catalogButton = endContent.querySelector('[catalog-elem="button"]');
    const pagination = wrapper.querySelector(".pagination");
    const paginationElems = pagination.querySelectorAll(".elem");
    const paginationFirstElem = pagination.querySelector(".first");
    const paginationLastElem = pagination.querySelector(".last");
    const firstDots = pagination.querySelector(".first_dots");
    const lastDots = pagination.querySelector(".last_dots");
    const btn = wrapper.querySelector(".add_more");
    const catalogContainer = wrapper.querySelector(
      '[project-elem="container"]'
    );

    const markingCategoryWrapper = wrapper.querySelector(".marking_category");
    const clientCategoryWrapper = wrapper.querySelector(".clients_category");
    const categoryProjectsSlider = wrapper.querySelector(".category_projects");
    const sliderWrapper =
      categoryProjectsSlider.querySelector(".swiper-wrapper");
    const categriesElems = sliderWrapper.querySelectorAll(
      ".category_project_slide_elem"
    );
    const allCategoriesElem = sliderWrapper.querySelector(
      ".all_categories_elem"
    );

    let pageCount = 0;
    let projectsCount = 0;
    let lastPage = 0;

    let categoryProjectSlug;
    let clientCategoryProjectArray = [];
    let categoryProjectMarkingArray = [];

    function getActivePaginationElem() {
      for (let i = 0; i < paginationElems.length; i++) {
        if (paginationElems[i].textContent == pageCount + 1) {
          paginationElems[i].classList.add("active");
        } else {
          paginationElems[i].classList.remove("active");
        }
      }
      showFirstPaginationElem();
    }

    function showFirstPaginationElem() {
      if (pageCount >= 2) {
        paginationFirstElem.classList.add("show");
        firstDots.classList.add("show");
      } else {
        paginationFirstElem.classList.remove("show");
        firstDots.classList.remove("show");
      }
      if (pageCount >= 0 && pageCount < 4) {
        if (pageCount >= lastPage - 3) {
          paginationLastElem.classList.remove("show");
          lastDots.classList.remove("show");

          if (pageCount >= lastPage - 1) {
            paginationElems[2].style.display = "none";
            if (paginationElems[1].textContent == "") {
              paginationElems[1].style.display = "none";
            } else {
              paginationElems[1].style.display = "flex";
            }
          } else {
            if (paginationElems[1].textContent == "") {
              paginationElems[1].style.display = "none";
            } else {
              paginationElems[1].style.display = "flex";
            }
            if (paginationElems[2].textContent == "") {
              paginationElems[2].style.display = "none";
            } else {
              paginationElems[2].style.display = "flex";
            }
          }
        } else {
          paginationElems[2].style.display = "flex";
          paginationLastElem.classList.add("show");
          lastDots.classList.add("show");
        }
      } else {
        if (pageCount >= lastPage - 2) {
          paginationLastElem.classList.remove("show");
          lastDots.classList.remove("show");

          if (pageCount >= lastPage - 1) {
            paginationElems[2].style.display = "none";
          } else {
            paginationElems[2].style.display = "flex";
          }
        } else {
          paginationLastElem.classList.add("show");
          lastDots.classList.add("show");
        }
      }
    }

    function loadItems(addMoreBtn = false) {
      let data = {
        count: projectsCount,
        page: pageCount,
        addMoreBtn: addMoreBtn ? true : false,
        category_project: categoryProjectSlug ? categoryProjectSlug : "",
        client_category_project:
          clientCategoryProjectArray.length !== 0 && clientCategoryProjectArray
            ? clientCategoryProjectArray
            : "",
        category_project_marking:
          categoryProjectMarkingArray.length !== 0 &&
          categoryProjectMarkingArray
            ? categoryProjectMarkingArray
            : "",
      };

      let params = new URLSearchParams(data);
      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/project/load-ajax-project-list/?${params.toString()}`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then(function (data) {
          if (data.data.length == 0) {
            loader.classList.add("hide");
            noneContentText.classList.add("show");
          } else {
            lastPage = +data.count;
            const paginationArray = [];
            paginationLastElem.textContent = `${lastPage}`;
            loader.classList.add("hide");
            endContent.classList.add("show");
            smallLoader.classList.remove("show");
            for (let i in data.data) {
              addAjaxCatalogItem(data.data[i]);
            }
            if (data.next) {
              catalogButton.disabled = false;
            } else {
              catalogButton.disabled = true;
            }
            for (
              let i = pageCount == 0 ? pageCount : pageCount - 1;
              !data.small
                ? i < pageCount + 3
                : +data.count > 1
                ? i <= pageCount + 1
                : i <= pageCount;
              i++
            ) {
              paginationArray.push(i);
            }

            paginationElems.forEach((el) => (el.textContent = ""));
            paginationArray.forEach((el, i) => {
              if (paginationElems[i]) {
                paginationElems[i].textContent = +el + 1;
              }
            });
            loader.classList.add("hide");
            urlParams.set("page", pageCount + 1);
            getActivePaginationElem();
          }
          history.pushState({}, "", currentUrl);
        });
    }

    window.onload = () => {
      const pageGetParam = urlParams.get("page");
      const industryGetParam = urlParams.get("industry");
      const categoryGetParam = urlParams.get("category_project");
      const markingGetParam = urlParams.get("marking");
      if (pageGetParam) {
        pageCount = +pageGetParam - 1;
        projectsCount = pageCount * 10;
      }
      if (industryGetParam) {
        const arrayIndustryParams = industryGetParam.split(",");
        const industryElems =
          clientCategoryWrapper.querySelectorAll(".category_elem");
        const industryHeightContainer = clientCategoryWrapper.querySelector(
          ".category_elem_container_max_height"
        );
        arrayIndustryParams.forEach((param) => {
          for (let i = 0; i < industryElems.length; i++) {
            if (industryElems[i].getAttribute("param") == param) {
              industryElems[i].classList.add("active");
              industryHeightContainer.prepend(industryElems[i]);
            }
          }
        });

        clientCategoryProjectArray = arrayIndustryParams;
      }
      if (categoryGetParam) {
        categoryProjectSlug = categoryGetParam;

        categriesElems.forEach((el) => {
          if (el.getAttribute("slug") == categoryGetParam) {
            allCategoriesElem.classList.remove("active");
            el.classList.add("active");
            sliderWrapper.prepend(el);
          }
        });
      }
      if (markingGetParam) {
        const arrayMarkingParams = markingGetParam.split(",");
        categoryProjectMarkingArray = arrayMarkingParams;

        const markingElems =
          markingCategoryWrapper.querySelectorAll(".category_elem");
        const markingHeightContainer = markingCategoryWrapper.querySelector(
          ".category_elem_container_max_height"
        );

        arrayMarkingParams.forEach((param) => {
          for (let i = 0; i < markingElems.length; i++) {
            if (markingElems[i].getAttribute("param") == param) {
              markingElems[i].classList.add("active");
              markingHeightContainer.prepend(markingElems[i]);
            }
          }
        });
      }
      if (categoryProjectSlug == "markirovka-chestnyij-znak") {
        markingCategoryWrapper.classList.add("show");
      } else {
        markingCategoryWrapper.classList.remove("show");
        urlParams.delete("marking");
        categoryProjectMarkingArray = "";
      }

      loadItems();
    };

    paginationElems.forEach((elem) => {
      if (!elem.classList.contains("active")) {
        elem.onclick = () => {
          pageCount = +elem.textContent - 1;
          projectsCount = pageCount * 10;
          preLoaderLogic();
          loadItems(true);
        };
      }
    });

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      projectsCount = 0;
      preLoaderLogic();
      loadItems(true);
    };

    catalogButton.onclick = () => {
      projectsCount += 10;
      +pageCount++;
      noneContentText.classList.remove("show");
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems(true);
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      projectsCount = pageCount * 10;
      preLoaderLogic();
      loadItems(true);
    };

    categriesElems.forEach((elem) => {
      elem.onclick = () => {
        const slug = elem.getAttribute("slug");
        sliderWrapper.style.transform = "translate3d(0px, 0px, 0px)";
        if (slug) {
          if (!elem.classList.contains("active")) {
            for (let i = 0; i < categriesElems.length; i++) {
              categriesElems[i].classList.remove("active");
            }
            allCategoriesElem.classList.remove("active");
            elem.classList.add("active");
            sliderWrapper.prepend(elem);
            urlParams.set("category_project", slug);
            categoryProjectSlug = slug;
            if (categoryProjectSlug == "markirovka-chestnyij-znak") {
              markingCategoryWrapper.classList.add("show");
            } else {
              markingCategoryWrapper.classList.remove("show");
              urlParams.delete("marking");
              categoryProjectMarkingArray = "";
            }
          } else {
            elem.classList.remove("active");
            allCategoriesElem.classList.add("active");
            sliderWrapper.prepend(allCategoriesElem);
            categoryProjectSlug = "";
            urlParams.delete("category_project");
          }
        } else {
          for (let i = 0; i < categriesElems.length; i++) {
            categriesElems[i].classList.remove("active");
          }
          allCategoriesElem.classList.add("active");
          sliderWrapper.prepend(allCategoriesElem);
          categoryProjectSlug = "";
          urlParams.delete("category_project");
          urlParams.delete("marking");
          categoryProjectMarkingArray = "";
        }
        preLoaderLogic();
        pageCount = 0;
        projectsCount = 0;
        loadItems(true);

        if (categoryProjectSlug == "markirovka-chestnyij-znak") {
          markingCategoryWrapper.classList.add("show");
        } else {
          markingCategoryWrapper.classList.remove("show");
          urlParams.delete("marking");
          categoryProjectMarkingArray = "";
        }
      };
    });

    filterLogic(clientCategoryWrapper, clientCategoryProjectArray);
    filterLogic(markingCategoryWrapper, categoryProjectMarkingArray, true);

    function preLoaderLogic() {
      loader.classList.remove("hide");
      catalogContainer.innerHTML = "";
      noneContentText.classList.remove("show");
      endContent.classList.remove("show");
    }

    function filterLogic(wrapper, array, marking = false) {
      openAllFilterElems(wrapper);
      const heigtContainer = wrapper.querySelector(
        ".category_elem_container_max_height"
      );
      const categoryElems = wrapper.querySelectorAll(".category_elem");

      categoryElems.forEach((elem) => {
        elem.onclick = () => {
          elem.classList.toggle("active");
          const filterParam = elem.getAttribute("param");
          if (elem.classList.contains("active")) {
            heigtContainer.prepend(elem);
            array.push(filterParam);
            const filterString = urlParams.get(
              marking ? "marking" : "industry"
            );
            if (filterString) {
              urlParams.set(marking ? "marking" : "industry", array.join());
            } else {
              urlParams.set(marking ? "marking" : "industry", array.join(","));
            }
            preLoaderLogic();
            pageCount = 0;
            marking
              ? (categoryProjectMarkingArray = array)
              : (clientCategoryProjectArray = array);
            loadItems();
          } else {
            const activeClientsCatigoriesElems =
              heigtContainer.querySelectorAll(".active");
            if (
              activeClientsCatigoriesElems[
                activeClientsCatigoriesElems.length - 1
              ]
            ) {
              activeClientsCatigoriesElems[
                activeClientsCatigoriesElems.length - 1
              ].after(elem);
            }
            const filteredParamsArray = array.filter((el) => el != filterParam);
            array = filteredParamsArray;
            preLoaderLogic();
            if (filteredParamsArray.length == 0) {
              urlParams.delete(marking ? "marking" : "industry");
            } else {
              urlParams.set(marking ? "marking" : "industry", array.join());
            }
            marking
              ? (categoryProjectMarkingArray = array)
              : (clientCategoryProjectArray = array);
            loadItems();
          }
        };
      });
    }

    function renderCatalogItem(orderData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[project-elem="project-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      catalogContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }

    function openAllFilterElems(filterWrapper) {
      const clientCategoryContainer = filterWrapper.querySelector(
        ".category_elem_container"
      );
      const addMoreBtn = filterWrapper.querySelector(".filters_add_more_btn");
      addMoreBtn.onclick = () => {
        clientCategoryContainer.classList.add("is_open");
        addMoreBtn.classList.add("hide");
      };
    }
  }
});
