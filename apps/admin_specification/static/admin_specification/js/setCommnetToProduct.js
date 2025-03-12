import { showErrorValidation } from "/static/core/js/functions.js";

export function setCommentProductItem(el) {
  if (el) {
    const overlay = document.querySelector(".okt_product_comment_overlay");
    const closeBtn = overlay.querySelector(".close_btn");
    const textAreaComment = overlay.querySelector(".comment_text_area");
    const error = overlay.querySelector(".error");
    const submitBtn = overlay.querySelector(".btn");
    const commentButton = el.querySelector(".comment");

    function validate() {
      const commentValue = el.getAttribute("data-comment-item");
      if (commentValue) {
        textAreaComment.value = commentValue;
      } else {
        textAreaComment.value = "";
      }
    }

    function openOverlay() {
      validate();
      overlay.classList.add("show");
      setTimeout(() => {
        overlay.classList.add("visible");
      }, 600);

      submitBtn.onclick = () => {
        if (!textAreaComment.value) {
          el.setAttribute("data-comment-item", "");
          if (commentButton.classList.contains("true")) {
            commentButton.classList.remove("true");
            commentButton.classList.add("false");
            commentButton.textContent = "Добавить комментарий";
          }
          closeOverlay();
        } else {
          el.setAttribute("data-comment-item", textAreaComment.value);
          if (commentButton.classList.contains("false")) {
            commentButton.classList.remove("false");
            commentButton.classList.add("true");
            commentButton.textContent = "Посмотреть комментарий";
          }
          closeOverlay();
        }
      };
    }

    function closeOverlay() {
      validate();
      overlay.classList.remove("visible");
      setTimeout(() => {
        overlay.classList.remove("show");
      }, 600);
    }

    closeBtn.onclick = () => {
      closeOverlay();
    };

    commentButton.onclick = () => {
      openOverlay();
    };
  }
}
