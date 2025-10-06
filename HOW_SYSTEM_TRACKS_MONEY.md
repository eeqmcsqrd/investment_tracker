# How The System Actually Tracks Money - The Truth

## THE CRITICAL FINDING

**The system CANNOT distinguish between deposits and market gains.**

**Everything is treated as "income"!**

---

## What The Code Actually Does

Looking at `recalc_total_income_for_date()` in `data_handler_db.py` (line 1531):

```python
# For each investment account on this date
delta = current_value - previous_value

if delta > 0:
    total_income_usd += delta  # ALL increases = "income"
```

**That's it. There's NO logic to separate:**
- ❌ Deposits you made
- ❌ Market gains
- ❌ Dividends
- ❌ Interest

**They're ALL treated as "income".**

---

## Concrete Examples

### Example 1: You Deposit Money

**What you do:**
- October 1: Fidelity 401k = $10,000
- October 2: You deposit $1,000
- October 2: Fidelity 401k = $11,000

**What the system records:**
```
Date: October 2
Account: Fidelity 401k
Previous: $10,000
Current: $11,000
Delta: +$1,000

SUSTAINABILITY "INCOME": +$1,000 ✅
```

**Result:** Counted as income

---

### Example 2: Market Goes Up

**What happens:**
- October 1: Fidelity 401k = $10,000
- October 2: Market rises 10%, no deposit
- October 2: Fidelity 401k = $11,000

**What the system records:**
```
Date: October 2
Account: Fidelity 401k
Previous: $10,000
Current: $11,000
Delta: +$1,000

SUSTAINABILITY "INCOME": +$1,000 ✅
```

**Result:** ALSO counted as income

---

### Example 3: Both Deposit AND Market Gain

**What happens:**
- October 1: Fidelity 401k = $10,000
- October 2: You deposit $500 AND market goes up $500
- October 2: Fidelity 401k = $11,000

**What the system records:**
```
Date: October 2
Account: Fidelity 401k
Previous: $10,000
Current: $11,000
Delta: +$1,000

SUSTAINABILITY "INCOME": +$1,000 ✅
```

**Result:** Both combined, no distinction

---

## The System's Logic

### What It Tracks:
```python
Income = SUM of all (Current Value - Previous Value) where delta > 0
```

### What It Does NOT Track:
- ❌ Whether increase is from deposit
- ❌ Whether increase is from market gain
- ❌ Whether increase is from dividend
- ❌ Whether increase is from interest
- ❌ Whether increase is from currency exchange

### Why?
**Because the system only knows:**
1. What value was yesterday
2. What value is today
3. The difference

**It has NO information about WHY the value changed.**

---

## Your Specific Numbers Explained

### Your "Income": $29,629.61

This $29,629.61 is the sum of ALL increases across ALL days:

```
Day 1: Accounts increased by $100 → Income +$100
Day 2: Accounts increased by $150 → Income +$150
Day 3: Accounts increased by $200 → Income +$200
...
Total: $29,629.61
```

**This includes:**
- ✅ Every deposit you made
- ✅ Every market gain
- ✅ Every dividend received
- ✅ Every interest payment
- ✅ Every currency gain
- ✅ **ALL increases combined**

### Your "Expenses": $29,433.77

This is from Revolut - EUR decreases only:

```
Day 1: Revolut decreased by €50 → Expense +€50
Day 2: Revolut decreased by €30 → Expense +€30
...
Total: €29,433.77 (converted to USD)
```

**This includes:**
- ✅ Money you spent
- ✅ Withdrawals
- ✅ Transfers out of Revolut

### Your Net: $195.84

```
Net = Total Increases - Revolut Decreases
    = $29,629.61 - $29,433.77
    = $195.84
```

**This does NOT mean you only saved $195.84.**

**This means: Total account increases exceeded Revolut spending by $195.84**

---

## The Real Problem With My Earlier Explanation

### What I Said (WRONG):
> "Your savings: $195.84"
> "Market gains: $3,927.96"

### The Truth:
**The system has NO IDEA which is which!**

Both are included in the $29,629.61 "income" figure.

---

## What "Sustainability" ACTUALLY Measures

### It measures:
```
All account value increases (from ANY source)
  MINUS
Only Revolut decreases (spending)
```

### It does NOT measure:
- ❌ Your actual savings rate
- ❌ Market gains separately
- ❌ Deposits separately
- ❌ True cash flow

---

## Why "Portfolio Performance" Is More Accurate

Portfolio Performance shows:
```
Start Value:  $191,485.90
End Value:    $195,609.70
Change:       $4,123.80
```

**This is TOTAL wealth change.**

**It's accurate because it doesn't try to separate things.**

---

## The Only Way To Separate Deposits From Gains

### Method 1: Track Manually (NOT done by system)
You would need to record separately:
```
October 2:
- Deposited: $1,000 (manual entry)
- Market gain: $500 (calculated separately)
- Total increase: $1,500
```

**Your app does NOT do this.**

### Method 2: Calculate Based on Deposits
If you KNEW exactly when and how much you deposited:
```
Total Deposits = (manually sum all deposits made)
Market Gains = Portfolio Change - Total Deposits
```

**Your app does NOT track this.**

