window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".specification-container");
  if (wrapper) {
    const products = [];
    const specifications = wrapper.querySelectorAll(".item_container");
    specifications.forEach((specification) => {
      const itemQuantity = specification.querySelector(".input-quantity").value;
      const itemID = specification.getAttribute("data-product-pk");
      const nameProductNew = specification.getAttribute(
        "data-product-name-new"
      );
      const itemPriceStatus = specification.getAttribute(
        "data-price-exclusive"
      );
      const itemPrice = specification.getAttribute("data-price");
      const extraDiscount = specification.querySelector(".discount-input");
      const productSpecificationId = specification.getAttribute(
        "data-product-specification-id"
      );
      const deliveryDate = specification.querySelector(".invoice-data-input");
      const commentItem = specification.querySelector(
        'textarea[name="comment-input-name"]'
      ).value;
      const inputPrice = specification.querySelector(".price-input");
      const saleMotrum = specification.querySelector(".motrum_sale_persent");
      const vendor = specification.getAttribute("data-vendor");

      const product = {
        product_id: +itemID,
        quantity: +itemQuantity,
        price_exclusive: +itemPriceStatus,
        price_one: +getCurrentPrice(itemPrice),
        product_specif_id: productSpecificationId
          ? productSpecificationId
          : null,
        extra_discount: extraDiscount.value,
        date_delivery: deliveryDate.value,
        product_name_new: nameProductNew,
        product_new_article: nameProductNew,
        comment: commentItem ? commentItem : null,
        sale_motrum: saleMotrum ? saleMotrum.textContent : null,
        vendor: vendor ? vendor : null,
      };

      if (deliveryDate) {
        if (!deliveryDate.value) {
          validate = false;
          deliveryDate.style.border = "1px solid red";
          deliveryDate.style.borderRadius = "10px";
        }
      }

      if (inputPrice) {
        if (!inputPrice.value) {
          validate = false;
          inputPrice.style.border = "1px solid red";
          inputPrice.style.borderRadius = "10px";
        }
      }
      if (validate === true) {
        products.push(product);
      }
    });
  }
});
