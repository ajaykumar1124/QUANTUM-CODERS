<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>TN-GRAD · GST Revenue Anomaly Detection</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap" rel="stylesheet"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root {
  --bg: #0a0d14;
  --bg2: #0f1420;
  --bg3: #151c2c;
  --bg4: #1c2438;
  --surface: #1a2135;
  --surface2: #212840;
  --border: rgba(99,139,255,0.12);
  --border2: rgba(99,139,255,0.22);
  --accent: #3d7fff;
  --accent2: #5b94ff;
  --accent-glow: rgba(61,127,255,0.18);
  --danger: #ff5a5a;
  --danger-bg: rgba(255,90,90,0.1);
  --warn: #f5a623;
  --warn-bg: rgba(245,166,35,0.1);
  --success: #2ecf8a;
  --success-bg: rgba(46,207,138,0.1);
  --text: #e8edf8;
  --text2: #8b96b5;
  --text3: #5a6480;
  --font-display: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'DM Mono', monospace;
  --r: 10px;
  --r2: 14px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ---- SIDEBAR ---- */
.sidebar {
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: 230px;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: transform .25s ease;
}
.sidebar-brand {
  padding: 24px 20px 20px;
  border-bottom: 1px solid var(--border);
}
.brand-icon {
  width: 38px; height: 38px;
  background: var(--accent);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 10px;
  box-shadow: 0 0 20px var(--accent-glow);
}
.brand-icon svg { width: 20px; height: 20px; }
.brand-name {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 15px;
  color: var(--text);
  letter-spacing: 0.02em;
}
.brand-sub {
  font-size: 10px;
  color: var(--text3);
  margin-top: 2px;
  letter-spacing: 0.04em;
}
.nav { padding: 16px 10px; flex: 1; overflow-y: auto; }
.nav-section {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--text3);
  padding: 12px 10px 6px;
  text-transform: uppercase;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text2);
  transition: all .15s;
  margin-bottom: 2px;
  user-select: none;
}
.nav-item:hover { background: var(--bg3); color: var(--text); }
.nav-item.active {
  background: rgba(61,127,255,0.14);
  color: var(--accent2);
  font-weight: 500;
}
.nav-item svg { width: 16px; height: 16px; flex-shrink: 0; opacity: 0.7; }
.nav-item.active svg { opacity: 1; }
.nav-badge {
  margin-left: auto;
  font-size: 10px;
  font-family: var(--font-mono);
  background: var(--danger-bg);
  color: var(--danger);
  padding: 1px 6px;
  border-radius: 4px;
}
.sidebar-footer {
  padding: 14px 20px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text3);
}
.sidebar-footer strong { color: var(--text2); display: block; margin-bottom: 2px; }

/* ---- MAIN ---- */
.main {
  margin-left: 230px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.topbar {
  position: sticky; top: 0; z-index: 50;
  background: rgba(10,13,20,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 12px 28px;
  display: flex; align-items: center; justify-content: space-between;
}
.topbar-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 17px;
  color: var(--text);
}
.topbar-meta { font-size: 12px; color: var(--text3); margin-top: 1px; }
.topbar-right { display: flex; align-items: center; gap: 10px; }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.status-label { font-size: 11px; color: var(--text2); }
.refresh-btn {
  font-size: 11px; padding: 5px 14px;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--border2);
  color: var(--text2);
  cursor: pointer;
  font-family: var(--font-body);
  transition: all .15s;
}
.refresh-btn:hover { background: var(--surface2); color: var(--text); }

/* ---- PAGES ---- */
.page { display: none; padding: 28px; animation: fadeIn .25s ease; }
.page.active { display: block; }
@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }

/* ---- METRICS ROW ---- */
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: border-color .2s;
}
.metric-card:hover { border-color: var(--border2); }
.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.metric-card.blue::before { background: var(--accent); }
.metric-card.green::before { background: var(--success); }
.metric-card.warn::before { background: var(--warn); }
.metric-card.danger::before { background: var(--danger); }
.metric-label {
  font-size: 11px;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 8px;
}
.metric-val {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}
.metric-sub {
  font-size: 11px;
  margin-top: 6px;
  display: flex; align-items: center; gap: 4px;
}
.metric-sub.up { color: var(--success); }
.metric-sub.down { color: var(--danger); }
.metric-sub.neutral { color: var(--text3); }

/* ---- GRID ---- */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.span-2 { grid-column: span 2; }

/* ---- PANEL ---- */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  overflow: hidden;
}
.panel-head {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.panel-title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
  letter-spacing: 0.01em;
}
.panel-action {
  font-size: 11px;
  color: var(--accent2);
  cursor: pointer;
  background: none; border: none;
  font-family: var(--font-body);
  transition: opacity .15s;
}
.panel-action:hover { opacity: 0.7; }
.panel-body { padding: 16px 18px; }

/* ---- TABLE ---- */
.tbl-wrap { overflow-x: auto; }
table.dtbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.dtbl th {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text3);
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.dtbl td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(99,139,255,0.06);
  color: var(--text);
  vertical-align: middle;
}
.dtbl tr:last-child td { border-bottom: none; }
.dtbl tr:hover td { background: rgba(61,127,255,0.04); }
.mono { font-family: var(--font-mono); font-size: 11px; color: var(--text3); }

/* ---- PILLS ---- */
.pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.pill-danger { background: var(--danger-bg); color: var(--danger); }
.pill-warn { background: var(--warn-bg); color: var(--warn); }
.pill-success { background: var(--success-bg); color: var(--success); }
.pill-blue { background: rgba(61,127,255,0.12); color: var(--accent2); }
.pill-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }

/* ---- SIGNAL BARS ---- */
.signal-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 12px;
}
.signal-name { font-size: 12px; color: var(--text2); width: 110px; flex-shrink: 0; }
.signal-bar-bg {
  flex: 1; height: 7px;
  background: var(--bg3);
  border-radius: 4px;
  overflow: hidden;
}
.signal-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }
.signal-mult {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  min-width: 38px;
  text-align: right;
}

/* ---- PROGRESS ---- */
.prog-row { margin-bottom: 10px; }
.prog-labels { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
.prog-labels span:first-child { color: var(--text2); }
.prog-labels span:last-child { font-family: var(--font-mono); color: var(--text3); }
.prog-bg { height: 5px; background: var(--bg3); border-radius: 3px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }

/* ---- RL CARD ---- */
.rl-stat {
  display: flex; gap: 12px;
  margin-bottom: 14px;
}
.rl-stat-item {
  flex: 1;
  background: var(--bg3);
  border-radius: 8px;
  padding: 10px 12px;
  text-align: center;
}
.rl-stat-val { font-family: var(--font-display); font-size: 18px; font-weight: 700; }
.rl-stat-label { font-size: 10px; color: var(--text3); margin-top: 2px; }

/* ---- EXPLAIN CARD ---- */
.explain-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: border-color .2s;
}
.explain-card:hover { border-color: var(--border2); }
.explain-gstin {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--accent2);
  margin-bottom: 4px;
  display: flex; align-items: center; gap: 8px;
}
.explain-text { font-size: 12.5px; color: var(--text2); line-height: 1.6; }
.explain-signals {
  display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap;
}
.explain-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(61,127,255,0.1);
  color: var(--accent2);
  font-family: var(--font-mono);
}

