import { cities, attractions } from "../data/attractions.js";

function getRandomItems(arr, count) {
  const shuffled = arr.slice().sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

export function parseTravel(input) {
  console.log("파싱 시작:", input);
  try {
    // 입력에서 여러 도시 감지
    let detectedCities = [];
    for (const city of cities) {
      if (input.includes(city.name)) {
        detectedCities.push(city);
      }
    }
    if (detectedCities.length === 0) {
      detectedCities = [cities[3]]; // 기본값: 강릉
    }
    console.log(
      "감지된 도시들:",
      detectedCities.map((c) => c.name)
    );
    const datePattern =
      /(\d{1,2}월?\s*\d{1,2}일?)|(\d{4}-\d{1,2}-\d{1,2})|(\d{1,2}\/\d{1,2})/g;
    let dates = input.match(datePattern) || [];
    if (dates.length < 2) {
      dates = ["7월 25일", "7월 26일", "7월 27일", "7월 28일", "7월 29일"];
    }
    console.log("감지된 날짜:", dates);
    const maxDays = Math.min(dates.length, detectedCities.length > 1 ? 5 : 3);
    const itinerary = [];
    for (let i = 0; i < maxDays; i++) {
      const cityIndex = i % detectedCities.length;
      const currentCity = detectedCities[cityIndex];
      const cityData = attractions[currentCity.name] || {
        spots: [],
        foods: [],
      };
      // 명소 2~3개, 맛집 1~2개 랜덤 선택
      const numSpots = Math.min(
        cityData.spots.length,
        2 + Math.floor(Math.random() * 2)
      );
      const numFoods = Math.min(
        cityData.foods.length,
        1 + Math.floor(Math.random() * 2)
      );
      const spots = getRandomItems(cityData.spots, numSpots).map(
        (name, idx) => ({
          name,
          lat: currentCity.lat + (Math.random() - 0.5) * 0.02,
          lng: currentCity.lng + (Math.random() - 0.5) * 0.02,
          time: `${9 + idx * 2}:00`,
          city: currentCity.name,
          type: "spot",
        })
      );
      const foods = getRandomItems(cityData.foods, numFoods).map(
        (name, idx) => ({
          name,
          lat: currentCity.lat + (Math.random() - 0.5) * 0.02,
          lng: currentCity.lng + (Math.random() - 0.5) * 0.02,
          time: `${11 + idx * 2}:30`,
          city: currentCity.name,
          type: "food",
        })
      );
      // 명소와 맛집을 랜덤하게 섞어서 locations 생성
      const locations = [...spots, ...foods].sort(() => 0.5 - Math.random());
      itinerary.push({
        day: i + 1,
        date: dates[i] || `${i + 1}일차`,
        city: currentCity.name,
        locations,
        distance: 0, // km, 추후 계산
        duration: 0, // 분, 추후 계산
      });
    }
    console.log("생성된 일정:", itinerary);
    const result = {
      cities: detectedCities,
      primaryCity: detectedCities[0],
      itinerary: itinerary,
    };
    if (!result.itinerary || result.itinerary.length === 0) {
      throw new Error("일정이 생성되지 않았습니다");
    }
    return result;
  } catch (error) {
    console.error("파싱 오류:", error);
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
              type: "spot",
            },
            {
              name: "오죽헌",
              lat: 37.7519,
              lng: 128.8761,
              time: "11:00",
              city: "강릉",
              type: "spot",
            },
          ],
          distance: 0,
          duration: 0,
        },
      ],
    };
  }
}
