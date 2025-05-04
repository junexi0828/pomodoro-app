import { useEffect } from 'react';

interface Marker {
  lat: number;
  lng: number;
  label?: string;
}

interface Marker {
  lat: number;
  lng: number;
  label?: string; 
}

interface Props {
  center?: {
    lat: number;
    lng: number;
  }; // 🔹 지도 중심 위치 (선택적)
  markers: Marker[]; 
}

function NaverMap({ center, markers }: Props) {
  useEffect(() => {
    const timer = setInterval(() => {
      const mapElement = document.getElementById('map');

      if (
        typeof window !== 'undefined' &&
        window.naver &&
        window.naver.maps &&
        mapElement
      ) {
        clearInterval(timer);

        // 중심 위치는 center가 있으면 그걸 쓰고, 없으면 첫 번째 마커의 위치
        const mapCenter = center || markers[0];

        const map = new window.naver.maps.Map(mapElement, {
          center: new window.naver.maps.LatLng(mapCenter.lat, mapCenter.lng),
          zoom: 14,
        });

        markers.forEach((m) => {
          const marker = new window.naver.maps.Marker({
            position: new window.naver.maps.LatLng(m.lat, m.lng),
            map,
          });

          if (m.label) {
            const infoWindow = new window.naver.maps.InfoWindow({
              content: `<div style="padding:4px 8px;font-size:12px;">${m.label}</div>`,
            });

            window.naver.maps.Event.addListener(marker, 'click', () => {
              infoWindow.open(map, marker);
            });
          }
        });
      }
    }, 300);

    return () => clearInterval(timer);
  }, [center, markers]);

  return <div id="map" style={{ width: '100%', height: '400px' }} />;
}

export default NaverMap;
