"""
===============================================================================
getValue Platform - Complete System (All-in-One)
מערכת ניתוח פיננסי מלאה לפלטפורמת getValue

גרסה: 1.0.0
תאריך: ינואר 2026
נוצר עבור: רמי

כל המערכת בקובץ אחד - מוכן לשימוש!
===============================================================================

🚀 התחלה מהירה:

# התקנת requirements (רק פעם אחת)
!pip install requests

# שימוש:
manager = GetValueDataManager()
company = manager.load_company("AAPL")  # או טקסט מאקסל

===============================================================================
"""

# ===============================================================================
# SECTION 1: IMPORTS
# ===============================================================================

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime
from enum import Enum
import re
import time
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("⚠️  Installing requests...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'requests'])
    import requests


# ===============================================================================
# SECTION 2: FINANCIAL MODELS (מבני נתונים)
# ===============================================================================

class PeriodType(Enum):
    """סוג תקופה"""
    TTM = "TTM"
    QUARTERLY = "Q"
    ANNUAL = "Y"


@dataclass
class IncomeStatement:
    """דוח רווח והפסד"""
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
    """דוח תזרים מזומנים"""
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
        if self.cash_flow_from_operations and self.capital_expenditures:
            self.free_cash_flow = self.cash_flow_from_operations - self.capital_expenditures
            return self.free_cash_flow
        return None
    
    def calculate_adjusted_fcf(self) -> Optional[float]:
        fcf = self.calculate_fcf()
        if fcf and self.stock_based_compensation:
            self.adjusted_fcf = fcf - self.stock_based_compensation
            return self.adjusted_fcf
        return None


@dataclass
class BalanceSheet:
    """מאזן"""
    cash_and_equivalents: Optional[float] = None
    current_assets: Optional[float] = None
    total_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_debt: Optional[float] = None
    equity_value: Optional[float] = None
    shares_outstanding: Optional[float] = None
    minority_interest: Optional[float] = None
    preferred_stock: Optional[float] = None


@dataclass
class DebtBreakdown:
    """פירוט החוב"""
    current_portion_long_term_debt: Optional[float] = None
    current_portion_capital_leases: Optional[float] = None
    long_term_debt: Optional[float] = None
    capital_leases: Optional[float] = None
    total_debt: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    net_debt: Optional[float] = None
    
    def calculate_net_debt(self) -> Optional[float]:
        if self.total_debt and self.cash_and_equivalents:
            self.net_debt = self.total_debt - self.cash_and_equivalents
            return self.net_debt
        return None


@dataclass
class MarketData:
    """נתוני שוק"""
    date: Optional[datetime] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None


@dataclass
class FinancialPeriod:
    """תקופה פיננסית בודדת"""
    period_type: PeriodType
    period_name: str
    period_end_date: Optional[datetime] = None
    
    income_statement: IncomeStatement = field(default_factory=IncomeStatement)
    cash_flow: CashFlow = field(default_factory=CashFlow)
    balance_sheet: BalanceSheet = field(default_factory=BalanceSheet)
    debt_breakdown: DebtBreakdown = field(default_factory=DebtBreakdown)
    market_data: Optional[MarketData] = None
    
    num_employees: Optional[int] = None
    corporate_tax_rate: Optional[float] = None
    beta: Optional[float] = None


@dataclass
class CompanyFinancials:
    """נתונים פיננסיים מלאים של חברה"""
    ticker: str
    company_name: str
    currency: str = "USD"
    last_updated: Optional[datetime] = None
    
    ttm: Optional[FinancialPeriod] = None
    quarterly_data: List[FinancialPeriod] = field(default_factory=list)
    annual_data: List[FinancialPeriod] = field(default_factory=list)
    
    wacc: Optional[float] = None
    cost_of_debt: Optional[float] = None
    cost_of_equity: Optional[float] = None


# ===============================================================================
# SECTION 3: FINANCIAL RATIOS (חישוב יחסים)
# ===============================================================================

class FinancialRatios:
    """מחלקה לחישוב יחסים פיננסיים"""
    
    def __init__(self, period: FinancialPeriod, previous_period: Optional[FinancialPeriod] = None):
        self.period = period
        self.previous_period = previous_period
        self.income = period.income_statement
        self.cash_flow = period.cash_flow
        self.balance = period.balance_sheet
        self.debt = period.debt_breakdown
        self.market = period.market_data
    
    # Valuation
    def pe_ratio(self) -> Optional[float]:
        if self.market and self.market.market_cap and self.income.net_income:
            return self.market.market_cap / self.income.net_income
        return None
    
    def ps_ratio(self) -> Optional[float]:
        if self.market and self.market.market_cap and self.income.revenues:
            return self.market.market_cap / self.income.revenues
        return None
    
    # Profitability
    def gross_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.revenues != 0 and self.income.gross_profit:
            return self.income.gross_profit / self.income.revenues
        return None
    
    def operating_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.revenues != 0 and self.income.operating_income:
            return self.income.operating_income / self.income.revenues
        return None
    
    def net_margin(self) -> Optional[float]:
        if self.income.revenues and self.income.revenues != 0 and self.income.net_income:
            return self.income.net_income / self.income.revenues
        return None
    
    # Returns
    def roe(self) -> Optional[float]:
        if not self.previous_period:
            return None
        curr_equity = self.balance.equity_value
        prev_equity = self.previous_period.balance_sheet.equity_value
        if curr_equity and prev_equity and self.income.net_income:
            avg_equity = (curr_equity + prev_equity) / 2
            if avg_equity != 0:
                return self.income.net_income / avg_equity
        return None
    
    def roic(self, tax_rate: Optional[float] = None) -> Optional[float]:
        if not self.income.operating_income:
            return None
        if tax_rate is None and self.income.income_tax and self.income.operating_income:
            tax_rate = self.income.income_tax / self.income.operating_income
        if tax_rate is None:
            return None
        nopat = self.income.operating_income * (1 - tax_rate)
        invested_capital = 0
        if self.debt.total_debt:
            invested_capital += abs(self.debt.total_debt)
        if self.balance.equity_value:
            invested_capital += self.balance.equity_value
        if invested_capital != 0:
            return nopat / invested_capital
        return None
    
    # Capital Structure
    def interest_coverage(self) -> Optional[float]:
        if self.income.interest_expense and self.income.interest_expense != 0:
            return self.income.operating_income / abs(self.income.interest_expense)
        return None
    
    def calculate_all_ratios(self, wacc: Optional[float] = None) -> dict:
        """חישוב כל היחסים"""
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


# ===============================================================================
# SECTION 4: PERIOD MANAGER (ניהול תקופות דינמי)
# ===============================================================================

class PeriodManager:
    """מנהל תקופות - זיהוי ועדכון דינמי"""
    
    def __init__(self, company: CompanyFinancials):
        self.company = company
    
    @staticmethod
    def parse_period_info(period_name: str):
        """פירוק שם תקופה"""
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
        """חישוב TTM מ-4 רבעונים"""
        if len(self.company.quarterly_data) < 4:
            return None
        
        sorted_quarters = self._sort_periods(self.company.quarterly_data[:4])
        ttm = FinancialPeriod(period_type=PeriodType.TTM, period_name="TTM")
        
        # חיבור Income Statement
        ttm.income_statement.revenues = self._sum_field(sorted_quarters, 'income_statement', 'revenues')
        ttm.income_statement.gross_profit = self._sum_field(sorted_quarters, 'income_statement', 'gross_profit')
        ttm.income_statement.operating_income = self._sum_field(sorted_quarters, 'income_statement', 'operating_income')
        ttm.income_statement.net_income = self._sum_field(sorted_quarters, 'income_statement', 'net_income')
        ttm.income_statement.eps = sorted_quarters[0].income_statement.eps
        
        # Cash Flow
        ttm.cash_flow.cash_flow_from_operations = self._sum_field(sorted_quarters, 'cash_flow', 'cash_flow_from_operations')
        ttm.cash_flow.free_cash_flow = self._sum_field(sorted_quarters, 'cash_flow', 'free_cash_flow')
        
        # Balance Sheet - מהרבעון האחרון
        ttm.balance_sheet = sorted_quarters[0].balance_sheet
        ttm.market_data = sorted_quarters[0].market_data
        
        return ttm
    
    def identify_last_full_year(self) -> Optional[int]:
        """זיהוי השנה המלאה האחרונה"""
        if not self.company.quarterly_data:
            if self.company.annual_data:
                sorted_annual = self._sort_periods(self.company.annual_data)
                _, year, _ = self.parse_period_info(sorted_annual[0].period_name)
                return year
            return None
        
        sorted_quarters = self._sort_periods(self.company.quarterly_data)
        _, year, quarter = self.parse_period_info(sorted_quarters[0].period_name)
        
        if quarter == 4:
            return year
        return year - 1
    
    def print_period_structure(self):
        """הדפסת מבנה תקופות"""
        print("="*70)
        print("📊 Period Structure")
        print("="*70)
        
        if self.company.ttm:
            print(f"\n🔄 TTM: Calculated from 4 latest quarters")
        
        last_year = self.identify_last_full_year()
        if last_year:
            print(f"📅 Last Full Year: {last_year}")
        
        if self.company.quarterly_data:
            print(f"\n📈 Quarterly Data: {len(self.company.quarterly_data)} quarters")
            for i, q in enumerate(self.company.quarterly_data[:5], 1):
                rev = q.income_statement.revenues
                print(f"   {i}. {q.period_name:12s} - Revenue: ${rev:,.0f}M" if rev else f"   {i}. {q.period_name}")
        
        print("="*70)
    
    def _sort_periods(self, periods: List[FinancialPeriod]) -> List[FinancialPeriod]:
        """מיון תקופות מהחדש לישן"""
        def sort_key(period):
            ptype, year, quarter = self.parse_period_info(period.period_name)
            return (year, quarter if quarter else 0)
        return sorted(periods, key=sort_key, reverse=True)
    
    @staticmethod
    def _sum_field(periods: List[FinancialPeriod], obj_name: str, field_name: str) -> Optional[float]:
        """סיכום שדה"""
        total = 0
        count = 0
        for period in periods:
            obj = getattr(period, obj_name)
            value = getattr(obj, field_name, None)
            if value is not None:
                total += value
                count += 1
        return total if count > 0 else None


# ===============================================================================
# SECTION 5: FINANCIAL API CLIENT
# ===============================================================================

class FinancialDataAPI:
    """Client למשיכת נתונים מ-API"""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.rate_limit_delay = 0.25
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """ביצוע בקשת API"""
        time.sleep(max(0, self.rate_limit_delay - (time.time() - self.last_request_time)))
        self.last_request_time = time.time()
        
        if params is None:
            params = {}
        params['apikey'] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def fetch_complete_data(self, symbol: str, num_periods: int = 10) -> Optional[CompanyFinancials]:
        """משיכת נתונים מלאים"""
        print(f"🔍 Fetching {symbol} from API...")
        
        # Profile
        profile = self._make_request(f"/profile/{symbol}")
        if not profile or len(profile) == 0:
            return None
        profile = profile[0]
        
        company = CompanyFinancials(
            ticker=symbol,
            company_name=profile.get('companyName', symbol),
            currency=profile.get('currency', 'USD'),
            last_updated=datetime.now()
        )
        
        # Quarterly data
        quarterly_income = self._make_request(f"/income-statement/{symbol}", {"period": "quarter", "limit": num_periods})
        if quarterly_income:
            company.quarterly_data = self._parse_periods(quarterly_income, PeriodType.QUARTERLY)
            print(f"✅ Loaded {len(company.quarterly_data)} quarters")
        
        # TTM
        if len(company.quarterly_data) >= 4:
            manager = PeriodManager(company)
            company.ttm = manager.calculate_ttm_from_quarters()
            print(f"✅ TTM calculated")
        
        return company
    
    def _parse_periods(self, income_data: List[Dict], period_type: PeriodType) -> List[FinancialPeriod]:
        """המרת נתוני API"""
        periods = []
        for income in income_data:
            date_str = income.get('date', '')
            period_str = income.get('period', '')
            year = income.get('calendarYear', '')
            
            if period_type == PeriodType.QUARTERLY:
                period_name = f"{year} {period_str}"
            else:
                period_name = str(year)
            
            period = FinancialPeriod(
                period_type=period_type,
                period_name=period_name
            )
            
            # Income Statement
            period.income_statement.revenues = self._get_millions(income, 'revenue')
            period.income_statement.net_income = self._get_millions(income, 'netIncome')
            period.income_statement.gross_profit = self._get_millions(income, 'grossProfit')
            period.income_statement.operating_income = self._get_millions(income, 'operatingIncome')
            period.income_statement.eps = income.get('eps')
            
            periods.append(period)
        
        return periods
    
    @staticmethod
    def _get_millions(data: Dict, key: str) -> Optional[float]:
        """המרת ערך למיליונים"""
        value = data.get(key)
        if value is None:
            return None
        try:
            return float(value) / 1_000_000
        except:
            return None


# ===============================================================================
# SECTION 6: DATA LOADER (טוען נתונים אוניברסלי)
# ===============================================================================

class FinancialDataParser:
    """Parser לנתונים פיננסיים"""
    
    @staticmethod
    def parse_from_text(text: str, ticker: str = "UNKNOWN") -> CompanyFinancials:
        """Parse מטקסט"""
        lines = text.strip().split('\n')
        data = []
        for line in lines:
            row = re.split(r'\t+', line)
            data.append(row)
        
        company = CompanyFinancials(ticker=ticker, company_name=ticker)
        
        # מציאת כותרות
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
        
        # קריאת נתונים
        field_map = {
            'Revenues': ('income_statement', 'revenues'),
            'Gross profit': ('income_statement', 'gross_profit'),
            'Operating income': ('income_statement', 'operating_income'),
            'Net Income': ('income_statement', 'net_income'),
            'EPS': ('income_statement', 'eps'),
            'Cash flow from operations': ('cash_flow', 'cash_flow_from_operations'),
            'Free Cash flow': ('cash_flow', 'free_cash_flow'),
        }
        
        for row in data[header_row_idx + 1:]:
            if not row or not row[0]:
                continue
            field = row[0].strip()
            if field in field_map:
                obj_name, attr_name = field_map[field]
                for col_idx in range(1, min(len(row), len(periods) + 1)):
                    try:
                        value = float(row[col_idx].replace(',', ''))
                        period = periods[col_idx - 1]
                        obj = getattr(period, obj_name)
                        setattr(obj, attr_name, value)
                    except:
                        pass
        
        # שמירת תקופות
        for period in periods:
            if period.period_type == PeriodType.TTM:
                company.ttm = period
            elif period.period_type == PeriodType.QUARTERLY:
                company.quarterly_data.append(period)
        
        # חישוב TTM אוטומטי
        if company.ttm is None and len(company.quarterly_data) >= 4:
            manager = PeriodManager(company)
            company.ttm = manager.calculate_ttm_from_quarters()
        
        return company


class GetValueDataManager:
    """מנהל נתונים מרכזי"""
    
    def __init__(self, api_key: str = "69724f3b18d8b1.58945206"):
        self.api_key = api_key
        self.api_client = FinancialDataAPI(api_key) if api_key else None
        self.companies: Dict[str, CompanyFinancials] = {}
    
    def load_company(self, source: Union[str, Path], ticker: Optional[str] = None) -> Optional[CompanyFinancials]:
        """טעינת חברה"""
        source_str = str(source)
        
        # זיהוי אוטומטי
        if len(source_str) <= 5 and source_str.isupper() and self.api_client:
            # סימול מניה - טעינה מ-API
            print(f"📡 Loading {source_str} from API...")
            company = self.api_client.fetch_complete_data(source_str)
        elif '\t' in source_str or source_str.count('\n') > 3:
            # טקסט מועתק
            print(f"📝 Loading from text...")
            company = FinancialDataParser.parse_from_text(source_str, ticker or "UNKNOWN")
        else:
            print(f"❌ Could not detect source type")
            return None
        
        if company:
            self.companies[company.ticker] = company
            print(f"✅ Loaded {company.ticker}")
            
            # הצגת מבנה
            manager = PeriodManager(company)
            manager.print_period_structure()
        
        return company


# ===============================================================================
# SECTION 7: EXAMPLES & USAGE (דוגמאות שימוש)
# ===============================================================================

def example_load_from_text():
    """דוגמה: טעינה מטקסט"""
    print("\n" + "="*70)
    print("📝 Example: Load from Text (Copy from Excel)")
    print("="*70 + "\n")
    
    # טקסט לדוגמה
    sample_data = """Last updated: 11/22/2025
Financials of	AAPL

Income statement	2024 Q4	2024 Q3	2024 Q2	2024 Q1
Revenues	94930	85777	85777	90753
Gross profit	42831	39671	39671	41863
Net Income	14736	21448	21448	23636
EPS	0.97	1.40	1.40	1.53

Cashflow	2024 Q4	2024 Q3	2024 Q2	2024 Q1
Cash flow from operations	29943	29943	25790	67150
Free Cash flow	143566	143566	127877	143566"""
    
    manager = GetValueDataManager()
    company = manager.load_company(sample_data, ticker="AAPL")
    
    if company and company.ttm:
        print(f"\n💰 TTM Results:")
        print(f"   Revenue: ${company.ttm.income_statement.revenues:,.0f}M")
        print(f"   Net Income: ${company.ttm.income_statement.net_income:,.0f}M")
        
        # חישוב יחסים
        ratios = FinancialRatios(company.ttm)
        print(f"\n📊 Ratios:")
        if ratios.net_margin():
            print(f"   Net Margin: {ratios.net_margin():.1%}")
        if ratios.operating_margin():
            print(f"   Operating Margin: {ratios.operating_margin():.1%}")


def example_load_from_api():
    """דוגמה: טעינה מ-API"""
    print("\n" + "="*70)
    print("📡 Example: Load from API")
    print("="*70 + "\n")
    
    manager = GetValueDataManager()
    company = manager.load_company("AAPL")  # מזהה אוטומטית שזה סימול
    
    if company and company.ttm:
        print(f"\n💰 {company.company_name}")
        print(f"   Revenue: ${company.ttm.income_statement.revenues:,.0f}M")
        print(f"   Net Income: ${company.ttm.income_statement.net_income:,.0f}M")


# ===============================================================================
# MAIN - הפעלה אוטומטית
# ===============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║              getValue Platform - All-in-One System                ║
    ║                      מערכת ניתוח פיננסי מלאה                     ║
    ║                                                                   ║
    ║  API Key: 69724f3b18d8b1.58945206 (כבר משולב!)                   ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("🚀 Running examples...\n")
    
    # דוגמה 1: טעינה מטקסט (עובד תמיד)
    example_load_from_text()
    
    # דוגמה 2: טעינה מ-API (דורש אינטרנט)
    try:
        example_load_from_api()
    except Exception as e:
        print(f"\n⚠️  API example skipped (requires internet): {e}")
    
    print("\n" + "="*70)
    print("✅ Examples completed!")
    print("="*70)
    
    print("""
    
    📖 How to use:
    
    # Option 1: Load from API (internet required)
    manager = GetValueDataManager()
    company = manager.load_company("AAPL")
    
    # Option 2: Load from text (always works)
    data = '''
    Income statement    2024 Q4    2024 Q3
    Revenues           94930      85777
    Net Income         14736      21448
    '''
    company = manager.load_company(data, ticker="AAPL")
    
    # Analyze
    if company and company.ttm:
        ratios = FinancialRatios(company.ttm)
        print(f"Net Margin: {ratios.net_margin():.1%}")
    
    """)


# ===============================================================================
# END OF FILE
# ===============================================================================