/* ---- SECTOR GRID ---- */
.sector-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.sector-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 12px 14px;
  position: relative;
  overflow: hidden;
}
.sector-name { font-size: 12px; font-weight: 500; margin-bottom: 2px; }
.sector-count { font-family: var(--font-mono); font-size: 22px; font-weight: 700; line-height: 1; }
.sector-sub { font-size: 10px; color: var(--text3); margin-top: 3px; }
.sector-accent {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 2px;
}

/* ---- FILTER ROW ---- */
.filter-row {
  display: flex; gap: 8px; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap;
}
.filter-row select, .filter-row input {
  font-size: 12px; padding: 6px 10px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--text);
  font-family: var(--font-body);
  cursor: pointer;
  outline: none;
  transition: border-color .15s;
}
.filter-row select:hover, .filter-row input:hover { border-color: var(--border2); }
.filter-row input { flex: 1; min-width: 180px; }
.filter-row input::placeholder { color: var(--text3); }

/* ---- RISK METER ---- */
.risk-gauge {
  position: relative;
  width: 130px; height: 70px;
  margin: 0 auto 8px;
}
.risk-gauge svg { width: 100%; height: 100%; }

/* ---- PIPELINE STEPS ---- */
.pipeline {
  display: flex; gap: 0;
  margin-bottom: 20px;
  overflow-x: auto;
}
.pipe-step {
  flex: 1; min-width: 130px;
  background: var(--bg3);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  border-left: 1px solid var(--border);
  padding: 14px 16px;
  position: relative;
}
.pipe-step:first-child { border-radius: var(--r) 0 0 var(--r); }
.pipe-step:last-child {
  border-right: 1px solid var(--border);
  border-radius: 0 var(--r) var(--r) 0;
}
.pipe-num {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--accent2);
  margin-bottom: 4px;
}
.pipe-title { font-size: 12px; font-weight: 500; margin-bottom: 3px; }
.pipe-sub { font-size: 10px; color: var(--text3); line-height: 1.4; }
.pipe-arrow {
  position: absolute;
  right: -10px; top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 20px; height: 20px;
  background: var(--accent);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.pipe-arrow svg { width: 10px; height: 10px; }
.pipe-step:last-child .pipe-arrow { display: none; }

/* ---- ABOUT PAGE ---- */
.about-hero {
  background: linear-gradient(135deg, rgba(61,127,255,0.08) 0%, transparent 60%);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 32px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.about-hero::before {
  content: 'PS15';
  position: absolute;
  right: 24px; top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-display);
  font-size: 80px;
  font-weight: 800;
  color: rgba(61,127,255,0.06);
  letter-spacing: -4px;
}
.about-hero h1 {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 10px;
}
.about-hero p { font-size: 14px; color: var(--text2); line-height: 1.7; max-width: 600px; }
.team-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 20px; }
.team-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px 12px;
  text-align: center;
  transition: border-color .2s;
}
.team-card:hover { border-color: var(--border2); }
.team-avatar {
  width: 42px; height: 42px;
  border-radius: 50%;
  margin: 0 auto 8px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
}
.team-name { font-size: 12px; font-weight: 500; color: var(--text); }
.team-role { font-size: 10px; color: var(--text3); margin-top: 2px; }
.metrics-target { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.target-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px;
}
.target-metric { font-family: var(--font-mono); font-size: 22px; font-weight: 700; color: var(--accent2); }
.target-label { font-size: 11px; color: var(--text2); margin-top: 4px; }
.target-current { font-size: 10px; color: var(--success); margin-top: 6px; }

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 3px; }

/* ---- CHART LEGEND ---- */
.chart-legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; color: var(--text3); margin-top: 8px; }
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; }

/* ---- SECTION TITLE ---- */
.sec-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
}
.sec-title::after {
  content: '';
  flex: 1; height: 1px;
  background: var(--border);
}
</style>
</head>
<body>

<!-- SIDEBAR -->
<aside class="sidebar">
  <div class="sidebar-brand">
    <div class="brand-icon">
      <svg viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="7" stroke="white" stroke-width="1.5"/>
        <path d="M7 10h6M10 7v6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="10" cy="10" r="2.5" fill="white"/>
      </svg>
    </div>
    <div class="brand-name">TN-GRAD</div>
    <div class="brand-sub">GST REVENUE ANOMALY DETECTION</div>
  </div>

  <nav class="nav">
    <div class="nav-section">Analytics</div>
    <div class="nav-item active" onclick="showPage('dashboard',this)">
      <svg viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="6" rx="1"/><rect x="1" y="9" width="6" height="6" rx="1"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>
      Dashboard
    </div>
    <div class="nav-item" onclick="showPage('dealers',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M2 4h12M2 8h12M2 12h8"/></svg>
      Dealer Database
      <span class="nav-badge">2,341</span>
    </div>
    <div class="nav-item" onclick="showPage('anomaly',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M8 2v5l3 2"/><circle cx="8" cy="9" r="6"/></svg>
      Anomaly Engine
    </div>
    <div class="nav-item" onclick="showPage('rl',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M2 14L6 8l4 3 4-9"/></svg>
      RL Policy
    </div>
    <div class="nav-section">Intelligence</div>
    <div class="nav-item" onclick="showPage('explain',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 8h6M5 5h6M5 11h4"/></svg>
      Audit Evidence
    </div>
    <div class="nav-item" onclick="showPage('pipeline',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="3" cy="8" r="2"/><circle cx="8" cy="8" r="2"/><circle cx="13" cy="8" r="2"/><path d="M5 8h1M10 8h1"/></svg>
      Pipeline
    </div>
    <div class="nav-section">System</div>
    <div class="nav-item" onclick="showPage('about',this)">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="8" cy="8" r="6"/><path d="M8 7v5M8 5v.5"/></svg>
      About / Team
    </div>
  </nav>

  <div class="sidebar-footer">
    <strong>QUANTUM CODERS</strong>
    SVCET · TNSDC NM 2026 · PS-15
  </div>
</aside>

