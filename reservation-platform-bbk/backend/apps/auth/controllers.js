import axios from 'axios';
import pool from '../../common/config/database.js';
import { generateToken, hashPassword, comparePassword } from '../../common/utils/auth.js';

export const signup = async (req, res) => {
  try {
    const { email, password, userType, businessInfo } = req.body;
    const connection = await pool.getConnection();

    const [existingUsers] = await connection.query(
      'SELECT * FROM Users WHERE Email = ?',
      [email]
    );

    if (existingUsers.length > 0) {
      connection.release();
      return res.status(400).json({ message: '이미 존재하는 이메일입니다.' });
    }

    const hashedPassword = await hashPassword(password);

    const [result] = await connection.query(
      'INSERT INTO Users (Email, Password, UserType, BusinessInfo) VALUES (?, ?, ?, ?)',
      [email, hashedPassword, userType, businessInfo || null]
    );

    connection.release();

    const token = generateToken({ userId: result.insertId, email, userType });

    res.status(201).json({
      id: result.insertId,
      email,
      userType,
      token
    });
  } catch (error) {
    console.error('회원가입 에러:', error);
    res.status(500).json({ message: '서버 에러가 발생했습니다.' });
  }
};

export const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const connection = await pool.getConnection();

    const [users] = await connection.query(
      'SELECT * FROM Users WHERE Email = ?',
      [email]
    );

    connection.release();

    if (users.length === 0) {
      return res.status(401).json({ message: '이메일 또는 비밀번호가 올바르지 않습니다.' });
    }

    const user = users[0];
    const isValidPassword = await comparePassword(password, user.Password);

    if (!isValidPassword) {
      return res.status(401).json({ message: '이메일 또는 비밀번호가 올바르지 않습니다.' });
    }

    const token = generateToken({ 
      userId: user.UserID, 
      email: user.Email, 
      userType: user.UserType 
    });

    res.json({
      id: user.UserID,
      email: user.Email,
      userType: user.UserType,
      token
    });
  } catch (error) {
    console.error('로그인 에러:', error);
    res.status(500).json({ message: '서버 에러가 발생했습니다.' });
  }
};

export const getNaverAuthUrl = (req, res) => {
  const state = Math.random().toString(36).substring(2);
  const naverAuthURL = `https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=${process.env.NAVER_CLIENT_ID}&redirect_uri=${process.env.NAVER_REDIRECT_URI}&state=${state}`;
  res.json({ url: naverAuthURL });
};

export const handleNaverCallback = async (req, res) => {
  const { code, state } = req.query;
  
  try {
    const tokenResponse = await axios.get('https://nid.naver.com/oauth2.0/token', {
      params: {
        grant_type: 'authorization_code',
        client_id: process.env.NAVER_CLIENT_ID,
        client_secret: process.env.NAVER_CLIENT_SECRET,
        code,
        state
      }
    });

    const { access_token } = tokenResponse.data;

    const userResponse = await axios.get('https://openapi.naver.com/v1/nid/me', {
      headers: { 
        Authorization: `Bearer ${access_token}`
      }
    });

    const naverUser = userResponse.data.response;
    
    const connection = await pool.getConnection();
    const [users] = await connection.query(
      'SELECT * FROM Users WHERE Email = ? AND Provider = "naver"',
      [naverUser.email]
    );

    let user;
    if (users.length === 0) {
      const [result] = await connection.query(
        'INSERT INTO Users (Email, Name, Provider, ProviderID) VALUES (?, ?, "naver", ?)',
        [naverUser.email, naverUser.name, naverUser.id]
      );
      user = {
        id: result.insertId,
        email: naverUser.email,
        name: naverUser.name,
        provider: 'naver'
      };
    } else {
      user = users[0];
    }

    connection.release();

    const token = generateToken({ 
      userId: user.UserID || user.id, 
      email: user.Email || user.email 
    });

    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}`);
  } catch (error) {
    console.error('네이버 로그인 에러:', error);
    res.redirect(`${process.env.FRONTEND_URL}/login?error=naver_login_failed`);
  }
}; 