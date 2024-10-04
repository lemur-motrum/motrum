import { getCookie } from "/static/core/js/functions.js";
const btn = document.querySelector(".call-back-link");
if (btn) {
    btn.addEventListener("click", (event) => {
        let dataArr = {
            name: "NaME Mane",
            phone: "89276892240",
        };
  
        let data = JSON.stringify(dataArr);
        let csrfToken = getCookie("csrftoken");
        let endpoint = "/api/v1/emails/call-back-email/";
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