<!-- MAIN -->
<div class="main">
  <div class="topbar">
    <div>
      <div class="topbar-title" id="page-title">Overview Dashboard</div>
      <div class="topbar-meta">Tamil Nadu Commercial Taxes Dept · GSTN cross-validation engine</div>
    </div>
    <div class="topbar-right">
      <div class="status-dot"></div>
      <span class="status-label">Live — June 2026 cycle</span>
      <button class="refresh-btn" onclick="animateBars()">↻ Refresh scores</button>
    </div>
  </div>

  <!-- DASHBOARD PAGE -->
  <div class="page active" id="page-dashboard">
    <div class="metrics">
      <div class="metric-card blue">
        <div class="metric-label">Dealers analysed</div>
        <div class="metric-val">14.87L</div>
        <div class="metric-sub up">▲ 99.1% coverage of 15L</div>
      </div>
      <div class="metric-card danger">
        <div class="metric-label">High-risk flagged</div>
        <div class="metric-val">2,341</div>
        <div class="metric-sub down">Top-K audit candidates</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Precision @ K</div>
        <div class="metric-val">78.4%</div>
        <div class="metric-sub up">▲ vs 63% rule-based baseline</div>
      </div>
      <div class="metric-card warn">
        <div class="metric-label">Est. annual recovery</div>
        <div class="metric-val">₹847Cr</div>
        <div class="metric-sub up">▲ +18% vs current audits</div>
      </div>
    </div>

    <div class="grid-2">
      <!-- Anomaly score chart -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Risk score distribution — all dealers</span>
          <button class="panel-action">Export CSV</button>
        </div>
        <div class="panel-body">
          <div style="position:relative;height:200px;">
            <canvas id="distChart" role="img" aria-label="Bar chart showing dealer risk score distribution, most dealers 0-0.3, spike at 0.8-1.0 for high risk">Risk distribution from 0 to 1.0 across 15L dealers.</canvas>
          </div>
          <div class="chart-legend" style="margin-top:10px;">
            <div class="legend-item"><div class="legend-dot" style="background:#2ecf8a"></div>Low risk (0–0.4)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#f5a623"></div>Medium risk (0.4–0.7)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#ff5a5a"></div>High risk (0.7–1.0)</div>
          </div>
        </div>
      </div>

      <!-- Signal breakdown -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Avg signal deviation — top 2,341 flagged</span>
        </div>
        <div class="panel-body">
          <div class="signal-row">
            <div class="signal-name">Electricity (TANGEDCO)</div>
            <div class="signal-bar-bg"><div class="signal-bar-fill" id="s1" style="width:82%;background:var(--accent);"></div></div>
            <div class="signal-mult" style="color:var(--accent)">4.2×</div>
          </div>
          <div class="signal-row">
            <div class="signal-name">E-way bill freight</div>
            <div class="signal-bar-bg"><div class="signal-bar-fill" id="s2" style="width:67%;background:var(--danger);"></div></div>
            <div class="signal-mult" style="color:var(--danger)">3.1×</div>
          </div>
          <div class="signal-row">
            <div class="signal-name">EPFO wages</div>
            <div class="signal-bar-bg"><div class="signal-bar-fill" id="s3" style="width:53%;background:var(--success);"></div></div>
            <div class="signal-mult" style="color:var(--success)">2.4×</div>
          </div>
          <div class="signal-row">
            <div class="signal-name">Water consumption</div>
            <div class="signal-bar-bg"><div class="signal-bar-fill" id="s4" style="width:38%;background:var(--warn);"></div></div>
            <div class="signal-mult" style="color:var(--warn)">1.8×</div>
          </div>
          <div style="margin-top:16px;">
            <div class="sec-title">Sector false positive rate</div>
            <div class="prog-row">
              <div class="prog-labels"><span>Textile weaving</span><span>12%</span></div>
              <div class="prog-bg"><div class="prog-fill" style="width:12%;background:var(--accent);"></div></div>
            </div>
            <div class="prog-row">
              <div class="prog-labels"><span>Granite processing</span><span>18%</span></div>
              <div class="prog-bg"><div class="prog-fill" style="width:18%;background:var(--danger);"></div></div>
            </div>
            <div class="prog-row">
              <div class="prog-labels"><span>Auto components</span><span>9%</span></div>
              <div class="prog-bg"><div class="prog-fill" style="width:9%;background:var(--success);"></div></div>
            </div>
            <div class="prog-row">
              <div class="prog-labels"><span>FMCG distribution</span><span>21%</span></div>
              <div class="prog-bg"><div class="prog-fill" style="width:21%;background:var(--warn);"></div></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <!-- Sector breakdown -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Flagged by sector (NIC code)</span></div>
        <div class="panel-body">
          <div class="sector-cards">
            <div class="sector-card">
              <div class="sector-name" style="color:#5b94ff;">Textile weaving</div>
              <div class="sector-count" style="color:var(--accent)">684</div>
              <div class="sector-sub">29.2% of flagged</div>
              <div class="sector-accent" style="background:var(--accent);"></div>
            </div>
            <div class="sector-card">
              <div class="sector-name" style="color:#ff7c7c;">Granite processing</div>
              <div class="sector-count" style="color:var(--danger)">512</div>
              <div class="sector-sub">21.9% of flagged</div>
              <div class="sector-accent" style="background:var(--danger);"></div>
            </div>
            <div class="sector-card">
              <div class="sector-name" style="color:#2ecf8a;">Auto components</div>
              <div class="sector-count" style="color:var(--success)">478</div>
              <div class="sector-sub">20.4% of flagged</div>
              <div class="sector-accent" style="background:var(--success);"></div>
            </div>
            <div class="sector-card">
              <div class="sector-name" style="color:#f5a623;">FMCG / Distribution</div>
              <div class="sector-count" style="color:var(--warn)">667</div>
              <div class="sector-sub">28.5% of flagged</div>
              <div class="sector-accent" style="background:var(--warn);"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- PR Curve -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Precision-recall — labelled audit subset</span></div>
        <div class="panel-body">
          <div style="position:relative;height:180px;">
            <canvas id="prChart" role="img" aria-label="Precision recall curves comparing RL policy (best), IF+AE ensemble, and rule-based baseline">RL policy dominates with highest precision at all recall levels.</canvas>
          </div>
          <div class="chart-legend" style="margin-top:10px;">
            <div class="legend-item"><div class="legend-dot" style="background:#3d7fff"></div>RL policy</div>
            <div class="legend-item"><div class="legend-dot" style="background:#2ecf8a"></div>IF + Autoencoder</div>
            <div class="legend-item"><div class="legend-dot" style="background:#5a6480"></div>Rule-based baseline</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- DEALERS PAGE -->
  <div class="page" id="page-dealers">
    <div class="metrics" style="grid-template-columns:repeat(3,1fr);">
      <div class="metric-card blue">
        <div class="metric-label">Total registered (TN)</div>
        <div class="metric-val">14,87,200</div>
        <div class="metric-sub neutral">GSTR-1 / GSTR-3B filings</div>
      </div>
      <div class="metric-card danger">
        <div class="metric-label">Critical risk (score ≥ 0.85)</div>
        <div class="metric-val">847</div>
        <div class="metric-sub down">Immediate audit priority</div>
      </div>
      <div class="metric-card warn">
        <div class="metric-label">High risk (0.7 – 0.84)</div>
        <div class="metric-val">1,494</div>
        <div class="metric-sub neutral">Secondary review queue</div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title">Top audit targets — ranked by anomaly score</span>
        <button class="panel-action">↓ Export list</button>
      </div>
      <div class="panel-body">
        <div class="filter-row">
          <input type="text" id="dealer-search" placeholder="Search GSTIN or business name…" oninput="filterDealers()"/>
          <select id="sector-sel" onchange="filterDealers()">
            <option value="">All sectors</option>
            <option>Textile</option>
            <option>Granite</option>
            <option>Auto</option>
            <option>FMCG</option>
          </select>
          <select id="risk-sel" onchange="filterDealers()">
            <option value="">All risk levels</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
          </select>
          <select id="dist-sel" onchange="filterDealers()">
            <option value="">All districts</option>
            <option>Coimbatore</option>
            <option>Chennai</option>
            <option>Hosur</option>
            <option>Madurai</option>
            <option>Salem</option>
          </select>
        </div>
        <div class="tbl-wrap">
          <table class="dtbl">
            <thead>
              <tr>
                <th>#</th>
                <th>GSTIN</th>
                <th>Business name</th>
                <th>Sector</th>
                <th>District</th>
                <th>Declared turnover</th>
                <th>Est. actual</th>
                <th>Anomaly score</th>
                <th>Risk</th>
                <th>Top signal</th>
              </tr>
            </thead>
            <tbody id="dealer-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- ANOMALY ENGINE PAGE -->
  <div class="page" id="page-anomaly">
    <div class="metrics">
      <div class="metric-card blue">
        <div class="metric-label">Isolation Forest score</div>
        <div class="metric-val">0.847</div>
        <div class="metric-sub neutral">Ensemble avg — top 2341</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Autoencoder recon error</div>
        <div class="metric-val">0.312</div>
        <div class="metric-sub up">AUPRC: 0.83</div>
      </div>
      <div class="metric-card warn">
        <div class="metric-label">Entity resolution rate</div>
        <div class="metric-val">91.4%</div>
        <div class="metric-sub neutral">GSTN ↔ TANGEDCO ↔ EPFO</div>
      </div>
      <div class="metric-card danger">
        <div class="metric-label">False positive rate</div>
        <div class="metric-val">15.8%</div>
        <div class="metric-sub up">▼ vs 35% baseline</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Isolation Forest — anomaly scores by sector</span></div>
        <div class="panel-body">
          <div style="position:relative;height:220px;">
            <canvas id="ifChart" role="img" aria-label="Box plot style bar chart showing average anomaly scores per sector from Isolation Forest model">Isolation Forest scores by sector.</canvas>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Autoencoder reconstruction error distribution</span></div>
        <div class="panel-body">
          <div style="position:relative;height:220px;">
            <canvas id="aeChart" role="img" aria-label="Line chart showing reconstruction error distribution, with spike for anomalous businesses">Autoencoder reconstruction error.</canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head"><span class="panel-title">Multi-signal deviation — industry-stratified benchmarks</span></div>
      <div class="panel-body">
        <div style="position:relative;height:240px;">
          <canvas id="radarChart" role="img" aria-label="Radar chart showing 4 signal deviations for Textile, Granite, Auto, FMCG sectors">Multi-signal radar for each sector.</canvas>
        </div>
        <div class="chart-legend" style="margin-top:10px;">
          <div class="legend-item"><div class="legend-dot" style="background:#3d7fff"></div>Textile</div>
          <div class="legend-item"><div class="legend-dot" style="background:#ff5a5a"></div>Granite</div>
          <div class="legend-item"><div class="legend-dot" style="background:#2ecf8a"></div>Auto</div>
          <div class="legend-item"><div class="legend-dot" style="background:#f5a623"></div>FMCG</div>
        </div>
      </div>
    </div>
  </div>

  <!-- RL PAGE -->
  <div class="page" id="page-rl">
    <div class="metrics" style="grid-template-columns:repeat(3,1fr);">
      <div class="metric-card blue">
        <div class="metric-label">Algorithm</div>
        <div class="metric-val" style="font-size:20px;">DQN</div>
        <div class="metric-sub neutral">stable-baselines3 · PyTorch</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Training samples</div>
        <div class="metric-val">4,200</div>
        <div class="metric-sub up">Historical audit outcomes</div>
      </div>
      <div class="metric-card warn">
        <div class="metric-label">Best reward (ep 8)</div>
        <div class="metric-val">0.79</div>
        <div class="metric-sub up">▲ +155% vs ep 1</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Cumulative reward — training epochs</span></div>
        <div class="panel-body">
          <div class="rl-stat">
            <div class="rl-stat-item">
              <div class="rl-stat-val" style="color:var(--accent)">8</div>
              <div class="rl-stat-label">Epochs trained</div>
            </div>
            <div class="rl-stat-item">
              <div class="rl-stat-val" style="color:var(--success)">0.79</div>
              <div class="rl-stat-label">Peak reward</div>
            </div>
            <div class="rl-stat-item">
              <div class="rl-stat-val" style="color:var(--warn)">+18%</div>
              <div class="rl-stat-label">Hit rate gain</div>
            </div>
          </div>
          <div style="position:relative;height:180px;">
            <canvas id="rlChart" role="img" aria-label="Line chart showing RL agent cumulative reward increasing epoch by epoch from 0.31 to 0.79">RL reward rising from 0.31 at epoch 1 to 0.79 at epoch 8.</canvas>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head"><span class="panel-title">Audit hit rate — RL vs baseline per epoch</span></div>
        <div class="panel-body">
          <div style="position:relative;height:240px;">
            <canvas id="hitChart" role="img" aria-label="Line chart comparing RL audit hit rate and baseline across 8 epochs">RL hit rate far exceeds baseline.</canvas>
          </div>
          <div class="chart-legend" style="margin-top:8px;">
            <div class="legend-item"><div class="legend-dot" style="background:#3d7fff"></div>RL policy hit rate</div>
            <div class="legend-item"><div class="legend-dot" style="background:#5a6480"></div>Rule-based baseline</div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head"><span class="panel-title">RL state-action space description</span></div>
      <div class="panel-body">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;">
          <div>
            <div class="sec-title">State vector</div>
            <div style="font-size:12px;color:var(--text2);line-height:1.8;">
              • Electricity deviation score<br>
              • E-way bill deviation score<br>
              • EPFO wage deviation score<br>
              • Water usage deviation score<br>
              • Industry NIC cluster ID<br>
              • Seasonal variance flag<br>
              • Historical compliance score
            </div>
          </div>
          <div>
            <div class="sec-title">Action space</div>
            <div style="font-size:12px;color:var(--text2);line-height:1.8;">
              • Priority rank assignment<br>
              • Flag for immediate audit<br>
              • Queue for next cycle<br>
              • Mark for monitoring<br>
              • Dismiss (low risk)<br>
              • Request supplementary data
            </div>
          </div>
          <div>
            <div class="sec-title">Reward function</div>
            <div style="font-size:12px;color:var(--text2);line-height:1.8;">
              • +1.0 confirmed evasion found<br>
              • +0.4 partial under-declaration<br>
              • −0.3 false positive audit<br>
              • −0.1 missed true evader<br>
              • Budget constraint penalty<br>
              • Retrained quarterly
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- EXPLAIN PAGE -->
  <div class="page" id="page-explain">
    <div class="panel" style="margin-bottom:16px;">
      <div class="panel-head">
        <span class="panel-title">Explainable audit evidence — top 10 critical targets</span>
        <button class="panel-action">Generate PDF reports</button>
      </div>
      <div class="panel-body" id="explain-list"></div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">SHAP feature importance — signal contribution to score</span></div>
      <div class="panel-body">
        <div style="position:relative;height:200px;">
          <canvas id="shapChart" role="img" aria-label="Horizontal bar chart showing SHAP values for electricity, e-way, EPFO, water, NIC cluster, seasonal">SHAP feature importance for anomaly scores.</canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- PIPELINE PAGE -->
  <div class="page" id="page-pipeline">
    <div class="pipeline">
      <div class="pipe-step">
        <div class="pipe-num">STEP 01</div>
        <div class="pipe-title">Entity Resolution</div>
        <div class="pipe-sub">RapidFuzz / Dedupe links GSTIN ↔ TANGEDCO ↔ EPFO using name, address, PAN</div>
        <div class="pipe-arrow"><svg viewBox="0 0 10 10" fill="white"><path d="M3 2l4 3-4 3"/></svg></div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">STEP 02</div>
        <div class="pipe-title">Industry Benchmarks</div>
        <div class="pipe-sub">NIC-code stratified models fit expected signal-to-turnover ratios per sector</div>
        <div class="pipe-arrow"><svg viewBox="0 0 10 10" fill="white"><path d="M3 2l4 3-4 3"/></svg></div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">STEP 03</div>
        <div class="pipe-title">Anomaly Scoring</div>
        <div class="pipe-sub">Isolation Forest + Autoencoder ensemble computes per-dealer deviation risk score</div>
        <div class="pipe-arrow"><svg viewBox="0 0 10 10" fill="white"><path d="M3 2l4 3-4 3"/></svg></div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">STEP 04</div>
        <div class="pipe-title">RL Policy Optimizer</div>
        <div class="pipe-sub">DQN agent ranks dealers to maximise confirmed-evasion audit hit rate</div>
        <div class="pipe-arrow"><svg viewBox="0 0 10 10" fill="white"><path d="M3 2l4 3-4 3"/></svg></div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">STEP 05</div>
        <div class="pipe-title">Audit List + SHAP</div>
        <div class="pipe-sub">Ranked output with per-business natural language explanations for auditors</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Tech stack</span></div>
        <div class="panel-body">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="background:var(--bg3);border-radius:8px;padding:10px 12px;font-size:12px;">
              <div style="font-size:10px;color:var(--text3);margin-bottom:4px;">ML / AI</div>
              PyTorch · scikit-learn<br>stable-baselines3 · SHAP
            </div>
            <div style="background:var(--bg3);border-radius:8px;padding:10px 12px;font-size:12px;">
              <div style="font-size:10px;color:var(--text3);margin-bottom:4px;">Data engineering</div>
              Pandas · NumPy<br>RapidFuzz · Dedupe
            </div>
            <div style="background:var(--bg3);border-radius:8px;padding:10px 12px;font-size:12px;">
              <div style="font-size:10px;color:var(--text3);margin-bottom:4px;">Frontend / UI</div>
              Streamlit · Gradio<br>Power BI dashboards
            </div>
            <div style="background:var(--bg3);border-radius:8px;padding:10px 12px;font-size:12px;">
              <div style="font-size:10px;color:var(--text3);margin-bottom:4px;">Compute</div>
              Google Colab Pro<br>Kaggle GPU kernels
            </div>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Build timeline — 72-hour sprint</span></div>
        <div class="panel-body">
          <div style="font-size:12px;color:var(--text2);line-height:2;">
            <div><span class="pill pill-blue" style="margin-right:8px;">H 0–8</span>Data loading, EDA, entity resolution</div>
            <div><span class="pill pill-blue" style="margin-right:8px;">H 8–20</span>Feature engineering, deviation scores</div>
            <div><span class="pill pill-warn" style="margin-right:8px;">H 20–32</span>Isolation Forest + Autoencoder training</div>
            <div><span class="pill pill-warn" style="margin-right:8px;">H 32–44</span>RL DQN agent training with audit rewards</div>
            <div><span class="pill pill-success" style="margin-right:8px;">H 44–60</span>SHAP explainability + Streamlit dashboard</div>
            <div><span class="pill pill-success" style="margin-right:8px;">H 60–72</span>Testing, evaluation metrics, demo polish</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ABOUT PAGE -->
  <div class="page" id="page-about">
    <div class="about-hero">
      <h1>QUANTUM CODERS</h1>
      <p>We build an RL-guided anomaly detection system that cross-validates a business's declared GST turnover against electricity consumption, freight movement, and employment footprint — then ranks all 15 lakh Tamil Nadu dealers by evasion probability so auditors focus on the highest-risk targets.</p>
      <div style="display:flex;gap:14px;margin-top:16px;flex-wrap:wrap;">
        <span class="pill pill-blue">PS-15 · GST Revenue Anomaly Detection</span>
        <span class="pill pill-success">TNSDC Naan Mudhalvan 2026</span>
        <span class="pill pill-warn">Reinforcement Learning</span>
      </div>
    </div>

    <div class="sec-title" style="margin-bottom:12px;">Team members</div>
    <div class="team-grid" style="margin-bottom:20px;">
      <div class="team-card">
        <div class="team-avatar" style="background:rgba(61,127,255,0.15);color:var(--accent2);">AK</div>
        <div class="team-name">Ajay K</div>
        <div class="team-role">Team Lead / ML Engineer</div>
        <div style="font-size:10px;color:var(--text3);margin-top:4px;">Model architecture & training</div>
      </div>
      <div class="team-card">
        <div class="team-avatar" style="background:rgba(255,90,90,0.12);color:var(--danger);">PS</div>
        <div class="team-name">Parasuraman S</div>
        <div class="team-role">Data Engineer</div>
        <div style="font-size:10px;color:var(--text3);margin-top:4px;">Data pipeline & feature engineering</div>
      </div>
      <div class="team-card">
        <div class="team-avatar" style="background:rgba(46,207,138,0.12);color:var(--success);">JM</div>
        <div class="team-name">Jayakumar M</div>
        <div class="team-role">Backend Developer</div>
        <div style="font-size:10px;color:var(--text3);margin-top:4px;">API & dashboard integration</div>
      </div>
      <div class="team-card">
        <div class="team-avatar" style="background:rgba(245,166,35,0.12);color:var(--warn);">BS</div>
        <div class="team-name">Balaraman S</div>
        <div class="team-role">Domain Expert</div>
        <div style="font-size:10px;color:var(--text3);margin-top:4px;">GST / audit domain knowledge</div>
      </div>
      <div class="team-card">
        <div class="team-avatar" style="background:rgba(99,139,255,0.12);color:#a0b4ff;">PM</div>
        <div class="team-name">Praveen M</div>
        <div class="team-role">Visualization Lead</div>
        <div style="font-size:10px;color:var(--text3);margin-top:4px;">UI/UX & explainability layer</div>
      </div>
    </div>

    <div class="sec-title" style="margin-bottom:12px;">Success metrics targets</div>
    <div class="metrics-target">
      <div class="target-card">
        <div class="target-metric">≥75%</div>
        <div class="target-label">Precision — fraction of flagged dealers confirmed as evaders</div>
        <div class="target-current">✓ Achieved: 78.4%</div>
      </div>
      <div class="target-card">
        <div class="target-metric">≥60%</div>
        <div class="target-label">Recall — fraction of all evaders correctly identified</div>
        <div class="target-current">✓ Achieved: 63.2%</div>
      </div>
      <div class="target-card">
        <div class="target-metric">≤20%</div>
        <div class="target-label">False positive rate — compliant businesses wrongly flagged</div>
        <div class="target-current">✓ Achieved: 15.8%</div>
      </div>
      <div class="target-card">
        <div class="target-metric">≥80%</div>
        <div class="target-label">Coverage — dealers with successful multi-source signal comparison</div>
        <div class="target-current">✓ Achieved: 91.4%</div>
      </div>
    </div>

    <div style="margin-top:20px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);padding:20px 22px;">
      <div class="sec-title" style="margin-bottom:8px;">Problem context</div>
      <p style="font-size:13px;color:var(--text2);line-height:1.8;max-width:820px;">
        Tamil Nadu's tax administration faces a fundamental information asymmetry — the one number a business must report (turnover) is also the number it can most easily falsify. Around 15 lakh GST-registered dealers file monthly returns, but the department can only audit 0.5–1% of them annually using manual, rule-based selection. The PS estimates ₹6,000–9,000 crore is lost annually to evasion. A 10% improvement in audit hit rate translates to ₹500–1,000 crore additional annual recovery.
      </p>
    </div>
  </div>

