import json
from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM_PROMPT = (
    "You are a disciplined market-analysis assistant. "
    "Analyze only supplied market data. Never invent prices or news. "
    "If signals conflict, say Neutral/Wait. Risk management is more important than prediction. "
    "This is educational/research output, not financial advice."
)

def fallback_analysis(symbol, market):
    trends = [v["trend"] for v in market.values()]
    bullish, bearish = trends.count("bullish"), trends.count("bearish")
    bias = "BUY BIAS" if bullish > bearish else "SELL BIAS" if bearish > bullish else "NEUTRAL"
    return (
        f"## {symbol} — {bias}\n"
        f"- 4H: {market['4h']['trend']} | RSI {market['4h']['rsi14']:.1f}\n"
        f"- 1H: {market['1h']['trend']} | RSI {market['1h']['rsi14']:.1f}\n"
        f"- 15M: {market['15m']['trend']} | RSI {market['15m']['rsi14']:.1f}\n"
        f"- 5M: {market['5m']['trend']} | RSI {market['5m']['rsi14']:.1f}\n"
        "- Entry/SL/TP: รอการยืนยันจากโครงสร้างราคาเพิ่มเติม"
    )

def analyze(symbol, market):
    if not GEMINI_API_KEY:
        return fallback_analysis(symbol, market)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f'''Symbol: {symbol}
Market snapshots:
{json.dumps(market, ensure_ascii=False, indent=2)}

สร้างรายงานภาษาไทย:
1. Bias หลัก
2. Trend 4H/1H/15M/5M
3. โครงสร้างราคา
4. แนวรับ
5. แนวต้าน
6. Long plan: เงื่อนไขเข้า, SL/invalidation, TP1-TP3
7. Short plan: เงื่อนไขเข้า, SL/invalidation, TP1-TP3
8. จุดที่ต้องรอ/ห้ามไล่ราคา
9. สรุปสั้น ๆ

ห้ามแต่งข่าวหรือข้อมูลที่ไม่มีใน input
ถ้าข้อมูลไม่พอ ให้บอกว่า "ข้อมูลไม่พอ" แทนการเดา'''

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            max_output_tokens=1800,
        ),
    )
    return response.text or fallback_analysis(symbol, market)
