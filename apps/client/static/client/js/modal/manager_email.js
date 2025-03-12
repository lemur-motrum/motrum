import { getCookie } from "/static/core/js/functions.js";
import { setErrorModal } from "/static/core/js/error_modal.js";

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
      .then((response) => {
        if (response.status >= 200 && response.status < 300) {
          return response.json();
        } else {
          setErrorModal();
        }
      })
      .then((data) => {
        console.log(data);
        window.location.reload();
      });
  });
}
