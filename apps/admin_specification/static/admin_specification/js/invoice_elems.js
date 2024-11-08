import { getCookie } from "/static/core/js/functions.js";

export function invoiceItem(container) {
  if (container) {
    const invoiceOverlay = document.querySelector(".invoice-overlay");
    const modalWindow = invoiceOverlay.querySelector(".modal-window");
    const closeBtn = modalWindow.querySelector(".close-btn");
    const invoiceContainer = modalWindow.querySelector(
      '[invoice-elem="container"]'
    );

    function loadInvoiceItems(specificationId) {
      let csrfToken = getCookie("csrftoken");
      fetch(`/api/v1/order/${specificationId}/get-specification-product/`, {
        method: "GET",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then(function (data) {
          const createTextDateDelivery = (elem) => {
            const orderData = new Date(elem["date_delivery"]);
            const today = new Date();
            const delta = orderData.getTime() - today.getTime();
            let dayDifference = +Math.ceil(delta / 1000 / 60 / 60 / 24);
            let result;
            if (dayDifference >= 7) {
              result = +Math.ceil(dayDifference / 7);
            } else {
              dayDifference = dayDifference += 1;
            }
            function num_word(value, words) {
              value = Math.abs(value) % 100;
              var num = value % 10;
              if (value > 10 && value < 20) return words[2];
              if (num > 1 && num < 5) return words[1];
              if (num == 1) return words[0];
              return words[2];
            }
            if (dayDifference > 7) {
              return `${result} ${num_word(result, [
                "неделя",
                "недели",
                "недель",
              ])}`;
            } else {
              return "1 неделя";
            }
          };

          for (let i in data) {
            if (data[i]["date_delivery"]) {
              data[i]["text_delivery"] = createTextDateDelivery(data[i]);
            }

            addAjaxCatalogItem(data[i]);
          }
        });
    }
    function renderCatalogItem(orderData) {
      let ajaxTemplateWrapper = document.querySelector(
        '[template-elem="wrapper"]'
      );
      let ajaxCatalogElementTemplate = ajaxTemplateWrapper.querySelector(
        '[invoice-elem="invoice-item"]'
      ).innerText;

      return nunjucks.renderString(ajaxCatalogElementTemplate, orderData);
    }

    function addAjaxCatalogItem(ajaxElemData) {
      let renderCatalogItemHtml = renderCatalogItem(ajaxElemData);
      invoiceContainer.insertAdjacentHTML("beforeend", renderCatalogItemHtml);
    }

    if (container) {
      const interval = setInterval(() => {
        const specificationsItems = container.querySelectorAll(
          ".specification_item"
        );
        if (specificationsItems.length > 0) {
          clearInterval(interval);
          specificationsItems.forEach((specificationItem) => {
            const createInvoiceContainer = specificationItem.querySelector(
              ".invoice-table_item_value"
            );
            const invoiceBtn = createInvoiceContainer.querySelector(
              ".create-bill-button"
            );
            const invoiceLink =
              createInvoiceContainer.querySelector(".invoice-link");

            const specificationId =
              specificationItem.getAttribute("specification-id");
            if (invoiceBtn) {
              function openInvoiceModal() {
                invoiceBtn.setAttribute("text-content", invoiceBtn.textContent);
                invoiceBtn.disabled = true;
                invoiceBtn.textContent = "";
                invoiceBtn.innerHTML = "<div class='small_loader'></div>";
                invoiceOverlay.classList.add("show");
                document.body.style.overflowY = "hidden";
                setTimeout(() => {
                  invoiceOverlay.classList.add("visible");
                }, 600);
                loadInvoiceItems(specificationId);

                const interval = setInterval(() => {
                  const invoiceItems =
                    invoiceContainer.querySelectorAll(".invoice-item");
                  if (invoiceItems.length > 0) {
                    clearInterval(interval);
                    const createInvoiceBtn =
                      modalWindow.querySelector(".invoice-btn");
                    createInvoiceBtn.onclick = () => {
                      let validate = true;
                      const inputs = modalWindow.querySelectorAll(
                        ".invoice-data-input"
                      );
                      for (let i = 0; i < inputs.length; i += 1) {
                        if (!inputs[i].value) {
                          validate = false;
                          break;
                        }
                      }
                      if (validate == true) {
                        createInvoiceBtn.disabled = true;
                        createInvoiceBtn.textContent = "";
                        createInvoiceBtn.innerHTML =
                          "<div class='small_loader'></div>";
                        const csrfToken = getCookie("csrftoken");
                        const dataArray = [];
                        invoiceItems.forEach((el) => {
                          const id = el.getAttribute("invoice-elem-id");
                          const value = el.querySelector(
                            ".invoice-data-input"
                          ).value;

                          const dataObject = {
                            id: id,
                            text_delivery: value,
                          };
                          dataArray.push(dataObject);
                        });

                        const data = JSON.stringify(dataArray);

                        fetch(
                          `/api/v1/order/${specificationId}/create-bill-admin/`,
                          {
                            method: "UPDATE",
                            headers: {
                              "Content-Type": "application/json",
                              "X-CSRFToken": csrfToken,
                            },
                            body: data,
                          }
                        )
                          .then((response) => {
                            if (
                              response.status === 200 ||
                              response.status === 201
                            ) {
                              return response.json();
                            } else {
                              throw new Error("Ошибка");
                            }
                          })
                          .then((response) => {
                            console.log(response);
                            invoiceBtn.disabled = false;
                            invoiceBtn.innerHTML = "";
                            invoiceBtn.textContent = "Обновите счет";
                            invoiceBtn.setAttribute(
                              "text-content",
                              invoiceBtn.textContent
                            );
                            invoiceOverlay.classList.remove("visible");
                            if (invoiceOverlay.classList.contains("show")) {
                              document.body.style.overflowY = "scroll";
                            }
                            setTimeout(() => {
                              invoiceOverlay.classList.remove("show");
                              invoiceContainer.innerHTML = "";
                            }, 600);
                            if (!invoiceLink) {
                              invoiceBtn.classList.add("changed");
                              invoiceBtn.textContent = "Обновить счет";
                              const link =
                                specificationItem.querySelector(
                                  ".invoice-link"
                                );
                              if (link) {
                                link.remove();
                              }
                              createInvoiceContainer.innerHTML += `<a class="invoice-link" href='${response.pdf}'>Скачать счет №${response.name_bill}</a>`;
                              const btn =
                                specificationItem.querySelector(".changed");
                              btn.onclick = () => openInvoiceModal();
                            } else {
                              invoiceBtn.classList.add("changed");
                              invoiceBtn.textContent = "Обновить счет";
                              const link =
                                specificationItem.querySelector(
                                  ".invoice-link"
                                );
                              link.remove();
                              createInvoiceContainer.innerHTML += `<a class="invoice-link" href='${response.pdf}'>Скачать счет №${response.name_bill}</a>`;
                              const btn =
                                specificationItem.querySelector(".changed");
                              btn.onclick = () => openInvoiceModal();
                            }
                            createInvoiceBtn.disabled = false;
                            createInvoiceBtn.innerHTML = "";
                            createInvoiceBtn.textContent = "Создать счет";
                            const addPayBtn = specificationItem.querySelector(
                              ".add_payment_button"
                            );
                            addPayBtn.style.display = "block";
                          });
                      }
                    };
                  }
                });
              }
              invoiceBtn.onclick = () => openInvoiceModal();
              closeBtn.onclick = () => {
                document
                  .querySelectorAll(".create-bill-button")
                  .forEach((el) => {
                    if (el.disabled) {
                      el.innerHTML = "";
                      el.textContent = el.getAttribute("text-content");
                      el.disabled = false;
                    }
                  });
                invoiceOverlay.classList.remove("visible");
                if (invoiceOverlay.classList.contains("show")) {
                  document.body.style.overflowY = "scroll";
                }
                setTimeout(() => {
                  invoiceOverlay.classList.remove("show");
                  invoiceContainer.innerHTML = "";
                }, 600);
              };
            }
          });
        }
      });
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const specificationContainer = document.querySelector(
    ".specification_container"
  );
  invoiceItem(specificationContainer);
});
