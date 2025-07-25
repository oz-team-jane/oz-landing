import { highlightMarker } from "./mapControl.js";

export function displayItinerary(parsed, dayStats = []) {
  const itineraryDiv = document.getElementById("itinerary");
  let html = "";
  parsed.itinerary.forEach((day, dayIdx) => {
    const stat = dayStats[dayIdx] || { distance: 0, duration: 0 };
    html += `
      <div class="day-item itinerary-card">
        <div class="day-date">Day ${day.day} - ${day.date} (${day.city})</div>
        <div class="itinerary-meta">
          <span>이동거리: <b>${stat.distance}km</b></span>
          <span>예상시간: <b>${stat.duration}분</b></span>
        </div>
        <div class="itinerary-locations">
          ${day.locations
            .map(
              (loc, locIdx) => `
                <div class="location-item" data-day="${dayIdx}" data-loc="${locIdx}">
                  <span class="loc-type ${loc.type}">${
                loc.type === "food" ? "🍴" : "📍"
              }</span>
                  <strong>${loc.time}</strong> - ${loc.name}
                </div>
              `
            )
            .join("")}
        </div>
      </div>
    `;
  });
  itineraryDiv.innerHTML = html;
  document.getElementById("shareSection").style.display = "block";

  // 일정 항목 클릭 시 마커 강조
  itineraryDiv.querySelectorAll(".location-item").forEach((item) => {
    item.addEventListener("click", function () {
      const dayIdx = parseInt(this.getAttribute("data-day"));
      const locIdx = parseInt(this.getAttribute("data-loc"));
      highlightMarker(dayIdx, locIdx);
    });
  });
}
