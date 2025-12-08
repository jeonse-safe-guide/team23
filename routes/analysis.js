const express = require('express');
const router = express.Router();

// 분석 요청 API (더미 로직)
router.post('/analysis/request', (req, res) => {
  const { address, deposit, jeonseType } = req.body || {};

  if (!address || !deposit) {
    return res.status(400).json({ error: 'address와 deposit은 필수입니다.' });
  }

  let riskScore = 50;
  const reasons = [];

  if (deposit > 300000000) {
    riskScore += 20;
    reasons.push('보증금이 3억 이상으로 고액 전세입니다.');
  }

  if (jeonseType === '다가구' || jeonseType === '원룸주택') {
    riskScore += 10;
    reasons.push('다가구/원룸주택 유형으로 구조적 위험이 있을 수 있습니다.');
  }

  if (riskScore > 100) riskScore = 100;

  res.json({
    address,
    deposit,
    jeonseType,
    riskScore,
    riskLevel: riskScore >= 70 ? 'HIGH' : riskScore >= 40 ? 'MEDIUM' : 'LOW',
    reasons,
  });
});

// 샘플 조회용 더미 API
router.get('/analysis/sample', (req, res) => {
  res.json({
    address: '서울시 ...',
    deposit: 200000000,
    jeonseType: '아파트',
    riskScore: 35,
    riskLevel: 'LOW',
    reasons: ['근저당 비율이 낮고, 시세 대비 보증금이 적정 수준입니다.'],
  });
});

module.exports = router;
