"""
طوكيو 52 - المحرك الجبارة (Tokyo 52 Engine)
دمج التوافق الثلاثي + العقل الذكي + الدخول الذكي للشموع + نظام المصادقة
"""
import asyncio, json, time, random, math, os, csv, threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import numpy as np

# ═══ الإعدادات ═══
EMAIL    = "x52anasx@gmail.com"
PASSWORD = "anas775312956"

# الأصول
ASSETS = [
    {"id":"EURUSD_otc", "name":"EUR/USD", "cat":"forex"}, {"id":"GBPUSD_otc", "name":"GBP/USD", "cat":"forex"},
    {"id":"USDJPY_otc", "name":"USD/JPY", "cat":"forex"}, {"id":"USDCHF_otc", "name":"USD/CHF", "cat":"forex"},
    {"id":"USDCAD_otc", "name":"USD/CAD", "cat":"forex"}, {"id":"AUDUSD_otc", "name":"AUD/USD", "cat":"forex"},
    {"id":"NZDUSD_otc", "name":"NZD/USD", "cat":"forex"}, {"id":"EURGBP_otc", "name":"EUR/GBP", "cat":"forex"},
    {"id":"EURJPY_otc", "name":"EUR/JPY", "cat":"forex"}, {"id":"GBPJPY_otc", "name":"GBP/JPY", "cat":"forex"},
    {"id":"AUDJPY_otc", "name":"AUD/JPY", "cat":"forex"}, {"id":"NZDJPY_otc", "name":"NZD/JPY", "cat":"forex"},
    {"id":"EURAUD_otc", "name":"EUR/AUD", "cat":"forex"}, {"id":"EURCHF_otc", "name":"EUR/CHF", "cat":"forex"},
    {"id":"GBPCHF_otc", "name":"GBP/CHF", "cat":"forex"}, {"id":"AUDCHF_otc", "name":"AUD/CHF", "cat":"forex"},
    {"id":"AUDCAD_otc", "name":"AUD/CAD", "cat":"forex"}, {"id":"AUDNZD_otc", "name":"AUD/NZD", "cat":"forex"},
    {"id":"GBPAUD_otc", "name":"GBP/AUD", "cat":"forex"}, {"id":"GBPNZD_otc", "name":"GBP/NZD", "cat":"forex"},
    {"id":"NZDCAD_otc", "name":"NZD/CAD", "cat":"forex"}, {"id":"NZDCHF_otc", "name":"NZD/CHF", "cat":"forex"},
    {"id":"EURCAD_otc", "name":"EUR/CAD", "cat":"forex"}, {"id":"CADJPY_otc", "name":"CAD/JPY", "cat":"forex"},
    {"id":"CADCHF_otc", "name":"CAD/CHF", "cat":"forex"}, {"id":"CHFJPY_otc", "name":"CHF/JPY", "cat":"forex"},
    {"id":"EURNZD_otc", "name":"EUR/NZD", "cat":"forex"}, {"id":"USDARS_otc", "name":"USD/ARS", "cat":"exotic"},
    {"id":"USDBRL_otc", "name":"USD/BRL", "cat":"exotic"}, {"id":"USDINR_otc", "name":"USD/INR", "cat":"exotic"},
    {"id":"USDMXN_otc", "name":"USD/MXN", "cat":"exotic"}, {"id":"USDZAR_otc", "name":"USD/ZAR", "cat":"exotic"},
    {"id":"USDBDT_otc", "name":"USD/BDT", "cat":"exotic"}, {"id":"USDPHP_otc", "name":"USD/PHP", "cat":"exotic"},
    {"id":"USDIDR_otc", "name":"USD/IDR", "cat":"exotic"}, {"id":"USDCOP_otc", "name":"USD/COP", "cat":"exotic"},
    {"id":"USDEGP_otc", "name":"USD/EGP", "cat":"exotic"}, {"id":"USDDZD_otc", "name":"USD/DZD", "cat":"exotic"},
    {"id":"USDPKR_otc", "name":"USD/PKR", "cat":"exotic"}, {"id":"USDNGN_otc", "name":"USD/NGN", "cat":"exotic"},
    {"id":"XAUUSD_otc", "name":"Gold", "cat":"commodity"}, {"id":"XAGUSD_otc", "name":"Silver", "cat":"commodity"},
    {"id":"USOIL_otc", "name":"USCrude", "cat":"commodity"}, {"id":"UKOIL_otc", "name":"UKBrent", "cat":"commodity"},
    {"id":"BTCUSD_otc", "name":"Bitcoin", "cat":"crypto"}, {"id":"ETHUSD_otc", "name":"Ethereum", "cat":"crypto"},
    {"id":"LTCUSD_otc", "name":"Litecoin", "cat":"crypto"}, {"id":"XRPUSD_otc", "name":"Ripple", "cat":"crypto"},
    {"id":"BNBUSD_otc", "name":"BNB", "cat":"crypto"}, {"id":"SOLUSD_otc", "name":"Solana", "cat":"crypto"},
    {"id":"MSFT_otc", "name":"Microsoft", "cat":"stock"}, {"id":"BA_otc", "name":"Boeing", "cat":"stock"},
    {"id":"META_otc", "name":"Facebook", "cat":"stock"}, {"id":"PFE_otc", "name":"Pfizer", "cat":"stock"},
    {"id":"JNJ_otc", "name":"J&J", "cat":"stock"}, {"id":"INTC_otc", "name":"Intel", "cat":"stock"},
]

