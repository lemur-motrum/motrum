// SortableJS для сортировки элементов в корзине
// Sortable доступен глобально через CDN

window.addEventListener("DOMContentLoaded", () => {
  // Находим контейнер с элементами корзины
  const cartContainer = document.querySelector('.spetification_table');
  
  if (cartContainer) {
    // Инициализируем Sortable для элементов корзины
    const sortable = new Sortable(cartContainer, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      
      // События
      onStart: function (evt) {
        console.log('Начало перетаскивания');
      },
      
      onEnd: function (evt) {
        console.log('Конец перетаскивания');
        // Здесь можно добавить логику сохранения нового порядка
        saveNewOrder();
      },
      
      // Фильтры - какие элементы можно перетаскивать
      filter: '.item_container-delete_btn, .change_icon_container, .save_icon_container',
      onMove: function (evt) {
        // Запрещаем перетаскивание кнопок удаления/редактирования
        return !evt.related.classList.contains('item_container-delete_btn') &&
               !evt.related.classList.contains('change_icon_container') &&
               !evt.related.classList.contains('save_icon_container');
      }
    });
  }
  
  // Функция для сохранения нового порядка элементов
  function saveNewOrder() {
    const items = cartContainer.querySelectorAll('.item_container');
    const orderData = [];
    
    items.forEach((item, index) => {
      const itemId = item.getAttribute('data-id');
      if (itemId) {
        orderData.push({
          id: itemId,
          order: index
        });
      }
    });
    
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
          console.error('Ошибка сохранения порядка');
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
});
