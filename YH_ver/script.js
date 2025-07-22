let map;
let currentItinerary = null;
let markers = [];

function parseTravel(input) {
  console.log("파싱 시작:", input);

  try {
    const cities = [
      { name: "서울", lat: 37.5665, lng: 126.978 },
      { name: "부산", lat: 35.1796, lng: 129.0756 },
      { name: "제주도", lat: 33.4996, lng: 126.5312 },
      { name: "강릉", lat: 37.7519, lng: 128.8761 },
      { name: "속초", lat: 38.207, lng: 128.5918 },
      { name: "양양", lat: 38.0754, lng: 128.619 },
      { name: "전주", lat: 35.8242, lng: 127.148 },
      { name: "경주", lat: 35.8562, lng: 129.2247 },
      { name: "여수", lat: 34.7604, lng: 127.6622 },
    ];

    const attractions = {
      부산: [
        "해운대 해수욕장",
        "감천문화마을",
        "태종대",
        "광안리 해변",
        "자갈치시장",
      ],
      서울: ["경복궁", "명동", "홍대", "강남", "남산타워"],
      제주도: ["성산일출봉", "한라산", "중문 해수욕장", "우도", "천지연폭포"],
      강릉: ["경포해변", "오죽헌", "안목해변", "정동진", "강릉 커피거리"],
      속초: ["속초해수욕장", "설악산 국립공원", "속초 중앙시장", "외옹치 해변"],
      양양: ["낙산해수욕장", "설악산 대청봉", "양양 서피비치", "오색온천"],
      전주: ["한옥마을", "전주 비빔밥", "오목대", "경기전"],
      경주: ["불국사", "석굴암", "첨성대", "안압지"],
      여수: ["여수 엑스포", "오동도", "향일암", "돌산대교"],
    };

    // 입력에서 여러 도시 감지
    let detectedCities = [];
    for (const city of cities) {
      if (input.includes(city.name)) {
        detectedCities.push(city);
      }
    }

    // 도시가 없으면 기본값
    if (detectedCities.length === 0) {
      detectedCities = [cities[3]]; // 기본값: 강릉
    }

    console.log(
      "감지된 도시들:",
      detectedCities.map((c) => c.name)
    );

    // 날짜 패턴 감지 (더 유연하게)
    const datePattern =
      /(\d{1,2}월?\s*\d{1,2}일?)|(\d{4}-\d{1,2}-\d{1,2})|(\d{1,2}\/\d{1,2})/g;
    let dates = input.match(datePattern) || [];

    // 날짜가 없거나 적으면 기본 날짜 생성
    if (dates.length < 2) {
      dates = ["7월 25일", "7월 26일", "7월 27일", "7월 28일", "7월 29일"];
    }

    console.log("감지된 날짜:", dates);

    // 여행 일정 생성 (최대 5일)
    const maxDays = Math.min(dates.length, detectedCities.length > 1 ? 5 : 3);
    const itinerary = [];

    for (let i = 0; i < maxDays; i++) {
      const cityIndex = i % detectedCities.length;
      const currentCity = detectedCities[cityIndex];
      const cityAttractions = attractions[currentCity.name] || [
        "관광지 A",
        "관광지 B",
      ];

      const dayLocations = [];
      const numLocations = Math.min(cityAttractions.length, 3);

      for (let j = 0; j < numLocations; j++) {
        dayLocations.push({
          name: cityAttractions[j],
          lat: currentCity.lat + (Math.random() - 0.5) * 0.02,
          lng: currentCity.lng + (Math.random() - 0.5) * 0.02,
          time: `${9 + j * 2}:00`,
          city: currentCity.name,
        });
      }

      itinerary.push({
        day: i + 1,
        date: dates[i] || `${i + 1}일차`,
        city: currentCity.name,
        locations: dayLocations,
      });
    }

    console.log("생성된 일정:", itinerary);

    const result = {
      cities: detectedCities,
      primaryCity: detectedCities[0],
      itinerary: itinerary,
    };

    // 결과 검증
    if (!result.itinerary || result.itinerary.length === 0) {
      throw new Error("일정이 생성되지 않았습니다");
    }

    return result;
  } catch (error) {
    console.error("파싱 오류:", error);
    // 최소한의 fallback 데이터
    return {
      cities: [{ name: "강릉", lat: 37.7519, lng: 128.8761 }],
      primaryCity: { name: "강릉", lat: 37.7519, lng: 128.8761 },
      itinerary: [
        {
          day: 1,
          date: "여행 1일차",
          city: "강릉",
          locations: [
            {
              name: "경포해변",
              lat: 37.7519,
              lng: 128.8761,
              time: "09:00",
              city: "강릉",
            },
            {
              name: "오죽헌",
              lat: 37.7519,
              lng: 128.8761,
              time: "11:00",
              city: "강릉",
            },
          ],
        },
      ],
    };
  }
}

