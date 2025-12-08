require('dotenv').config();

const express = require('express');
const cors = require('cors');

const healthRoutes = require('./routes/health');
const analysisRoutes = require('./routes/analysis');

const app = express();
const PORT = process.env.PORT || 80;

// 미들웨어
app.use(cors());
app.use(express.json());

// 라우트 연결
app.use('/', healthRoutes);
app.use('/', analysisRoutes);

// 404 처리
app.use((req, res, next) => {
  res.status(404).json({ error: 'Not Found', path: req.originalUrl });
});

// 공통 에러 핸들러
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal Server Error' });
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`Jeonse main server running on port ${PORT}`);
});

