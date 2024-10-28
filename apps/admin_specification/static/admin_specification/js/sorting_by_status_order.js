// window.addEventListener("DOMContentLoaded", () => {
//   const allSpecificationsContainer = document.querySelector(
//     ".all_specifications_container"
//   );
//   if (allSpecificationsContainer) {
//     let currentUrl = new URL(window.location.href);

//     const titles = allSpecificationsContainer.querySelector(".title");
//     const allOrdersBtn = titles.querySelector(".all_orders");
//     const ordersWithoutSpecification = titles.querySelector(
//       ".orders_without_specifications"
//     );
//     const titleItems = titles.querySelectorAll("span");
//     const searchParams = currentUrl.searchParams;

//     for (let i = 0; i < titleItems.length; i++) {
//       titleItems[i].onclick = () => {
//         if (!titleItems[i].classList.contains("active")) {
//           titleItems[i].classList.add("active");
//           if (titleItems[i - 1]) {
//             titleItems[i - 1].classList.remove("active");
//           } else {
//             titleItems[i + 1].classList.remove("active");
//           }
//         } else {
//           return;
//         }

//         if (ordersWithoutSpecification.classList.contains("active")) {
//           searchParams.set("specification", "+");
//           history.pushState({}, "", currentUrl);
//           LoadSpecifications(allSpecificationsContainer, true);
//         } else {
//           searchParams.delete("specification");
//           history.pushState({}, "", currentUrl);
//           LoadSpecifications(allSpecificationsContainer, false);
//         }
//       };
//     }
//   }
// });
