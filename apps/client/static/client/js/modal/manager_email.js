import { getCookie } from "/static/core/js/functions.js";
const btn = document.querySelector(".send-manager");
if (btn) {
  btn.addEventListener("click", (event) => {
    const dataArr = {
      client_id: 24,
      text_message: "jsfkjsdfkj sjdfnksjndf sjdfnskjdnfk",
    };

    const data = JSON.stringify(dataArr);
    const csrfToken = getCookie("csrftoken");
    const endpoint = "/api/v1/emails/manager-email/";
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
        window.location.reload();
      });
  });
}