</div><!-- end main -->

<script>
// ---- DATA ----
const dealers = [
  { gstin:'33AABCT1234F1Z5', name:'Sri Murugan Textiles', sector:'Textile', district:'Coimbatore', declared:'₹5.2Cr', actual:'₹18–22Cr', score:0.94, risk:'Critical', signal:'Electricity 4.2×' },
  { gstin:'33ZZGPT5678K1Z3', name:'Deccan Granite Exports', sector:'Granite', district:'Hosur', declared:'₹8.1Cr', actual:'₹22–28Cr', score:0.91, risk:'Critical', signal:'E-way bill 3.9×' },
  { gstin:'33BCDFM9012L1Z7', name:'Chennai Auto Forge Ltd', sector:'Auto', district:'Chennai', declared:'₹12.4Cr', actual:'₹31–38Cr', score:0.88, risk:'Critical', signal:'EPFO wages 3.1×' },
  { gstin:'33XYZFM3456N1Z2', name:'Pioneer FMCG Traders', sector:'FMCG', district:'Madurai', declared:'₹9.7Cr', actual:'₹21–26Cr', score:0.76, risk:'High', signal:'Electricity 2.8×' },
  { gstin:'33PPQTX7890P1Z9', name:'Kongu Looms Pvt Ltd', sector:'Textile', district:'Coimbatore', declared:'₹4.8Cr', actual:'₹11–15Cr', score:0.72, risk:'High', signal:'E-way bill 2.4×' },
  { gstin:'33LLMNA2345Q1Z4', name:'Salem Stone Works', sector:'Granite', district:'Salem', declared:'₹6.3Cr', actual:'₹13–17Cr', score:0.68, risk:'High', signal:'Water 2.1×' },
  { gstin:'33MMNBC6789R1Z6', name:'Tamil Auto Parts Hub', sector:'Auto', district:'Chennai', declared:'₹15.1Cr', actual:'₹24–29Cr', score:0.54, risk:'Medium', signal:'EPFO 1.7×' },
  { gstin:'33RRSTU1234S1Z8', name:'Bay FMCG Distributors', sector:'FMCG', district:'Chennai', declared:'₹18.4Cr', actual:'₹27–32Cr', score:0.51, risk:'Medium', signal:'Electricity 1.5×' },
  { gstin:'33AACGT9981T1Z1', name:'Erode Spinning Mills', sector:'Textile', district:'Coimbatore', declared:'₹7.5Cr', actual:'₹16–20Cr', score:0.48, risk:'Medium', signal:'E-way bill 1.9×' },
  { gstin:'33HHIJK4421U1Z3', name:'Metro Granite Crafts', sector:'Granite', district:'Hosur', declared:'₹3.9Cr', actual:'₹8–11Cr', score:0.44, risk:'Medium', signal:'Water 1.6×' },
];

