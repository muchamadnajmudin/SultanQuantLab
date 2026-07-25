# SultanQuantLab

> Professional Quantitative Trading Research Platform

SultanQuantLab adalah platform **backtesting dan riset trading berbasis Python** yang dikembangkan untuk membantu trader melakukan pengujian strategi secara objektif, analisis performa, optimasi parameter, dan pengembangan sistem trading kuantitatif.

Project ini dirancang dengan arsitektur modular agar setiap komponen dapat dikembangkan, diuji, dan ditingkatkan secara independen.

---

# Features

## Market Analysis

- EMA Indicator
- RSI Indicator
- Stochastic Indicator
- ATR Indicator
- ADX Indicator


## Trading Engine

- Strategy Engine
- Backtest Engine
- Risk Engine
- Trade Management


## Performance Analysis

- Statistics Engine
- Profit Factor
- Expectancy
- Risk Reward Analysis
- Drawdown Analysis
- Sharpe Ratio
- Recovery Factor
- Equity Curve


## Optimization

- Optimizer Engine
- Parameter Testing
- Strategy Ranking


## Reporting

- Trade Journal
- Text Report
- Visual Analytics
- Equity Curve Chart
- Drawdown Chart
- Profit Distribution
- Monthly Returns


## Architecture

- Modular Design
- Separation of Engine Layer
- Config Driven Strategy
- Research Oriented Workflow

---

# Project Structure

```text
SultanQuantLab/
│
├── archive/
│
├── config/
│   └── settings.py
│
├── data/
│   └── Market Data CSV
│
├── database/
│
├── docs/
│   ├── MODULE_CONTRACT.md
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── CHANGELOG_DEV.md
│
├── engine/
│   ├── loader.py
│   ├── indicator_engine.py
│   ├── strategy_engine.py
│   ├── backtest_engine.py
│   ├── statistics_engine.py
│   ├── optimizer_engine.py
│   ├── trade_logger.py
│   ├── visual_engine.py
│   └── pipeline.py
│
├── indicators/
│
├── optimizer/
│
├── reports/
│   ├── report_engine.py
│   ├── report_writer.py
│   └── output/
│
├── strategies/
│
├── tests/
│
├── CHANGELOG.md
├── PROJECT_SPEC.md
├── SULTANQUANT_AI_CONTEXT.md
├── README.md
└── main.py
```

---

# Documentation

Project documentation:

- [Module Contract](docs/MODULE_CONTRACT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Development Changelog](docs/CHANGELOG_DEV.md)

---

# Current Strategy

Default strategy:

## XAUUSD Quant Strategy

Components:

- EMA Trend Filter
- EMA 20 / EMA 50 / EMA 200
- RSI (2)
- Stochastic (21,2,2)
- ATR Stop Loss
- ATR Take Profit
- ADX Trend Filter


Risk Management:

- Risk Per Trade
- ATR Based Stop Loss
- ATR Based Take Profit
- Drawdown Monitoring

---

# Current Backtest Statistics

Statistics Engine provides:

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

# Latest Backtest Result

Current benchmark:

```text
Total Trade       : 61
Winner            : 26
Loser             : 35

Win Rate          : 42.62%

Gross Profit      : 181.07
Gross Loss        : 92.32
Net Profit        : 88.75

Profit Factor     : 1.96

Expectancy        : 1.45

Average Win       : 6.96
Average Loss      : 2.64

Average RR        : 2.00

Maximum Drawdown  : 18.25
Recovery Factor   : 4.86

Sharpe Ratio      : 0.26
```

---

# Reports Output

Generated reports:

```text
reports/output/

├── backtest_report.txt
├── trade_journal.csv
├── equity_curve.png
├── drawdown.png
├── profit_distribution.png
└── monthly_returns.png
```

---

# Installation

Clone repository:

```bash
git clone https://github.com/muchamadnajmudin/SultanQuantLab.git
```

Masuk folder project:

```bash
cd SultanQuantLab
```

Install dependency:

```bash
pip install -r requirements.txt
```

Jalankan program:

```bash
python main.py
```

---

# Development Roadmap

## Sprint 1.0 Foundation ✅

Completed:

- Project Structure
- Data Loader
- Indicators
- Strategy Engine
- Backtest Engine
- Modular Architecture


## Sprint 2.0 Statistics ✅

Completed:

- Performance Metrics
- Risk Analysis
- Equity Calculation


## Sprint 2.1 Optimizer ✅

Completed:

- Parameter Optimization
- Result Ranking


## Sprint 2.2 Trade Journal ✅

Completed:

- Trade Logging
- CSV Export


## Sprint 2.3 Visual Analytics ✅

Completed:

- Equity Curve Chart
- Drawdown Chart
- Profit Distribution
- Monthly Returns


## Sprint 2.4 HTML Report ⏳

Target:

- Professional Backtest Report
- Performance Dashboard
- Statistics Summary
- Embedded Charts
- Trade Journal Integration


## Sprint 2.5 Optimizer Pro

Target:

- Grid Search
- Multi Parameter Optimization
- Top Ranking System
- Optimization Report


## Sprint 3.0 Institutional Grade

Target:

- Walk Forward Optimization
- Monte Carlo Simulation
- Multi Symbol Testing
- Portfolio Backtest
- AI Quant Analysis
- Cloud Research Platform

---

# Development Workflow

```text
Modify Code

↓

Run Test

↓

Run Backtest

↓

Verify Result

↓

git add .

↓

git commit

↓

git push
```

---

# Module Development Rule

Before modifying any module:

1. Check existing function interface.
2. Check all files importing the module.
3. Do not change function parameters tanpa update caller.
4. Maintain backward compatibility.
5. Update documentation after architectural changes.

Main technical contract:

```text
docs/MODULE_CONTRACT.md
```

---

# License

This project is developed for:

- Research purposes
- Educational purposes
- Quantitative trading development


---

# Author

**Muchamad Najmudin**

Founder of SultanQuantLab