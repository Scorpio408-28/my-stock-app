import streamlit as st
import yfinance as ticker_data
from openai import OpenAI

# 1. 網頁介面設定
st.set_page_config(page_title="AI 股市分析助手", page_icon="📈")
st.title("📈 AI 股市投資策略分析")

# 側邊欄設定 API Key
with st.sidebar:
    api_key = st.text_input("請輸入 OpenAI API Key", type="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")
    target_stock = st.text_input("輸入股票代號 (例如: 2330.TW 或 AAPL)", value="2330.TW")

if st.button("開始抓取資訊並分析"):
    if not api_key:
        st.error("請先輸入 API Key！")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner('正在爬取網路新聞與股價數據...'):
            try:
                # 2. 爬取股市資訊
                stock = ticker_data.Ticker(target_stock)
                news = stock.news[:5]  # 抓取前 5 則最新新聞
                info = stock.info
                
                # 整理新聞內容
                news_context = ""
                for n in news:
                    news_context += f"標題: {n['title']}\n"
                
                current_price = info.get('currentPrice', '未知')

                # 3. 呼叫 OpenAI 進行分析
                prompt = f"""
                你是資深投資分析師。請根據以下資訊，為股票代號 {target_stock} 進行分析：
                
                當前股價: {current_price}
                最新相關新聞:
                {news_context}
                
                請給出：
                1. 今日投資策略（建議：看多、看空或觀望）。
                2. 詳細原因分析（結合新聞與市場氛圍）。
                3. 風險提示。
                請用繁體中文回答。
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 4. 顯示結果
                st.subheader(f"📊 {target_stock} 分析報告")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"發生錯誤: {e}")

st.info("註：本工具僅供參考，投資前請自行評估風險。")