# الحالة العامة للبوت والموقع
bot_state = {
    "connected": False, "balance": 0.0, "account_type": "PRACTICE",
    "auto_trade": False, "selected_assets": [a["id"] for a in ASSETS[:10]],
    "trades_history": [], "pending_signals": []
}
signals_db = {}
client = None
global_lock = False

# ═══ قاعدة بيانات المستخدمين والمصادقة ═══
USERS_DB = {
    EMAIL: {
        "password": PASSWORD, 
        "role": "admin", 
        "fname": "Anas", 
        "lname": "X", 
        "approved": True
    }
}
PENDING_USERS = []

# ==========================================
# مؤشرات رياضية
# ==========================================
def ema_arr(data, period):
    arr=np.array(data,dtype=float); n=len(arr)
    period=max(1,min(period,n-1)) if n>1 else 1
    if n<2: return arr.copy()
    out=np.zeros(n); out[period-1]=np.mean(arr[:period]); k=2.0/(period+1)
    for i in range(period,n): out[i]=arr[i]*k+out[i-1]*(1-k)
    return out

def calc_rsi(closes, period=14):
    arr=np.array(closes,dtype=float); n=len(arr)
    if n<6: return 50.0
    p=min(period,n-1); w=arr[-p*4:] if n>=p*4 else arr; d=np.diff(w)
    if len(d)==0: return 50.0
    g=np.where(d>0,d,0.0); l=np.where(d<0,-d,0.0)
    pg=min(p,len(g)); ag=np.mean(g[:pg]); al=np.mean(l[:pg])
    for i in range(pg,len(g)): ag=(ag*(pg-1)+g[i])/pg; al=(al*(pg-1)+l[i])/pg
    return round(100-100/(1+ag/al),2) if al>0 else 100.0

def calc_macd(closes):
    if len(closes)<35: return None,None,None
    arr=np.array(closes,dtype=float)
    ml=ema_arr(arr,12)-ema_arr(arr,26); sg=ema_arr(ml,9); ht=ml-sg
    s=max(0,min(35,len(ml)-5))
    return ml[s:],sg[s:],ht[s:]

def calc_stoch(clist, kp=14, sm=3):
    n=len(clist)
    if n<6: return 50.0,50.0
    kv=[]
    for i in range(min(kp,n-1),n):
        sl=clist[max(0,i-kp+1):i+1]
        h=max(x["high"] for x in sl); lo=min(x["low"] for x in sl)
        kv.append(100*(clist[i]["close"]-lo)/(h-lo) if h!=lo else 50.0)
    if not kv: return 50.0,50.0
    d=float(np.mean(kv[-sm:])) if len(kv)>=sm else float(np.mean(kv))
    return round(kv[-1],2),round(d,2)

