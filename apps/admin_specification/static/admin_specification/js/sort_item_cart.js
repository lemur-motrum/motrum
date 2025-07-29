// SortableJS для сортировки элементов в корзине
// Sortable доступен глобально через CDN

window.addEventListener("DOMContentLoaded", () => {
  // Находим контейнер с элементами корзины
  const cartContainer = document.getElementById('drop_items');
  console.log("cartContainer", cartContainer);
  
  if (cartContainer) {
    // Сортируем элементы по полю order при загрузке страницы
    sortItemsByOrder();
    
    // Перетаскивание работает только при клике на пустые области
    // Все остальные обработчики убраны, так как проверка происходит в onStart
    
    // Инициализируем Sortable для элементов корзины
    const sortable = new Sortable(cartContainer, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      
      // Перетаскивание работает только при клике на элементы с классом drag-handle
      handle: '.drag-handle',
      
      // Автоматическая прокрутка при перетаскивании
      scroll: true,
      scrollSensitivity: 50,
      scrollSpeed: 10,
      
      // События
      onStart: function (evt) {
        console.log('Начало перетаскивания элемента:', evt.item);
        evt.item.classList.add('dragging');
      },
      
      onEnd: function (evt) {
        console.log('Конец перетаскивания');
        evt.item.classList.remove('dragging');
        // Здесь можно добавить логику сохранения нового порядка
        saveNewOrder();
      },
      
      // Перетаскивание работает только при клике на пустые области
      // Фильтр убран, так как проверка происходит в onStart
    });
  }
  
  // Функция для сохранения нового порядка элементов
  function saveNewOrder() {
    const items = cartContainer.querySelectorAll('.item_container');
    const orderData = [];
    
    items.forEach((item, index) => {
      const itemId = item.getAttribute('data-id');
      if (itemId) {
        // Определяем новый порядок: существующие элементы от 1, новые (order=0) в конце
        const currentOrder = parseInt(item.getAttribute('data-order')) || 0;
        let newOrder;
        
        if (currentOrder === 0) {
          // Новые элементы (order=0) получают порядок в конце
          newOrder = index + 1;
        } else {
          // Существующие элементы сохраняют свой порядок, но обновляем его
          newOrder = index + 1;
        }
        
        // Обновляем атрибут data-order для каждого элемента
        item.setAttribute('data-order', newOrder);
        
        orderData.push({
          id: itemId,
          order: newOrder
        });
      }
    });
    
    console.log('Новый порядок элементов:', orderData);
    
    // Отправляем данные на сервер для сохранения порядка
    if (orderData.length > 0) {
      fetch('/admin_specification/save_cart_order/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ order: orderData })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('Порядок элементов сохранен');
        } else {
          console.error('Ошибка сохранения порядка:', data.error);
        }
      })
      .catch(error => {
        console.error('Ошибка при сохранении порядка:', error);
      });
    }
  }
  
  // Функция для получения CSRF токена
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  // Функция для сортировки элементов по полю order
  function sortItemsByOrder() {
    const items = cartContainer.querySelectorAll('.item_container');
    const itemsArray = Array.from(items);
    
    console.log('До сортировки:');
    itemsArray.forEach((item, index) => {
      const order = item.getAttribute('data-order');
      const id = item.getAttribute('data-id');
      console.log(`Элемент ${index}: data-order="${order}", data-id="${id}"`);
    });
    
    // Сортируем элементы по атрибуту data-order или data-id
    itemsArray.sort((a, b) => {
      // Получаем значения order, преобразуем в числа, если нет - используем 0
      const orderAStr = a.getAttribute('data-order');
      const orderBStr = b.getAttribute('data-order');
      
      const orderA = (orderAStr !== null && orderAStr !== '') ? (parseInt(orderAStr) || 0) : (parseInt(a.getAttribute('data-id')) || 0);
      const orderB = (orderBStr !== null && orderBStr !== '') ? (parseInt(orderBStr) || 0) : (parseInt(b.getAttribute('data-id')) || 0);
      
      console.log(`Сравниваем: ${orderA} vs ${orderB} (${orderAStr} vs ${orderBStr})`);
      
      // Сортируем по возрастанию (1, 2, 3, ..., 0 в конце)
      if (orderA === 0 && orderB !== 0) return 1;  // 0 идет в конец
      if (orderB === 0 && orderA !== 0) return -1; // 0 идет в конец
      return orderA - orderB; // Остальные сортируются по возрастанию
    });
    
    console.log('После сортировки:');
    itemsArray.forEach((item, index) => {
      const order = item.getAttribute('data-order');
      console.log(`Элемент ${index}: data-order="${order}"`);
    });
    
    // Перемещаем элементы в правильном порядке
    itemsArray.forEach((item, index) => {
      // Устанавливаем атрибут data-order если его нет
      if (!item.getAttribute('data-order')) {
        item.setAttribute('data-order', index);
      }
      cartContainer.appendChild(item);
    });
    
    console.log('Элементы отсортированы по порядку:', itemsArray.length);
  }
});
