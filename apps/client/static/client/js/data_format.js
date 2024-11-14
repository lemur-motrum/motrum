window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".site_order_container");
  if (wrapper) {
    const interval = setInterval(() => {
      const orderItems = wrapper.querySelectorAll(".order_item");
      if (orderItems.length > 0) {
        clearInterval(interval);
        orderItems.forEach((orderItem) => {
          const date = orderItem.querySelector(".order_date_value");
          const formatterData = new Date(date.textContent);
          const currentDate = formatterData.toLocaleString("ru-RU", {
            year: "numeric",
            month: "long",
            day: "numeric",
          });
          date.textContent = currentDate;
        });
      }
    });
  }
});