# ==========================================
# الاستراتيجية الجبارة (محرك طوكيو 52)
# ==========================================
def tokyo_52_engine(clist_m):
    closes_m=[c["close"] for c in clist_m]
    n=len(closes_m)
    if n < 50: return None, 0, 2, {}

    ef = ema_arr(np.array(closes_m), 9)
    em = ema_arr(np.array(closes_m), 21)
    es = ema_arr(np.array(closes_m), 50)
    
    trend_score = 0
    trend_dir = "neutral"
    if ef[-1] > em[-1] > es[-1]: trend_score = 3; trend_dir = "call"
    elif ef[-1] < em[-1] < es[-1]: trend_score = 3; trend_dir = "put"
    elif ef[-1] > em[-1]: trend_score = 1; trend_dir = "call"
    elif ef[-1] < em[-1]: trend_score = 1; trend_dir = "put"

    rsi = calc_rsi(closes_m)
    sk, sd_v = calc_stoch(clist_m)
    ml, sg, ht = calc_macd(closes_m)
    
    momentum_score = 0
    momentum_dir = "neutral"
    
    if rsi < 30: momentum_score += 2; momentum_dir = "call"
    elif rsi > 70: momentum_score += 2; momentum_dir = "put"
    
    if sk < 20 and sk > sd_v: momentum_score += 2; momentum_dir = "call"
    elif sk > 80 and sk < sd_v: momentum_score += 2; momentum_dir = "put"
    
    if ml is not None and len(ml) >= 3:
        if ml[-2] <= sg[-2] and ml[-1] > sg[-1] and ht[-1] > ht[-2]: 
            momentum_score += 3; momentum_dir = "call"
        elif ml[-2] >= sg[-2] and ml[-1] < sg[-1] and ht[-1] < ht[-2]: 
            momentum_score += 3; momentum_dir = "put"

    if trend_dir == momentum_dir and trend_dir != "neutral" and momentum_score >= 3:
        total_score = trend_score + momentum_score
        confidence = min(95, 50 + (total_score * 5)) 
        expiry = 2 if total_score < 8 else 3 if total_score < 11 else 5
        details = {"rsi": rsi, "stoch_k": sk, "trend": trend_dir, "score": total_score}
        return trend_dir, confidence, expiry, details
        
    return None, 0, 2, {}

# ==========================================
# الدخول الذكي للشموع
# ==========================================
async def smart_entry(asset_id, direction, expiry_minutes):
    timeframe_sec = expiry_minutes * 60
    now = datetime.now()
    seconds_elapsed = now.second + (now.microsecond / 1e6)
    
    try:
        candles = await client.get_candles(asset_id, 60, 0, 1)
        if not candles: return False, "لا توجد بيانات شمعة"
        
        current_candle = candles[-1]
        open_price = current_candle["open"]
        current_price = current_candle["close"]
        
        if direction == "call" and current_price < open_price:
            return True, "enter_now"
        elif direction == "put" and current_price > open_price:
            return True, "enter_now"
            
        seconds_to_wait = 60 - seconds_elapsed
        if seconds_to_wait > 5:
            await asyncio.sleep(seconds_to_wait)
            return True, "enter_new_candle"
        else:
            return False, "candle_ending_skip"
            
    except Exception as e:
        return False, str(e)