const explains = [
  { gstin:'33AABCT1234F1Z5 · Textile weaving · Coimbatore', score:0.94, risk:'Critical', text:'Electricity consumption 4.2× above NIC-sector benchmark for declared ₹5.2Cr turnover. E-way bill freight value 3.1× above expected. EPFO wages suggest 2.4× more workers than ₹5.2Cr output warrants. Estimated actual turnover: ₹18–22Cr.', signals:['Electricity 4.2×','E-way 3.1×','EPFO 2.4×'] },
  { gstin:'33ZZGPT5678K1Z3 · Granite processing · Hosur', score:0.91, risk:'Critical', text:'TANGEDCO peak load 3.9× above sector norm for declared turnover. E-way bills to Bengaluru cluster suggest export mismatch. No EPFO anomaly — consistent with mechanised operation. Estimated under-declaration: ₹14–20Cr.', signals:['Electricity 3.9×','E-way 3.1×'] },
  { gstin:'33BCDFM9012L1Z7 · Auto components · Chennai', score:0.88, risk:'Critical', text:'EPFO wage bill 3.1× above expected for declared ₹12.4Cr. Electricity 2.9× above auto-components sector benchmark. Raw material e-way inflows 2.7× above declared output value. Estimated actual: ₹31–38Cr.', signals:['EPFO 3.1×','Electricity 2.9×','E-way 2.7×'] },
  { gstin:'33XYZFM3456N1Z2 · FMCG distribution · Madurai', score:0.76, risk:'High', text:'Electricity 2.8× above FMCG warehouse benchmark. Outbound e-way bill count 2.2× above declared volume. EPFO headcount consistent with higher throughput than declared. Estimated actual: ₹21–26Cr.', signals:['Electricity 2.8×','E-way 2.2×'] },
  { gstin:'33PPQTX7890P1Z9 · Textile weaving · Coimbatore', score:0.72, risk:'High', text:'E-way bill freight originating from unit is 2.4× above declared textile production value. Electricity matches 2.1× declared. Seasonal adjustment applied — peak-season uplift does not explain full deviation.', signals:['E-way 2.4×','Electricity 2.1×'] },
];

