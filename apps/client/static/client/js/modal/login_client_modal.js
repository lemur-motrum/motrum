import { setErrorModal } from "../../../../../core/static/core/js/error_modal.js";

function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function addNewClient(endpointClient, phone, pin) {
  const clientAdd = document.querySelector(".client_add");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      let dataArr = {
        phone: phone,
        pin: pin,
      };

      let data = JSON.stringify(dataArr);
      let csrfToken = getCookie("csrftoken");
      console.log(data);
      fetch(endpointClient, {
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
        })
        .catch((error) => console.error(error));
    });
  }
}
addNewClient("/api/v1/client/login/", "89276892252", "1111");

function updateClient() {
  const idClient = "9";
  const endpoint = "/api/v1/client/" + idClient + "/";
  const clientAdd = document.querySelector(".client_update");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      let dataArr = {
        contact_name: "contact_name",
        phone: "89276892240",
        email: "steisysi@gmail.com",
        username: "89276892240",
        password: "",
      };

      let data = JSON.stringify(dataArr);
      let csrfToken = getCookie("csrftoken");
      console.log(data);
      fetch(endpoint, {
        // изменила метод
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
        })
        .catch((error) => console.error(error));
    });
  }
}
updateClient();

function addRequisites() {
  const idClient = 10;
  const endpoint = "/api/v1/requisites/add/";
  const clientAdd = document.querySelector(".client_requisites");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      let dataArr = [
        {
          requisites: {
            contract: "111111111",
            legal_entity: "3Юридическ1ое лицо",
            inn: "1111",
            kpp: "11111",
            ogrn: "1111",
            legal_post_code: "1111",
            legal_city: "dsgsdfsf",
            legal_address: "aweaeawe",
            postal_post_code: "1111",
            postal_city: "wewqweqe",
            postal_address: "qweqwee",
            client: idClient,
          },

          account_requisites: [],
        },
      ];

      let data = JSON.stringify(dataArr);
      let csrfToken = getCookie("csrftoken");
      console.log(data);
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
        })
        .catch((error) => console.error(error));
    });
  }
}
addRequisites();

function updateRequisites() {
  const idClient = 10;
  const idRequisites = 63;
  const endpoint = "/api/v1/requisites/" + idRequisites + "/update/";
  const clientAdd = document.querySelector(".client_upd");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      let dataArr = [
        {
          requisites: {
            id: idRequisites,
            contract: null,
            legal_entity: "4Юридическое лицо",
            inn: "ss4444",
            kpp: "ss44444",
            ogrn: "4444",
            legal_post_code: 4444,
            legal_city: "dsgsdfsf",
            legal_address: "aweaeawe",
            postal_post_code: "ss4444",
            postal_city: "wewqweqe",
            postal_address: "qweqwee",
            client: idClient,
          },
          account_requisites: [
            {
              account_requisites: "ss5555",
              bank: "sfdfs",
              kpp: "115555",
              bic: "5555",
              requisites: idRequisites,
              id: 37,
            },
            {
              account_requisites: "ss5555",
              bank: "sfdfs",
              kpp: "115555",
              bic: "5555",
              requisites: idRequisites,
              id: 38,
            },
          ],
        },
      ];

      let data = JSON.stringify(dataArr);
      let csrfToken = getCookie("csrftoken");
      console.log(data);
      fetch(endpoint, {
        // изменила метод
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
        })
        .catch((error) => console.error(error));
    });
  }
}
updateRequisites();

function getAllClient() {
  const clientAdd = document.querySelector(".client_info");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      const idClient = 10;
      const endpoint = "/api/v1/client-requisites/" + idClient + "/";

      let csrfToken = getCookie("csrftoken");

      fetch(endpoint, {
        method: "GET",
        data: [],
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
        })
        .catch((error) => console.error(error));
    });
  }
}
getAllClient();

// function addEmailCall() {
//   const clientAdd = document.querySelector(".coll");
//   if (clientAdd) {
//     clientAdd.addEventListener("click", (event) => {
//       const name = "sfsdfsf";
//       const phone = "526626526";
//       const endpoint = "/send_email_callback";
//       const clientAdd = document.querySelector(".client_update");
//       let dataArr = {
//         name: name,
//         phone: phone,
//       };

//       let data = JSON.stringify(dataArr);
//       let csrfToken = getCookie("csrftoken");
//       console.log(data);
//       fetch(endpoint, {
//         method: "POST",
//         body: data,
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//       })
//         .then((response) => response.json())
//         .then((data) => {
//           console.log(data);
//         });
//     });
//   }
// }
// addEmailCall();

// function addEmailManager() {
//   const clientAdd = document.querySelector(".send-manager");
//   if (clientAdd) {
//     clientAdd.addEventListener("click", (event) => {
//       const client_id = "21";
//       const text_message =
//         "werweукйукйцукйцку  йцуцуцйуй цйуй цуй уйцу йцуйцуйцццццццццццццццццццццццццццццццццццццццццццrwer";
//       const endpoint = "/send_email_manager";
//       const clientAdd = document.querySelector(".client_update");
//       let dataArr = {
//         client_id: client_id,
//         text_message: text_message,
//       };

//       let data = JSON.stringify(dataArr);
//       let csrfToken = getCookie("csrftoken");
//       console.log(data);
//       fetch(endpoint, {
//         method: "POST",
//         body: data,
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//       })
//         .then((response) => response.json())
//         .then((data) => {
//           console.log(data);
//         });
//     });
//   }
// }
// addEmailManager();
