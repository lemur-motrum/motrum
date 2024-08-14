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
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        });
    });
  }
}
addNewClient("/api/v1/client/login/", "89276892248", "1111");

function updateClient() {
  // const idClient = element.getAttribute("data-client-id");
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
        method: "UPDATE",
        body: data,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        });
    });
  }
}
updateClient();

function addRequisites() {
  // const idClient = element.getAttribute("data-client-id");
  const idClient = 39;
  const endpoint = "/api/v1/client_requisites/" + idClient + "/add/";
  const clientAdd = document.querySelector(".client_requisites");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      let dataArr = [
        {
          requisites: {
            contract: 23423424,
            legal_entity: "3Юридическ1ое лицо",
            inn: 123212,
            kpp: 1232123,
            ogrn: 122313,
            legal_post_code: 1223123,
            legal_city: "dsgsdfsf",
            legal_address: "aweaeawe",
            postal_post_code: 12313,
            postal_city: "wewqweqe",
            postal_address: "qweqwee",
            client: idClient,
          },

          account_requisites: [
            {
              account_requisites: 23424,
              bank: "sfdfs",
              kpp: 12313,
              bic: 12313,
              requisites: null,
            },
            {
              account_requisites: 23424,
              bank: "sfdfs",
              kpp: 12313,
              bic: 12313,
              requisites: null,
            },
          ],
        },
        {
          requisites: {
            contract: null,
            legal_entity: "4Юридическое лицо",
            inn: 123212,
            kpp: 1232123,
            ogrn: 122313,
            legal_post_code: 1223123,
            legal_city: "dsgsdfsf",
            legal_address: "aweaeawe",
            postal_post_code: 12313,
            postal_city: "wewqweqe",
            postal_address: "qweqwee",
            client: idClient,
          },
          account_requisites: [
            {
              account_requisites: 23424,
              bank: "sfdfs",
              kpp: 12313,
              bic: 12313,
              requisites: null,
            },
          ],
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
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        });
    });
  }
}
addRequisites();

function getAllClient(endpointClient, phone, pin) {
  const clientAdd = document.querySelector(".client_info");
  if (clientAdd) {
    clientAdd.addEventListener("click", (event) => {
      const idClient = 10;
      const endpoint = "/api/v1/client_requisites/" + idClient + "/requisites/";
      const clientAdd = document.querySelector(".client_update");

      let csrfToken = getCookie("csrftoken");

      fetch(endpoint, {
        method: "GET",
        data: [],
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        });
    });
  }
}
getAllClient();
