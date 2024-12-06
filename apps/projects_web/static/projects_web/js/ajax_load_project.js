import { getCookie } from "/static/core/js/functions.js";
console.log(999)
let currentUrl = new URL(window.location.href);
window.addEventListener("DOMContentLoaded", () => {
    const catalogWrapper = document.querySelector('[project-elem="wrapper"]');
    if (catalogWrapper) {
        let paramsArray = [];
        const btn = catalogWrapper.querySelector(".add_more");
        const catalogContainer = catalogWrapper.querySelector(
            '[project-elem="container"]'
        );
        let productCount = 0;

        function loadItems(
        ) {
            let data = {
                count: productCount,
                // category_project: "markirovka-chestnyij-znak",
                client_category_project:["sborka"],
                // category_project_marking: ["markirovka1"]

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
            console.log(data)
            for (let i in data.data) {
                console.log(data.data[i])
                addAjaxCatalogItem(data.data[i]);
              }
          })
        } 
        
        window.onload = () => {
          
            loadItems();
          };


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
    }
    })

