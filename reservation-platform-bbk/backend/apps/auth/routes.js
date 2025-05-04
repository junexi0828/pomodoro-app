import express from 'express';
import { signup, login, getNaverAuthUrl, handleNaverCallback } from './controllers.js';

const router = express.Router();

router.post('/signup', signup);
router.post('/login', login);
router.get('/naver', getNaverAuthUrl);
router.get('/naver/callback', handleNaverCallback);

export default router; 