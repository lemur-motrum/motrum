window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".contacts-wrapper");
  if (wrapper) {
    const mapWrapper = wrapper.querySelector(".map-wrapper");

    ymaps.ready(function () {
      var myMap = new ymaps.Map(
          "map",
          {
            center: [53.23437595926513, 50.19160323322894],
            zoom: 17,
          },
          {
            searchControlProvider: "yandex#search",
          }
        ),
        myPlacemark = new ymaps.Placemark(
          [53.23449182826312, 50.19393139065387],
          myMap.getCenter(),
          {
            // Опции.
            // Необходимо указать данный тип макета.
            iconLayout: "default#imageWithContent",
            // Своё изображение иконки метки.
            iconImageHref: "../../../../static/core/images/map-bullet.png",
            // Размеры метки.
            iconImageSize: [50.5, 79],
            // Смещение левого верхнего угла иконки относительно
            // её "ножки" (точки привязки).
            iconImageOffset: [-21, -79],
          }
        );

      myMap.behaviors.disable("scrollZoom");
      // myMap.behaviors.disable("drag");
      myMap.controls.remove("zoomControl");
      myMap.controls.remove("geolocationControl");
      myMap.controls.remove("routeButtonControl");
      myMap.controls.remove("trafficControl");
      myMap.controls.remove("searchControl");
      myMap.controls.remove("typeSelector");
      myMap.controls.remove("fullscreenControl");
      myMap.controls.remove("taxiControl");
      myMap.controls.remove("rulerControl");
      myMap.geoObjects.add(myPlacemark);
    });
  }
});
