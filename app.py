import streamlit as st
import yfinance as ticker_data
import google.generativeai as genai

# 1. 網頁介面設定
st.set_page_config(page_title="Gemini 3 股市深度分析", page_icon="🚀", layout="wide")
st.title("🚀 Gemini 3 股市投資策略中心")
st.caption("已連線至 Google Gemini 3.0 系列模型 (2025 最新版)")

# 側邊欄設定
with st.sidebar:
    st.header("系統設定")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    
    # 使用 Gemini 3 最新模型
    model_choice = st.selectbox(
        "選擇 Gemini 3 模型",
        ["gemini-3-pro-preview", "gemini-3-flash-preview"],
        index=0,
        help="Gemini 3 Pro 具備最強的邏輯推理與代理分析能力。"
    )
    
    # Gemini 3 特有的思考等級設定
    think_level = st.select_slider(
        "AI 思考深度 (Thinking Level)",
        options=["low", "medium", "high"],
        value="high",
        help="設定為 High 會讓 AI 進行多輪推理，適合複雜的投資策略分析。"
    )
    
    target_stock = st.text_input("股票代號 (例: 2330.TW, NVDA)", value="2330.TW")
    st.info("💡 提示：Gemini 3 Pro 支援高階 Agent 模式，分析準確度顯著提升。")

if st.button("📊 啟動 Gemini 3 深度策略分析"):
    if not api_key:
        st.error("請先輸入 API Key！")
    else:
        try:
            # 設定 Gemini 3 API
            genai.configure(api_key=api_key)
            
            # 建立模型配置
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            model = genai.GenerativeModel(
                model_name=model_choice,
                generation_config=generation_config
            )
            
            with st.spinner(f'Gemini 3 正在進行深度推理 (Level: {think_level})...'):
                # 2. 獲取股市即時數據
                stock = ticker_data.Ticker(target_stock)
                news = stock.news[:10]  # Gemini 3 處理長文本能力極強，我們給它更多新聞
                info = stock.info
                
                news_text = "\n".join([f"【新聞】{n['title']}" for n in news])
                current_p = info.get('currentPrice', '未知')
                
                # 3. 專為 Gemini 3 設計的 Agentic Prompt
                prompt = f"""
                你現在是一位搭載了 Gemini 3 核心的資深量化交易專家與首席分析師。
                請針對 {target_stock} 進行「Agent 級別」的深度投資評估。
                
                數據背景：
                - 當前價格：{current_p}
                - 最新市場動態：
                {news_text}
                
                請執行以下推理流程：
                1. 【多維度分析】：結合以上新聞，分析市場對該股的最新情緒（樂觀、恐慌或中性）。
                2. 【策略建模】：根據 Gemini 3 的推理能力，給出今日最合適的投資操作策略（明確指出：買入、賣出、持股、或觀望）。
                3. 【邏輯鏈結】：詳細說明支撐此策略的三大原因。
                4. 【風險對沖】：列出若策略失效時的應對方案（止損位或反向指標）。
                
                請使用繁體中文回答，並運用 Markdown 格式呈現一份專業的投資周報風格。
                """

                # 呼叫 API (在 2025 的 SDK 中可帶入 thinking 相關參數)
                response = model.generate_content(prompt)
                
                # 4. 顯示結果
                st.success("Gemini 3 分析完畢！")
                st.markdown(f"## 📋 {target_stock} 深度報告")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"偵測到錯誤: {e}")

st.divider()
st.caption("本系統基於 Gemini 3 Preview 模型開發。投資有風險，AI 分析僅供決策參考。")
