# ==========================================================

# SULTAN QUANT OS

# PROJECT STATE

# Version : 5.6.0

# ==========================================================

Last Update : 2026-08-09

---

# PROJECT OVERVIEW

Project Name :

SULTAN QUANT OS

Current Version :

5.6.0

Project Status :

INSTITUTIONAL ENGINE OPERATIONAL
NEEDS FURTHER OPTIMIZATION

Purpose :

Professional Quantitative Trading Framework
built with Python and MetaTrader 5.

Long-Term Goal :

Build SULTAN QUANT OS into an Institutional Portfolio Engine
capable of evaluating, ranking, validating, allocating, and
routing trading strategies using quantitative evidence.

Primary Objective :

Maximize long-term risk-adjusted profitability and robustness,
not simply maximize backtest profit.

---

# CORE DESIGN PRINCIPLE

SULTAN QUANT OS is designed as a layered quantitative
decision system.

Architecture:

DATA
↓
INDICATORS
↓
STRATEGIES
↓
BACKTEST
↓
STATISTICS
↓
RISK
↓
OPTIMIZATION
↓
MONTE CARLO
↓
WALK FORWARD
↓
STRATEGY ANALYSIS
↓
STRATEGY RANKING
↓
PORTFOLIO ENGINE
↓
PORTFOLIO RISK
↓
PORTFOLIO DECISION
↓
INSTITUTIONAL REPORT
↓
FINAL DECISION

The Institutional Report is a decision/reporting layer.

It must NOT silently modify:

* strategy logic
* scoring formulas
* risk formulas
* portfolio allocation formulas
* WFO calculations
* Monte Carlo calculations

Existing module contracts must be preserved unless
callers and tests are checked first.

---

# CURRENT PROJECT STRUCTURE

config/

data/

database/

engine/

indicators/

optimizer/

analyzer/

reports/

strategies/

tests/

archive/

---

# CURRENT CORE ENGINE MODULES

## Engine

engine/backtest_engine.py

Responsibility:

* Execute historical backtest
* Generate trades
* Produce equity information

engine/indicator_engine.py

Responsibility:

* Indicator calculation
* Indicator preparation

engine/institutional_engine.py

Responsibility:

* Institutional pipeline
* Backtest execution
* Monte Carlo
* Walk Forward
* Risk analysis
* Strategy ranking
* Portfolio evaluation
* Institutional reporting

engine/loader.py

Responsibility:

* Load market data

engine/optimizer_engine.py

Responsibility:

* Parameter optimization

engine/pipeline.py

Responsibility:

* Connect major engine stages

engine/risk_engine.py

Responsibility:

* Risk calculations
* Drawdown
* Risk metrics

engine/statistics_engine.py

Responsibility:

* Performance statistics

engine/strategy_engine.py

Responsibility:

* Load strategy from Registry
* Execute selected strategy
* Preserve strategy interface

engine/trade.py

Responsibility:

* Trade data structure

engine/trade_logger.py

Responsibility:

* Trade journal logging

engine/visual_engine.py

Responsibility:

* Generate performance visualizations

engine/wfo_visual_engine.py

Responsibility:

* Walk Forward visualization

---

# STRATEGY ARCHITECTURE

## Strategy Registry

strategies/registry.py

Responsibilities:

* Register available strategies
* Return strategy callable
* List registered strategies
* Preserve strategy lookup interface

## Strategy Manager

strategies/strategy_manager.py

Responsibilities:

* Manage strategy evaluation
* Compare strategies
* Select best strategy candidate

## Strategy Analyzer

analyzer/strategy_analyzer.py

Responsibilities:

* Analyze strategy quality
* Generate score
* Generate grade
* Identify strengths
* Identify weaknesses
* Generate recommendations

## Strategy Ranking

The Institutional Portfolio Engine evaluates registered
strategies and produces ranking based on existing scoring
logic.

The report layer does not modify the scoring formula.

---

# CURRENT REGISTERED STRATEGIES

Current registry contains 12 strategies:

1. xau_strategy
2. sultan_baseline
3. price_action
4. smart_money
5. trend_following
6. fibonacci
7. breakout
8. mean_reversion
9. supply_demand
10. momentum
11. seasonal
12. statistical_quant

---

# STRATEGY EVALUATION STATUS

Latest Institutional Run:

Total Strategies Evaluated : 12

SUCCESS : 6

INSUFFICIENT_DATA : 6

FAILED : 0

Qualified Strategies : 6

Qualified strategies are currently defined as:

evaluation_status == SUCCESS

INSUFFICIENT_DATA strategies must never be treated
as valid portfolio candidates.

FAILED strategies must remain explicitly visible in
institutional reporting.

---

# CURRENT STRATEGY RANKING