# ==========================================
# سيرفر الموقع (API)
# ==========================================
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        
    def do_OPTIONS(self): self.send_response(200); self.cors(); self.end_headers()
        
    def do_GET(self):
        path = self.path.split("?")[0]
        
        # عرض الموقع الرئيسي
        if path == "/" or path == "/tokyo52.html":
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(script_dir, "tokyo52.html")
                with open(filepath, "rb") as f: content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.cors(); self.send_header("Content-Length", len(content)); self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.reply({"error": "HTML file not found: " + str(e)}, 404)
            return
            
        # مسارات API
        if path == "/status": self.reply(bot_state)
        elif path == "/assets": self.reply({"assets": ASSETS})
        elif path == "/signals": self.reply({"signals": list(signals_db.values())})
        elif path == "/get_pending_signals": self.reply({"lst_signals": bot_state["pending_signals"]})
        else: self.reply({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length else "{}"
        data = json.loads(post_data)
        
        if path == "/login":
            email = data.get("email", "")
            password = data.get("password", "")
            user = USERS_DB.get(email)
            if user and user["password"] == password:
                if not user.get("approved", False):
                    self.reply({"success": False, "message": "حسابك قيد المراجعة من المدير"})
                else:
                    self.reply({"success": True, "role": user["role"], "email": email, "fname": user.get("fname", "")})
            else:
                self.reply({"success": False, "message": "البريد الإلكتروني أو كلمة المرور غير صحيحة"})
                
        elif path == "/register":
            email = data.get("email", "")
            if email in USERS_DB:
                self.reply({"success": False, "message": "هذا البريد مسجل بالفعل"})
            else:
                new_user = {
                    "password": data.get("password"),
                    "role": "user",
                    "fname": data.get("fname", ""),
                    "lname": data.get("lname", ""),
                    "approved": False
                }
                USERS_DB[email] = new_user
                PENDING_USERS.append(email)
                self.reply({"success": True, "message": "تم التسجيل بنجاح، بانتظار موافقة المدير"})
                
        elif path == "/update_settings":
            if "auto_trade" in data: bot_state["auto_trade"] = data["auto_trade"]
            if "account_type" in data: bot_state["account_type"] = data["account_type"]
            if "selected_assets" in data: bot_state["selected_assets"] = data["selected_assets"]
            self.reply({"status": "success"})
        else:
            self.reply({"error": "Not found"}, 404)

    def reply(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.cors()
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

# ==========================================
# حلقة البوت الرئيسية
# ==========================================
async def bot_loop():
    global client, global_lock, bot_state
    try:
        from pyquotex.stable_api import Quotex
        client = Quotex(email=EMAIL, password=PASSWORD, lang="ar")
        status, reason = await client.connect()
        if status:
            bot_state["connected"] = True
            try:
                bot_state["balance"] = await client.get_balance()
                await client.change_account(bot_state["account_type"])
            except: pass
            print("✅ اتصال طوكيو 52 ناجح!")
        else:
            bot_state["connected"] = False
            print(f"❌ فشل الاتصال: {reason}")
            return
    except Exception as e:
        print(f"❌ خطأ في الاستيراد أو الاتصال: {e}")
        return

    while True:
        try:
            if not bot_state["connected"]: await asyncio.sleep(10); continue
            
            try: bot_state["balance"] = await client.get_balance()
            except: pass
            
            for asset_id in bot_state["selected_assets"]:
                if global_lock: continue
                
                try:
                    candles = await client.get_candles(asset_id, 60, 0, 100)
                    if not candles or len(candles) < 50: continue
                    
                    direction, confidence, expiry, details = tokyo_52_engine(candles)
                    
                    now = datetime.now()
                    asset_name = next((a["name"] for a in ASSETS if a["id"] == asset_id), asset_id)
                    
                    if direction and confidence >= 70:
                        signal_data = {
                            "asset": asset_id, "asset_name": asset_name,
                            "direction": direction, "confidence": confidence,
                            "expiry": expiry, "time": now.strftime("%H:%M:%S"),
                            "status": "new"
                        }
                        signals_db[asset_id] = signal_data
                        
                        if confidence >= 85:
                            bot_state["pending_signals"].append({
                                "asset": asset_name, "direction": direction,
                                "time": now.strftime("%H:%M"), "confidence": confidence
                            })
                        
                        if bot_state["auto_trade"]:
                            global_lock = True
                            can_enter, reason_entry = await smart_entry(asset_id, direction, expiry)
                            
                            if can_enter:
                                print(f"🚀 فتح صفقة {direction} على {asset_name}")
                                try:
                                    status_trade, trade_id = await client.buy(10, asset_id, direction, expiry*60)
                                    if status_trade:
                                        await asyncio.sleep(expiry * 60 + 5)
                                        bot_state["trades_history"].append({"asset": asset_name, "result": "done"})
                                except: pass
                            global_lock = False
                                
                except Exception as e:
                    global_lock = False
                    
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ خطأ عام في الحلقة: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("=" * 58)
    print("  ⚡ طوكيو 52 - المحرك الجبارة (Tokyo 52 Engine)")
    print("=" * 58)
    
    threading.Thread(target=lambda: asyncio.run(bot_loop()), daemon=True).start()
    time.sleep(3)
    
    try:
        srv = HTTPServer(("0.0.0.0", 8765), Handler)
        print("✅ سيرفر الموقع يعمل على البورت 8765")
        srv.serve_forever()
    except KeyboardInterrupt: print("\n⛔ إيقاف")
