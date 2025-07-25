let map;
let markers = [];
let routeLayers = [];

// Leaflet Routing Machine이 필요합니다. (CDN: https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js)

export function initMap() {
  try {
    if (typeof L === "undefined") {
      console.error("Leaflet이 로드되지 않았습니다");
      document.getElementById("map").innerHTML =
        '<div style="text-align: center; padding: 50px; color: #666;">지도 로딩 중 오류가 발생했습니다.<br>간단한 지도 대신 텍스트 기반 결과를 표시합니다.</div>';
      return;
    }
    map = L.map("map").setView([37.7519, 128.8761], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);
    console.log("지도 초기화 완료");
  } catch (error) {
    console.error("지도 초기화 오류:", error);
    document.getElementById("map").innerHTML =
      '<div style="text-align: center; padding: 50px; color: #666;">지도 로딩 중 오류가 발생했습니다.<br>간단한 지도 대신 텍스트 기반 결과를 표시합니다.</div>';
  }
}

export function clearMap() {
  if (typeof L !== "undefined" && map) {
    markers.forEach((marker) => map.removeLayer(marker));
    routeLayers.forEach((layer) => map.removeLayer(layer));
  }
  markers = [];
  routeLayers = [];
}

// day별 locations 경로를 지도에 표시하고, 거리/시간 계산 결과를 콜백으로 반환
export function addMarkersToMap(itinerary, onRouteStats) {
  if (typeof L === "undefined" || !map) {
    console.log("지도를 사용할 수 없어 마커 추가/경로 생성을 건너뜁니다");
    return;
  }
  try {
    clearMap();
    const colors = ["red", "blue", "green", "orange", "violet"];
    let bounds = [];
    let dayStats = [];
    let routingCount = 0;
    itinerary.forEach((day, dayIndex) => {
      // 마커 추가
      day.locations.forEach((location, locIndex) => {
        let markerOptions = {};
        if (location.type === "food") {
          markerOptions.icon = L.icon({
            iconUrl: "https://cdn-icons-png.flaticon.com/512/1046/1046784.png",
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
          });
        }
        const marker = L.marker(
          [location.lat, location.lng],
          markerOptions
        ).addTo(map).bindPopup(`
            <b>Day ${day.day}: ${location.name}</b><br>
            시간: ${location.time}<br>
            날짜: ${day.date}<br>
            도시: ${location.city}
          `);
        marker._dayIndex = dayIndex;
        marker._locIndex = locIndex;
        markers.push(marker);
        bounds.push([location.lat, location.lng]);
      });
      // Routing Machine 경로 표시
      if (window.L && window.L.Routing && day.locations.length > 1) {
        const waypoints = day.locations.map((loc) =>
          L.latLng(loc.lat, loc.lng)
        );
        const router = L.Routing.control({
          waypoints,
          lineOptions: {
            styles: [
              {
                color: colors[dayIndex % colors.length],
                weight: 5,
                opacity: 0.7,
              },
            ],
            addWaypoints: false,
          },
          draggableWaypoints: false,
          fitSelectedRoutes: false,
          // createMarker 옵션 제거(기본값 사용, TBT 마커 표시)
          routeWhileDragging: false,
          show: false, // 안내 패널 숨김
          router: L.Routing.osrmv1({
            serviceUrl: "https://router.project-osrm.org/route/v1",
          }),
        }).addTo(map);
        routeLayers.push(router);
        // 안내 패널 DOM 숨기기
        router.on("routeselected", function () {
          const container = router._container;
          if (container) {
            container.style.display = "none";
          }
        });
        router.on("routesfound", function (e) {
          const route = e.routes[0];
          const distance = Math.round(route.summary.totalDistance / 100) / 10; // km
          const duration = Math.round(route.summary.totalTime / 60); // 분
          dayStats[dayIndex] = { distance, duration };
          routingCount++;
          if (
            routingCount === itinerary.length &&
            typeof onRouteStats === "function"
          ) {
            onRouteStats(dayStats);
          }
        });
      } else {
        dayStats[dayIndex] = { distance: 0, duration: 0 };
        routingCount++;
        if (
          routingCount === itinerary.length &&
          typeof onRouteStats === "function"
        ) {
          onRouteStats(dayStats);
        }
      }
    });
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }
    console.log("마커 및 경로 추가 완료:", markers.length + "개");
  } catch (error) {
    console.error("마커/경로 추가 오류:", error);
  }
}

// 마커 강조 함수 (itinerary day/loc 인덱스 기반)
export function highlightMarker(dayIndex, locIndex) {
  if (!markers[dayIndex * 10 + locIndex]) return;
  const marker = markers.find(
    (m) => m._dayIndex === dayIndex && m._locIndex === locIndex
  );
  if (marker) {
    marker.openPopup();
    map.setView(marker.getLatLng(), 14, { animate: true });
  }
}