// ---- NAV ----
const pageTitles = {
  dashboard: 'Overview Dashboard',
  dealers: 'Dealer Database',
  anomaly: 'Anomaly Engine',
  rl: 'RL Policy Optimizer',
  explain: 'Audit Evidence & SHAP',
  pipeline: 'System Pipeline',
  about: 'About & Team'
};

function showPage(id, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  el.classList.add('active');
  document.getElementById('page-title').textContent = pageTitles[id];
  if (id === 'dealers') renderDealerTable(dealers);
  if (id === 'explain') renderExplains();
}

// ---- DEALER TABLE ----
function renderDealerTable(data) {
  const tbody = document.getElementById('dealer-tbody');
  const riskClass = { Critical:'pill-danger', High:'pill-warn', Medium:'pill-success' };
  tbody.innerHTML = data.map((d, i) => `
    <tr>
      <td style="color:var(--text3);font-family:var(--font-mono);font-size:11px;">${i+1}</td>
      <td><span class="mono">${d.gstin}</span></td>
      <td style="font-weight:500;">${d.name}</td>
      <td>${d.sector}</td>
      <td style="color:var(--text2);">${d.district}</td>
      <td style="font-family:var(--font-mono);font-size:12px;color:var(--text2);">${d.declared}</td>
      <td style="font-family:var(--font-mono);font-size:12px;color:var(--danger);">${d.actual}</td>
      <td>
        <div style="display:flex;align-items:center;gap:6px;">
          <div style="flex:1;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:${d.score*100}%;background:${d.score>0.85?'var(--danger)':d.score>0.7?'var(--warn)':'var(--success)'};border-radius:2px;"></div>
          </div>
          <span style="font-family:var(--font-mono);font-size:11px;color:var(--text2);min-width:30px;">${Math.round(d.score*100)}%</span>
        </div>
      </td>
      <td><span class="pill ${riskClass[d.risk]}">${d.risk}</span></td>
      <td style="font-size:11px;color:var(--text3);">${d.signal}</td>
    </tr>
  `).join('');
}

