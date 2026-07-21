# SultanQuantLab

> Professional Quantitative Trading Research Platform

SultanQuantLab adalah platform backtesting dan riset trading yang dikembangkan menggunakan Python. Proyek ini dirancang untuk membantu trader menguji strategi secara objektif, melakukan optimasi parameter, serta menghasilkan statistik performa yang lengkap.

---

# Features

- EMA Indicator
- RSI Indicator
- Stochastic Indicator
- ATR Indicator
- ADX Indicator
- Strategy Engine
- Backtest Engine
- Statistics Engine
- Optimizer Engine
- Risk Engine
- Modular Architecture

---

# Project Structure

```
SultanQuantLab/
│
├── archive/
├── config/
├── data/
├── engine/
├── indicators/
├── optimizer/
├── strategies/
├── tests/
│
├── CHANGELOG.md
├── PROJECT_SPEC.md
├── SULTANQUANT_AI_CONTEXT.md
├── README.md
└── main.py
```

---

# Current Strategy

Current default strategy:

- EMA Trend Filter
- RSI (2)
- Stochastic (21,2,2)
- ATR Stop Loss
- ATR Take Profit
- ADX Trend Filter

---

# Current Statistics

The Statistics Engine currently provides:

- Total Trade
- Winner
- Loser
- Win Rate
- Gross Profit
- Gross Loss
- Net Profit
- Profit Factor
- Average Win
- Average Loss
- Expectancy
- Average Trade
- Maximum Win
- Maximum Loss
- Average Risk Reward
- Maximum Drawdown
- Maximum Drawdown Percentage
- Win Streak
- Loss Streak
- Recovery Factor
- Sharpe Ratio
- Equity Curve

---

# Installation

Clone repository

```bash
git clone https://github.com/muchamadnajmudin/SultanQuantLab.git
```

Masuk ke folder project

```bash
cd SultanQuantLab
```

Install dependency

```bash
pip install -r requirements.txt
```

Jalankan program

```bash
python main.py
```

---

# Roadmap

## Version 2.3

- Professional Repository
- Performance Engine
- Better Documentation

## Version 2.4

- Report Engine
- PDF Report
- Excel Report

## Version 2.5

- Visualization
- Equity Curve Chart
- Drawdown Chart

## Version 3.0

- AI Quant Platform
- Telegram Integration
- Dashboard
- Cloud Support

---

# Development Workflow

```
Code

↓

Test

↓

git add .

↓

git commit

↓

git push
```

---

# License

This project is developed for research and educational purposes.

---

# Author

**Muchamad Najmudin**

Founder of SultanQuantLab