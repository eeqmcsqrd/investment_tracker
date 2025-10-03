# Investment Tracker - New Advanced Analytics Features

## Overview

Your investment tracker now includes comprehensive advanced analytics features to provide deeper insights into your portfolio's performance, risk profile, diversification, and cash flows.

## New Tab: 📊 Advanced Analytics

Access these features through the new "Advanced Analytics" tab in the main app.

---

## 1. 📊 Risk & Volatility Analysis

### Key Metrics Displayed:

#### **Sharpe Ratio**
- **What it is**: Risk-adjusted return metric
- **How to interpret**:
  - < 0: Poor (losing money relative to risk-free rate)
  - 0 - 0.5: Below Average
  - 0.5 - 1.0: Good
  - 1.0 - 2.0: Very Good
  - > 2.0: Excellent
- **Why it matters**: Shows if you're being adequately compensated for the risk you're taking

#### **Annual Volatility**
- **What it is**: Standard deviation of returns, annualized
- **How to interpret**:
  - Lower = more stable/predictable
  - Higher = more volatile/risky
  - Typical values: 5-15% (conservative), 15-25% (moderate), 25%+ (aggressive)
- **Why it matters**: Measures how much your portfolio value fluctuates

#### **Maximum Drawdown**
- **What it is**: Largest peak-to-trough decline in your portfolio
- **Additional info provided**:
  - When the drawdown started
  - When it reached the bottom
  - Recovery date (if recovered)
  - Days to recover
- **Why it matters**: Shows the worst-case scenario you've experienced

#### **Annualized Return**
- **What it is**: Compound annual growth rate (CAGR)
- **Why it matters**: Standardizes returns across different time periods

### Additional Risk Metrics (in Detailed View):

- **Sortino Ratio**: Like Sharpe but only penalizes downside volatility
- **Beta**: Sensitivity to market movements (if benchmark selected)
- **Alpha**: Excess return over what CAPM predicts (if benchmark selected)
- **Value at Risk (VaR 95%)**: Maximum expected loss 95% of the time
- **Conditional VaR (CVaR)**: Average loss in worst 5% of cases

---

## 2. 🔗 Investment Correlation Analysis

### Portfolio Diversification Score
- **Range**: 0-100
- **Interpretation**:
  - 70-100: Well diversified
  - 40-70: Moderately diversified
  - 0-40: Poorly diversified
- **Why it matters**: Diversification reduces portfolio risk without necessarily reducing returns

### Correlation Heatmap
- **Visual display**: Color-coded matrix showing how investments move together
- **Colors**:
  - Dark Blue (-1.0): Perfect negative correlation (move opposite)
  - White (0.0): No correlation (independent movements)
  - Dark Red (+1.0): Perfect positive correlation (move together)

### Insights Provided:

#### ⚠️ **Highly Correlated Investments**
- Identifies pairs with correlation > 0.7
- **Risk**: These investments don't provide diversification
- **Action**: Consider if you need both, or if you're over-concentrated

#### ✅ **Well-Diversified Pairs**
- Identifies pairs with correlation < 0.3
- **Benefit**: These investments provide good diversification
- **Action**: These are good building blocks for a balanced portfolio

### Use Cases:
1. **Identifying redundancy**: Do you really need both Trade Republic and 401k if they're highly correlated?
2. **Finding balance**: Pair highly correlated stocks with uncorrelated crypto for better diversification
3. **Risk management**: See which investments will likely fall together during market downturns

---

## 3. 💰 Cash Flow & Contribution Analysis

### Key Insights:

#### **Total Contributions**
- Sum of all money you've deposited across all investments

#### **Investment Growth**
- Total profit/loss from market movements
- Calculated as: Current Value - Total Contributions

#### **Growth Percentage**
- Return on your contributions: (Growth / Contributions) × 100%

### Visualizations:

#### **Contribution vs Growth Pie Chart**
- Shows what percentage of your portfolio is:
  - Your original contributions (what you put in)
  - Investment gains (what the market gave you)
- **Why it matters**: Understand how much wealth is from savings vs investing

