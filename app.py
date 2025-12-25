import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 網頁配置
st.set_page_config(page_title="Gemini 3 新聞驅動選股器", page_icon="🗞️", layout="wide")
st.title("🗞️ Gemini 3 全球新聞實時選股")
st.caption("2025 最新版 - 自動從最新 20 則新聞中尋找交易機會")

# 側邊欄設定
with st.sidebar:
    st.header("系統設定")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    market_focus = st.selectbox("關注市場", ["美股 (International)", "台股 (Taiwan)"])
    st.divider()
    st.info("本模式會掃描最新的 20 則財經新聞，並由 AI 決定推薦哪支股票。")

# 函式：抓取最新的 20 則財經新聞標題
def get_latest_finance_news(market):
    news_list = []
    # 使用 Yahoo Finance 的 RSS Feed 獲取最新新聞
    if market == "美股 (International)":
        url = "https://finance.yahoo.com/news/"
    else:
        url = "https://tw.stock.yahoo.com/news/"
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抓取新聞標題 (這裡根據 Yahoo 網頁結構抓取)
        links = soup.find_all('h3')
        for link in links:
            title = link.get_text()
            if len(title) > 10: # 過濾掉太短的無效標題
                news_list.append(title)
            if len(news_list) >= 20: # 只要 20 則
                break
    except Exception as e:
        st.error(f"新聞抓取失敗: {e}")
    return news_list

if st.button("🔍 掃描最新 20 則新聞並尋找投資機會"):
    if not api_key:
        st.error("請先輸入 API Key！")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro') # 或使用最新的 gemini-2.0-flash-exp
            
            with st.spinner('正在讀取最新財經新聞...'):
                # 第一步：抓新聞
                latest_news = get_latest_finance_news(market_focus)
                
                if not latest_news:
                    st.error("未能獲取新聞，請稍後再試。")
                else:
                    st.subheader("📋 最新 20 則新聞摘要")
                    for i, n in enumerate(latest_news):
                        st.write(f"{i+1}. {n}")
                    
                    # 第二步：把新聞丟給 AI，叫它找出提到的股票代號
                    news_context = "\n".join(latest_news)
                    find_ticker_prompt = f"""
                    以下是最近的 20 則財經新聞標題：
                    {news_context}
                    
                    請從中執行以下任務：
                    1. 識別出這些新聞中提到的具體股票（例如：輝達、台積電、Tesla 等）。
                    2. 回傳這些股票的「正確代號」（美股直接用代號如 NVDA，台股請用 2330.TW 這種格式）。
                    3. 只回傳代號，用逗號隔開，例如: AAPL,NVDA,2330.TW。
                    4. 如果新聞中沒有提到明確的股票，請回傳 "None"。
                    """
                    
                    ticker_res = model.generate_content(find_ticker_prompt).text.strip()
                    
                    if "None" in ticker_res or not ticker_res:
                        st.warning("當前新聞中沒有發現明確的個股機會，建議稍後再試。")
                    else:
                        tickers = [t.strip() for t in ticker_res.split(',')]
                        st.info(f"AI 識別出的相關股票: {', '.join(tickers)}")
                        
                        # 第三步：抓取這些股票的即時數據
                        stock_data_context = ""
                        for t in tickers:
                            try:
                                s = yf.Ticker(t)
                                info = s.info
                                price = info.get('currentPrice', 'N/A')
                                change = info.get('regularMarketChangePercent', 0)
                                stock_data_context += f"股票: {t}, 現價: {price}, 今日漲跌: {change:.2f}%\n"
                            except:
                                continue
                        
                        # 第四步：最後總結建議
                        final_prompt = f"""
                        你是 Gemini 3 專業投資顧問。根據以下新聞背景與即時股價，請給我今天最推薦的一隻股票及操作建議。
                        
                        新聞背景：
                        {news_context}
                        
                        即時股價：
                        {stock_data_context}
                        
                        請提供：
                        1. **今日推薦股票** (代號與名稱)。
                        2. **推薦原因** (為什麼從這 20 則新聞中選中它？)。
                        3. **精確操作指南**：
                           - **買入區間**：(具體價格區間)
                           - **目標獲利位**：(停利價格)
                           - **防守止損位**：(停損價格)
                        4. **操作策略**：(例如：分批進場、短線當沖或是長期持有)。
                        
                        請使用繁體中文，並用美觀的排版回覆。
                        """
                        
                        final_analysis = model.generate_content(final_prompt)
                        st.success("🎯 Gemini 3 深度分析結果")
                        st.markdown(final_analysis.text)

        except Exception as e:
            st.error(f"發生錯誤: {e}")

st.divider()
st.caption("免責聲明：本工具基於 AI 分析新聞內容，投資前請務必自行評估市場風險。")