Latest result:

1. xau_strategy

Score : 70.0
Profit Factor : 1.96
Win Rate : 42.62%
Grade : C

2. price_action

Score : 60.0
Profit Factor : 1.31
Win Rate : 39.92%
Grade : D

3. fibonacci

Score : 40.0
Profit Factor : 1.08
Win Rate : 33.87%
Grade : F

4. trend_following

Score : 30.0
Profit Factor : 0.96
Win Rate : 32.40%
Grade : F

5. sultan_baseline

Score : 30.0
Profit Factor : 0.93
Win Rate : 33.22%
Grade : F

6. breakout

Score : 30.0
Profit Factor : 0.93
Win Rate : 31.92%
Grade : F

7. smart_money

Status : INSUFFICIENT_DATA

8. mean_reversion

Status : INSUFFICIENT_DATA

9. supply_demand

Status : INSUFFICIENT_DATA

10. momentum

Status : INSUFFICIENT_DATA

11. seasonal

Status : INSUFFICIENT_DATA

12. statistical_quant

Status : INSUFFICIENT_DATA

---

# CURRENT SELECTED STRATEGY

Selected Strategy :

xau_strategy

Rank :

1

Score :

70.0

Profit Factor :

1.96

Win Rate :

42.62%

Grade :

C

Router Recommended :

False

Important:

The selected strategy is NOT automatically considered
ready for live trading.

Selection means it is currently the highest-ranked
qualified strategy under the existing evaluation system.

---

# CURRENT BACKTEST RESULT

Latest Institutional Run:

Total Trade :

61

Winner :

26

Loser :

35

Win Rate :

42.62%

Gross Profit :

181.07

Gross Loss :

92.32

Net Profit :

88.75

Profit Factor :

1.96

Average Win :

6.96

Average Loss :

2.64

Expectancy :

1.45

Average Trade :

1.45

Maximum Win :

23.59

Maximum Loss :

-6.26

Average RR :

2.0

Maximum Drawdown :

18.25

Maximum Drawdown Percent :

20.56%

Maximum Win Streak :

5

Maximum Loss Streak :

10

Recovery Factor :

4.86

Sharpe Ratio :

0.26

---

# CURRENT MONTE CARLO RESULT

Simulation Count :

1000

Initial Balance :

10000.0

Median Balance :

10087.38

Mean Balance :

10089.18

Std Balance :

43.46

Best Balance :

10240.15

Worst Balance :

9966.54

Probability Profit :

98.5%

Probability Loss :

1.5%

Ruin Probability :

0.0%

Worst Drawdown :

64.35

Median Drawdown :

18.95

Drawdown Percentile 95 :

35.6

Mean Drawdown :

20.92

Std Drawdown :

8.15

Risk Level :

LOW

Robustness Score :

100.0

Valid Simulations :

1000

Invalid Simulations :

0

---

# CURRENT WALK FORWARD RESULT

Total Window :

45

Average Profit Factor :

0.51

Average Net Profit :

1.91

Profitable Window :

18

Losing Window :

27

Profitable Window Ratio :

40.0%

PF >= 1 Ratio :

17.78%

Median Profit Factor :

0.0

Best Profit Factor :

5.34

Worst Profit Factor :

0.0

Std Profit Factor :

1.23

Median Net Profit :

0.0

Best Net Profit :

23.59

Worst Net Profit :

-8.10

Std Net Profit :

5.97

Maximum Losing Streak :

4

Maximum Winning Streak :

4

Stability Score :

40.0

PF Consistency Score :

21.44

Return Consistency Score :

35.5

WFO Robustness Score :

33.08

Overfitting Score :

80.0

Overfitting Risk :

HIGH

---

# CURRENT RISK DASHBOARD

Quality Score :

65

Risk Level :

ACCEPTABLE

Profit Factor Score :

20

WFO Stability :

40.0

WFO Score :

15

Monte Carlo Risk :

LOW

Monte Carlo Score :

20

Monte Carlo Robustness :

100.0

Drawdown :

20.56%

Drawdown Score :

10

Current Recommendations:

* Improve Profit Factor above 2.0
* Reduce maximum drawdown below 20%
* Increase Walk Forward stability

---

# CURRENT PORTFOLIO ALLOCATION

Latest allocation:

xau_strategy :

41.18%

price_action :

35.29%

fibonacci :

23.53%

Total :

100.00%

Important:

Only qualified SUCCESS strategies are eligible for
portfolio allocation.

---

# CURRENT PORTFOLIO RISK

Exposure :

1.0

Concentration :

0.41

Portfolio Drawdown :

29.2

Risk Score :

0.88

Status :

ELEVATED

---

# CURRENT PORTFOLIO DECISION