#### **Cash Flow Waterfall Chart**
- Timeline of deposits and withdrawals
- **Green bars**: Deposits (money in)
- **Red bars**: Withdrawals (money out)
- **Blue line**: Cumulative cash flow
- **Why it matters**: See your investment patterns over time

#### **Investment-Specific Cash Flows**
- Drill down into any specific investment
- See when you added or withdrew money
- Useful for tracking 401k contributions, rebalancing actions, etc.

### Advanced Metrics (Behind the Scenes):

- **Money-Weighted Return (MWR)**: Accounts for timing of cash flows
- **Time-Weighted Return (TWR)**: Pure investment performance, ignoring cash flows
- Comparison helps you understand if your timing of contributions helped or hurt returns

---

## How to Use These Features

### 1. Start with Risk Metrics
- Check if your Sharpe ratio is adequate (aim for >1.0)
- Review volatility - is it within your comfort zone?
- Understand your maximum drawdown - could you handle this again?

### 2. Review Diversification
- Check your diversification score
- Identify highly correlated investments
- Consider rebalancing if score is low

### 3. Analyze Cash Flows
- Understand how much of your wealth is contributions vs returns
- Review if your deposit pattern makes sense
- Plan future contributions based on historical patterns

### Example Analysis Workflow:

```
1. Risk Check:
   - Sharpe Ratio: 1.2 ✅ (Good risk-adjusted returns)
   - Volatility: 18% ⚠️ (Moderate, acceptable)
   - Max Drawdown: -22% ⚠️ (Significant but recovered)

2. Diversification Review:
   - Score: 65/100 ⚠️ (Could be better)
   - Found: Binance ↔ Sui Wallet corr 0.95 ⚠️
   - Action: Both are crypto - consider adding more stocks/bonds

3. Cash Flow Insights:
   - Contributions: $50,000
   - Growth: $12,500 (25% return)
   - Finding: 80% of value is contributions
   - Action: Stay invested for more growth potential
```

---

## Tips for Better Portfolio Management

### Based on Risk Metrics:
- **High volatility + Low Sharpe**: Consider reducing exposure to volatile assets
- **Negative max drawdown not recovered**: May indicate poor performing investments
- **High Sortino vs Sharpe**: Your downside risk is well-managed

### Based on Correlations:
- **Many high correlations**: Portfolio is not well diversified
- **All low correlations**: Great! But ensure you understand each investment
- **Crypto highly correlated**: Normal - consider adding other asset classes

### Based on Cash Flows:
- **Growth < 0**: Your investments lost money - review strategy
- **High contributions, low growth**: Either too conservative or not enough time
- **Low contributions, high growth**: Great investment performance!

---

## Technical Notes

### Data Requirements:
- Risk metrics require at least 30 data points (days) for accuracy
- Correlation analysis requires at least 2 investments with overlapping dates
- Cash flow analysis uses inferred flows based on value changes

### Calculation Methods:
- All returns are calculated using daily data points
- Annualization uses 252 trading days per year
- Risk-free rate assumed at 2% annually (US Treasury rate)
- Correlations use Pearson correlation coefficient

### Limitations:
- Cash flows are **inferred** from value changes (not actual transaction data)
- Assumes portfolio-wide returns for all investments (approximation)
- Short time periods may show misleading correlations
- Cryptocurrency 24/7 trading not adjusted for

---

## Files Added to Your System

1. **risk_metrics.py** - Risk and volatility calculations
2. **correlation_analysis.py** - Correlation matrix and diversification analysis
3. **cash_flow_tracker.py** - Cash flow inference and tracking
4. **advanced_analytics_components.py** - UI components for the new tab

These modules are fully optimized and integrated with your existing investment tracker.

---

## Questions & Support

If you have questions about interpreting any of these metrics or want to add more features, let me know!

**Common Questions:**

Q: Why is my Sharpe ratio negative?
A: Your returns are below the risk-free rate. Consider reviewing your investment strategy.

Q: Should I worry about high correlation between my investments?
A: It depends on your goals. High correlation means less diversification, which increases risk but isn't inherently bad if you're confident in that sector.

Q: How accurate is the cash flow analysis?
A: It's an approximation. For perfect accuracy, you'd need to log every transaction. However, it's quite accurate for identifying major trends and contributions.
