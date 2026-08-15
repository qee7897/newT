# Trading AI Bot — Gemini MVP

ระบบต้นแบบ:
**TradingView → Binance market data → Multi-timeframe → Gemini → Telegram report**

## ค่าเริ่มต้น
- Symbol: BTCUSDT
- Timeframes: 4h, 1h, 15m, 5m
- Schedule: ทุกวัน 09:00 ตาม TIMEZONE
- AI: Google Gemini API
- Report: Telegram

ระบบนี้เป็นเครื่องมือวิเคราะห์ ไม่ได้ส่งคำสั่งซื้อขายจริง

## ติดตั้ง

ต้องมี Python 3.11+

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Windows:

    .venv\Scripts\activate

คัดลอก `.env.example` เป็น `.env` แล้วใส่ `GEMINI_API_KEY`

Google แนะนำ official Google GenAI SDK สำหรับ Python (`google-genai`) และตัวอย่างการใช้งานใช้ `genai.Client()` + `client.models.generate_content(...)`.

## รัน

    uvicorn app.main:app --host 0.0.0.0 --port 8000

ทดสอบ:
- GET /health
- GET /analyze
- POST /webhook/tradingview

เปิด:
`http://127.0.0.1:8000/docs`

## TradingView

Webhook URL:

    https://YOUR-DOMAIN/webhook/tradingview

ตัวอย่าง payload:

    {"symbol":"BTCUSDT","timeframe":"15m","price":"{{close}}"}

MVP ใช้ TradingView เป็น trigger และดึง OHLC จาก Binance เพื่อคำนวณ indicator ให้สม่ำเสมอ

## Telegram

สร้าง Telegram bot แล้วใส่:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

## ความปลอดภัย

อย่า commit `.env` ลง GitHub
ใช้ HTTPS สำหรับ webhook
ตั้ง WEBHOOK_SECRET
อย่าใส่คีย์ซื้อขายจริงในระบบนี้

## ขั้นต่อไป

เพิ่ม:
1. ข่าวเศรษฐกิจ
2. Smart Money / market structure
3. กราฟพร้อมโซน
4. รายงานแบบเดียวกับตัวอย่าง
5. Dashboard
6. แจ้งเตือนหลายสินทรัพย์
7. Risk engine ก่อนพิจารณาเชื่อม exchange
