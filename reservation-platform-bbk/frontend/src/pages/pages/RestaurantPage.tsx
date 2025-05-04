import React, { useState, useEffect } from 'react';
import { Star, MapPin, Clock, Users, Car, ChevronDown, Calendar } from 'lucide-react';
import { useParams, Link } from 'react-router-dom';
import { fetchRestaurantById, Restaurant } from '../../utils/utils/api';
import NaverMap from '../../components/components/NaverMap';
import axios from 'axios';

function RestaurantPage() {
  const [selectedTime, setSelectedTime] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [guestCount, setGuestCount] = useState(2);
  const { id } = useParams();
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  const availableTimes = [
    '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'
  ];

  useEffect(() => {
    const loadRestaurant = async () => {
    const params = new URLSearchParams(window.location.search);
    const name = params.get('name');
    const email = params.get('email');

    if (name && email) {
      const userInfo = { name, email };
      localStorage.setItem('user', JSON.stringify(userInfo));
      console.log('✅ 유저 정보 저장됨:', userInfo);

    // URL 깔끔하게 정리 (쿼리스트링 제거)
    window.history.replaceState({}, '', window.location.pathname);
  }
      try {
        if (id) {
          const data = await fetchRestaurantById(Number(id));
          setRestaurant(data);
        }
      } catch (err) {
        console.error('레스토랑 불러오기 오류:', err);
        setError('레스토랑 정보를 불러오는 데 실패했습니다.');
      }
    };

    const user = localStorage.getItem('user');
    if (user) {
      const parsed = JSON.parse(user);
      setUserEmail(parsed.email);
    }

    loadRestaurant();
  }, [id]);

  const handleReservation = async () => {
    console.log('🟡 selectedDate:', selectedDate);
    console.log('🟡 selectedTime:', selectedTime);
    console.log('🟡 userEmail:', userEmail);
    console.log('🟡 restaurant:', restaurant);
    if (!selectedDate || !selectedTime || !restaurant || !userEmail) {
      alert('날짜, 시간, 사용자 정보를 모두 선택해주세요.');
      return;
    }

    try {
      const userRes = await axios.get(`http://223.130.155.88:3000/api/users/email/${userEmail}`);
      const userId = userRes.data?.UserID;

      const reservationDateTime = `${selectedDate}T${selectedTime}:00`;

      const res = await axios.post('http://223.130.155.88:3000/api/reservations', {
        user_id: userId,
        restaurant_id: restaurant.RestaurantID,
        reservation_time: reservationDateTime,
        guest_count: guestCount
      });

      alert('예약이 완료되었습니다.');
    } catch (err) {
      console.error('예약 오류:', err);
      alert('예약 중 오류가 발생했습니다.');
    }
  };

  if (error) {
    return <div className="text-center mt-20 text-red-500">{error}</div>;
  }

  if (!restaurant) {
    return <div className="text-center mt-20 text-gray-500">로딩 중...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="relative h-[60vh] w-full">
        <img 
          src={restaurant.ImageURL || 'https://source.unsplash.com/600x400/?restaurant'}
          alt={restaurant.RestaurantName} 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-32 relative z-10">
        <div className="bg-white rounded-xl shadow-xl p-8 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <Link to="/" className="text-indigo-900 hover:text-indigo-700 mb-4 inline-block">← 목록으로 돌아가기</Link>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{restaurant.RestaurantName}</h1>
              <div className="flex items-center gap-2 mb-3">
                {[...Array(restaurant.Stars)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600">{restaurant.Menu}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">위치</h2>
              <div className="bg-gray-200 rounded-lg h-[300px] mb-4">
                <NaverMap
                  latitude={restaurant.Latitude}
                  longitude={restaurant.Longitude}
                  markers={[{
                    lat: restaurant.Latitude,
                    lng: restaurant.Longitude,
                    label: restaurant.RestaurantName,
                  }]}
                />
              </div>
              <div className="flex items-start gap-2">
                <MapPin className="w-5 h-5 text-indigo-900 mt-1" />
                <p className="text-gray-600">{restaurant.AddressDetail || restaurant.Location}</p>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-6">레스토랑 정보</h2>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-2">소개</h3>
                  <p className="text-gray-600">{restaurant.Description}</p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">운영 정보</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center gap-2">
                      <Car className="w-5 h-5 text-indigo-900" />
                      <span>{restaurant.Parking ? '주차 가능' : '주차 불가'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span>📞</span>
                      <span>{restaurant.PhoneNumber || '전화번호 정보 없음'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-indigo-900" />
                      <span>총 {restaurant.NumberOfSeats}석</span>
                    </div>
                    {restaurant.OpeningHours && (
                      <div className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-indigo-900" />
                        <span>{restaurant.OpeningHours}</span>
                      </div>
                    )}
                    {restaurant.Services && (
                      <div className="md:col-span-2">
                        <p className="text-gray-600">🍽️ <strong>편의서비스:</strong> {restaurant.Services}</p>
                      </div>
                    )}
                    {restaurant.Website && (
                      <div className="md:col-span-2">
                        <a href={restaurant.Website} target="_blank" rel="noopener noreferrer" className="text-indigo-700 underline">
                          웹사이트 방문하기
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
              <h2 className="text-2xl font-semibold mb-6">예약하기</h2>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">날짜 선택</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-900 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">시간 선택</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <select
                    value={selectedTime}
                    onChange={(e) => setSelectedTime(e.target.value)}
                    className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-indigo-900 focus:border-transparent"
                  >
                    <option value="">시간을 선택해주세요</option>
                    {availableTimes.map(time => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                </div>
              </div>

              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-2">인원</label>
                <div className="relative">
                  <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <select
                    value={guestCount}
                    onChange={(e) => setGuestCount(parseInt(e.target.value))}
                    className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-indigo-900 focus:border-transparent"
                  >
                    {[...Array(10)].map((_, i) => (
                      <option key={i + 1} value={i + 1}>{i + 1}명</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                </div>
              </div>

              <button
                onClick={handleReservation}
                className="w-full bg-indigo-900 text-white py-3 rounded-lg hover:bg-indigo-800 transition-colors"
              >
                예약 하기
              </button>

              <p className="mt-4 text-sm text-gray-500 text-center">
                예약금 10만원이 결제됩니다
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-12">
          <h2 className="text-2xl font-semibold mb-6">리뷰</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border-l-4 border-indigo-900 pl-4">
              <p className="text-gray-600 mb-2">"최고의 다이닝 경험이었습니다. 셰프의 창의적인 요리와 세심한 서비스가 인상적이었습니다."</p>
              <p className="text-sm text-gray-500">- 김서연</p>
            </div>
            <div className="border-l-4 border-indigo-900 pl-4">
              <p className="text-gray-600 mb-2">"와인 페어링이 환상적이었고, 코스의 구성이 완벽했습니다."</p>
              <p className="text-sm text-gray-500">- 이준호</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RestaurantPage;