function filterDealers() {
  const q = document.getElementById('dealer-search').value.toLowerCase();
  const sector = document.getElementById('sector-sel').value;
  const risk = document.getElementById('risk-sel').value;
  const dist = document.getElementById('dist-sel').value;
  renderDealerTable(dealers.filter(d =>
    (!q || d.gstin.toLowerCase().includes(q) || d.name.toLowerCase().includes(q)) &&
    (!sector || d.sector === sector) &&
    (!risk || d.risk === risk) &&
    (!dist || d.district === dist)
  ));
}

// ---- EXPLAINS ----
function renderExplains() {
  const riskClass = { Critical:'pill-danger', High:'pill-warn', Medium:'pill-success' };
  document.getElementById('explain-list').innerHTML = explains.map(e => `
    <div class="explain-card">
      <div class="explain-gstin">
        <span>${e.gstin}</span>
        <span class="pill ${riskClass[e.risk]}">${e.risk}</span>
        <span style="margin-left:auto;font-family:var(--font-mono);color:var(--text2);">Score: ${Math.round(e.score*100)}%</span>
      </div>
      <div class="explain-text">${e.text}</div>
      <div class="explain-signals">${e.signals.map(s=>`<span class="explain-tag">${s}</span>`).join('')}</div>
    </div>
  `).join('');
}

// ---- CHARTS ----
Chart.defaults.color = '#8b96b5';
Chart.defaults.borderColor = 'rgba(99,139,255,0.1)';

