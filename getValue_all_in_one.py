"""
getValue Platform - Streamlit App (Enhanced Simple Version)
גרסה פשוטה + TTM דינמי + דוחות מעודכנים
"""

import streamlit as st
import pandas as pd
from getValue_all_in_one import (
    GetValueDataManager, 
    PeriodManager,
    FinancialRatios
)

# ========================================
# הגדרות עמוד
# ========================================

st.set_page_config(
    page_title="getValue - Financial Analysis",
    page_icon="📊",
    layout="wide"
)

# CSS פשוט
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# כותרת
# ========================================

st.markdown('<h1 class="main-title">📊 getValue - ניתוח פיננסי</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">מערכת ניתוח מתקדמת מבוססת API | Financial Modeling Prep</p>', unsafe_allow_html=True)
st.markdown("---")

# ========================================
# Sidebar - תפריט צד
# ========================================

with st.sidebar:
    st.markdown("## ⚙️ הגדרות")
    
    st.info("🌐 **API אוטומטי** הוא הדרך המומלצת!")
    
    # בחירת מקור נתונים
    data_source = st.radio(
        "📥 בחר מקור נתונים:",
        ["🌐 API אוטומטי (מומלץ)", "📝 העתק מאקסל (חלופה)", "⚡ דוגמה מהירה"],
        help="API מספק נתונים מלאים ומעודכנים"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ מידע")
    st.markdown("""
    **getValue מתבסס על:**
    - 🌐 **API** - מקור הנתונים העיקרי
    - 📊 נתונים מ-Financial Modeling Prep
    - 🔄 עדכון אוטומטי
    
    **פיצ'רים:**
    - ✅ TTM אוטומטי
    - ✅ דוחות דינמיים
    - ✅ יחסים פיננסיים
    - ✅ 10+ רבעונים/שנים
    """)

# ========================================
# אתחול
# ========================================

# API Key
API_KEY = "zF2GUU9LVP2ICuLDKJJ9SwQhkzw1TN4i"

# Session state
if 'company' not in st.session_state:
    st.session_state.company = None
if 'manager' not in st.session_state:
    st.session_state.manager = GetValueDataManager(api_key=API_KEY)

# ========================================
# טעינת נתונים
# ========================================

if "API" in data_source:  # API אוטומטי (מומלץ)
    st.markdown("### 🌐 טעינה מ-API (הדרך המומלצת)")
    st.success("✨ API מספק נתונים מלאים, מדויקים ומעודכנים מ-Financial Modeling Prep")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "סימול מניה:",
            value="AAPL",
            placeholder="AAPL, MSFT, GOOGL, TSLA...",
            help="הזן סימול מניה אמריקאי"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 טען נתונים", type="primary", use_container_width=True):
            with st.spinner(f'🔍 מושך נתונים עבור {ticker}...'):
                try:
                    company = st.session_state.manager.load_company(ticker.upper())
                    if company:
                        st.session_state.company = company
                        st.success(f"✅ נטען בהצלחה: {company.company_name}")
                        st.info(f"📊 נמשכו {len(company.quarterly_data)} רבעונים + TTM אוטומטי")
                    else:
                        st.error("❌ לא הצלחתי לטעון את הנתונים מה-API")
                        st.info("💡 בדוק שהסימול נכון, או נסה להשתמש באפשרות 'העתק מאקסל'")
                except Exception as e:
                    st.error(f"❌ שגיאה בטעינה מ-API: {str(e)}")
                    st.info("💡 אפשר לנסות להשתמש באפשרות 'העתק מאקסל' כחלופה")

elif "אקסל" in data_source:  # העתק מאקסל (חלופה)
    st.markdown("### 📝 העתק מאקסל (אפשרות חלופית)")
    st.warning("⚠️ שים לב: API הוא הדרך המומלצת. השתמש באפשרות זו רק אם יש לך נתונים משלך.")
    st.info("💡 טיפ: בחר את הטבלה באקסל, לחץ Ctrl+C, והדבק כאן למטה")
    
    data_text = st.text_area(
        "הדבק כאן את הנתונים מהאקסל:",
        height=200,
        placeholder="""Income statement\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Revenues\t94930\t85777\t85777\t90753
Gross profit\t42831\t39671\t39671\t41863
Net Income\t14736\t21448\t21448\t23636
EPS\t0.97\t1.40\t1.40\t1.53

Cashflow\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Cash flow from operations\t29943\t29943\t25790\t67150
Free Cash flow\t23632\t23445\t20563\t28773""",
        help="העתק את הטבלה מאקסל (כולל הכותרות) והדבק כאן"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker_text = st.text_input(
            "סימול החברה:",
            value="AAPL",
            placeholder="למשל: AAPL",
            help="הזן את הסימול של החברה"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 נתח נתונים", type="primary", use_container_width=True):
            if data_text.strip():
                with st.spinner('מנתח נתונים...'):
                    try:
                        company = st.session_state.manager.load_company(data_text, ticker=ticker_text.upper())
                        if company:
                            st.session_state.company = company
                            st.success(f"✅ נותח בהצלחה: {ticker_text.upper()}")
                            
                            # הצגת מידע על מה שנטען
                            if company.ttm:
                                st.info(f"🔄 TTM חושב אוטומטית מ-{len(company.quarterly_data)} רבעונים")
                        else:
                            st.error("❌ לא הצלחתי לנתח את הנתונים")
                            st.warning("💡 ודא שהנתונים מועתקים נכון עם טאבים בין העמודות")
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
                        st.warning("💡 טיפ: העתק את הטבלה מאקסל עם Ctrl+C ולא באמצעות Copy Special")
            else:
                st.warning("⚠️ נא להדביק נתונים מאקסל בתיבת הטקסט")
    
    # דוגמת פורמט
    with st.expander("📋 ראה דוגמה לפורמט נכון"):
        st.code("""Income statement\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Revenues\t94930\t85777\t85777\t90753
Gross profit\t42831\t39671\t39671\t41863
Operating income\t29590\t28355\t28355\t29553
Net Income\t14736\t21448\t21448\t23636
EPS\t0.97\t1.40\t1.40\t1.53

Cashflow\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Cash flow from operations\t29943\t29943\t25790\t67150
Free Cash flow\t23632\t23445\t20563\t28773""", language="text")
        
        st.markdown("""
        **חשוב:**
        - השורה הראשונה צריכה להכיל "Income statement" + התקופות
        - כל עמודה מופרדת ב-TAB (לא רווח!)
        - השמות צריכים להיות באנגלית
        - המספרים ללא פסיקים
        """)

else:  # דוגמה מהירה
    st.info("👇 לחץ לטעינת דוגמה של Apple")
    
    if st.button("🍎 טען דוגמה", type="primary"):
        sample_data = """Income statement\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Revenues\t94930\t85777\t85777\t90753
Gross profit\t42831\t39671\t39671\t41863
Operating income\t29590\t28355\t28355\t29553
Net Income\t14736\t21448\t21448\t23636
EPS\t0.97\t1.40\t1.40\t1.53

Cashflow\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Cash flow from operations\t29943\t29943\t25790\t67150
Free Cash flow\t23632\t23445\t20563\t28773"""
        
        with st.spinner('טוען דוגמה...'):
            company = st.session_state.manager.load_company(sample_data, ticker="AAPL")
            st.session_state.company = company
            st.success("✅ דוגמה נטענה: Apple Inc.")

# ========================================
# הצגת תוצאות
# ========================================

company = st.session_state.company

if company:
    st.markdown("---")
    
    # ========================================
    # מידע כללי + TTM
    # ========================================
    
    st.markdown(f"### 💼 {company.company_name} ({company.ticker})")
    
    # מטריקות TTM
    if company.ttm:
        st.markdown("#### 📊 TTM (12 חודשים אחרונים)")
        
        ttm = company.ttm
        inc = ttm.income_statement
        cf = ttm.cash_flow
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if inc.revenues:
                st.metric("💰 הכנסות", f"${inc.revenues:,.0f}M")
        
        with col2:
            if inc.net_income:
                margin = (inc.net_income / inc.revenues * 100) if inc.revenues else 0
                st.metric("✅ רווח נקי", f"${inc.net_income:,.0f}M", f"{margin:.1f}%")
        
        with col3:
            if inc.eps:
                st.metric("📈 EPS", f"${inc.eps:.2f}")
        
        with col4:
            if cf.free_cash_flow:
                st.metric("💵 FCF", f"${cf.free_cash_flow:,.0f}M")
        
        # יחסים פיננסיים מהירים
        st.markdown("#### 📊 יחסים פיננסיים (TTM)")
        
        ratios = FinancialRatios(ttm)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            gross_m = ratios.gross_margin()
            if gross_m:
                st.metric("מרווח גולמי", f"{gross_m:.1%}")
        
        with col2:
            net_m = ratios.net_margin()
            if net_m:
                st.metric("מרווח נקי", f"{net_m:.1%}")
        
        with col3:
            operating_m = ratios.operating_margin()
            if operating_m:
                st.metric("מרווח תפעולי", f"{operating_m:.1%}")
        
        with col4:
            pe = ratios.pe_ratio()
            if pe:
                st.metric("P/E Ratio", f"{pe:.1f}")
    
    # ========================================
    # מבנה תקופות
    # ========================================
    
    st.markdown("---")
    st.markdown("### 📅 מבנה תקופות")
    
    pm = PeriodManager(company)
    last_year = pm.identify_last_full_year()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"🔄 **TTM:** {'מחושב מ-4 רבעונים' if company.ttm else 'לא זמין'}")
    
    with col2:
        st.info(f"📅 **שנה מלאה אחרונה:** {last_year if last_year else 'לא זוהה'}")
    
    with col3:
        st.info(f"📊 **רבעונים:** {len(company.quarterly_data)} | **שנים:** {len(company.annual_data)}")
    
    # ========================================
    # בחירת סוג דוח
    # ========================================
    
    st.markdown("---")
    st.markdown("### 📋 דוחות פיננסיים")
    
    period_choice = st.radio(
        "בחר סוג דוח:",
        ["Quarterly (רבעוני)", "Annual (שנתי)"],
        horizontal=True
    )
    
    # ========================================
    # פונקציות עזר ליצירת טבלאות
    # ========================================
    
    def create_financial_dataframe(periods_list, include_ttm=True):
        """יצירת DataFrame עם TTM + תקופות"""
        
        if not periods_list:
            return pd.DataFrame()
        
        # בניית המילון של נתונים
        data_dict = {}
        
        # הוספת TTM אם קיים
        if include_ttm and company.ttm:
            data_dict['TTM'] = {
                'Revenues': company.ttm.income_statement.revenues,
                'Gross Profit': company.ttm.income_statement.gross_profit,
                'Operating Income': company.ttm.income_statement.operating_income,
                'Net Income': company.ttm.income_statement.net_income,
                'EPS': company.ttm.income_statement.eps,
                'Operating CF': company.ttm.cash_flow.cash_flow_from_operations,
                'Free Cash Flow': company.ttm.cash_flow.free_cash_flow,
            }
        
        # הוספת כל התקופות
        for period in periods_list:
            inc = period.income_statement
            cf = period.cash_flow
            
            data_dict[period.period_name] = {
                'Revenues': inc.revenues,
                'Gross Profit': inc.gross_profit,
                'Operating Income': inc.operating_income,
                'Net Income': inc.net_income,
                'EPS': inc.eps,
                'Operating CF': cf.cash_flow_from_operations,
                'Free Cash Flow': cf.free_cash_flow,
            }
        
        # המרה ל-DataFrame
        df = pd.DataFrame(data_dict)
        
        # עיצוב - פורמט מספרים
        def format_number(x):
            if pd.isna(x) or x is None:
                return "-"
            if abs(x) < 10:  # EPS
                return f"${x:.2f}"
            else:  # מיליונים
                return f"${x:,.0f}M"
        
        # החלת הפורמט על כל התאים
        df_styled = df.applymap(format_number)
        
        return df_styled
    
    def create_balance_sheet_df(periods_list, include_ttm=True):
        """יצירת DataFrame למאזן"""
        
        if not periods_list:
            return pd.DataFrame()
        
        data_dict = {}
        
        # TTM (מהרבעון האחרון)
        if include_ttm and company.ttm:
            bs = company.ttm.balance_sheet
            data_dict['TTM'] = {
                'Cash & Equivalents': bs.cash_and_equivalents,
                'Current Assets': bs.current_assets,
                'Total Assets': bs.total_assets,
                'Current Liabilities': bs.current_liabilities,
                'Total Debt': bs.total_debt,
                'Equity': bs.equity_value,
            }
        
        # תקופות
        for period in periods_list:
            bs = period.balance_sheet
            data_dict[period.period_name] = {
                'Cash & Equivalents': bs.cash_and_equivalents,
                'Current Assets': bs.current_assets,
                'Total Assets': bs.total_assets,
                'Current Liabilities': bs.current_liabilities,
                'Total Debt': bs.total_debt,
                'Equity': bs.equity_value,
            }
        
        df = pd.DataFrame(data_dict)
        
        def format_number(x):
            if pd.isna(x) or x is None:
                return "-"
            return f"${x:,.0f}M"
        
        return df.applymap(format_number)
    
    # ========================================
    # הצגת הטבלאות
    # ========================================
    
    # בחירת התקופות לפי סוג הדוח
    if "Quarterly" in period_choice:
        periods_to_show = company.quarterly_data[:10]  # 10 רבעונים
        show_ttm = True
    else:
        periods_to_show = company.annual_data[:10]  # 10 שנים
        show_ttm = False
    
    # 1. Income Statement + Cash Flow
    st.markdown("#### 📄 Income Statement & Cash Flow")
    
    if periods_to_show:
        df_income = create_financial_dataframe(periods_to_show, include_ttm=show_ttm)
        st.dataframe(df_income, use_container_width=True)
    else:
        st.warning("⚠️ אין נתונים זמינים לתקופה זו")
    
    # 2. Balance Sheet
    st.markdown("#### ⚖️ Balance Sheet")
    
    if periods_to_show:
        df_balance = create_balance_sheet_df(periods_to_show, include_ttm=show_ttm)
        st.dataframe(df_balance, use_container_width=True)
    else:
        st.warning("⚠️ אין נתונים זמינים לתקופה זו")
    
    # ========================================
    # טבלת רבעונים מפורטת
    # ========================================
    
    if "Quarterly" in period_choice and company.quarterly_data:
        st.markdown("---")
        st.markdown("#### 📊 טבלת רבעונים מפורטת")
        
        quarterly_details = []
        for q in company.quarterly_data[:12]:
            inc = q.income_statement
            cf = q.cash_flow
            
            # חישוב שינוי רבעוני
            if inc.revenues:
                quarterly_details.append({
                    "רבעון": q.period_name,
                    "הכנסות ($M)": f"{inc.revenues:,.0f}" if inc.revenues else "-",
                    "רווח נקי ($M)": f"{inc.net_income:,.0f}" if inc.net_income else "-",
                    "מרווח נקי": f"{(inc.net_income/inc.revenues*100):.1f}%" if (inc.revenues and inc.net_income) else "-",
                    "EPS ($)": f"{inc.eps:.2f}" if inc.eps else "-",
                    "FCF ($M)": f"{cf.free_cash_flow:,.0f}" if cf.free_cash_flow else "-",
                })
        
        if quarterly_details:
            df_details = pd.DataFrame(quarterly_details)
            st.dataframe(df_details, use_container_width=True, hide_index=True)

else:
    # אין נתונים
    st.info("👆 בחר מקור נתונים מהתפריט הצדדי והתחל!")
    
    st.markdown("## 🚀 איך להתחיל?")
    
    st.success("🌐 **API אוטומטי** הוא הדרך המומלצת - מספק נתונים מלאים ומעודכנים!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ API אוטומטי ⭐
        **הדרך המומלצת!**
        
        - 🌐 נתונים מלאים מהאינטרנט
        - 📊 10+ רבעונים + 10 שנים
        - 🔄 TTM אוטומטי
        - ✅ מעודכן תמיד
        - 🚀 פשוט הזן סימול!
        
        **זו הדרך הטובה ביותר!**
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ העתק מאקסל
        **אפשרות חלופית**
        
        - 📝 להעלות נתונים משלך
        - 🔧 לשימוש מיוחד בלבד
        - ⚠️ פחות מומלץ מ-API
        
        השתמש רק אם:
        - יש לך נתונים ייחודיים
        - API לא זמין
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ דוגמה מהירה
        **להדגמה בלבד**
        
        - ⚡ ראה את המערכת בפעולה
        - 🍎 דוגמה של Apple
        - 📊 כולל TTM וכל הפיצ'רים
        
        מומלץ לנסות קודם!
        """)
    
    # הסבר על TTM
    st.markdown("---")
    st.markdown("### ✨ למה API?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **יתרונות API:**
        - ✅ נתונים מלאים (Income, Balance, Cash Flow)
        - ✅ 10 רבעונים + 10 שנים
        - ✅ TTM מחושב אוטומטית
        - ✅ כל היחסים הפיננסיים
        - ✅ תמיד מעודכן
        """)
    
    with col2:
        st.markdown("""
        **TTM (Trailing Twelve Months)** = 12 החודשים האחרונים
        
        המערכת מחשבת אוטומטית:
        - 🔄 מחבר 4 רבעונים אחרונים
        - 📊 מציג בטבלאות כעמודה ראשונה
        - 🎯 הנתון הכי רלוונטי!
        """)

# ========================================
# Footer
# ========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>getValue Platform</strong> | Powered by Financial Modeling Prep API | גרסה 1.2.0</p>
    <p>🌐 נתמך על API | 📊 TTM דינמי | 💹 יחסים פיננסיים | 📈 דוחות מעודכנים</p>
    <p style='font-size: 0.9em; margin-top: 10px;'>API הוא מקור הנתונים העיקרי והמומלץ</p>
</div>
""", unsafe_allow_html=True)
