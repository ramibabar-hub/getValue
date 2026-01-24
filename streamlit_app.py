"""
getValue Platform - Streamlit Web App
אתר ניתוח פיננסי מלא

להרצה מקומית:
    streamlit run app.py

פריסה ל-Streamlit Cloud:
    1. העלה ל-GitHub
    2. חבר ל-Streamlit Cloud
    3. Deploy!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys

# ייבוא המערכת שלנו
from getValue_all_in_one import (
    GetValueDataManager, 
    FinancialRatios, 
    PeriodManager,
    CompanyFinancials
)

# ========================================
# הגדרות עמוד
# ========================================

st.set_page_config(
    page_title="getValue - ניתוח פיננסי",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# כותרת ראשית
# ========================================

st.markdown('<h1 class="main-header">📊 getValue Platform</h1>', unsafe_allow_html=True)
st.markdown("### מערכת ניתוח פיננסי מקצועית")
st.markdown("---")

# ========================================
# Sidebar - תפריט צד
# ========================================

with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=getValue", use_container_width=True)
    st.markdown("## ⚙️ הגדרות")
    
    # בחירת מקור נתונים
    data_source = st.radio(
        "📥 מקור נתונים:",
        ["API אוטומטי", "העתק מאקסל", "דוגמה מהירה"],
        help="בחר איך לטעון את הנתונים"
    )
    
    st.markdown("---")
    
    # מידע
    st.markdown("### ℹ️ אודות")
    st.markdown("""
    **getValue Platform** מספקת:
    - ✅ ניתוח פיננסי אוטומטי
    - ✅ 40+ יחסים פיננסיים
    - ✅ גרפים אינטראקטיביים
    - ✅ TTM דינמי
    - ✅ השוואת חברות
    """)
    
    st.markdown("---")
    st.markdown("**גרסה:** 1.0.0")
    st.markdown("**נוצר עבור:** רמי")

# ========================================
# אזור ראשי - טעינת נתונים
# ========================================

# אתחול session state
if 'company' not in st.session_state:
    st.session_state.company = None
if 'manager' not in st.session_state:
    st.session_state.manager = GetValueDataManager()

# טעינה לפי מקור
if data_source == "API אוטומטי":
    st.markdown("## 🌐 טעינה מ-API")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "סימול מניה:",
            value="AAPL",
            placeholder="AAPL, MSFT, GOOGL...",
            help="הזן סימול מניה אמריקאי"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 טען נתונים", type="primary", use_container_width=True):
            with st.spinner(f'טוען {ticker}...'):
                try:
                    company = st.session_state.manager.load_company(ticker.upper())
                    if company:
                        st.session_state.company = company
                        st.success(f"✅ נטען בהצלחה: {company.company_name}")
                    else:
                        st.error("❌ לא הצלחתי לטעון את הנתונים. נסה להעתיק מאקסל במקום.")
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

elif data_source == "העתק מאקסל":
    st.markdown("## 📝 העתק נתונים מאקסל")
    
    data_text = st.text_area(
        "הדבק כאן את הנתונים מהאקסל:",
        height=200,
        placeholder="""Income statement\t2024 Q4\t2024 Q3\t2024 Q2\t2024 Q1
