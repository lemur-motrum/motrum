import { getCookie, showErrorValidation } from "/static/core/js/functions.js";
import { invoiceItem } from "../js/invoice_elems.js";
import { changePayment } from "../js/change_payment.js";
import { completeOrder } from "../js/complete_order.js";

let csrfToken = getCookie("csrftoken");

const currentUrl = new URL(window.location.href);

window.addEventListener("DOMContentLoaded", () => {
  const specificationWrapper = document.querySelector(
    '[specification-elem="wrapper"]'
  );
  if (specificationWrapper) {
    const allSpecifications = document.querySelector(
      ".all_specifications_table"
    );
    const specificationContainer = specificationWrapper.querySelector(
      '[specification-elem="container"]'
    );
    let specificationCount = 0;
    let pageCount = 0;
    let lastPage = 0;
    const loader = document.querySelector(".loader");
    const smallLoader = specificationWrapper.querySelector(".small_loader");
    const endContent = specificationWrapper.querySelector(".end_content");
    const catalogButton = endContent.querySelector('[project-elem="button"]');
    const pagination = endContent.querySelector(".pagination");
    const paginationElems = pagination.querySelectorAll(".elem");
    const paginationFirstElem = pagination.querySelector(".first");
    const paginationLastElem = pagination.querySelector(".last");
    const firstDots = pagination.querySelector(".first_dots");
    const lastDots = pagination.querySelector(".last_dots");

    function getActivePaginationElem() {
      for (let i = 0; i < paginationElems.length; i++) {
        if (paginationElems[i].textContent == pageCount + 1) {
          paginationElems[i].classList.add("active");
        } else {
          paginationElems[i].classList.remove("active");
        }
      }
      showFirstPagintationElem();
    }

    function showFirstPagintationElem() {
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

    function loadItems(
      pagintaionFn = false,
      cleanArray = false,
      addMoreBtn = false,
      specification = false
    ) {
      const IsFrame = document.getAttribute('data-http-frame')
      const BxIdOrder = document.getAttribute('data-bitrix-id-order')
      let data = {
        count: !pagintaionFn ? specificationCount : 0,
        page: pageCount,
        addMoreBtn: addMoreBtn ? true : false,
        specification: specification ? "+" : null,
      };
      let params = new URLSearchParams(data);
      
      fetch(
        `/api/v1/order/load-ajax-specification-list/?${params.toString()}`,
        {
          method: "GET",
          headers: {
            "X-CSRFToken": csrfToken,
            Accept: 'application/json',
          },
        }
      )
        .then((response) => response.json())
        .then(function (data) {
          loader.classList.add("hide");
          smallLoader.classList.remove("show");
          lastPage = +data.count;
          const pagintationArray = [];
          paginationLastElem.textContent = `... ${lastPage}`;
          if (data.count > 1) {
            endContent.classList.add("show");
          }
          for (let i in data.data) {
            addAjaxCatalogItem(data.data[i]);
            const currentSpecificatons =
              allSpecifications.querySelectorAll(".table_item");
            currentSpecificatons.forEach((item) => {
              const changeButton = item.querySelector(
                ".change-specification-button"
              );
              const changeBillButton = item.querySelector(
                ".change-bill-button"
              );
              const updateButton = item.querySelector(
                ".uptate-specification-button"
              );

              const specificationId = item.getAttribute("specification-id");
              const cartId = item.getAttribute("data-cart-id");

              if (changeButton) {
                uptadeOrChanegeSpecification(
                  changeButton,
                  null,
                  specificationId,
                  cartId
                );
              }
              if (updateButton) {
                uptadeOrChanegeSpecification(
                  updateButton,
                  null,
                  specificationId,
                  cartId
                );
              }
              if (changeBillButton) {
                uptadeOrChanegeSpecification(
                  changeBillButton,
                  "bill-upd=True",
                  specificationId,
                  cartId
                );
              }
            });
          }

          if (data.next) {
            catalogButton.disabled = false;
          } else {
            catalogButton.disabled = true;
          }

          for (
            let i = pageCount == 0 ? pageCount : pageCount - 1;
            !data.small
              ? i < pageCount + 2
              : +data.count > 1
              ? i <= pageCount + 1
              : i <= pageCount;
            i++
          ) {
            pagintationArray.push(i);
          }
          if (cleanArray) {
            paginationElems.forEach((elem) => {
              elem.textContent = "";
            });
          }
          paginationElems.forEach((el) => (el.textContent = ""));
          pagintationArray.forEach((el, i) => {
            if (paginationElems[i]) {
              paginationElems[i].textContent = +el + 1;
            }
          });

          getActivePaginationElem();
          invoiceItem(specificationContainer);
          changePayment(specificationContainer, showErrorValidation);
          completeOrder(specificationContainer);
          currentUrl.searchParams.set("page", pageCount + 1);
          history.pushState({}, "", currentUrl);
        });
    }

    window.onload = () => {
      const pageNumGetParam = currentUrl.searchParams.get("page");
      if (pageNumGetParam) {
        pageCount = +pageNumGetParam - 1;
        specificationCount = pageCount * 10;
        loadItems(false, false, false, false);
      } else {
        loadItems(false, false, false, false);
      }
    };

    paginationFirstElem.onclick = () => {
      pageCount = 0;
      preloaderLogic();
      loadItems(true, true, false, false);
    };
    paginationElems.forEach((elem) => {
      elem.onclick = () => {
        pageCount = +elem.textContent - 1;
        preloaderLogic();
        loadItems(false, false, false, false);
      };
    });

    catalogButton.onclick = () => {
      specificationCount += 10;
      +pageCount++;
      endContent.classList.remove("show");
      smallLoader.classList.add("show");
      loadItems(false, false, true, false);
    };

    paginationLastElem.onclick = () => {
      pageCount = lastPage - 1;
      preloaderLogic();
      loadItems(false, true, false, false);
    };

    function renderCatalogItem(orderData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[specification-elem="specification-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      specificationContainer.insertAdjacentHTML(
        "beforeend",
        renderCatalogItemHtml
      );
    }
    function preloaderLogic() {
      endContent.classList.remove("show");
      specificationContainer.innerHTML = "";
      loader.classList.remove("hide");
      specificationCount = pageCount * 10;
    }
    const allSpecificationsContainer = document.querySelector(
      ".all_specifications_container"
    );
    if (allSpecificationsContainer) {
      let currentUrl = new URL(window.location.href);

      const titles = allSpecificationsContainer.querySelector(".title");
      const ordersWithoutSpecification = titles.querySelector(
        ".orders_without_specifications"
      );
      const titleItems = titles.querySelectorAll("span");
      const smallAllSpecificationTitles =
        allSpecificationsContainer.querySelector(".all_specifications_titles");
      const smallNoSpecificationTitles =
        allSpecificationsContainer.querySelector(".no_specification_titles");
      const searchParams = currentUrl.searchParams;

      for (let i = 0; i < titleItems.length; i++) {
        titleItems[i].onclick = () => {
          if (!titleItems[i].classList.contains("active")) {
            titleItems[i].classList.add("active");
            if (titleItems[i - 1]) {
              titleItems[i - 1].classList.remove("active");
            } else {
              titleItems[i + 1].classList.remove("active");
            }
          } else {
            return;
          }

          if (ordersWithoutSpecification.classList.contains("active")) {
            searchParams.set("specification", "+");
            history.pushState({}, "", currentUrl);
            pageCount = 0;
            smallAllSpecificationTitles.classList.remove("show");
            smallNoSpecificationTitles.classList.add("show");
            preloaderLogic();
            loadItems(false, false, false, true);
          } else {
            searchParams.delete("specification");
            history.pushState({}, "", currentUrl);
            pageCount = 0;
            smallAllSpecificationTitles.classList.add("show");
            smallNoSpecificationTitles.classList.remove("show");
            preloaderLogic();
            loadItems(false, false, false, false);
          }
        };
      }
    }
  }
});

export function uptadeOrChanegeSpecification(
  button,
  getParams,
  idCart,
  idSpecification
) {
  button.onclick = () => {
    console.log(button);
    button.setAttribute("text-content", button.textContent);
    const typeSave = button.getAttribute("data-type-save");
    button.disabled = true;
    button.textContent = "";
    button.innerHTML = "<div class='small_loader'></div>";
    document.cookie = `cart=${idSpecification}; path=/; SameSite=None; Secure`;
    document.cookie = `specificationId=${idCart}; path=/; SameSite=None; Secure`;
    document.cookie = `type_save=${typeSave}; path=/; SameSite=None; Secure`;
    
    const endpoint = `/api/v1/order/${idSpecification}/update-order-admin/`;

    fetch(endpoint, {
      method: "UPDATE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((response) => {
        window.location.href = `/admin_specification/current_specification/?${getParams}`;
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = "";
          button.textContent = button.getAttribute("text-content");
        }, 3000);
      });
  };
}
