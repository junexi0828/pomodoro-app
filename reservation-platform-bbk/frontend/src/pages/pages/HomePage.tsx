import React, { useEffect, useState } from 'react';
import { Star, MapPin, ChevronRight, Phone, Mail, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchRestaurants, Restaurant } from "../../utils/utils/api";
import NaverMap from "../../components/components/NaverMap";

function HomePage() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    const checkNaverMapsLoaded = () => {
      if (window.naver && window.naver.maps) {
        setMapLoaded(true);
      } else {
        setTimeout(checkNaverMapsLoaded, 500);
      }
    };

    checkNaverMapsLoaded();
  }, []);

  useEffect(() => {
    fetchRestaurants()
      .then(setRestaurants)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  // 유효한 위치 정보가 있는 레스토랑만 필터링
  const validLocationRestaurants = restaurants.filter(
    (r) => r.Latitude && r.Longitude
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative bg-indigo-900 py-16 text-center text-white">
        <h2 className="text-4xl font-bold mb-4">미슐랭 스타 레스토랑을 한 곳에서</h2>
        <p className="text-indigo-100 text-lg max-w-2xl mx-auto">
          국내 최고의 미슐랭 스타 레스토랑들을 만나보세요. <br>
          </br> 특별한 날을 위한 프리미엄 다이닝 경험을 제공합니다.
        </p>
      </div>

      {/* Map Section */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-xl font-bold mb-4">내 주변 미슐랭 레스토랑</h2>
        {!loading && mapLoaded && validLocationRestaurants.length > 0 && (
          <NaverMap
            markers={validLocationRestaurants.map((r) => ({
              lat: r.Latitude,
              lng: r.Longitude,
              name: r.RestaurantName,
            }))}
            center={validLocationRestaurants[0] ? {
              lat: validLocationRestaurants[0].Latitude,
              lng: validLocationRestaurants[0].Longitude,
            } : undefined}
          />
        )}
      </div>

      {/* Restaurant List */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h3 className="text-2xl font-semibold text-gray-900 mb-8">추천 레스토랑</h3>

        {loading ? (
          <p className="text-center text-gray-600">로딩 중...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {restaurants.map((restaurant) => (
              <div key={restaurant.RestaurantID} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className="relative h-48">
                <img 
                  src={restaurant.ImageURL || 'https://source.unsplash.com/400x300/?restaurant'} 
                  alt={restaurant.RestaurantName}
                  className="w-full h-full object-cover"
                />
                  <div className="absolute top-4 right-4 bg-white px-3 py-1 rounded-full">
                    <div className="flex items-center gap-1">
                      {[...Array(restaurant.Stars)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-2">{restaurant.RestaurantName}</h4>
                  <div className="flex items-center gap-2 text-gray-600 mb-4">
                    <MapPin className="w-4 h-4" />
                    <span>{restaurant.Location}</span>
                  </div>
                  <Link to={`/restaurant/${restaurant.RestaurantID}`} className="flex items-center gap-1 text-indigo-900 hover:text-indigo-700">
                    자세히 보기 <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    {/* VIP Section */}
    <div className="bg-gray-900 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-indigo-900/20 rounded-2xl p-8 backdrop-blur">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-3xl font-bold text-white mb-4">VIP 컨시어지 서비스</h3>
              <p className="text-gray-300 mb-6">
                기업 고객을 위한 프리미엄 예약 서비스를 제공합니다.<br />
                전담 컨시어지가 귀하의 특별한 날을 완벽하게 준비해드립니다.
              </p>
              <div className="space-y-4">
                <div className="flex items-center gap-3 text-gray-300">
                  <Users className="w-5 h-5" />
                  <span>기업 행사 및 VIP 고객 맞춤 서비스</span>
                </div>
                <div className="flex items-center gap-3 text-gray-300">
                  <Phone className="w-5 h-5" />
                  <span>24시간 전담 매니저 상담</span>
                </div>
                <div className="flex items-center gap-3 text-gray-300">
                  <Mail className="w-5 h-5" />
                  <span>특별 혜택 및 프로모션</span>
                </div>
              </div>
            </div>
            <div className="text-center md:text-right">
              <Link to="/vip">
                <button className="inline-flex items-center px-6 py-3 border-2 border-white text-white hover:bg-white hover:text-indigo-900 rounded-lg transition-colors">
                  VIP 문의하기
                  <ChevronRight className="w-5 h-5 ml-2" />
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  );
}


export default HomePage;
