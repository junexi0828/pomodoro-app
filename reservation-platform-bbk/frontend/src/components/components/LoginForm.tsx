import React, { useState, FormEvent, ChangeEvent } from 'react';
import { useAuth } from '../../context/contexts/AuthContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface FormData {
  email: string;
  password: string;
}

const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('/api/login', formData);
      login(response.data);
      navigate('/');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('이메일 또는 비밀번호가 올바르지 않습니다.');
        } else if (err.response?.status === 500) {
          setError('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } else {
          setError('로그인 중 오류가 발생했습니다.');
        }
      } else {
        setError('로그인 중 오류가 발생했습니다.');
      }
    }
  };

  const handleNaverLogin = async () => {
    try {
      const response = await axios.get('/api/auth/naver');
      window.location.href = response.data.url;
    } catch (error) {
      setError('네이버 로그인을 시작하는 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">로그인</h2>
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">이메일</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">비밀번호</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition-colors mb-4"
        >
          로그인
        </button>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">또는</span>
          </div>
        </div>

        <button
          type="button"
          onClick={handleNaverLogin}
          className="w-full bg-[#03C75A] text-white py-2 px-4 rounded hover:bg-[#02b350] transition-colors flex items-center justify-center"
        >
          <img 
            src="/naver-icon.png" 
            alt="네이버 로고" 
            className="w-5 h-5 mr-2"
          />
          네이버로 로그인
        </button>
      </form>
    </div>
  );
};

export default LoginForm; 