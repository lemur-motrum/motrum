import { showErrorValidation, getCookie } from "/static/core/js/functions.js";

const csrfToken = getCookie("csrftoken");

function loadInvoiceItems() {
  let params = new URLSearchParams(data);
  let csrfToken = getCookie("csrftoken");
  fetch(`/api/v1/order/load-ajax-specification-list/?${params.toString()}`, {
    method: "GET",
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then(function (data) {
      console.log("data", data);
      for (let i in data.data) {
        console.log("data1", addAjaxCatalogItem(data.data[i]));
      }
    });
}
function renderCatalogItem(orderData) {
  const ajaxTemplateWrapper = modalWindow.querySelector(".invoice_content");
  const ajaxCatalogElementTemplate =
    ajaxTemplateWrapper.querySelector("invoice-item").innerText;
  return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
}

function addAjaxCatalogItem(ajaxElemData) {
  let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
  specificationContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
}

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(
    ".specification_container"
  );
  const invoiceOverlay = document.querySelector(".invoice-overlay");
  const modalWindow = invoiceOverlay.querySelector(".modal-window");
  if (specificationContainer) {
    const interval = setInterval(() => {
      const specificationsItems = specificationContainer.querySelectorAll(
        ".specification_item"
      );
      if (specificationsItems.length > 0) {
        clearInterval(interval);
        specificationsItems.forEach((specificationItem) => {
          const invoiceBtn = specificationItem.querySelector(
            ".create-bill-button"
          );

          invoiceBtn.onclick = () => {
            invoiceOverlay.classList.add("show");
            document.body.style.overflowY = "hidden";
            setTimeout(() => {
              invoiceOverlay.classList.add("visible");
            }, 600);
            loadInvoiceItems();
          };
          invoiceOverlay.onclick = () => {
            invoiceOverlay.classList.remove("visible");
            if (invoiceOverlay.classList.contains("show")) {
              document.body.style.overflowY = "scroll";
            }
            setTimeout(() => {
              invoiceOverlay.classList.remove("show");
            }, 600);
          };
          modalWindow.onclick = (e) => {
            e.stopPropagation();
          };
        });
      }
    });
  }
});
