import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface User {
  name: string;
  email: string;
}

function Layout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  // ✅ 네이버 로그인 성공 후 사용자 정보 URL에서 추출
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const name = params.get('name');
    const email = params.get('email');

    if (name && email) {
      setUser({ name, email });

      // ✅ 쿼리스트링 제거 (깔끔한 URL)
      navigate(location.pathname, { replace: true });
    }
  }, [location, navigate]);

  // ✅ 로그아웃 함수
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    navigate('/');
    toast.success('👋로그아웃 되었습니다.');
  };

  return (
    <>
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex-shrink-0">
              <Link to="/" className="text-2xl font-bold text-indigo-900">Eatscape</Link>
            </div>
            <nav className="hidden md:flex space-x-8 items-center">
              <Link to="/" className="text-gray-900 hover:text-indigo-900">홈</Link>
              <Link to="/vip" className="text-gray-900 hover:text-indigo-900">VIP 문의</Link>

              {user ? (
                <>
                  <span className="text-sm text-gray-700">{user.name} 님 환영합니다</span>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-white bg-indigo-600 px-3 py-1 rounded hover:bg-indigo-700"
                  >
                    로그아웃
                  </button>
                </>
              ) : (
                <Link to="/login" className="text-gray-900 hover:text-indigo-900">로그인</Link>
              )}
            </nav>
          </div>
        </div>
      </header>

      {children}

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Eatscape</h4>
              <p className="text-gray-600">
                최고의 미슐랭 스타 레스토랑 예약 플랫폼
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">고객 지원</h4>
              <ul className="space-y-2">
                <li>
                  <Link to="/contact" className="text-gray-600 hover:text-indigo-900">
                    고객센터
                  </Link>
                </li>
                <li>
                  <Link to="/faq" className="text-gray-600 hover:text-indigo-900">
                    자주 묻는 질문
                  </Link>
                </li>
                <li>
                  <Link to="/terms" className="text-gray-600 hover:text-indigo-900">
                    이용약관
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">비즈니스</h4>
              <ul className="space-y-2">
                <li>
                  <Link to="/partner" className="text-gray-600 hover:text-indigo-900">
                    파트너 문의
                  </Link>
                </li>
                <li>
                  <Link to="/corporate" className="text-gray-600 hover:text-indigo-900">
                    기업 회원
                  </Link>
                </li>
                <li>
                  <Link to="/privacy" className="text-gray-600 hover:text-indigo-900">
                    개인정보처리방침
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}

export default Layout;