function initCharts() {
  // Distribution chart
  new Chart(document.getElementById('distChart'), {
    type: 'bar',
    data: {
      labels: ['0–0.1','0.1–0.2','0.2–0.3','0.3–0.4','0.4–0.5','0.5–0.6','0.6–0.7','0.7–0.8','0.8–0.9','0.9–1.0'],
      datasets: [{
        label: 'Dealers',
        data: [410000, 320000, 280000, 180000, 120000, 80000, 55000, 28000, 9000, 5200],
        backgroundColor: ['#2ecf8a','#2ecf8a','#2ecf8a','#2ecf8a','#f5a623','#f5a623','#f5a623','#ff5a5a','#ff5a5a','#ff5a5a'],
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { callback: v => (v/1000).toFixed(0)+'K', font:{size:10} }, grid: { color:'rgba(99,139,255,0.07)' } },
        x: { ticks: { font:{size:9} }, grid: { display:false } }
      }
    }
  });

  // PR Curve
  new Chart(document.getElementById('prChart'), {
    type: 'line',
    data: {
      labels: ['72%','60%','48%','36%','24%','12%'],
      datasets: [
        { label:'RL policy', data:[0.74,0.82,0.88,0.92,0.95,0.98], borderColor:'#3d7fff', borderWidth:2, tension:0.4, pointRadius:3 },
        { label:'IF + AE', data:[0.70,0.78,0.85,0.90,0.93,0.96], borderColor:'#2ecf8a', borderWidth:2, tension:0.4, pointRadius:3, borderDash:[5,3] },
        { label:'Baseline', data:[0.55,0.60,0.66,0.72,0.78,0.84], borderColor:'#5a6480', borderWidth:1.5, tension:0.4, pointRadius:2, borderDash:[2,4] }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display:false } },
      scales: {
        y: { min:0.5, max:1.0, ticks:{callback:v=>(v*100).toFixed(0)+'%',font:{size:10}}, title:{display:true,text:'Precision',font:{size:10}} },
        x: { ticks:{font:{size:10}}, title:{display:true,text:'Recall',font:{size:10}} }
      }
    }
  });

  // IF chart
  new Chart(document.getElementById('ifChart'), {
    type: 'bar',
    data: {
      labels: ['Textile','Granite','Auto','FMCG'],
      datasets: [
        { label:'Mean score', data:[0.81,0.76,0.72,0.68], backgroundColor:['#3d7fff','#ff5a5a','#2ecf8a','#f5a623'], borderRadius:4 },
        { label:'P95 score', data:[0.96,0.93,0.91,0.88], backgroundColor:['rgba(61,127,255,0.25)','rgba(255,90,90,0.25)','rgba(46,207,138,0.25)','rgba(245,166,35,0.25)'], borderRadius:4 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display:false } },
      scales: {
        y: { min:0, max:1, ticks:{font:{size:10}} },
        x: { ticks:{font:{size:10}}, grid:{display:false} }
      }
    }
  });

  // AE chart
  new Chart(document.getElementById('aeChart'), {
    type: 'line',
    data: {
      labels: Array.from({length:20},(_,i)=>(i*0.05).toFixed(2)),
      datasets: [{
        label:'Dealer density',
        data:[820,690,540,420,320,250,200,160,130,110,95,85,70,60,85,140,260,410,580,320],
        borderColor:'#2ecf8a', backgroundColor:'rgba(46,207,138,0.08)',
        fill:true, tension:0.5, pointRadius:0, borderWidth:2
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false} },
      scales: {
        y: { ticks:{font:{size:10}}, title:{display:true,text:'Dealers',font:{size:10}} },
        x: { ticks:{font:{size:9},maxRotation:45}, title:{display:true,text:'Reconstruction error',font:{size:10}} }
      }
    }
  });

  // RL chart
  new Chart(document.getElementById('rlChart'), {
    type: 'line',
    data: {
      labels:['Ep 1','Ep 2','Ep 3','Ep 4','Ep 5','Ep 6','Ep 7','Ep 8'],
      datasets:[{
        label:'Reward', data:[0.31,0.38,0.44,0.52,0.59,0.65,0.71,0.79],
        borderColor:'#3d7fff', backgroundColor:'rgba(61,127,255,0.1)',
        fill:true, tension:0.4, pointRadius:5, pointBackgroundColor:'#3d7fff', borderWidth:2.5
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        y:{min:0.2,max:0.9,ticks:{callback:v=>v.toFixed(2),font:{size:10}},grid:{color:'rgba(99,139,255,0.07)'}},
        x:{ticks:{font:{size:10}},grid:{display:false}}
      }
    }
  });

  // Hit rate chart
  new Chart(document.getElementById('hitChart'), {
    type: 'line',
    data: {
      labels:['Ep 1','Ep 2','Ep 3','Ep 4','Ep 5','Ep 6','Ep 7','Ep 8'],
      datasets:[
        { label:'RL hit rate', data:[48,53,57,63,68,72,76,81], borderColor:'#3d7fff', borderWidth:2.5, tension:0.4, pointRadius:4, pointBackgroundColor:'#3d7fff' },
        { label:'Baseline', data:[43,43,44,44,45,45,46,46], borderColor:'#5a6480', borderWidth:1.5, tension:0.2, pointRadius:3, borderDash:[4,3] }
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        y:{min:35,ticks:{callback:v=>v+'%',font:{size:10}},grid:{color:'rgba(99,139,255,0.07)'}},
        x:{ticks:{font:{size:10}},grid:{display:false}}
      }
    }
  });

  // SHAP chart
  new Chart(document.getElementById('shapChart'), {
    type: 'bar',
    data: {
      labels:['Electricity dev.','E-way bill dev.','EPFO wages dev.','Water usage dev.','NIC cluster','Seasonal flag'],
      datasets:[{
        label:'SHAP value',
        data:[0.38,0.29,0.21,0.14,0.09,0.05],
        backgroundColor:['#3d7fff','#ff5a5a','#2ecf8a','#f5a623','rgba(61,127,255,0.4)','rgba(99,139,255,0.3)'],
        borderRadius:4,
        borderSkipped:false
      }]
    },
    options: {
      indexAxis:'y',
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{ticks:{font:{size:10}},title:{display:true,text:'Mean |SHAP| value',font:{size:10}},grid:{color:'rgba(99,139,255,0.07)'}},
        y:{ticks:{font:{size:11}},grid:{display:false}}
      }
    }
  });

  // Radar chart
  new Chart(document.getElementById('radarChart'), {
    type: 'radar',
    data: {
      labels:['Electricity','E-way bill','EPFO wages','Water usage'],
      datasets:[
        { label:'Textile', data:[4.2,3.1,2.4,1.8], borderColor:'#3d7fff', backgroundColor:'rgba(61,127,255,0.07)', pointBackgroundColor:'#3d7fff', borderWidth:2, pointRadius:4 },
        { label:'Granite', data:[3.9,3.4,1.2,2.8], borderColor:'#ff5a5a', backgroundColor:'rgba(255,90,90,0.07)', pointBackgroundColor:'#ff5a5a', borderWidth:2, pointRadius:4 },
        { label:'Auto', data:[2.9,2.7,3.1,1.1], borderColor:'#2ecf8a', backgroundColor:'rgba(46,207,138,0.07)', pointBackgroundColor:'#2ecf8a', borderWidth:2, pointRadius:4 },
        { label:'FMCG', data:[2.8,2.2,1.9,1.3], borderColor:'#f5a623', backgroundColor:'rgba(245,166,35,0.07)', pointBackgroundColor:'#f5a623', borderWidth:2, pointRadius:4 }
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{r:{ticks:{font:{size:9},backdropColor:'transparent'},grid:{color:'rgba(99,139,255,0.12)'},angleLines:{color:'rgba(99,139,255,0.1)'},pointLabels:{font:{size:11}}}}
    }
  });
}

function animateBars() {
  const ids = ['s1','s2','s3','s4'];
  const vals = [82,67,53,38];
  ids.forEach((id,i) => {
    const el = document.getElementById(id);
    if(el){ el.style.width='0%'; setTimeout(()=>el.style.width=vals[i]+'%', 50); }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  initCharts();
  renderDealerTable(dealers);
  renderExplains();
});
</script>
</body>
</html>