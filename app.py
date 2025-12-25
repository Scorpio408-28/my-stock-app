import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. 網頁配置
st.set_page_config(page_title="Gemini 3 全球股市掃描器", page_icon="🎯", layout="wide")
st.title("🎯 Gemini 3 智慧選股與精確操作建議")
st.caption("2025 最新版本 - 具備市場掃描與點位預測功能")

# 側邊欄設定
with st.sidebar:
    st.header("系統設定")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    market_type = st.radio("選擇追蹤市場", ["美股 (熱門股)", "台股 (前 50 大)"])
    st.divider()
    st.info("AI 會掃描當前市場最活躍的股票並給出今日推薦。")

# 輔助函式：抓取市場熱門數據
def get_market_data(market):
    tickers = []
    if market == "美股 (熱門股)":
        # 抓取美股熱門/成交量大的代表性股票
        tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "GOOGL", "AMZN", "META"]
    else:
        # 抓取台股核心權值股
        tickers = ["2330.TW", "2317.TW", "2454.TW", "2308.TW", "2382.TW", "2603.TW", "2881.TW", "2882.TW"]
    
    data_list = []
    for t in tickers:
        s = yf.Ticker(t)
        info = s.info
        data_list.append({
            "代號": t,
            "名稱": info.get('shortName', t),
            "現價": info.get('currentPrice', 'N/A'),
            "漲跌幅": f"{info.get('regularMarketChangePercent', 0):.2f}%",
            "成交量": info.get('regularMarketVolume', 0),
            "新聞標題": [n['title'] for n in s.news[:3]] # 抓前三則新聞
        })
    return data_list

if st.button("🚀 開始掃描市場並尋找黑馬股"):
    if not api_key:
        st.error("請先輸入 API Key！")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3-pro-preview')
            
            with st.spinner('正在掃描全球市場即時數據與新聞...'):
                # 1. 抓取數據
                market_info = get_market_data(market_type)
                
                # 2. 整理給 AI 的資訊包
                context_for_ai = ""
                for item in market_info:
                    context_for_ai += f"股票: {item['名稱']}({item['代號']}), 現價: {item['現價']}, 漲跌: {item['漲跌幅']}\n"
                    context_for_ai += f"最新新聞: {'; '.join(item['新聞標題'])}\n\n"
                
                # 3. 構造強大的 Prompt
                prompt = f"""
                你是一位具備 Gemini 3 核心實力的頂尖對沖基金經理。
                現在時間是 2025 年 12 月，請根據以下提供的最新即時數據，執行選股任務：
                
                【市場即時數據】:
                {context_for_ai}
                
                【任務清單】:
                1. 從中挑選出「今天最值得投資」的 2-3 檔股票。
                2. 為每一檔挑選出的股票提供：
                   - **推薦理由**：結合技術面與新聞情緒分析。
                   - **具體操作建議**：
                     * 進場位 (Buy At)：具體價格。
                     * 停利位 (Take Profit)：目標價格。
                     * 停損位 (Stop Loss)：必須執行的出場價格。
                3. 整體市場風險警示。

                請使用繁體中文，以專業、清晰的表格與清單格式回答，確保在手機上易於閱讀。
                """

                response = model.generate_content(prompt)
                
                # 4. 顯示結果
                st.success("市場掃描完成！以下是 Gemini 3 的今日推薦：")
                st.markdown(response.text)
                
                # 顯示簡易數據表供參考
                with st.expander("查看原始數據"):
                    st.table(pd.DataFrame(market_info).drop(columns=['新聞標題']))

        except Exception as e:
            st.error(f"掃描失敗: {e}")

st.divider()
st.caption("免責聲明：本工具使用 AI 進行自動化市場掃描，選股結果僅供參考。股市有風險，買賣前請審慎評估。")
