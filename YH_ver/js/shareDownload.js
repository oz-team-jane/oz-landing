export function shareItinerary(currentItinerary) {
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

export function downloadItinerary(currentItinerary) {
  if (!currentItinerary) return;
  // PDF 다운로드 기능은 현재 미구현 (유료 안내 알림 제거)
}
