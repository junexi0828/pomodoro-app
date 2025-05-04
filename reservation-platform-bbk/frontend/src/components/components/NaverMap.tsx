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
  latitude?: number;
  longitude?: number;
  center?: {
    lat: number;
    lng: number;
  };
  markers: Marker[];
}

function NaverMap({ latitude, longitude, center, markers }: Props) {
  // latitude/longitude가 있으면 center로 변환
  const mapCenter = center || (latitude && longitude ? { lat: latitude, lng: longitude } : markers[0]);
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
  }, [mapCenter, markers]);

  return <div id="map" style={{ width: '100%', height: '400px' }} />;
}

export default NaverMap;
