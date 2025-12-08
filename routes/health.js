const express = require('express');
const router = express.Router();

// 헬스 체크
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'jeonse-main',
    timestamp: new Date().toISOString(),
  });
});

// DB 헬스 체크 (db.js 사용)
const db = require('../db');

router.get('/db-health', async (req, res, next) => {
  try {
    const [rows] = await db.query('SELECT 1 AS ok');
    res.json({ db: 'ok', result: rows });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
