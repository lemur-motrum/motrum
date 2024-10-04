import { getCookie } from "/static/core/js/functions.js";
const btn = document.querySelector(".send-manager");
if (btn) {
    btn.addEventListener("click", (event) => {
        let dataArr = {
          client_id: 24,
          text_message:"jsfkjsdfkj sjdfnksjndf sjdfnskjdnfk",
        };
  
        let data = JSON.stringify(dataArr);
        let csrfToken = getCookie("csrftoken");
        let endpoint = "/api/v1/emails/manager-email/";
        fetch(endpoint, {
          method: "POST",
          body: data,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
            window.location.reload()
          });
      });
}