### Method 3: Track Each Transaction Type
```
Transaction types:
- Deposit
- Withdrawal
- Market Gain
- Dividend
- Interest
```

**Your app does NOT do this either.**

---

## What Your App Actually Tracks

### Tracked:
1. ✅ **Date**: When you update values
2. ✅ **Investment**: Which account
3. ✅ **Value**: Current value
4. ✅ **Previous Value**: Value on previous date (calculated)
5. ✅ **Delta**: Current - Previous

### NOT Tracked:
1. ❌ **Transaction Type**: Deposit vs gain
2. ❌ **Source of Change**: Why value changed
3. ❌ **Actual Deposits**: Money you added
4. ❌ **Actual Gains**: Market performance
5. ❌ **Transaction Categories**: Any breakdown

---

## Concrete Example With Real Data

Let's say you have this history:

### Your Fidelity 401k

**October 1:**
- Value: $50,000
- You update the app: $50,000

**October 15 (Payday):**
- You deposit $500 from paycheck
- Market went up 2% = $1,000
- New value: $51,500
- You update the app: $51,500

**What the system records:**

```python
Date: October 15
Account: Fidelity 401k
Previous: $50,000
Current: $51,500
Delta: +$1,500

# System calculates:
if delta > 0:
    income += $1,500  # ALL of it = "income"

# System has NO IDEA that:
# - $500 was your deposit
# - $1,000 was market gain
```

**Sustainability "Income": $1,500**
- ✅ Includes your $500 deposit
- ✅ Includes your $1,000 market gain
- ❌ Cannot tell them apart

---

## How To Actually Calculate Your Real Savings

Since the system can't do it, you need to manually track:

### Step 1: Identify All Deposits
Look through your history and note:
```
Jan 1: Deposited $1,000 to 401k
Feb 1: Deposited $1,000 to 401k
Mar 1: Deposited $1,000 to 401k
...
Total Deposits: $X
```

### Step 2: Calculate Market Performance
```
Portfolio Change = Start to End difference
Deposits = Sum of all deposits
Withdrawals = Sum of all withdrawals

Market Gains = Portfolio Change - Deposits + Withdrawals
```

### Step 3: Your Numbers
```
Portfolio Change:  $4,123.80
Deposits:         $X (you need to calculate)
Withdrawals:      $Y (you need to calculate)

Market Gains = $4,123.80 - $X + $Y
```

---

## Why The Sustainability Number Is Misleading

### Your Sustainability Says:
```
Income:  $29,629.61
Expense: $29,433.77
Net:     $195.84
```

### What This ACTUALLY Means:
```
"My investment accounts increased by $29,629.61 total
 AND I spent $29,433.77 from Revolut
 NET RESULT: Accounts grew $195.84 more than I spent from Revolut"
```

### What People THINK It Means:
```
"I saved $195.84 after market gains"  ← WRONG
```

### What You WANT To Know:
```
"How much did I actually deposit vs market gains?"  ← Can't tell from system
```

---

## The Bottom Line

### Question: "How does the system distinguish deposits from market gains?"

### Answer: **IT DOESN'T.**

The system treats ALL value increases as "income":
- ✅ Deposits → Income
- ✅ Market gains → Income
- ✅ Dividends → Income
- ✅ Interest → Income
- ✅ Currency gains → Income
- ✅ **Everything → Income**

### The Code Proof:
```python
# Line 1585 in data_handler_db.py
delta = float(curr_val) - float(prev_val)

# Line 1598
total_income_usd += delta * rate

# That's it. No logic to distinguish sources.
```

---

## What This Means For You

### Your $29,629.61 "Income"
This is:
- Your deposits (unknown amount)
- Plus market gains (unknown amount)
- Plus dividends (unknown amount)
- Plus everything else (unknown amounts)
- **= $29,629.61 total**

### Your $195.84 "Net"
This means:
- Total account increases exceeded Revolut spending by $195.84
- NOT "you saved $195.84"
- NOT "market gains were $3,927.96"
- Just: Net positive flow of $195.84

### Your $4,123.80 Portfolio Gain
This is ACCURATE:
- Your wealth increased by $4,123.80
- Includes everything
- Most reliable number

---

## Recommendation

### What To Trust:
✅ **Portfolio Performance: $4,123.80**
- This is your true wealth change
- It's accurate and complete

### What To Question:
⚠️ **Sustainability Net: $195.84**
- This mixes deposits and gains
- Can't tell what's what
- Misleading label "income"

### What To Do:
1. Use Portfolio Performance for wealth tracking
2. Manually track your deposits if you need that data
3. Calculate: Market Gains = Portfolio Change - (Deposits - Withdrawals)
4. Don't rely on Sustainability for savings rate

---

## Summary

| Question | Answer |
|----------|---------|
| Does system separate deposits from gains? | ❌ NO |
| What is "income"? | ALL value increases |
| What is "expense"? | Only Revolut decreases |
| What is "net"? | Increases - Revolut spending |
| Can I trust "net" as savings? | ❌ NO |
| What should I trust? | Portfolio Performance |

**The system is simple:**
- Tracks values over time ✅
- Calculates differences ✅
- Labels all increases as "income" ⚠️
- Cannot distinguish sources ❌

