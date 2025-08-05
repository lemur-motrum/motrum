window.addEventListener("DOMContentLoaded", () => {
  // Небольшая задержка для загрузки стилей
  setTimeout(() => {
    const promoTextContainer = document.getElementById("promo-text-container");
    const promoTextContent = document.getElementById("promo-text-content");
    const promoTextBtn = document.getElementById("promo-text-btn");
  
  
  
  if (promoTextContainer && promoTextContent && promoTextBtn) {
    // Проверяем, если текст больше 4 строк
    const computedStyle = window.getComputedStyle(promoTextContent);
    const lineHeight = parseInt(computedStyle.lineHeight) || parseInt(computedStyle.fontSize) * 1.2;
    const maxHeight = lineHeight * 4; // 4 строки
    const contentHeight = promoTextContent.scrollHeight;
    const buffer = 20; // Буфер в пикселях для точности
    
    console.log("Height calculations:", { lineHeight, maxHeight, contentHeight });
    
    if (contentHeight > maxHeight + buffer) {
      console.log("Text is longer than 4 lines, showing button");
      // Показываем кнопку
      promoTextBtn.classList.remove("hide");
      promoTextBtn.style.display = "flex";
      promoTextBtn.style.visibility = "visible";
      promoTextBtn.style.opacity = "1";
      
      console.log("Button styles after showing:", {
        display: promoTextBtn.style.display,
        visibility: promoTextBtn.style.visibility,
        opacity: promoTextBtn.style.opacity,
        classList: promoTextBtn.classList.toString(),
        offsetHeight: promoTextBtn.offsetHeight,
        offsetWidth: promoTextBtn.offsetWidth
      });
      
      // Обработчик клика на кнопку
      promoTextBtn.addEventListener("click", () => {
        const isExpanded = promoTextContent.classList.contains("expanded");
        
        if (isExpanded) {
          // Сворачиваем текст
          promoTextContent.classList.remove("expanded");
          promoTextBtn.style.setProperty("--button-text", "Показать еще");
        } else {
          // Разворачиваем текст
          promoTextContent.classList.add("expanded");
          promoTextBtn.style.setProperty("--button-text", "Скрыть");
        }
      });
    } else {
      console.log("Text is not longer than 4 lines, hiding button");
    }
  } 
  }, 100);
}); 