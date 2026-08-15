from fastapi import FastAPI, HTTPException, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import SYMBOL, TIMEZONE, SCHEDULE_HOUR, SCHEDULE_MINUTE, WEBHOOK_SECRET
from .market import collect_market
from .analyzer import analyze
from .notify import send_telegram

app = FastAPI(title="Trading AI Bot", version="0.1.0")
scheduler = BackgroundScheduler(timezone=TIMEZONE)

def run_report(symbol=SYMBOL):
    market = collect_market(symbol)
    report = analyze(symbol, market)
    send_telegram(report)
    return report

@app.get("/health")
def health():
    return {"ok": True, "symbol": SYMBOL, "timezone": TIMEZONE}

@app.get("/analyze")
def analyze_now():
    return {"symbol": SYMBOL, "report": run_report(SYMBOL)}

@app.post("/webhook/tradingview")
async def tradingview_webhook(request: Request):
    if WEBHOOK_SECRET:
        if request.headers.get("x-webhook-secret", "") != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": (await request.body()).decode("utf-8", errors="ignore")}
    symbol = str(payload.get("symbol", SYMBOL)).replace("/", "").upper()
    return {"ok": True, "received": payload, "report": run_report(symbol)}

def scheduled_job():
    try:
        run_report(SYMBOL)
    except Exception as e:
        send_telegram(f"Trading AI Bot error: {type(e).__name__}: {e}")

@app.on_event("startup")
def startup():
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, timezone=TIMEZONE),
        id="daily-report",
        replace_existing=True,
    )
    scheduler.start()

@app.on_event("shutdown")
def shutdown():
    if scheduler.running:
        scheduler.shutdown()