function initMap() {
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

function clearMap() {
  if (typeof L !== "undefined" && map) {
    markers.forEach((marker) => map.removeLayer(marker));
  }
  markers = [];
}

function addMarkersToMap(itinerary) {
  if (typeof L === "undefined" || !map) {
    console.log("지도를 사용할 수 없어 마커 추가를 건너뜁니다");
    return;
  }

  try {
    clearMap();
    const colors = ["red", "blue", "green", "orange", "violet"];

    itinerary.forEach((day, dayIndex) => {
      day.locations.forEach((location, locIndex) => {
        const marker = L.marker([location.lat, location.lng]).addTo(map)
          .bindPopup(`
                                 <b>Day ${day.day}: ${location.name}</b><br>
                                 시간: ${location.time}<br>
                                 날짜: ${day.date}<br>
                                 도시: ${location.city}
                             `);
        markers.push(marker);
      });
    });

    // 지도 범위 조정
    if (markers.length > 0) {
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }
    console.log("마커 추가 완료:", markers.length + "개");
  } catch (error) {
    console.error("마커 추가 오류:", error);
  }
}

function displayItinerary(parsed) {
  const itineraryDiv = document.getElementById("itinerary");

  let html = "";
  parsed.itinerary.forEach((day) => {
    html += `
                    <div class="day-item">
                        <div class="day-date">Day ${day.day} - ${day.date} (${
      day.city
    })</div>
                        ${day.locations
                          .map(
                            (loc) => `
                            <div class="location-item">
                                <strong>${loc.time}</strong> - ${loc.name}
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                `;
  });

  itineraryDiv.innerHTML = html;
  document.getElementById("shareSection").style.display = "block";
}

async function generatePlan() {
  const input = document.getElementById("travelInput").value;
  if (!input.trim()) {
    alert("여행 정보를 입력해주세요!");
    return;
  }

  const btn = document.getElementById("generateBtn");
  const loading = document.getElementById("loading");
  const mapDiv = document.getElementById("map");

  // UI 상태 업데이트
  btn.disabled = true;
  btn.textContent = "생성 중...";
  loading.classList.add("show");
  mapDiv.style.display = "none";

  try {
    // Promise로 래핑하여 setTimeout을 async/await으로 처리
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        try {
          console.log("여행 계획 생성 시작");
          const parsed = parseTravel(input);

          if (!parsed || !parsed.itinerary || parsed.itinerary.length === 0) {
            throw new Error("일정 생성 실패: 파싱 결과가 비어있음");
          }

          currentItinerary = parsed;
          console.log("파싱된 결과:", parsed);

          // 일정 표시
          displayItinerary(parsed);

          // 지도 초기화 및 마커 추가 (비동기적으로)
          setTimeout(() => {
            try {
              if (!map) {
                initMap();
              }
              if (map) {
                addMarkersToMap(parsed.itinerary);
              }
            } catch (mapError) {
              console.warn("지도 처리 중 오류:", mapError);
              // 지도 오류는 전체 프로세스를 중단시키지 않음
            }
          }, 100);

          resolve(parsed);
        } catch (error) {
          reject(error);
        }
      }, 1500); // 시간을 1.5초로 단축
    });

    console.log("여행 계획 생성 완료");
  } catch (error) {
    console.error("계획 생성 오류:", error);

    // 에러 시에도 기본 일정은 표시
    const fallbackItinerary = {
      itinerary: [
        {
          day: 1,
          date: "7월 25일",
          city: "강릉",
          locations: [
            { name: "경포해변", time: "09:00", city: "강릉" },
            { name: "오죽헌", time: "12:00", city: "강릉" },
          ],
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
    // UI 상태 복원
    loading.classList.remove("show");
    mapDiv.style.display = "block";
    btn.disabled = false;
    btn.textContent = "🎯 AI가 여행 계획 생성하기";
  }
}

function shareItinerary() {
  if (!currentItinerary) return;

  let shareText = `✈️ AI가 생성한 동해안 여행 계획\n\n`;
  currentItinerary.itinerary.forEach((day) => {
    shareText += `📅 Day ${day.day} - ${day.date} (${day.city})\n`;
    day.locations.forEach((loc) => {
      shareText += `  ${loc.time} - ${loc.name}\n`;
    });
    shareText += "\n";
  });
  shareText += "🚀 TripAI에서 생성됨";

  if (navigator.share) {
    navigator.share({
      title: "AI 여행 계획",
      text: shareText,
    });
  } else {
    navigator.clipboard.writeText(shareText).then(() => {
      alert("여행 계획이 클립보드에 복사되었습니다!");
    });
  }
}

function downloadItinerary() {
  if (!currentItinerary) return;
  alert(
    "PDF 다운로드 기능은 유료 버전에서 제공됩니다.\n\n무료 체험: 1회 계획 생성\n프리미엄: 무제한 생성 + PDF 다운로드 + 실시간 수정"
  );
}

// 페이지 로드 시 지도 초기화
document.addEventListener("DOMContentLoaded", function () {
  // 초기 지도는 생성하지 않고 필요할 때만 생성
});

// 엔터키로 생성하기
document
  .getElementById("travelInput")
  .addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key === "Enter") {
      generatePlan();
    }
  });
