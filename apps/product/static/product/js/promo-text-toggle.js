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
    const buffer = 20; // Буфер в пикселях для точностиconst lines = Math.round(promoTextContent.scrollHeight / lineHeight);
   
    const isOverflowing = promoTextContent.scrollHeight - promoTextContent.clientHeight > 1;
    // contentHeight > maxHeight + buffer
    if (isOverflowing) {
     
      // Показываем кнопку
      promoTextBtn.classList.remove("hide");
      promoTextBtn.style.display = "flex";
      promoTextBtn.style.visibility = "visible";
      promoTextBtn.style.opacity = "1";
     
      
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
    } 
  } 
  }, 100);
}); 