Decision :

CAUTIOUS

Best Strategy :

xau_strategy

Profit Factor :

1.96

Drawdown :

20.56%

Score :

70.0

Risk Status :

ELEVATED

Reason :

Drawdown is elevated.

---

# CURRENT FINAL INSTITUTIONAL DECISION

Backtest:

Profit Factor :

1.96

Drawdown :

20.56%

Walk Forward:

Stability :

40.0%

Overfitting Risk :

HIGH

Monte Carlo:

Risk :

LOW

Robustness :

100.0

Portfolio:

Risk Status :

ELEVATED

Portfolio Decision :

CAUTIOUS

Final Assessment :

NEEDS FURTHER OPTIMIZATION

Current system conclusion:

The strategy is profitable in the tested backtest,
but current evidence is insufficient for live trading.

Primary weaknesses are:

1. WFO stability is too low.
2. WFO overfitting risk is HIGH.
3. Portfolio risk is ELEVATED.
4. Drawdown remains relatively high.
5. Profit Factor is only slightly below the 2.0 target.

---

# CURRENT INSTITUTIONAL REPORT

Report Engine:

institutional_report_engine.py

Current Version :

5.6.0

Responsibilities:

* Generate Institutional Research Report
* Merge Backtest
* Merge Monte Carlo
* Merge Walk Forward
* Merge Risk Dashboard
* Merge Strategy Quality Analysis
* Merge Portfolio Ranking
* Merge Qualified Strategies
* Merge Portfolio Allocation
* Merge Portfolio Risk
* Merge Portfolio Decision
* Produce Executive Summary
* Produce Final Institutional Decision

Output:

reports/output/institutional_report.txt

---

# CURRENT GENERATED REPORTS

Text Report:

reports/output/backtest_report.txt

HTML Report:

reports/output/backtest_report.html

Trade Journal:

reports/output/trade_journal.csv

Visual Reports:

reports/output/equity_curve.png

reports/output/drawdown.png

reports/output/profit_distribution.png

reports/output/monthly_returns.png

Institutional Report:

reports/output/institutional_report.txt

---

# PRICE ACTION ARCHITECTURE

Current Price Action architecture contains:

strategies/price_action.py

strategies/price_action_patterns.py

strategies/price_action_swings.py

strategies/price_action_structure.py

strategies/price_action_confirmation.py

strategies/price_action_trade.py

strategies/risk_builder.py

Current design principle:

Keep the Price Action architecture stable first.

Do not add every possible pattern/filter simultaneously.

Signal quality improvements should be implemented
incrementally while preserving interfaces.

---

# FIBONACCI ARCHITECTURE

Current modules include:

strategies/fibonacci.py

strategies/fibonacci_engine.py

Current Fibonacci strategy remains part of the
institutional strategy universe.

Further signal refinement can be developed in later
optimization sprints.

---

# TEST STATUS

Latest known test status:

44 tests collected

44 tests passed

0 tests failed

Test suite covers major areas including:

* Backtest
* Drawdown
* Equity Curve
* Fibonacci
* Institutional Report
* Market Analyzer
* Market Structure
* Monte Carlo
* Monte Carlo Analyzer
* Monthly Returns
* Optimizer
* Pending Orders
* Position
* Price Action
* Price Action Confirmation
* Price Action Score
* Price Action Strategy
* Strategy Manager
* Other core modules

IMPORTANT:

Before modifying existing modules:

1. Read current source.
2. Check current version.
3. Check callers.
4. Check tests.
5. Identify actual failure.
6. Patch minimally.
7. Run tests.
8. Validate runtime output.
9. Update project state.
10. Update changelog/version when appropriate.

---

# CURRENT DEVELOPMENT PRIORITY

The project has moved beyond the original basic
backtesting stage.

The current priority is NOT simply adding more indicators.

The priority is:

INSTITUTIONAL PORTFOLIO ENGINE

Focus areas:

1. Strategy evaluation
2. Strategy ranking
3. Strategy quality analysis
4. Walk Forward robustness
5. Monte Carlo robustness
6. Portfolio allocation
7. Portfolio risk
8. Portfolio decision
9. Institutional reporting
10. Live-trading readiness framework

---

# CURRENT MAJOR PROBLEM

The current system can already produce an institutional-style
analysis, but the evidence quality is not yet strong enough
for live deployment.

Main issue:

WFO stability = 40%

WFO overfitting risk = HIGH

Therefore:

Do NOT interpret the current xau_strategy selection
as confirmation of institutional robustness.

The system currently identifies the best candidate,
but the candidate still requires further validation.

---

# NEXT DEVELOPMENT PRIORITIES

## PRIORITY 1

WFO QUALITY

Investigate why:

