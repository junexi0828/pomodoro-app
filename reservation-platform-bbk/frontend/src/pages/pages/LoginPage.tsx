import { toast } from 'react-toastify';

function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            로그인
          </h2>
        </div>
        <div className="mt-8 space-y-6">
          <a 
            href="http://223.130.155.88:3000/auth/naver"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#03C75A] hover:bg-[#02b350] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#03C75A]"
          >
            네이버로 로그인
          </a>
        </div>
      </div>
    </div>
  );
}

export default LoginPage; 

