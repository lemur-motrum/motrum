window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".contacts-wrapper");
  if (wrapper) {
    const mapWrapper = wrapper.querySelector(".map-wrapper");
    ymaps.ready(function () {
      // const {YMapZoomControl, YMapGeolocationControl} = await ymaps3.import('@yandex/ymaps3-controls@0.0.1');
      const myMap = new ymaps.Map(
          "map",
          {
            center:
              window.innerWidth > 576
                ? [53.234504811961656, 50.19189402114864]
                : [53.236397293742286, 50.19255920898432],
            zoom: 16,
          },
          {
            searchControlProvider: "yandex#search",
          }
        ),
        myPlacemark = new ymaps.Placemark(
          [53.23432457121684, 50.19386812698358],
          myMap.getCenter(),
          {
            iconLayout: "default#imageWithContent",
            iconImageHref: "../../../../static/core/images/map-bullet.png",
            iconImageSize: [50.5, 79],
            iconImageOffset: [-21, -79],
          }
        );
      // zoomControl = new ymaps.control.ZoomControl({
      //   options: {
      //     size: "small",
      //     position: {
      //       right: 10,
      //       top: 500,
      //     },
      //   },
      // });

      myMap.behaviors.disable("scrollZoom");
      myMap.controls.remove("geolocationControl");
      myMap.controls.remove("routeButtonControl");
      myMap.controls.remove("trafficControl");
      myMap.controls.remove("searchControl");
      myMap.controls.remove("typeSelector");
      myMap.controls.remove("fullscreenControl");
      myMap.controls.remove("taxiControl");
      myMap.controls.remove("rulerControl");

      myMap.geoObjects.add(myPlacemark);
      if (window.innerWidth <= 576) {
        myMap.controls.remove("zoomControl");
        // myMap.controls.add(zoomControl);
      }
    });
  }
});