* Average PF = 0.51
* Profitable windows = 18 / 45
* PF >= 1 ratio = 17.78%
* Stability = 40%
* WFO robustness = 33.08%
* Overfitting risk = HIGH

Goal:

Improve robustness without manipulating the scoring system.

---

## PRIORITY 2

PORTFOLIO RISK

Investigate:

* Portfolio drawdown = 29.2
* Concentration = 0.41
* Risk score = 0.88
* Status = ELEVATED

Goal:

Create a more defensible portfolio risk framework.

---

## PRIORITY 3

STRATEGY QUALITY

Investigate why only 6 of 12 strategies currently
produce SUCCESS results.

The remaining 6 strategies currently return:

INSUFFICIENT_DATA

They should not receive artificial scores.

Goal:

Implement or improve those strategies only when their
actual signal logic and data requirements are ready.

---

## PRIORITY 4

LIVE READINESS

The final decision engine must remain conservative.

Current target:

READY FOR LIVE TRADING only when the evidence satisfies
the institutional thresholds.

Current threshold framework includes:

Profit Factor >= 2.0

Drawdown <= 15%

WFO Stability >= 80%

Monte Carlo Robustness >= 90%

Monte Carlo Risk = LOW

Portfolio Risk not HIGH or CRITICAL

Portfolio Decision not REJECT or STOP

Qualified Strategy Count > 0

Current system does NOT satisfy these requirements.

---

# DEVELOPMENT RULES

RULE 1

Never replace a source file merely because another version
appears in memory or in an earlier conversation.

Always inspect the CURRENT PROJECT source.

---

RULE 2

Never assume the version from an earlier chat is current.

Read the actual file/version from the project.

---

RULE 3

Before changing a function:

Check its callers.

Check its tests.

Preserve public interfaces unless a deliberate migration
is performed.

---

RULE 4

Do not modify scoring formulas inside the report engine.

The report engine is a decision/reporting layer.

---

RULE 5

Do not treat INSUFFICIENT_DATA as a failed strategy.

INSUFFICIENT_DATA means insufficient evidence/data.

FAILED means an actual evaluation failure.

---

RULE 6

Never artificially promote a strategy because its score
looks better.

Ranking must follow actual evaluation results.

---

RULE 7

Never declare LIVE READY from backtest alone.

Live readiness requires:

Backtest
+
Monte Carlo
+
Walk Forward
+
Risk
+
Portfolio validation

---

RULE 8

Every significant source change must be followed by:

TEST
+
RUNTIME VALIDATION
+
PROJECT STATE UPDATE

---

# CURRENT SOP

Every future development session must follow:

CURRENT PROJECT
↓
READ ACTIVE SOURCE
↓
CHECK VERSION
↓
CHECK CALLERS
↓
CHECK TESTS
↓
IDENTIFY ACTUAL PROBLEM
↓
PATCH / UPGRADE
↓
RUN TESTS
↓
VALIDATE OUTPUT
↓
UPDATE PROJECT STATE
↓
UPDATE CHANGELOG
↓
INCREMENT VERSION
↓
CONTINUE NEXT TASK

If the current source is unavailable,
do not assume its contents from memory.

---

# VERSION CONTROL RULE

The authoritative version is the version inside
the CURRENT PROJECT SOURCE.

Conversation memory is NOT authoritative.

Older chat messages are NOT authoritative.

Old code pasted in chat is NOT authoritative.

PROJECT_STATE.md is a project navigation/state document,
not a replacement for inspecting the actual source.

---

# CURRENT PROJECT CONDITION

Architecture :

OPERATIONAL

Core Engine :

OPERATIONAL

Strategy Registry :

OPERATIONAL

Strategy Evaluation :

OPERATIONAL

Strategy Ranking :

OPERATIONAL

Monte Carlo :

OPERATIONAL

Walk Forward :

OPERATIONAL

Risk Dashboard :

OPERATIONAL

Portfolio Allocation :

OPERATIONAL

Portfolio Risk :

OPERATIONAL

Portfolio Decision :

OPERATIONAL

Institutional Report :

OPERATIONAL

Automated Tests :

PASSING

Live Trading Readiness :

NOT READY

Primary Development Objective :

IMPROVE ROBUSTNESS AND INSTITUTIONAL DECISION QUALITY

---

# IMPORTANT CURRENT FACT

The project is no longer at Sprint 2.x.

The old PROJECT_STATE describing:

Sprint 2.2
Visual Analytics
HTML Report
Optimizer Pro
Institutional Grade as future work

is OBSOLETE.

Those stages have already been substantially developed.

The project is currently in the
INSTITUTIONAL PORTFOLIO ENGINE stage.

---

# END OF PROJECT STATE
