import {
  showErrorValidation,
  getCookie,
  getDigitsNumber,
} from "/static/core/js/functions.js";
import { setErrorModal } from "/static/core/js/error_modal.js";
import { completeOrder } from "../js/complete_order.js";
import { uptadeOrChanegeSpecification } from "../js/ajax_specification_load.js";

export function changePayment(container, errorFn) {
  if (container) {
    const overlay = document.querySelector(".change_of_payment_overlay");
    const closeBtn = overlay.querySelector(".close_btn");
    const modalWindow = overlay.querySelector(".modal-window");
    const paymentInput = modalWindow.querySelector(".payment_input");
    const paymentError = modalWindow.querySelector(".payment_error");
    const paymentChangeButton = modalWindow.querySelector(
      ".change-payment-btn"
    );
    const interval = setInterval(() => {
      const specifications = container.querySelectorAll(".table_item");
      if (specifications.length > 0) {
        clearInterval(interval);
        specifications.forEach((specification) => {
          const specificationId =
            specification.getAttribute("specification-id");
          const cartId = specification.getAttribute("data-cart-id");
          const paymentLink = specification.querySelector(
            ".price_bill_sum_paid"
          );
          const invoiceSpecificationContainer = specification.querySelector(
            ".invoice-table_item_value"
          );
          const changedItemButtonsContainer = specification.querySelector(
            ".table_item_value_change_buttons_container"
          );
          if (paymentLink) {
            getDigitsNumber(
              paymentLink,
              +paymentLink.getAttribute("bill-sum-paid")
            );
          }
          const paymentBtn = specification.querySelector(".add_payment_button");
          const orderId = specification.getAttribute("order-id");

          function changePayment() {
            let finishPromice = false;
            let csrfToken = getCookie("csrftoken");
            fetch(`/api/v1/order/${orderId}/get-payment/`, {
              method: "GET",
              headers: {
                "X-CSRFToken": csrfToken,
              },
            })
              .then((response) => {
                if (response.status == 200) {
                  return response.json();
                } else {
                  setErrorModal();
                  throw new Error("Ошибка");
                }
              })
              .then((response) => {
                paymentInput.setAttribute("summ-pay", response.sum_pay);
                finishPromice = true;
              })
              .catch((error) => console.error(error));
            const promiceModalInteval = setInterval(() => {
              if (finishPromice) {
                clearInterval(promiceModalInteval);
                overlay.classList.add("show");
                document.body.style.overflowY = "hidden";
                setTimeout(() => {
                  overlay.classList.add("visible");
                }, 600);
                paymentInput.addEventListener("input", function (e) {
                  let currentValue = this.value
                    .replace(",", ".")
                    .replace(/[^.\d]+/g, "")
                    .replace(/^([^\.]*\.)|\./g, "$1")
                    .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
                      return a + b + c.slice(0, 2);
                    });

                  if (currentValue > +paymentInput.getAttribute("summ-pay")) {
                    currentValue = +paymentInput.getAttribute("summ-pay");
                  }
                  paymentInput.value = currentValue;
                  const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
                  numbers.forEach((num) => {
                    if (paymentInput.value == `0${num}`) {
                      e.target.value = "0";
                    }
                  });
                });

                paymentChangeButton.onclick = () => {
                  if (!paymentInput.value) {
                    errorFn("Поле не заполнено", paymentError);
                  } else {
                    if (paymentInput.value == "0") {
                      errorFn("Значение не изменит сумму", paymentError);
                    } else {
                      paymentChangeButton.disabled = true;
                      paymentChangeButton.textContent = "";
                      paymentChangeButton.innerHTML =
                        "<div class='small_loader'></div>";
                      const objData = {
                        bill_sum_paid: paymentInput.value,
                      };
                      const data = JSON.stringify(objData);
                      fetch(`/api/v1/order/${orderId}/save-payment/`, {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                          "X-CSRFToken": csrfToken,
                        },
                        body: data,
                      })
                        .then((response) => {
                          if (response.status == 200) {
                            return response.json();
                          } else {
                            setErrorModal();
                            throw new Error("Ошибка");
                          }
                        })
                        .then((response) => {
                          paymentBtn.classList.add("changed");
                          if (paymentLink.textContent === "0") {
                            paymentLink.setAttribute(
                              "bill-sum-paid",
                              paymentInput.value
                            );
                            getDigitsNumber(
                              paymentLink,
                              +paymentLink.getAttribute("bill-sum-paid")
                            );
                          } else {
                            const count =
                              +paymentLink.getAttribute("bill-sum-paid") +
                              +paymentInput.value;
                            paymentLink.setAttribute("bill-sum-paid", count);
                            getDigitsNumber(
                              paymentLink,
                              +paymentLink.getAttribute("bill-sum-paid")
                            );
                          }
                          const addBillBtn = specification.querySelector(
                            ".create-bill-button"
                          );
                          if (addBillBtn) {
                            addBillBtn.style.display = "none";
                          }
                          overlay.classList.remove("visible");
                          if (overlay.classList.contains("show")) {
                            document.body.style.overflowY = "scroll";
                          }
                          setTimeout(() => {
                            overlay.classList.remove("show");
                            paymentInput.value = "";
                          }, 600);
                          paymentChangeButton.disabled = false;
                          paymentChangeButton.innerHTML = "";
                          paymentChangeButton.textContent = "Внести";
                          const intevalChangeBtn = setInterval(() => {
                            const changedBtn =
                              specification.querySelector("changed");
                            if (changedBtn) {
                              clearInterval(intevalChangeBtn);
                              changedBtn.onclick = () => changePayment();
                            }
                          });
                          paymentBtn.disabled = false;

                          if (response.is_all_sum == true) {
                            paymentBtn.style.display = "none";
                            const completeBtnContainer =
                              specification.querySelector(".first_table_value");
                            completeBtnContainer.innerHTML +=
                              '<button class="complete_order_button">Завершить заказ</button>';
                          }
                          const superUserSatus = document
                            .querySelector(".all_specifications_table")
                            .getAttribute("superuser");
                          if (superUserSatus == "true") {
                            if (
                              specification.querySelector(".change-bill-button")
                            ) {
                              specification
                                .querySelector(".change-bill-button")
                                .remove();
                            }
                            changedItemButtonsContainer.innerHTML +=
                              "<div class='change-bill-button'>Изменить счет</div>";
                            if (
                              specification.querySelector(".change-bill-button")
                            ) {
                              uptadeOrChanegeSpecification(
                                specification.querySelector(
                                  ".change-bill-button"
                                ),
                                "bill-upd=True",
                                specificationId,
                                cartId
                              );
                            }
                          }
                          const changePaymentButton =
                            specification.querySelector(
                              ".change-specification-button"
                            );
                          const description =
                            specification.querySelector(".description");

                          if (changePaymentButton && description) {
                            changePaymentButton.style.display = "none";
                            description.style.display = "none";
                          }
                          completeOrder(container);
                        })
                        .catch((error) => console.error(error));
                    }
                  }
                };
              }
            });
          }
          if (paymentBtn) {
            paymentBtn.onclick = () => changePayment();
          }
          closeBtn.onclick = () => {
            document.querySelectorAll(".add_payment_button").forEach((el) => {
              el.disabled = false;
            });
            overlay.classList.remove("visible");
            if (overlay.classList.contains("show")) {
              document.body.style.overflowY = "scroll";
            }
            setTimeout(() => {
              overlay.classList.remove("show");
              paymentInput.value = "";
            }, 600);
          };
        });
      }
    });
  }
}
