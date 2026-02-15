"""
getValue Platform - Stock Financial Agent
Type a ticker symbol and get a complete financial report for the last 10 years.

Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from financial_data import GetValueDataManager, PeriodManager, FinancialRatios

# ==============================================================================
# Page Config
# ==============================================================================

st.set_page_config(
    page_title="getValue - Stock Financial Agent",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    div[data-testid="stDataFrame"] table {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# Header
# ==============================================================================

st.markdown('<h1 class="main-title">getValue - Stock Financial Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Enter a ticker symbol to get 10 years of financial data</p>', unsafe_allow_html=True)

# ==============================================================================
# Session State
# ==============================================================================

API_KEY = "zF2GUU9LVP2ICuLDKJJ9SwQhkzw1TN4i"

if 'company' not in st.session_state:
    st.session_state.company = None
if 'manager' not in st.session_state:
    st.session_state.manager = GetValueDataManager(api_key=API_KEY)

# ==============================================================================
# Ticker Input
# ==============================================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    input_col, btn_col = st.columns([3, 1])
    with input_col:
        ticker = st.text_input(
            "Ticker Symbol:",
            value="",
            placeholder="e.g. MSFT, AAPL, GOOGL, TSLA...",
            label_visibility="collapsed",
        )
    with btn_col:
        fetch_clicked = st.button("Get Data", type="primary", use_container_width=True)

# ==============================================================================
# Data Fetching
# ==============================================================================

if fetch_clicked and ticker.strip():
    with st.spinner(f'Fetching data for {ticker.upper()}...'):
        try:
            company = st.session_state.manager.load_company(ticker.strip().upper())
            if company and company.annual_data:
                st.session_state.company = company
            else:
                st.error(f"Could not load data for '{ticker.upper()}'. Check the ticker symbol.")
                st.session_state.company = None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.company = None

# ==============================================================================
# Formatting Helpers
# ==============================================================================

def fmt_num(val, is_eps=False, is_shares=False):
    """Format a number for display."""
    if val is None:
        return ""
    if is_eps:
        return f"{val:.2f}"
    if is_shares:
        # shares are in millions, display as millions
        return f"{val:,.0f}"
    # Regular millions
    return f"{val:,.0f}"


def build_table(periods, rows_config, ltr=True):
    """
    Build a DataFrame from periods with specified rows.
    rows_config: list of (display_name, getter_func)
    ltr: if True, oldest year on left (reversed from API order)
    """
    if ltr:
        periods = list(reversed(periods))

    data = {}
    for period in periods:
        col_name = period.period_name
        col_values = {}
        for display_name, getter in rows_config:
            col_values[display_name] = getter(period)
        data[col_name] = col_values

    df = pd.DataFrame(data)
    return df


# ==============================================================================
# Display Results
# ==============================================================================

company = st.session_state.company

if company and company.annual_data:
    st.markdown("---")
    st.markdown(f"### {company.company_name} ({company.ticker})")

    periods = company.annual_data

    # ------------------------------------------------------------------
    # 1. Income Statement
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header">Income Statement</div>', unsafe_allow_html=True)

    income_rows = [
        ("Revenues",         lambda p: fmt_num(p.income_statement.revenues)),
        ("Gross Profit",     lambda p: fmt_num(p.income_statement.gross_profit)),
        ("Operating Income", lambda p: fmt_num(p.income_statement.operating_income)),
        ("EBITDA",           lambda p: fmt_num(p.income_statement.ebitda)),
        ("Interest Expense", lambda p: fmt_num(p.income_statement.interest_expense)),
        ("Income Tax",       lambda p: fmt_num(p.income_statement.income_tax)),
        ("Net Income",       lambda p: fmt_num(p.income_statement.net_income)),
        ("EPS",              lambda p: fmt_num(p.income_statement.eps, is_eps=True)),
    ]

    df_income = build_table(periods, income_rows, ltr=True)
    st.dataframe(df_income, use_container_width=True, height=330)

    # ------------------------------------------------------------------
    # 2. Cash Flow
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header">Cash Flow</div>', unsafe_allow_html=True)

    cashflow_rows = [
        ("Cash Flow from Operations",    lambda p: fmt_num(p.cash_flow.cash_flow_from_operations)),
        ("Capital Expenditures",          lambda p: fmt_num(p.cash_flow.capital_expenditures)),
        ("Free Cash Flow",               lambda p: fmt_num(p.cash_flow.free_cash_flow)),
        ("Stock Based Compensation",      lambda p: fmt_num(p.cash_flow.stock_based_compensation)),
        ("Adj. FCF",                      lambda p: fmt_num(p.cash_flow.adjusted_fcf)),
        ("Depreciation & Amortization",   lambda p: fmt_num(p.cash_flow.depreciation_amortization)),
        ("Change in Working Capital",     lambda p: fmt_num(p.cash_flow.change_in_working_capital)),
        ("Dividend Paid",                 lambda p: fmt_num(p.cash_flow.dividend_paid)),
        ("Repurchase of Common Stock",    lambda p: fmt_num(p.cash_flow.repurchase_of_common_stock)),
    ]

    df_cf = build_table(periods, cashflow_rows, ltr=True)
    st.dataframe(df_cf, use_container_width=True, height=365)

    # ------------------------------------------------------------------
    # 3. Balance Sheet
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header">Balance Sheet</div>', unsafe_allow_html=True)

    balance_rows = [
        ("Cash and Cash Equivalents",  lambda p: fmt_num(p.balance_sheet.cash_and_equivalents)),
        ("Current Assets",             lambda p: fmt_num(p.balance_sheet.current_assets)),
        ("Total Assets",               lambda p: fmt_num(p.balance_sheet.total_assets)),
        ("Total Current Liabilities",  lambda p: fmt_num(p.balance_sheet.current_liabilities)),
        ("Debt",                        lambda p: fmt_num(p.balance_sheet.total_debt)),
        ("Equity Value",               lambda p: fmt_num(p.balance_sheet.equity_value)),
        ("Shares Outstanding",         lambda p: fmt_num(p.income_statement.shares_outstanding, is_shares=True)),
        ("Minority Interest",          lambda p: fmt_num(p.balance_sheet.minority_interest)),
        ("Preferred Stock",            lambda p: fmt_num(p.balance_sheet.preferred_stock)),
        ("Avg. Equity",                lambda p: fmt_num(p.balance_sheet.avg_equity)),
        ("Avg. Assets",                lambda p: fmt_num(p.balance_sheet.avg_assets)),
    ]

    df_bs = build_table(periods, balance_rows, ltr=True)
    st.dataframe(df_bs, use_container_width=True, height=435)

    # ------------------------------------------------------------------
    # 4. Debt
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header">Debt</div>', unsafe_allow_html=True)

    debt_rows = [
        ("Current Portion of Long-Term Debt",          lambda p: fmt_num(p.debt_breakdown.current_portion_long_term_debt)),
        ("Current Portion of Capital Lease Obligations", lambda p: fmt_num(p.debt_breakdown.current_portion_capital_leases)),
        ("Long-Term Debt",                              lambda p: fmt_num(p.debt_breakdown.long_term_debt)),
        ("Capital Leases",                              lambda p: fmt_num(p.debt_breakdown.capital_leases)),
        ("Total Debt",                                  lambda p: fmt_num(p.debt_breakdown.total_debt)),
        ("Cash and Cash Equivalents",                   lambda p: fmt_num(p.debt_breakdown.cash_and_equivalents)),
        ("Net Debt",                                    lambda p: fmt_num(p.debt_breakdown.net_debt)),
    ]

    df_debt = build_table(periods, debt_rows, ltr=True)
    st.dataframe(df_debt, use_container_width=True, height=295)

    # ------------------------------------------------------------------
    # TTM Summary (if available)
    # ------------------------------------------------------------------
    if company.ttm:
        st.markdown("---")
        st.markdown('<div class="section-header">TTM Summary (Trailing Twelve Months)</div>', unsafe_allow_html=True)

        ttm = company.ttm
        inc = ttm.income_statement
        cf = ttm.cash_flow

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if inc.revenues is not None:
                st.metric("Revenues", f"${inc.revenues:,.0f}M")
        with c2:
            if inc.net_income is not None:
                st.metric("Net Income", f"${inc.net_income:,.0f}M")
        with c3:
            if inc.eps is not None:
                st.metric("EPS", f"${inc.eps:.2f}")
        with c4:
            if cf.free_cash_flow is not None:
                st.metric("Free Cash Flow", f"${cf.free_cash_flow:,.0f}M")

else:
    if not (fetch_clicked and ticker.strip()):
        st.markdown("---")
        st.info("Enter a ticker symbol above and click **Get Data** to fetch the financial report.")

# ==============================================================================
# Footer
# ==============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85rem;'>
    getValue Platform | Data: Financial Modeling Prep API | All amounts in $M (millions)
</div>
""", unsafe_allow_html=True)
