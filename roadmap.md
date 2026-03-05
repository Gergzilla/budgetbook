# Budget Book

**Product Vision:** To empower individuals to take control of their finances with an intuitive, insightful, and adaptable budget application that simplifies money management and fosters financial growth.

**Target Audience:** Individuals looking to track spending, set financial goals, and improve their financial health, from beginners to more experienced budgeters.

**Document Status:** Currently this document is very fluid and a work in progress generated from a generic template.

---

## Phase 1: Core Essentials & Manual Control (Months 1-3)

**Goal:** Establish a robust foundation for manual tracking and provide immediate value for basic budgeting needs. Focus on reliability and a straightforward user experience.

**Key Features & Importance:**

* **Manual Transaction Entry** (Critical - P0):
  * **Functionality:** Users can manually add income and expenses with date, amount, category, and notes.
  * **Importance:** The absolute core of a budget app. Without this, there's no budget. Must be quick and easy.
  * **Implementation Status:**
* **Transaction Entry From Imports** (Critical - P0):
  * **Functionality:** Users can import transactions from CSV file formats or bank statements such as PDF
  * **Importance:** Alleviate the hassle of manual entry for all transactions to improve UX and reduce time required for usability
  * **Implementation Status:**ss
* **Customizable Categories** (High - P1):
  * **Functionality:** Pre-defined common categories (e.g., Groceries, Rent, Utilities) with the ability for users to add, edit, and delete their own custom categories.
  * **Importance:** Personalization is key. Users need their budget to reflect their unique spending habits.
  * **Implementation Status:**
* **Basic Budget Creation** (High - P1):
  * **Functionality:** Users can set monthly budget limits for each category. Visual indication of budget progress (e.g., "spent X of Y").
  * **Importance:** Enables the "budgeting" aspect. Users need to see where they stand against their limits.
  * **Implementation Status:**
* **Transaction List & Basic Filtering** (Medium - P2):
  * **Functionality:** A chronological list of all transactions. Simple filters by category, date range. Search by notes.
  * **Importance:** Provides transparency and allows users to review their spending history.
  * **Implementation Status:**

---

## Phase 2: Automation & Insights (Months 4-7)

**Goal:** Reduce manual effort and provide deeper insights into spending patterns, making the app more powerful and "sticky."

**Key Features & Importance:**

* **Transaction Matching & Categorization** (High - P1):
  * **Functionality:** Algorithm to automatically categorize imported transactions based on merchant name, past behavior, or user-defined rules. Ability for users to review and re-categorize.
  * **Importance:** Maximizes the benefit of bank integration, turning raw data into actionable insights without constant manual intervention.
  * **Implementation Status:**
* **Recurring Transactions** (High - P1):
  * **Functionality:** Users can mark transactions as recurring (e.g., rent, salary) and the app will automatically add them for future periods.
  * **Importance:** Automates predictable income and expenses, simplifying budget planning and future forecasting.
  * **Implementation Status:**
* **Visual Spending Reports** (High - P1):
  * **Functionality:** Interactive charts and graphs (e.g., pie charts of spending by category, bar charts of spending over time).
  * **Importance:** Makes data digestible and highlights trends, helping users understand where their money goes at a glance.
  * **Implementation Status:**
* **Budget Rollover** (Medium - P2):
  * **Functionality:** Option to roll over remaining budget from one month to the next (e.g., if you underspent on groceries, that budget carries over).
  * **Importance:** Adds flexibility and realism to budgeting, especially for variable expenses.
  * **Implementation Status:**
* **Goal Tracking (Simple)** (Medium - P2):
  * **Functionality:** Users can set simple savings goals (e.g., "Save $500 for vacation"). Track progress towards the goal.
  * **Importance:** Motivates users by connecting their budgeting efforts to tangible financial aspirations.
  * **Implementation Status:**

---

## Phase 3: Advanced Tools & Personalization (Months 8-12)

**Goal:** Provide more sophisticated tools for financial planning, deeper customization, and a richer user experience.

**Key Features & Importance:**

* **User Onboarding & Account Creation** (Critical - P0):
  * **Functionality:** Simple signup (email/password, Google/Apple sign-in). Basic profile setup.
  * **Importance:** Not an initial priority as target audience is single user at first.  However it will greatly increase appeal and usability for public release.
  * **Implementation Status:**
