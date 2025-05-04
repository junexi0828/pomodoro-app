import express from 'express';
import dotenv from 'dotenv';
import corsMiddleware from '../../common/middlewares/cors.js';
import authRoutes from './routes.js';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// 미들웨어 설정
app.use(corsMiddleware);
app.use(express.json());

// 라우터 설정
app.use('/api', authRoutes);

// 서버 시작
app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 서버 실행 중: http://localhost:${port}`);
});