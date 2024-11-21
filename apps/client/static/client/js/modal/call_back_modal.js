import { getCookie } from "/static/core/js/functions.js";
const btn = document.querySelector(".call-back-link");
if (btn) {
  btn.addEventListener("click", () => {
    const dataArr = {
      name: "NaME Mane",
      phone: "89276892240",
    };

    const data = JSON.stringify(dataArr);
    const csrfToken = getCookie("csrftoken");
    const endpoint = "/api/v1/emails/call-back-email/";
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
