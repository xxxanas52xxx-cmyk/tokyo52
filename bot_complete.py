"""
طوكيو 52 - البوت المحلي (يعمل على جهازك ويرسل الإشارات لموقعك)
"""
import asyncio, json, time, requests
import numpy as np
from datetime import datetime

# رابط موقعك على Railway
WEBSITE_URL = "https://web-production-8e380.up.railway.app"

EMAIL = "x52anasx@gmail.com"
PASSWORD = "anas775312956"
ASSETS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "XAUUSD_otc", "BTCUSD_otc"]

# إرسال حالة البوت للموقع
def update_website_status(connected, balance):
    try:
        requests.post(f"{WEBSITE_URL}/update_bot_status", json={"connected": connected, "balance": balance}, timeout=5)
    except: pass

# إرسال إشارة جديدة للموقع
def send_signal_to_website(asset_name, direction, confidence, expiry):
    try:
        requests.post(f"{WEBSITE_URL}/new_signal", json={
            "asset": asset_name, "asset_name": asset_name, "direction": direction,
            "confidence": confidence, "expiry": expiry, "time": datetime.now().strftime("%H:%M:%S")
        }, timeout=5)
        print(f"   🌐 تم إرسال الإشارة للموقع!")
    except: pass

# دالة التحليل (نفس الاستراتيجية)
def ema_arr(data, period):
    arr=np.array(data,dtype=float); n=len(arr); period=max(1,min(period,n-1)) if n>1 else 1
    if n<2: return arr.copy()
    out=np.zeros(n); out[period-1]=np.mean(arr[:period]); k=2.0/(period+1)
    for i in range(period,n): out[i]=arr[i]*k+out[i-1]*(1-k)
    return out

def tokyo_52_engine(clist_m):
    closes_m = [c["close"] for c in clist_m]; n = len(closes_m)
    if n < 50: return None, 0, 2
    ef = ema_arr(np.array(closes_m), 9); em = ema_arr(np.array(closes_m), 21); es = ema_arr(np.array(closes_m), 50)
    if ef[-1] > em[-1] > es[-1]: return "call", 85, 2
    elif ef[-1] < em[-1] < es[-1]: return "put", 85, 2
    return None, 0, 2

async def bot_loop():
    from pyquotex.stable_api import Quotex
    client = Quotex(email=EMAIL, password=PASSWORD, lang="ar")
    status, reason = await client.connect()
    
    if status:
        print("✅ اتصال طوكيو 52 ناجح!")
        update_website_status(True, await client.get_balance())
    else:
        print(f"❌ فشل الاتصال: {reason}")
        update_website_status(False, 0)
        return

    while True:
        try:
            balance = await client.get_balance()
            update_website_status(True, balance)
            
            for asset_id in ASSETS:
                try:
                    candles = await client.get_candles(asset_id, 60, 0, 100)
                    if len(candles) < 50: continue
                    
                    direction, confidence, expiry = tokyo_52_engine(candles)
                    if direction:
                        print(f"🎯 إشارة {direction} على {asset_id} ثقة {confidence}%")
                        send_signal_to_website(asset_id, direction, confidence, expiry)
                        
                except Exception as e: print(f"خطأ تحليل {asset_id}: {e}")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"خطأ عام: {e}")
            update_website_status(False, 0)
            break

if __name__ == "__main__":
    asyncio.run(bot_loop())
