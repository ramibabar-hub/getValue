"""
getValue Platform - Financial Data Engine
Core module: data models, FMP API client, data formatting

Fetches Income Statement, Cash Flow, Balance Sheet data
from Financial Modeling Prep API for 10 years of annual data.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import re
import time

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'requests'])
    import requests


# ==============================================================================
# Data Models
# ==============================================================================

class PeriodType(Enum):
    TTM = "TTM"
    QUARTERLY = "Q"
    ANNUAL = "Y"


@dataclass
class IncomeStatement:
    revenues: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    interest_expense: Optional[float] = None
    income_tax: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    shares_outstanding: Optional[float] = None


@dataclass
class CashFlow:
    cash_flow_from_operations: Optional[float] = None
    capital_expenditures: Optional[float] = None
    free_cash_flow: Optional[float] = None
    stock_based_compensation: Optional[float] = None
    adjusted_fcf: Optional[float] = None
    depreciation_amortization: Optional[float] = None
    change_in_working_capital: Optional[float] = None
    dividend_paid: Optional[float] = None
    repurchase_of_common_stock: Optional[float] = None

    def calculate_fcf(self) -> Optional[float]:
        if self.free_cash_flow is not None:
            return self.free_cash_flow
        if self.cash_flow_from_operations is not None and self.capital_expenditures is not None:
            self.free_cash_flow = self.cash_flow_from_operations + self.capital_expenditures
            return self.free_cash_flow
        return None

    def calculate_adjusted_fcf(self) -> Optional[float]:
        fcf = self.calculate_fcf()
        if fcf is not None and self.stock_based_compensation is not None:
            self.adjusted_fcf = fcf - self.stock_based_compensation
            return self.adjusted_fcf
        return fcf


@dataclass
class BalanceSheet:
    cash_and_equivalents: Optional[float] = None
    current_assets: Optional[float] = None
    total_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_debt: Optional[float] = None
    equity_value: Optional[float] = None
    shares_outstanding: Optional[float] = None
    minority_interest: Optional[float] = None
    preferred_stock: Optional[float] = None
    avg_equity: Optional[float] = None
    avg_assets: Optional[float] = None


@dataclass
class DebtBreakdown:
    current_portion_long_term_debt: Optional[float] = None
    current_portion_capital_leases: Optional[float] = None
    long_term_debt: Optional[float] = None
    capital_leases: Optional[float] = None
    total_debt: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    net_debt: Optional[float] = None

    def calculate_net_debt(self) -> Optional[float]:
        if self.total_debt is not None and self.cash_and_equivalents is not None:
            self.net_debt = self.total_debt - self.cash_and_equivalents
            return self.net_debt
        return None


@dataclass
class MarketData:
    date: Optional[datetime] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None


@dataclass
class FinancialPeriod:
    period_type: PeriodType
    period_name: str
    period_end_date: Optional[datetime] = None

    income_statement: IncomeStatement = field(default_factory=IncomeStatement)
    cash_flow: CashFlow = field(default_factory=CashFlow)
    balance_sheet: BalanceSheet = field(default_factory=BalanceSheet)
    debt_breakdown: DebtBreakdown = field(default_factory=DebtBreakdown)
    market_data: Optional[MarketData] = None


@dataclass
class CompanyFinancials:
    ticker: str
    company_name: str
    currency: str = "USD"
    last_updated: Optional[datetime] = None

    ttm: Optional[FinancialPeriod] = None
    quarterly_data: List[FinancialPeriod] = field(default_factory=list)
    annual_data: List[FinancialPeriod] = field(default_factory=list)


# ==============================================================================
# Financial Ratios
# ==============================================================================

class FinancialRatios:
    def __init__(self, period: FinancialPeriod, previous_period: Optional[FinancialPeriod] = None):
        self.period = period
        self.previous_period = previous_period
        self.income = period.income_statement
        self.cash_flow = period.cash_flow
        self.balance = period.balance_sheet
        self.debt = period.debt_breakdown
        self.market = period.market_data

    def pe_ratio(self) -> Optional[float]:
        if self.market and self.market.market_cap and self.income.net_income:
            return self.market.market_cap / self.income.net_income
        return None

    def ps_ratio(self) -> Optional[float]:
        if self.market and self.market.market_cap and self.income.revenues:
            return self.market.market_cap / self.income.revenues
        return None

    def gross_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.gross_profit:
            return self.income.gross_profit / self.income.revenues
        return None

    def operating_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.operating_income:
            return self.income.operating_income / self.income.revenues
        return None

    def net_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.net_income:
            return self.income.net_income / self.income.revenues
        return None

    def roe(self) -> Optional[float]:
        if not self.previous_period:
            return None
        curr_eq = self.balance.equity_value
        prev_eq = self.previous_period.balance_sheet.equity_value
        if curr_eq and prev_eq and self.income.net_income:
            avg = (curr_eq + prev_eq) / 2
            if avg != 0:
                return self.income.net_income / avg
        return None

    def roic(self, tax_rate: Optional[float] = None) -> Optional[float]:
        if not self.income.operating_income:
            return None
        if tax_rate is None and self.income.income_tax and self.income.operating_income:
            tax_rate = abs(self.income.income_tax) / abs(self.income.operating_income)
        if tax_rate is None:
            return None
        nopat = self.income.operating_income * (1 - tax_rate)
        invested = 0
        if self.debt.total_debt:
            invested += abs(self.debt.total_debt)
        if self.balance.equity_value:
            invested += self.balance.equity_value
        if invested != 0:
            return nopat / invested
        return None

    def interest_coverage(self) -> Optional[float]:
        if self.income.interest_expense and self.income.interest_expense != 0:
            return self.income.operating_income / abs(self.income.interest_expense)
        return None

    def calculate_all_ratios(self) -> dict:
        return {
            'pe_ratio': self.pe_ratio(),
            'ps_ratio': self.ps_ratio(),
            'gross_margin': self.gross_margin(),
            'operating_margin': self.operating_margin(),
            'net_margin': self.net_margin(),
            'roe': self.roe(),
            'roic': self.roic(),
            'interest_coverage': self.interest_coverage(),
        }


# ==============================================================================
# Period Manager
# ==============================================================================

class PeriodManager:
    def __init__(self, company: CompanyFinancials):
        self.company = company

    @staticmethod
    def parse_period_info(period_name: str):
        period_name = period_name.strip()
        if period_name.upper() == 'TTM':
            return ('TTM', 0, None)
        quarter_match = re.match(r'(\d{4})\s*Q(\d)', period_name)
        if quarter_match:
            year, quarter = quarter_match.groups()
            return ('QUARTERLY', int(year), int(quarter))
        year_match = re.match(r'^(\d{4})$', period_name)
        if year_match:
            return ('ANNUAL', int(year_match.group(1)), None)
        return (None, 0, None)

    def calculate_ttm_from_quarters(self) -> Optional[FinancialPeriod]:
        if len(self.company.quarterly_data) < 4:
            return None
        sorted_q = self._sort_periods(self.company.quarterly_data[:4])
        ttm = FinancialPeriod(period_type=PeriodType.TTM, period_name="TTM")

        ttm.income_statement.revenues = self._sum_field(sorted_q, 'income_statement', 'revenues')
        ttm.income_statement.gross_profit = self._sum_field(sorted_q, 'income_statement', 'gross_profit')
        ttm.income_statement.operating_income = self._sum_field(sorted_q, 'income_statement', 'operating_income')
        ttm.income_statement.ebitda = self._sum_field(sorted_q, 'income_statement', 'ebitda')
        ttm.income_statement.interest_expense = self._sum_field(sorted_q, 'income_statement', 'interest_expense')
        ttm.income_statement.income_tax = self._sum_field(sorted_q, 'income_statement', 'income_tax')
        ttm.income_statement.net_income = self._sum_field(sorted_q, 'income_statement', 'net_income')
        ttm.income_statement.eps = self._sum_field(sorted_q, 'income_statement', 'eps')
        ttm.income_statement.shares_outstanding = sorted_q[0].income_statement.shares_outstanding

        ttm.cash_flow.cash_flow_from_operations = self._sum_field(sorted_q, 'cash_flow', 'cash_flow_from_operations')
        ttm.cash_flow.capital_expenditures = self._sum_field(sorted_q, 'cash_flow', 'capital_expenditures')
        ttm.cash_flow.free_cash_flow = self._sum_field(sorted_q, 'cash_flow', 'free_cash_flow')
        ttm.cash_flow.stock_based_compensation = self._sum_field(sorted_q, 'cash_flow', 'stock_based_compensation')
        ttm.cash_flow.depreciation_amortization = self._sum_field(sorted_q, 'cash_flow', 'depreciation_amortization')
        ttm.cash_flow.change_in_working_capital = self._sum_field(sorted_q, 'cash_flow', 'change_in_working_capital')
        ttm.cash_flow.dividend_paid = self._sum_field(sorted_q, 'cash_flow', 'dividend_paid')
        ttm.cash_flow.repurchase_of_common_stock = self._sum_field(sorted_q, 'cash_flow', 'repurchase_of_common_stock')
        ttm.cash_flow.calculate_fcf()
        ttm.cash_flow.calculate_adjusted_fcf()

        ttm.balance_sheet = sorted_q[0].balance_sheet
        ttm.debt_breakdown = sorted_q[0].debt_breakdown
        ttm.market_data = sorted_q[0].market_data

        return ttm

    def identify_last_full_year(self) -> Optional[int]:
        if not self.company.quarterly_data:
            if self.company.annual_data:
                s = self._sort_periods(self.company.annual_data)
                _, year, _ = self.parse_period_info(s[0].period_name)
                return year
            return None
        s = self._sort_periods(self.company.quarterly_data)
        _, year, quarter = self.parse_period_info(s[0].period_name)
        if quarter == 4:
            return year
        return year - 1

    def get_relevant_periods_order(self) -> dict:
        return {
            'ttm': self.company.ttm,
            'last_full_year': self.identify_last_full_year(),
            'quarterly': self.company.quarterly_data,
            'annual': self.company.annual_data,
        }

    def _sort_periods(self, periods: List[FinancialPeriod]) -> List[FinancialPeriod]:
        def sort_key(p):
            pt, year, quarter = self.parse_period_info(p.period_name)
            return (year, quarter if quarter else 0)
        return sorted(periods, key=sort_key, reverse=True)

    @staticmethod
    def _sum_field(periods: List[FinancialPeriod], obj_name: str, field_name: str) -> Optional[float]:
        total = 0
        count = 0
        for p in periods:
            obj = getattr(p, obj_name)
            val = getattr(obj, field_name, None)
            if val is not None:
                total += val
                count += 1
        return total if count > 0 else None


# ==============================================================================
# FMP API Client
# ==============================================================================

class FinancialDataAPI:
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.rate_limit_delay = 0.3
        self.last_request_time = 0

    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

        if params is None:
            params = {}
        params['apikey'] = self.api_key

        try:
            resp = self.session.get(f"{self.BASE_URL}{endpoint}", params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None

    @staticmethod
    def _to_millions(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value) / 1_000_000
        except (ValueError, TypeError):
            return None

    def fetch_company(self, symbol: str, num_years: int = 10) -> Optional[CompanyFinancials]:
        """Fetch complete financial data for a company."""
        symbol = symbol.upper().strip()

        # Company profile
        profile = self._request(f"/profile/{symbol}")
        if not profile or len(profile) == 0:
            return None
        p = profile[0]

        company = CompanyFinancials(
            ticker=symbol,
            company_name=p.get('companyName', symbol),
            currency=p.get('currency', 'USD'),
            last_updated=datetime.now(),
        )

        # Annual income statements
        annual_income = self._request(
            f"/income-statement/{symbol}",
            {"period": "annual", "limit": num_years + 1}
        ) or []

        # Annual balance sheets
        annual_balance = self._request(
            f"/balance-sheet-statement/{symbol}",
            {"period": "annual", "limit": num_years + 1}
        ) or []

        # Annual cash flow statements
        annual_cashflow = self._request(
            f"/cash-flow-statement/{symbol}",
            {"period": "annual", "limit": num_years + 1}
        ) or []

        # Quarterly income (for TTM)
        quarterly_income = self._request(
            f"/income-statement/{symbol}",
            {"period": "quarter", "limit": 8}
        ) or []

        # Quarterly balance sheets (for TTM)
        quarterly_balance = self._request(
            f"/balance-sheet-statement/{symbol}",
            {"period": "quarter", "limit": 8}
        ) or []

        # Quarterly cash flow (for TTM)
        quarterly_cashflow = self._request(
            f"/cash-flow-statement/{symbol}",
            {"period": "quarter", "limit": 8}
        ) or []

        # Build annual periods
        balance_by_date = {item.get('date', ''): item for item in annual_balance}
        cashflow_by_date = {item.get('date', ''): item for item in annual_cashflow}

        for inc in annual_income:
            date_str = inc.get('date', '')
            year = inc.get('calendarYear', '')
            period_name = str(year) if year else date_str[:4]

            period = FinancialPeriod(
                period_type=PeriodType.ANNUAL,
                period_name=period_name,
            )

            # Income Statement
            period.income_statement = IncomeStatement(
                revenues=self._to_millions(inc.get('revenue')),
                gross_profit=self._to_millions(inc.get('grossProfit')),
                operating_income=self._to_millions(inc.get('operatingIncome')),
                ebitda=self._to_millions(inc.get('ebitda')),
                interest_expense=self._to_millions(inc.get('interestExpense')),
                income_tax=self._to_millions(inc.get('incomeTaxExpense')),
                net_income=self._to_millions(inc.get('netIncome')),
                eps=inc.get('epsdiluted') or inc.get('eps'),
                shares_outstanding=self._to_millions(
                    inc.get('weightedAverageShsOutDil') or inc.get('weightedAverageShsOut')
                ),
            )

            # Balance Sheet
            bs_data = balance_by_date.get(date_str, {})
            period.balance_sheet = BalanceSheet(
                cash_and_equivalents=self._to_millions(bs_data.get('cashAndCashEquivalents')),
                current_assets=self._to_millions(bs_data.get('totalCurrentAssets')),
                total_assets=self._to_millions(bs_data.get('totalAssets')),
                current_liabilities=self._to_millions(bs_data.get('totalCurrentLiabilities')),
                total_debt=self._to_millions(bs_data.get('totalDebt')),
                equity_value=self._to_millions(bs_data.get('totalStockholdersEquity')),
                shares_outstanding=self._to_millions(
                    bs_data.get('commonStock') or inc.get('weightedAverageShsOutDil')
                ),
                minority_interest=self._to_millions(bs_data.get('minorityInterest')),
                preferred_stock=self._to_millions(bs_data.get('preferredStock')),
            )

            # Debt Breakdown
            period.debt_breakdown = DebtBreakdown(
                current_portion_long_term_debt=self._to_millions(bs_data.get('shortTermDebt')),
                current_portion_capital_leases=self._to_millions(bs_data.get('capitalLeaseObligations')),
                long_term_debt=self._to_millions(bs_data.get('longTermDebt')),
                capital_leases=self._to_millions(bs_data.get('capitalLeaseObligations')),
                total_debt=self._to_millions(bs_data.get('totalDebt')),
                cash_and_equivalents=self._to_millions(bs_data.get('cashAndCashEquivalents')),
                net_debt=self._to_millions(bs_data.get('netDebt')),
            )
            if period.debt_breakdown.net_debt is None:
                period.debt_breakdown.calculate_net_debt()

            # Cash Flow
            cf_data = cashflow_by_date.get(date_str, {})
            capex = self._to_millions(cf_data.get('capitalExpenditure'))
            period.cash_flow = CashFlow(
                cash_flow_from_operations=self._to_millions(cf_data.get('operatingCashFlow')),
                capital_expenditures=capex,
                free_cash_flow=self._to_millions(cf_data.get('freeCashFlow')),
                stock_based_compensation=self._to_millions(cf_data.get('stockBasedCompensation')),
                depreciation_amortization=self._to_millions(cf_data.get('depreciationAndAmortization')),
                change_in_working_capital=self._to_millions(cf_data.get('changeInWorkingCapital')),
                dividend_paid=self._to_millions(cf_data.get('dividendsPaid')),
                repurchase_of_common_stock=self._to_millions(cf_data.get('commonStockRepurchased')),
            )
            period.cash_flow.calculate_fcf()
            period.cash_flow.calculate_adjusted_fcf()

            company.annual_data.append(period)

        # Build quarterly periods (for TTM)
        q_balance_by_date = {item.get('date', ''): item for item in quarterly_balance}
        q_cashflow_by_date = {item.get('date', ''): item for item in quarterly_cashflow}

        for inc in quarterly_income:
            date_str = inc.get('date', '')
            period_str = inc.get('period', '')
            year = inc.get('calendarYear', '')
            period_name = f"{year} {period_str}" if period_str else date_str[:7]

            period = FinancialPeriod(
                period_type=PeriodType.QUARTERLY,
                period_name=period_name,
            )

            period.income_statement = IncomeStatement(
                revenues=self._to_millions(inc.get('revenue')),
                gross_profit=self._to_millions(inc.get('grossProfit')),
                operating_income=self._to_millions(inc.get('operatingIncome')),
                ebitda=self._to_millions(inc.get('ebitda')),
                interest_expense=self._to_millions(inc.get('interestExpense')),
                income_tax=self._to_millions(inc.get('incomeTaxExpense')),
                net_income=self._to_millions(inc.get('netIncome')),
                eps=inc.get('epsdiluted') or inc.get('eps'),
                shares_outstanding=self._to_millions(
                    inc.get('weightedAverageShsOutDil') or inc.get('weightedAverageShsOut')
                ),
            )

            bs_data = q_balance_by_date.get(date_str, {})
            period.balance_sheet = BalanceSheet(
                cash_and_equivalents=self._to_millions(bs_data.get('cashAndCashEquivalents')),
                current_assets=self._to_millions(bs_data.get('totalCurrentAssets')),
                total_assets=self._to_millions(bs_data.get('totalAssets')),
                current_liabilities=self._to_millions(bs_data.get('totalCurrentLiabilities')),
                total_debt=self._to_millions(bs_data.get('totalDebt')),
                equity_value=self._to_millions(bs_data.get('totalStockholdersEquity')),
                shares_outstanding=self._to_millions(bs_data.get('commonStock')),
                minority_interest=self._to_millions(bs_data.get('minorityInterest')),
                preferred_stock=self._to_millions(bs_data.get('preferredStock')),
            )

            period.debt_breakdown = DebtBreakdown(
                current_portion_long_term_debt=self._to_millions(bs_data.get('shortTermDebt')),
                current_portion_capital_leases=self._to_millions(bs_data.get('capitalLeaseObligations')),
                long_term_debt=self._to_millions(bs_data.get('longTermDebt')),
                capital_leases=self._to_millions(bs_data.get('capitalLeaseObligations')),
                total_debt=self._to_millions(bs_data.get('totalDebt')),
                cash_and_equivalents=self._to_millions(bs_data.get('cashAndCashEquivalents')),
                net_debt=self._to_millions(bs_data.get('netDebt')),
            )
            if period.debt_breakdown.net_debt is None:
                period.debt_breakdown.calculate_net_debt()

            cf_data = q_cashflow_by_date.get(date_str, {})
            period.cash_flow = CashFlow(
                cash_flow_from_operations=self._to_millions(cf_data.get('operatingCashFlow')),
                capital_expenditures=self._to_millions(cf_data.get('capitalExpenditure')),
                free_cash_flow=self._to_millions(cf_data.get('freeCashFlow')),
                stock_based_compensation=self._to_millions(cf_data.get('stockBasedCompensation')),
                depreciation_amortization=self._to_millions(cf_data.get('depreciationAndAmortization')),
                change_in_working_capital=self._to_millions(cf_data.get('changeInWorkingCapital')),
                dividend_paid=self._to_millions(cf_data.get('dividendsPaid')),
                repurchase_of_common_stock=self._to_millions(cf_data.get('commonStockRepurchased')),
            )
            period.cash_flow.calculate_fcf()
            period.cash_flow.calculate_adjusted_fcf()

            company.quarterly_data.append(period)

        # Calculate averages (Avg. Equity, Avg. Assets) for annual data
        self._calculate_averages(company.annual_data)

        # Calculate TTM from quarters
        if len(company.quarterly_data) >= 4:
            pm = PeriodManager(company)
            company.ttm = pm.calculate_ttm_from_quarters()

        # Trim to requested number of years
        company.annual_data = company.annual_data[:num_years]

        return company

    @staticmethod
    def _calculate_averages(annual_data: List[FinancialPeriod]):
        """Calculate Avg. Equity and Avg. Assets from consecutive annual periods."""
        for i in range(len(annual_data)):
            if i + 1 < len(annual_data):
                curr = annual_data[i].balance_sheet
                prev = annual_data[i + 1].balance_sheet
                if curr.equity_value is not None and prev.equity_value is not None:
                    curr.avg_equity = (curr.equity_value + prev.equity_value) / 2
                if curr.total_assets is not None and prev.total_assets is not None:
                    curr.avg_assets = (curr.total_assets + prev.total_assets) / 2


# ==============================================================================
# Text Parser (for Excel paste)
# ==============================================================================

class FinancialDataParser:
    @staticmethod
    def parse_from_text(text: str, ticker: str = "UNKNOWN") -> CompanyFinancials:
        lines = text.strip().split('\n')
        data = []
        for line in lines:
            row = re.split(r'\t+', line)
            data.append(row)

        company = CompanyFinancials(ticker=ticker, company_name=ticker)

        header_row_idx = None
        for idx, row in enumerate(data):
            if row and row[0] and 'Income statement' in str(row[0]):
                header_row_idx = idx
                break

        if header_row_idx is None:
            return company

        headers = data[header_row_idx]
        periods = []

        for col_idx in range(1, len(headers)):
            period_name = headers[col_idx].strip()
            if 'TTM' in period_name.upper():
                ptype = PeriodType.TTM
            elif 'Q' in period_name:
                ptype = PeriodType.QUARTERLY
            else:
                ptype = PeriodType.ANNUAL
            period = FinancialPeriod(period_type=ptype, period_name=period_name)
            periods.append(period)

        field_map = {
            'Revenues': ('income_statement', 'revenues'),
            'Gross profit': ('income_statement', 'gross_profit'),
            'Operating income': ('income_statement', 'operating_income'),
            'EBITDA': ('income_statement', 'ebitda'),
            'Interest Expense': ('income_statement', 'interest_expense'),
            'Income Tax': ('income_statement', 'income_tax'),
            'Net Income': ('income_statement', 'net_income'),
            'EPS': ('income_statement', 'eps'),
            'Cash flow from operations': ('cash_flow', 'cash_flow_from_operations'),
            'Capital expenditures': ('cash_flow', 'capital_expenditures'),
            'Free Cash flow': ('cash_flow', 'free_cash_flow'),
            'Stock based compensation': ('cash_flow', 'stock_based_compensation'),
            'Depreciation & Amortization': ('cash_flow', 'depreciation_amortization'),
            'Change in Working Capital': ('cash_flow', 'change_in_working_capital'),
            'Dividend paid': ('cash_flow', 'dividend_paid'),
            'Repurchase of Common Stock': ('cash_flow', 'repurchase_of_common_stock'),
        }

        for row in data[header_row_idx + 1:]:
            if not row or not row[0]:
                continue
            f = row[0].strip()
            if f in field_map:
                obj_name, attr_name = field_map[f]
                for ci in range(1, min(len(row), len(periods) + 1)):
                    try:
                        v = float(row[ci].replace(',', ''))
                        obj = getattr(periods[ci - 1], obj_name)
                        setattr(obj, attr_name, v)
                    except (ValueError, IndexError):
                        pass

        for period in periods:
            if period.period_type == PeriodType.TTM:
                company.ttm = period
            elif period.period_type == PeriodType.QUARTERLY:
                company.quarterly_data.append(period)
            else:
                company.annual_data.append(period)

        if company.ttm is None and len(company.quarterly_data) >= 4:
            pm = PeriodManager(company)
            company.ttm = pm.calculate_ttm_from_quarters()

        return company


# ==============================================================================
# Main Data Manager
# ==============================================================================

class GetValueDataManager:
    def __init__(self, api_key: str = "zF2GUU9LVP2ICuLDKJJ9SwQhkzw1TN4i"):
        self.api_key = api_key
        self.api_client = FinancialDataAPI(api_key) if api_key else None
        self.companies: Dict[str, CompanyFinancials] = {}

    def load_company(self, source: Union[str, Any], ticker: Optional[str] = None) -> Optional[CompanyFinancials]:
        source_str = str(source)

        if len(source_str) <= 6 and source_str.replace('.', '').isalpha() and self.api_client:
            company = self.api_client.fetch_company(source_str.upper())
        elif '\t' in source_str or source_str.count('\n') > 3:
            company = FinancialDataParser.parse_from_text(source_str, ticker or "UNKNOWN")
        else:
            return None

        if company:
            self.companies[company.ticker] = company

        return company
