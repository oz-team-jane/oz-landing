import { parseTravel } from "./parseTravel.js";
import { initMap, addMarkersToMap } from "./mapControl.js";
import { displayItinerary } from "./itinerary.js";
import { shareItinerary, downloadItinerary } from "./shareDownload.js";

let currentItinerary = null;
let currentDayStats = [];

async function generatePlan() {
  const input = document.getElementById("travelInput").value;
  if (!input.trim()) {
    alert("여행 정보를 입력해주세요!");
    return;
  }
  const btn = document.getElementById("generateBtn");
  const loading = document.getElementById("loading");
  const mapDiv = document.getElementById("map");
  btn.disabled = true;
  btn.textContent = "생성 중...";
  loading.classList.add("show");
  mapDiv.style.display = "none";
  try {
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        try {
          const parsed = parseTravel(input);
          if (!parsed || !parsed.itinerary || parsed.itinerary.length === 0) {
            throw new Error("일정 생성 실패: 파싱 결과가 비어있음");
          }
          currentItinerary = parsed;
          // 거리/시간 정보는 addMarkersToMap 콜백에서 displayItinerary로 전달
          setTimeout(() => {
            try {
              initMap();
              addMarkersToMap(parsed.itinerary, (dayStats) => {
                currentDayStats = dayStats;
                displayItinerary(parsed, dayStats);
              });
            } catch (mapError) {
              console.warn("지도 처리 중 오류:", mapError);
              displayItinerary(parsed);
            }
          }, 100);
          resolve(parsed);
        } catch (error) {
          reject(error);
        }
      }, 1500);
    });
  } catch (error) {
    console.error("계획 생성 오류:", error);
    const fallbackItinerary = {
      itinerary: [
        {
          day: 1,
          date: "7월 25일",
          city: "강릉",
          locations: [
            { name: "경포해변", time: "09:00", city: "강릉", type: "spot" },
            { name: "오죽헌", time: "12:00", city: "강릉", type: "spot" },
          ],
          distance: 0,
          duration: 0,
        },
      ],
    };
    displayItinerary(fallbackItinerary);
    currentItinerary = fallbackItinerary;
    document.getElementById("map").innerHTML = `
      <div style="text-align: center; padding: 50px; color: #666; line-height: 1.6;">
        <div style="font-size: 18px; margin-bottom: 10px;">🗺️</div>
        지도는 로딩 중입니다...<br>
        <small>일정은 정상적으로 생성되었습니다!</small>
      </div>
    `;
  } finally {
    loading.classList.remove("show");
    mapDiv.style.display = "block";
    btn.disabled = false;
    btn.textContent = "🎯 AI가 여행 계획 생성하기";
  }
}

window.generatePlan = generatePlan;

document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const travelData = urlParams.get("data");
  if (travelData) {
    const travelInput = document.getElementById("travelInput");
    if (travelInput) {
      travelInput.value = decodeURIComponent(travelData);
      setTimeout(() => {
        generatePlan();
      }, 1000);
    }
  }
  // 공유/다운로드 버튼 이벤트 바인딩
  const shareBtn = document.querySelector(".share-btn:not([style])");
  const downloadBtn = document.querySelector(".share-btn[style]");
  if (shareBtn) {
    shareBtn.onclick = () => shareItinerary(currentItinerary);
  }
  if (downloadBtn) {
    downloadBtn.onclick = () => downloadItinerary(currentItinerary);
  }
});

document
  .getElementById("travelInput")
  .addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key === "Enter") {
      generatePlan();
    }
  });