* **Forecasting & Future Budgeting** (High - P1):
  * **Functionality:** Based on recurring transactions and past spending, project future cash flow and budget needs. What-if scenarios.
  * **Importance:** Moves beyond just tracking to proactive financial planning, allowing users to anticipate future financial situations.
  * **Implementation Status:**
* **Customizable Dashboards** (High - P1):
  * **Functionality:** Users can customize the main dashboard to prioritize the information most relevant to them (e.g., specific budget progress, goal tracking, recent transactions).
  * **Importance:** Enhances user control and makes the app feel more personal and efficient.
  * **Implementation Status:**
* **Investment Tracking (Manual/Basic API)** (Medium - P2):
  * **Functionality:** Manual entry or basic API integration for investment accounts (stocks, crypto, mutual funds) to track current value and contribution.
  * **Importance:** Expands the net worth tracking, catering to users with more complex financial portfolios.
  * **Implementation Status:**
* **Debt Payoff Planning** (Medium - P2):
  * **Functionality:** Tools to model debt repayment strategies (e.g., snowball, avalanche method). Track progress on specific debts.
  * **Importance:** Provides actionable steps for users struggling with debt, helping them visualize and achieve debt freedom.
  * **Implementation Status:**
* **Advanced Transaction Rules** (Medium - P2):
  * **Functionality:** More sophisticated rules for auto-categorization (e.g., "if merchant contains 'Starbucks' AND amount < $10, categorize as 'Coffee'").
  * **Importance:** Further refines automation, reducing manual intervention and improving categorization accuracy.
  * **Implementation Status:**
* **Notifications & Alerts** (Medium - P2):
  * **Functionality:** Custom alerts for going over budget, upcoming bills, low account balances.
  * **Importance:** Keeps users engaged and proactive in managing their finances, preventing overdrafts or missed payments.
  * **Implementation Status:**
* **Bank Account Integration** (Low - P3):
  * **Functionality:** Securely connect to bank accounts (using third-party APIs like Plaid, Yodlee, etc.) to automatically import transactions. Users can select which accounts to connect.
  * **Importance:** **Game-changer.** Eliminates the biggest friction point (manual entry), dramatically improving user experience and data accuracy. Low Priority due to difficulty with each institution's proprietary interfaces
  * **Implementation Status:**
* **Net Worth (Manual Assets/Liabilities)** (Medium - P2):
  * **Functionality:** Users can manually add and track assets (e.g., cash, savings) and liabilities (e.g., credit card debt). A simple net worth calculation.
  * **Importance:** Offers a holistic view beyond just income/expenses, helping users see their overall financial picture.
  * **Implementation Status:**

---

## Phase 4: Expansion & Community (Months 13+)

**Goal:** Introduce features for broader financial management, social aspects, and continued growth.

**Key Features & Importance:**

* **Shared Budgets** (High - P1):
  * **Functionality:** Allow multiple users to share and contribute to a single budget (e.g., for couples, roommates).
  * **Importance:** Addresses a significant user need for joint financial management, expanding the app's utility.
  * **Implementation Status:**
* **Financial Learning Resources** (Medium - P2):
  * **Functionality:** In-app links or content on budgeting tips, saving strategies, investment basics, and financial literacy.
  * **Importance:** Positions the app as a financial partner, not just a tracker, adding educational value.
  * **Implementation Status:**
* **Receipt Scanning/OCR** (Medium - P2):
  * **Functionality:** Use device camera and OCR to automatically extract transaction details from receipts.
  * **Importance:** Offers an alternative or supplementary method to bank integration for specific types of purchases or cash transactions.
  * **Implementation Status:**
* **Custom Reports & Data Export** (Medium - P2):
  * **Functionality:** Users can create custom reports based on various parameters and export data (CSV, PDF).
  * **Importance:** Caters to power users who want more control over their data analysis.
  * **Implementation Status:**
* **Credit Score Tracking (Integration)** (Low - P3):
  * **Functionality:** Integration with a credit bureau to provide regular credit score updates and insights.
  * **Importance:** Adds another dimension to overall financial health tracking.
  * **Implementation Status:**
* **Gamification & Rewards** (Low - P3):
  * **Functionality:** Badges for achieving goals, streaks for consistent budgeting, potential partnerships for small rewards.
  * **Importance:** Enhances engagement and motivates users to stick with