Revenues\t94930\t85777\t85777\t90753
Net Income\t14736\t21448\t21448\t23636""",
        help="העתק את הטבלה מאקסל עם Ctrl+C והדבק כאן"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input("סימול החברה:", value="AAPL")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 נתח נתונים", type="primary", use_container_width=True):
            if data_text.strip():
                with st.spinner('מנתח...'):
                    try:
                        company = st.session_state.manager.load_company(data_text, ticker=ticker.upper())
                        if company:
                            st.session_state.company = company
                            st.success(f"✅ נותח בהצלחה: {ticker.upper()}")
                        else:
                            st.error("❌ לא הצלחתי לנתח את הנתונים")
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
            else:
                st.warning("⚠️ נא להדביק נתונים מאקסל")

else:  # דוגמה מהירה
    st.markdown("## ⚡ דוגמה מהירה")
    st.info("👇 לחץ כאן לטעינת דוגמה של Apple")
    
    if st.button("🍎 טען דוגמה - Apple", type="primary", use_container_width=True):
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

if company and company.ttm:
    st.markdown("---")
    st.markdown("## 📊 תוצאות הניתוח")
    
    # ========================================
    # מטריקות עיקריות
    # ========================================
    
    st.markdown(f"### 💼 {company.company_name} ({company.ticker})")
    
    ttm = company.ttm
    inc = ttm.income_statement
    cf = ttm.cash_flow
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if inc.revenues:
            st.metric(
                "💰 הכנסות (TTM)",
                f"${inc.revenues:,.0f}M",
                help="הכנסות 12 חודשים אחרונים"
            )
    
    with col2:
        if inc.net_income:
            st.metric(
                "✅ רווח נקי",
                f"${inc.net_income:,.0f}M",
                delta=f"{(inc.net_income/inc.revenues*100):.1f}%" if inc.revenues else None,
                help="רווח נקי TTM"
            )
    
    with col3:
        if inc.eps:
            st.metric(
                "📈 EPS",
                f"${inc.eps:.2f}",
                help="רווח למניה"
            )
    
    with col4:
        if cf.free_cash_flow:
            st.metric(
                "💵 תזרים חופשי",
                f"${cf.free_cash_flow:,.0f}M",
                help="Free Cash Flow TTM"
            )
    
    # ========================================
    # טאבים - ניתוח מפורט
    # ========================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 יחסים פיננסיים", "📈 גרפים", "📅 תקופות", "📋 נתונים גולמיים"])
    
    # Tab 1: יחסים
    with tab1:
        st.markdown("### 📊 יחסים פיננסיים")
        
        ratios = FinancialRatios(ttm)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### רווחיות (Profitability)")
            
            gross_m = ratios.gross_margin()
            if gross_m:
                st.progress(min(gross_m, 1.0))
                st.markdown(f"**מרווח גולמי:** {gross_m:.1%}")
            
            net_m = ratios.net_margin()
            if net_m:
                st.progress(min(net_m, 1.0))
                st.markdown(f"**מרווח נקי:** {net_m:.1%}")
            
            operating_m = ratios.operating_margin()
            if operating_m:
                st.progress(min(operating_m, 1.0))
                st.markdown(f"**מרווח תפעולי:** {operating_m:.1%}")
        
        with col2:
            st.markdown("#### תשואות (Returns)")
            
            roe = ratios.roe()
            if roe:
                st.markdown(f"**ROE:** {roe:.1%}")
            else:
                st.markdown("**ROE:** N/A (דורש תקופה קודמת)")
            
            roic = ratios.roic()
            if roic:
                st.markdown(f"**ROIC:** {roic:.1%}")
            else:
                st.markdown("**ROIC:** N/A")
            
            pe = ratios.pe_ratio()
            if pe:
                st.markdown(f"**P/E Ratio:** {pe:.1f}")
            else:
                st.markdown("**P/E Ratio:** N/A")
        
        # טבלת כל היחסים
        st.markdown("#### כל היחסים")
        all_ratios = ratios.calculate_all_ratios()
        
        ratios_df = pd.DataFrame([
            {"יחס": name.replace("_", " ").title(), "ערך": f"{value:.2%}" if value and abs(value) < 10 else (f"{value:.2f}" if value else "N/A")}
            for name, value in all_ratios.items()
        ])
        
        st.dataframe(ratios_df, use_container_width=True, hide_index=True)
    
    # Tab 2: גרפים
    with tab2:
        st.markdown("### 📈 גרפים אינטראקטיביים")
        
        if len(company.quarterly_data) >= 2:
            # גרף הכנסות
            quarters = []
            revenues = []
            net_incomes = []
            
            for q in company.quarterly_data[:8]:
                if q.income_statement.revenues:
                    quarters.append(q.period_name)
                    revenues.append(q.income_statement.revenues)
                    net_incomes.append(q.income_statement.net_income or 0)
            
            if len(revenues) >= 2:
                # גרף הכנסות
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=quarters,
                    y=revenues,
                    mode='lines+markers',
                    name='הכנסות',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10)
                ))
                
                fig1.update_layout(
                    title="מגמת הכנסות רבעונית",
                    xaxis_title="רבעון",
                    yaxis_title="הכנסות ($M)",
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
                # גרף רווח נקי
                if any(net_incomes):
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=quarters,
                        y=net_incomes,
                        name='רווח נקי',
                        marker_color='#2ca02c'
                    ))
                    
                    fig2.update_layout(
                        title="רווח נקי רבעוני",
                        xaxis_title="רבעון",
                        yaxis_title="רווח נקי ($M)",
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                
                # גרף מרווחים
                margins = []
                for q in company.quarterly_data[:8]:
                    if q.income_statement.revenues and q.income_statement.net_income:
                        margin = (q.income_statement.net_income / q.income_statement.revenues) * 100
                        margins.append(margin)
                    else:
                        margins.append(0)
                
                if any(margins):
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(
                        x=quarters,
                        y=margins,
                        mode='lines+markers',
                        name='מרווח נקי',
                        line=dict(color='#ff7f0e', width=3),
                        marker=dict(size=10),
                        fill='tozeroy'
                    ))
                    
                    fig3.update_layout(
                        title="מגמת מרווח נקי",
                        xaxis_title="רבעון",
                        yaxis_title="מרווח נקי (%)",
                        height=400
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("📊 אין מספיק נתונים רבעוניים להצגת גרפים")
    
    # Tab 3: תקופות
    with tab3:
        st.markdown("### 📅 מבנה תקופות")
        
        pm = PeriodManager(company)
        periods = pm.get_relevant_periods_order()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔄 TTM")
            if periods['ttm']:
                st.success("✅ מחושב מ-4 רבעונים אחרונים")
            else:
                st.warning("⚠️ לא זמין")
        
        with col2:
            st.markdown("#### 📅 שנה מלאה אחרונה")
            if periods['last_full_year']:
                st.info(f"📆 {periods['last_full_year']}")
            else:
                st.warning("⚠️ לא זוהה")
        
        with col3:
            st.markdown("#### 📊 סה\"כ תקופות")
            st.metric("רבעונים", len(company.quarterly_data))
            st.metric("שנים", len(company.annual_data))
        
        # טבלת רבעונים
        if company.quarterly_data:
            st.markdown("#### רבעונים זמינים")
            
            quarterly_data = []
            for q in company.quarterly_data[:10]:
                quarterly_data.append({
                    "רבעון": q.period_name,
                    "הכנסות ($M)": f"{q.income_statement.revenues:,.0f}" if q.income_statement.revenues else "N/A",
                    "רווח נקי ($M)": f"{q.income_statement.net_income:,.0f}" if q.income_statement.net_income else "N/A",
                    "EPS ($)": f"{q.income_statement.eps:.2f}" if q.income_statement.eps else "N/A"
                })
            
            df = pd.DataFrame(quarterly_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Tab 4: נתונים גולמיים
    with tab4:
        st.markdown("### 📋 נתונים גולמיים (TTM)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💼 Income Statement")
            income_data = {
                "שדה": ["Revenues", "Gross Profit", "Operating Income", "Net Income", "EPS"],
                "ערך": [
                    f"${inc.revenues:,.0f}M" if inc.revenues else "N/A",
                    f"${inc.gross_profit:,.0f}M" if inc.gross_profit else "N/A",
                    f"${inc.operating_income:,.0f}M" if inc.operating_income else "N/A",
                    f"${inc.net_income:,.0f}M" if inc.net_income else "N/A",
                    f"${inc.eps:.2f}" if inc.eps else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(income_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 💵 Cash Flow")
            cf_data = {
                "שדה": ["Operating CF", "Free Cash Flow", "CapEx", "Dividends"],
                "ערך": [
                    f"${cf.cash_flow_from_operations:,.0f}M" if cf.cash_flow_from_operations else "N/A",
                    f"${cf.free_cash_flow:,.0f}M" if cf.free_cash_flow else "N/A",
                    f"${cf.capital_expenditures:,.0f}M" if cf.capital_expenditures else "N/A",
                    f"${cf.dividend_paid:,.0f}M" if cf.dividend_paid else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(cf_data), use_container_width=True, hide_index=True)

else:
    # אין נתונים עדיין
    st.info("👆 בחר מקור נתונים מהתפריט הצדדי והתחל!")
    
    # הוראות
    st.markdown("## 🚀 איך להתחיל?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ API אוטומטי
        - הזן סימול מניה
        - לחץ "טען נתונים"
        - קבל ניתוח מלא!
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ העתק מאקסל
        - העתק טבלה מאקסל
        - הדבק בתיבת הטקסט
        - לחץ "נתח נתונים"
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ דוגמה מהירה
        - לחץ "טען דוגמה"
        - ראה את המערכת בפעולה
        - התחל לנתח!
        """)

# ========================================
# Footer
# ========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>getValue Platform</strong> | מערכת ניתוח פיננסי מקצועית | גרסה 1.0.0</p>
    <p>נוצר עבור רמי | Powered by Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)
