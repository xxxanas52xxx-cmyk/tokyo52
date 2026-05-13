"""
TOKYO 52 — v7.0 ULTIMATE
استراتيجية مدمجة: Triple Gate + MACD + RSI + Stochastic + BB + ADX + أنماط الشموع + تعلم ذاتي
مع نظام المستخدمين والصلاحيات الكاملة
"""
import asyncio, json, threading, time, random, math, csv, os, hashlib, uuid
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import numpy as np

# ═══ إعدادات الحساب ═══
EMAIL    = "x52anasx@gmail.com"
PASSWORD = "anas775312956"

# ═══ قائمة الأصول الكاملة ═══
ASSETS = [
    {"id":"EURUSD_otc","name":"EUR/USD","cat":"currencies"},{"id":"GBPUSD_otc","name":"GBP/USD","cat":"currencies"},
    {"id":"USDJPY_otc","name":"USD/JPY","cat":"currencies"},{"id":"USDCHF_otc","name":"USD/CHF","cat":"currencies"},
    {"id":"USDCAD_otc","name":"USD/CAD","cat":"currencies"},{"id":"AUDUSD_otc","name":"AUD/USD","cat":"currencies"},
    {"id":"NZDUSD_otc","name":"NZD/USD","cat":"currencies"},{"id":"EURGBP_otc","name":"EUR/GBP","cat":"currencies"},
    {"id":"EURJPY_otc","name":"EUR/JPY","cat":"currencies"},{"id":"GBPJPY_otc","name":"GBP/JPY","cat":"currencies"},
    {"id":"AUDJPY_otc","name":"AUD/JPY","cat":"currencies"},{"id":"NZDJPY_otc","name":"NZD/JPY","cat":"currencies"},
    {"id":"EURAUD_otc","name":"EUR/AUD","cat":"currencies"},{"id":"EURCHF_otc","name":"EUR/CHF","cat":"currencies"},
    {"id":"GBPCHF_otc","name":"GBP/CHF","cat":"currencies"},{"id":"AUDCHF_otc","name":"AUD/CHF","cat":"currencies"},
    {"id":"AUDCAD_otc","name":"AUD/CAD","cat":"currencies"},{"id":"AUDNZD_otc","name":"AUD/NZD","cat":"currencies"},
    {"id":"GBPAUD_otc","name":"GBP/AUD","cat":"currencies"},{"id":"GBPNZD_otc","name":"GBP/NZD","cat":"currencies"},
    {"id":"NZDCAD_otc","name":"NZD/CAD","cat":"currencies"},{"id":"NZDCHF_otc","name":"NZD/CHF","cat":"currencies"},
    {"id":"EURCAD_otc","name":"EUR/CAD","cat":"currencies"},{"id":"CADJPY_otc","name":"CAD/JPY","cat":"currencies"},
    {"id":"CADCHF_otc","name":"CAD/CHF","cat":"currencies"},{"id":"CHFJPY_otc","name":"CHF/JPY","cat":"currencies"},
    {"id":"EURNZD_otc","name":"EUR/NZD","cat":"currencies"},{"id":"USDARS_otc","name":"USD/ARS","cat":"currencies"},
    {"id":"USDBRL_otc","name":"USD/BRL","cat":"currencies"},{"id":"USDINR_otc","name":"USD/INR","cat":"currencies"},
    {"id":"USDMXN_otc","name":"USD/MXN","cat":"currencies"},{"id":"USDZAR_otc","name":"USD/ZAR","cat":"currencies"},
    {"id":"USDBDT_otc","name":"USD/BDT","cat":"currencies"},{"id":"USDPHP_otc","name":"USD/PHP","cat":"currencies"},
    {"id":"USDIDR_otc","name":"USD/IDR","cat":"currencies"},{"id":"USDCOP_otc","name":"USD/COP","cat":"currencies"},
    {"id":"USDEGP_otc","name":"USD/EGP","cat":"currencies"},{"id":"USDDZD_otc","name":"USD/DZD","cat":"currencies"},
    {"id":"USDPKR_otc","name":"USD/PKR","cat":"currencies"},{"id":"USDNGN_otc","name":"USD/NGN","cat":"currencies"},
    {"id":"XAUUSD_otc","name":"Gold","cat":"commodity"},{"id":"XAGUSD_otc","name":"Silver","cat":"commodity"},
    {"id":"USOIL_otc","name":"USCrude","cat":"commodity"},{"id":"UKOIL_otc","name":"UKBrent","cat":"commodity"},
    {"id":"BTCUSD_otc","name":"Bitcoin","cat":"crypto"},{"id":"ETHUSD_otc","name":"Ethereum","cat":"crypto"},
    {"id":"LTCUSD_otc","name":"Litecoin","cat":"crypto"},{"id":"BCHUSD_otc","name":"BitcoinCash","cat":"crypto"},
    {"id":"XRPUSD_otc","name":"Ripple","cat":"crypto"},{"id":"DASHUSD_otc","name":"Dash","cat":"crypto"},
    {"id":"ZECUSD_otc","name":"Zcash","cat":"crypto"},{"id":"BNBUSD_otc","name":"BNB","cat":"crypto"},
    {"id":"SOLUSD_otc","name":"Solana","cat":"crypto"},{"id":"AVAXUSD_otc","name":"Avalanche","cat":"crypto"},
    {"id":"LINKUSD_otc","name":"Chainlink","cat":"crypto"},{"id":"DOTUSD_otc","name":"Polkadot","cat":"crypto"},
    {"id":"ATOMUSD_otc","name":"Cosmos","cat":"crypto"},{"id":"TONUSD_otc","name":"Toncoin","cat":"crypto"},
    {"id":"AXSUSD_otc","name":"Axie","cat":"crypto"},{"id":"TRUMPUSD_otc","name":"Trump","cat":"crypto"},
    {"id":"MSFT_otc","name":"Microsoft","cat":"stock"},{"id":"BA_otc","name":"Boeing","cat":"stock"},
    {"id":"META_otc","name":"Facebook","cat":"stock"},{"id":"PFE_otc","name":"Pfizer","cat":"stock"},
    {"id":"JNJ_otc","name":"J&J","cat":"stock"},{"id":"AXP_otc","name":"AmExpress","cat":"stock"},
    {"id":"INTC_otc","name":"Intel","cat":"stock"},{"id":"MCD_otc","name":"McDonalds","cat":"stock"},
]
ASSET_IDS = [a["id"] for a in ASSETS]
ASSET_MAP = {a["id"]: a for a in ASSETS}
PORT = int(os.environ.get("PORT", 8765))

# ═══ مسارات الملفات ═══
def _path(name):
    for d in [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), os.path.expanduser("~")]:
        try:
            if os.access(d, os.W_OK): return os.path.join(d, name)
        except: pass
    return name

MEMORY_FILE = _path("trade_memory.csv")
USERS_FILE  = _path("users.json")
TRADES_FILE = _path("trades_log.json")

# ═══ الحالة العامة ═══
signals_db   = {}
trade_log    = []
bot_status   = {"connected": False, "error": None, "balance": None, "account_type": "PRACTICE"}
scan_state   = {"active": False, "auto_trade": False, "trade_amount": 1.0, "selected_assets": []}
last_signals = {}  # ذاكرة اللستات
client       = None
bg_loop      = None

# ═══ نظام المستخدمين ═══
def _load_users():
    try:
        with open(USERS_FILE, "r") as f: return json.load(f)
    except: return {
        "admin": {"password": hashlib.sha256("tokyo52admin".encode()).hexdigest(),
                  "role": "admin", "first": "المدير", "last": "العام", "email": EMAIL, "approved": True}
    }

def _save_users(u):
    try:
        with open(USERS_FILE, "w") as f: json.dump(u, f, ensure_ascii=False, indent=2)
    except: pass

users_db = _load_users()
sessions = {}  # token -> username

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def _new_token(): return str(uuid.uuid4())

def _get_user(req):
    token = req.headers.get("X-Token", "")
    return sessions.get(token)

# ═══ ذاكرة التعلم ═══
trade_memory = {aid: [] for aid in ASSET_IDS}
asset_cooldown = {aid: 0 for aid in ASSET_IDS}

def _load_memory():
    try:
        with open(MEMORY_FILE, newline="") as f:
            for row in csv.DictReader(f):
                aid = row.get("asset", "")
                if aid in trade_memory:
                    trade_memory[aid].append({
                        "result": row.get("result", ""), "signal": row.get("signal", ""),
                        "score": float(row.get("score", 0)), "time": row.get("time", "")
                    })
    except: pass

def _save_memory_row(aid, signal, score, result):
    try:
        exists = os.path.isfile(MEMORY_FILE)
        with open(MEMORY_FILE, "a", newline="") as f:
            w = csv.writer(f)
            if not exists: w.writerow(["asset", "signal", "score", "result", "time"])
            w.writerow([aid, signal, round(score, 2), result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except: pass

def _asset_win_rate(aid):
    mem = trade_memory.get(aid, [])
    if len(mem) < 3: return 0.5
    wins = sum(1 for m in mem[-30:] if m.get("result") == "win")
    return wins / min(len(mem), 30)

def _consecutive_losses(aid):
    mem = trade_memory.get(aid, [])
    count = 0
    for m in reversed(mem):
        if m.get("result") == "loss": count += 1
        else: break
    return count

# ═══ مؤشرات التحليل ═══
def sf(v, fb=0.0):
    try: return float(v) if v is not None else fb
    except: return fb

def clean_candles(raw):
    if not raw: return []
    out, prev = [], None
    for c in raw:
        cl = sf(c.get("close") or c.get("price"), 0.0)
        if cl == 0: cl = prev or 0.0
        if cl == 0: continue
        op = sf(c.get("open"), cl); hi = sf(c.get("high"), cl); lo = sf(c.get("low"), cl)
        if op == 0: op = cl
        if hi < max(op, cl): hi = max(op, cl)
        if lo > min(op, cl): lo = min(op, cl)
        out.append({"open": op, "close": cl, "high": hi, "low": lo, "time": sf(c.get("time"), 0)})
        prev = cl
    return out

def ema_arr(data, period):
    arr = np.array(data, dtype=float); n = len(arr)
    period = max(1, min(period, n - 1)) if n > 1 else 1
    if n < 2: return arr.copy()
    out = np.zeros(n); out[period-1] = np.mean(arr[:period]); k = 2.0 / (period + 1)
    for i in range(period, n): out[i] = arr[i] * k + out[i-1] * (1 - k)
    return out

def calc_rsi(closes, period=14):
    arr = np.array(closes, dtype=float); n = len(arr)
    if n < 6: return 50.0
    p = min(period, n-1); w = arr[-p*4:] if n >= p*4 else arr; d = np.diff(w)
    if len(d) == 0: return 50.0
    g = np.where(d > 0, d, 0.0); l = np.where(d < 0, -d, 0.0)
    pg = min(p, len(g)); ag = np.mean(g[:pg]); al = np.mean(l[:pg])
    for i in range(pg, len(g)): ag = (ag*(pg-1)+g[i])/pg; al = (al*(pg-1)+l[i])/pg
    return round(100 - 100/(1+ag/al), 2) if al > 0 else 100.0

def calc_macd(closes):
    if len(closes) < 35: return None, None, None
    arr = np.array(closes, dtype=float)
    ml = ema_arr(arr, 12) - ema_arr(arr, 26); sg = ema_arr(ml, 9); ht = ml - sg
    s = max(0, min(35, len(ml)-5)); return ml[s:], sg[s:], ht[s:]

def calc_stoch(clist, kp=14, sm=3):
    n = len(clist)
    if n < 6: return 50.0, 50.0
    kv = []
    for i in range(min(kp, n-1), n):
        sl = clist[max(0, i-kp+1):i+1]; h = max(x["high"] for x in sl); lo = min(x["low"] for x in sl)
        kv.append(100*(clist[i]["close"]-lo)/(h-lo) if h != lo else 50.0)
    if not kv: return 50.0, 50.0
    d = float(np.mean(kv[-sm:])) if len(kv) >= sm else float(np.mean(kv))
    return round(kv[-1], 2), round(d, 2)

def calc_bb(closes, period=20, mult=2.0):
    if len(closes) < 10: return None, None, None
    arr = np.array(closes[-min(period, len(closes)):], dtype=float)
    mid = float(np.mean(arr)); sd = float(np.std(arr))
    if sd == 0: return mid*0.998, mid, mid*1.002
    return mid - mult*sd, mid, mid + mult*sd

def calc_atr(clist, period=14):
    if len(clist) < 3: return 0.001
    c = clist[-min(period*2, len(clist)):]
    trs = [max(c[i]["high"]-c[i]["low"], abs(c[i]["high"]-c[i-1]["close"]), abs(c[i]["low"]-c[i-1]["close"])) for i in range(1, len(c))]
    return float(np.mean(trs)) if trs else 0.001

def calc_adx(clist, period=14):
    if len(clist) < 16: return 15.0
    c = clist[-min(60, len(clist)):]
    pdm, mdm, trl = [], [], []
    for i in range(1, len(c)):
        h, lo, ph, pl, pc = c[i]["high"], c[i]["low"], c[i-1]["high"], c[i-1]["low"], c[i-1]["close"]
        trl.append(max(h-lo, abs(h-pc), abs(lo-pc))); up = h-ph; dn = pl-lo
        pdm.append(up if up > dn and up > 0 else 0); mdm.append(dn if dn > up and dn > 0 else 0)
    def wld(a, p):
        p = min(p, len(a))
        if p == 0: return [0]
        s = sum(a[:p]); o = [s]
        for v in a[p:]: s = s - s/p + v; o.append(s)
        return o
    at, pd2, md = wld(trl, period), wld(pdm, period), wld(mdm, period); dx = []
    for a, p, m in zip(at, pd2, md):
        if a == 0: dx.append(0); continue
        pi, mi = 100*p/a, 100*m/a; s = pi+mi
        dx.append(100*abs(pi-mi)/s if s else 0)
    return round(float(np.mean(dx[-10:])), 2) if len(dx) >= 10 else 15.0

def calc_williams_r(clist, period=14):
    if len(clist) < period: return -50.0
    sl = clist[-period:]; h = max(x["high"] for x in sl); l = min(x["low"] for x in sl)
    return round((h-clist[-1]["close"])/(h-l)*-100, 2) if h != l else -50.0

def calc_cci(clist, period=20):
    if len(clist) < period: return 0.0
    sl = clist[-period:]; tp = [(x["high"]+x["low"]+x["close"])/3 for x in sl]
    avg = np.mean(tp); mad = np.mean([abs(x-avg) for x in tp])
    return round((tp[-1]-avg)/(0.015*mad), 2) if mad else 0.0

def calc_aroon(clist, period=14):
    if len(clist) < period: return 50.0, 50.0
    sl = clist[-period:]
    hh = max(c["high"] for c in sl); ll = min(c["low"] for c in sl)
    ph, pl = 0, 0
    for i, c in enumerate(reversed(sl)):
        if c["high"] == hh and ph == 0: ph = i
        if c["low"] == ll and pl == 0: pl = i
    return round((period-ph)/period*100, 2), round((period-pl)/period*100, 2)

def candle_patterns(clist):
    v = 0
    if len(clist) < 4: return v
    atr = calc_atr(clist, 14); bt = atr * 0.2
    bd = lambda c: abs(c["close"]-c["open"])
    su = lambda c: c["high"]-max(c["close"], c["open"])
    sl2 = lambda c: min(c["close"], c["open"])-c["low"]
    L = clist[-1]
    if sl2(L) > bd(L)*2.2 and su(L) < bd(L)*0.4 and bd(L) > bt: v += 3  # hammer
    if su(L) > bd(L)*2.2 and sl2(L) < bd(L)*0.4 and bd(L) > bt: v -= 3  # shooting star
    if len(clist) >= 2:
        P, C = clist[-2], clist[-1]
        if P["close"] < P["open"] and C["close"] > C["open"] and C["open"] < P["close"] and C["close"] > P["open"] and bd(C) > bd(P)*1.1: v += 4  # bullish engulfing
        if P["close"] > P["open"] and C["close"] < C["open"] and C["open"] > P["close"] and C["close"] < P["open"] and bd(C) > bd(P)*1.1: v -= 4  # bearish engulfing
    if len(clist) >= 3:
        A, B2, C2 = clist[-3], clist[-2], clist[-1]
        if A["close"] < A["open"] and abs(B2["close"]-B2["open"]) < atr*0.3 and C2["close"] > C2["open"]: v += 3  # morning star
        if A["close"] > A["open"] and abs(B2["close"]-B2["open"]) < atr*0.3 and C2["close"] < C2["open"]: v -= 3  # evening star
    return v

def find_pivots(clist, w=4):
    hs = [c["high"] for c in clist]; ls = [c["low"] for c in clist]; n = len(clist)
    pk, tr = [], []
    for i in range(w, n-w):
        if all(hs[i] >= hs[i-j] for j in range(1, w+1)) and all(hs[i] >= hs[i+j] for j in range(1, w+1)): pk.append((i, hs[i]))
        if all(ls[i] <= ls[i-j] for j in range(1, w+1)) and all(ls[i] <= ls[i+j] for j in range(1, w+1)): tr.append((i, ls[i]))
    return pk, tr

def trend_score(clist):
    if len(clist) < 25: return 0
    pk, tr = find_pivots(clist, 3); s = 0
    if len(pk) >= 2: s += 2 if pk[-1][1] > pk[-2][1]*1.0002 else (-2 if pk[-1][1] < pk[-2][1]*0.9998 else 0)
    if len(tr) >= 2: s += 2 if tr[-1][1] > tr[-2][1]*1.0002 else (-2 if tr[-1][1] < tr[-2][1]*0.9998 else 0)
    return s

def detect_divergence(clist, rsi):
    if len(clist) < 30: return 0
    n = min(40, len(clist)); pr = [c["close"] for c in clist[-n:]]; h = n//2
    pe, pl2, re = np.mean(pr[:h]), np.mean(pr[h:]), calc_rsi(pr[:h])
    if pl2 > pe*1.001 and rsi < re-6: return -3  # bearish div
    if pl2 < pe*0.999 and rsi > re+6: return +3  # bullish div
    return 0

# ═══ محرك التحليل الرئيسي — TRIPLE GATE ═══
def analyze(clist, asset_id=""):
    closes = [c["close"] for c in clist]; n = len(closes)
    res = {"signal": None, "score": 0, "gate1": 0, "gate2": 0, "gate3": 0,
           "reasons": [], "entry_type": "", "expiry_minutes": 2,
           "entry_method": "انتظار", "no_signal": ""}

    if n < 20: res["no_signal"] = "شموع غير كافية"; return res

    arr = np.array(closes, dtype=float)

    # ═══ البوابة 1: الاتجاه العام ═══
    g1 = 0
    if n >= 12:
        e9, e21, e50 = ema_arr(arr, min(9,n-1)), ema_arr(arr, min(21,n-1)), ema_arr(arr, min(50,n-1))
        if e9[-1] > e21[-1] > e50[-1]: g1 += 3; res["reasons"].append("EMA صاعد مكثف ↑")
        elif e9[-1] < e21[-1] < e50[-1]: g1 -= 3; res["reasons"].append("EMA هابط مكثف ↓")
        elif e9[-1] > e21[-1]: g1 += 1
        elif e9[-1] < e21[-1]: g1 -= 1
        if n >= 10:
            sl2 = (e9[-1]-e9[-6])/abs(e9[-6])*100 if e9[-6] != 0 else 0
            if sl2 > 0.03: g1 += 1
            elif sl2 < -0.03: g1 -= 1
    # Aroon
    aup, adn = calc_aroon(clist, 14)
    if aup > 75 and adn < 30: g1 += 2; res["reasons"].append(f"Aroon صاعد ({aup:.0f})")
    elif adn > 75 and aup < 30: g1 -= 2; res["reasons"].append(f"Aroon هابط ({adn:.0f})")
    g1 += trend_score(clist)
    adx = calc_adx(clist)
    res["gate1"] = g1

    # ═══ البوابة 2: الزخم والتذبذب ═══
    g2 = 0
    rsi = calc_rsi(closes)
    if rsi < 25: g2 += 4; res["reasons"].append(f"RSI تشبع بيعي ({rsi:.0f})")
    elif rsi < 35: g2 += 3; res["reasons"].append(f"RSI منطقة شراء ({rsi:.0f})")
    elif rsi < 42: g2 += 2
    elif rsi > 75: g2 -= 4; res["reasons"].append(f"RSI تشبع شرائي ({rsi:.0f})")
    elif rsi > 65: g2 -= 3; res["reasons"].append(f"RSI منطقة بيع ({rsi:.0f})")
    elif rsi > 58: g2 -= 2

    sk, sd2 = calc_stoch(clist)
    if sk < 15: g2 += 4; res["reasons"].append(f"Stoch تشبع بيعي ({sk:.0f})")
    elif sk < 30: g2 += 2
    elif sk > 85: g2 -= 4; res["reasons"].append(f"Stoch تشبع شرائي ({sk:.0f})")
    elif sk > 70: g2 -= 2
    # تقاطع Stoch
    if sk > sd2 and sk < 40: g2 += 2; res["reasons"].append("Stoch تقاطع صاعد ↑")
    elif sk < sd2 and sk > 60: g2 -= 2; res["reasons"].append("Stoch تقاطع هابط ↓")

    ml, sg, ht = calc_macd(closes)
    if ml is not None and len(ml) >= 3:
        if ml[-2] <= sg[-2] and ml[-1] > sg[-1]: g2 += 4; res["reasons"].append("MACD تقاطع صاعد ↑")
        elif ml[-2] >= sg[-2] and ml[-1] < sg[-1]: g2 -= 4; res["reasons"].append("MACD تقاطع هابط ↓")
        elif ml[-1] > sg[-1]: g2 += 1
        else: g2 -= 1
        if ht is not None and len(ht) >= 2:
            if ht[-1] > 0 and ht[-1] > ht[-2]: g2 += 1
            elif ht[-1] < 0 and ht[-1] < ht[-2]: g2 -= 1

    wr = calc_williams_r(clist)
    if wr < -82: g2 += 3; res["reasons"].append(f"Williams R ذروة بيع ({wr:.0f})")
    elif wr > -18: g2 -= 3; res["reasons"].append(f"Williams R ذروة شراء ({wr:.0f})")

    cci = calc_cci(clist)
    if cci < -130: g2 += 2; res["reasons"].append(f"CCI تشبع ({cci:.0f})")
    elif cci > 130: g2 -= 2; res["reasons"].append(f"CCI تشبع ({cci:.0f})")

    g2 += detect_divergence(clist, rsi)
    res["gate2"] = g2

    # ═══ البوابة 3: السعر والهيكل ═══
    g3 = 0; cp = closes[-1]
    bb_lo, bb_mid, bb_hi = calc_bb(closes)
    if bb_mid:
        if cp < bb_lo: g3 += 4; res["reasons"].append("سعر تحت BB السفلي ↑")
        elif cp < bb_lo*1.001: g3 += 3
        elif cp > bb_hi: g3 -= 4; res["reasons"].append("سعر فوق BB العلوي ↓")
        elif cp > bb_hi*0.999: g3 -= 3

    try:
        pk, tr = find_pivots(clist, 4)
        nr = min(p[1] for p in pk[-8:] if p[1] > cp) if any(p[1] > cp for p in pk[-8:]) else cp*1.005
        ns = max(t[1] for t in tr[-8:] if t[1] < cp) if any(t[1] < cp for t in tr[-8:]) else cp*0.995
        ds = round((cp-ns)/cp*100, 4); dr = round((nr-cp)/cp*100, 4)
        if ds < 0.12: g3 += 4; res["reasons"].append("قرب دعم قوي ↑")
        elif ds < 0.25: g3 += 3
        if dr < 0.12: g3 -= 4; res["reasons"].append("قرب مقاومة قوية ↓")
        elif dr < 0.25: g3 -= 3
    except: pass

    g3 += candle_patterns(clist)
    res["gate3"] = g3

    # ═══ القرار النهائي ═══
    def gd(v, t=2): return 1 if v >= t else (-1 if v <= -t else 0)
    d1, d2, d3 = gd(g1), gd(g2), gd(g3)
    gs = [d for d in [d1, d2, d3] if d != 0]
    ca = sum(1 for d in gs if d > 0); pu = sum(1 for d in gs if d < 0)

    if ca >= 2: direction, agr = "call", ca
    elif pu >= 2: direction, agr = "put", pu
    else: res["no_signal"] = "توافق غير كافي بين البوابات"; return res

    ds2 = 1 if direction == "call" else -1

    # نقاط الثقة الأساسية
    base = 70 if agr >= 3 else (64 if agr == 2 and adx >= 20 else 60)
    bonus_g1 = min(10, max(0, g1*ds2*1.2))
    bonus_g2 = min(12, max(0, g2*ds2))
    bonus_g3 = min(10, max(0, g3*ds2*1.2))
    adx_bonus = (4 if adx >= 28 else 2 if adx >= 20 else 0)

    # تعديل بناء على سجل الأصل
    wr2 = _asset_win_rate(asset_id)
    losses = _consecutive_losses(asset_id)
    memory_adj = (wr2 - 0.5) * 10  # +5 إذا معدل فوز 100%، -5 إذا 0%
    memory_adj -= losses * 2  # خصم 2 لكل خسارة متتالية

    conf = int(min(96, base + bonus_g1 + bonus_g2 + bonus_g3 + adx_bonus + memory_adj))
    conf = max(50, conf)

    # مدة الصفقة الذكية
    em = 1 if agr >= 3 and adx >= 28 else (2 if agr >= 3 else 3)

    # طريقة الدخول
    co = clist[-1]["open"]
    meth = "انتظار إغلاق الشمعة"
    if direction == "call" and cp < co: meth = "دخول فوري"
    elif direction == "put" and cp > co: meth = "دخول فوري"

    stren = "استثنائية" if conf >= 85 else ("قوية جداً" if conf >= 75 else ("قوية" if conf >= 65 else "جيدة"))

    res.update({
        "signal": direction, "score": conf, "strength": stren,
        "entry_type": "GOLD" if agr >= 3 else "SILVER",
        "expiry_minutes": em, "expiry_seconds": em*60,
        "entry_method": meth, "agreeing_gates": agr,
        "adx": round(adx, 1), "rsi": round(rsi, 1),
        "macd_cross": ml is not None and len(ml) >= 2 and ((ml[-2] <= sg[-2] and ml[-1] > sg[-1]) or (ml[-2] >= sg[-2] and ml[-1] < sg[-1]))
    })
    return res

# ═══ شموع تجريبية واقعية ═══
def demo_candles(count=250):
    rng = random.Random(int(time.time()*1000) % 9999999); price = 1.0 + rng.random()*50; bv = 0.0005
    segs = [('up',25,2.0),('down',20,1.5),('up',30,2.5),('sideways',15,1.0),('down',25,2.0),('up',20,1.8)]
    out = []; si = 0; sp = 0
    for i in range(count):
        while si < len(segs)-1 and sp >= segs[si][1]: si += 1; sp = 0
        t, _, s = segs[si]; v = bv*s
        tr = v*0.35*(1 if t == 'up' else -1 if t == 'down' else 0); ns = v*(0.6 if t != 'sideways' else 0.3)
        ch = tr + (rng.random()-0.5)*ns*2; op = price; price += ch
        out.append({"open":op,"close":price,"high":max(op,price)+rng.random()*v*0.2,"low":min(op,price)-rng.random()*v*0.2,"time":int(time.time())-count+i}); sp += 1
    return out

# ═══ جلب الشموع من المنصة ═══
async def fetch_candles(asset_id, tf=60, target=200):
    if not client or not bot_status["connected"]: return []
    seen = {}; now_ts = int(time.time())
    for attempt in range(5):
        try:
            if attempt == 0: batch = await client.get_candles(asset_id, tf, 0, 100)
            else:
                try: batch = await client.get_candles(asset_id, tf, now_ts - attempt*100*tf, 100)
                except: batch = await client.get_candles(asset_id, tf, attempt*100, 100)
            if not batch: break
            for c in clean_candles(batch):
                if c["time"] not in seen: seen[c["time"]] = c
            if len(seen) >= target: break
            await asyncio.sleep(0.1)
        except: break
    return sorted(seen.values(), key=lambda c: c["time"])

# ═══ تحليل الأصل (sync) ═══
def analyze_asset_sync(asset_id):
    info = ASSET_MAP.get(asset_id, {"id": asset_id, "name": asset_id, "cat": "currencies"})
    try:
        clist = demo_candles(250); mode = "demo"
        if client and bot_status["connected"] and bg_loop:
            try:
                future = asyncio.run_coroutine_threadsafe(fetch_candles(asset_id, 60, 200), bg_loop)
                clist_r = future.result(timeout=10)
                if len(clist_r) > 30: clist = clist_r; mode = "live"
            except: pass

        # تحقق من cooldown
        if asset_cooldown.get(asset_id, 0) > time.time():
            return signals_db.get(asset_id, {})

        a = analyze(clist, asset_id)
        now = datetime.now(); em = a.get("expiry_minutes", 2)
        secs = 60 - now.second; et = datetime.fromtimestamp(now.timestamp()+secs).strftime("%H:%M:%S")
        score = a.get("score", 0); has = a.get("signal") is not None and score >= 60

        data = {
            "asset": asset_id, "asset_name": info["name"], "asset_cat": info["cat"],
            "time": now.strftime("%H:%M:%S"), "signal": a.get("signal"), "score": score,
            "strength": a.get("strength", ""), "reasons": a.get("reasons", []),
            "gate1": a.get("gate1", 0), "gate2": a.get("gate2", 0), "gate3": a.get("gate3", 0),
            "entry_type": a.get("entry_type", ""), "expiry_minutes": em, "expiry_seconds": em*60,
            "entry_time": et, "seconds_to_entry": secs, "last_price": round(clist[-1]["close"], 6),
            "mode": mode, "has_signal": has, "strong_signal": has and score >= 75,
            "no_signal_reason": a.get("no_signal", ""), "trade_status": "signal_only",
            "entry_method": a.get("entry_method", "انتظار"), "agreeing_gates": a.get("agreeing_gates", 0),
            "adx": a.get("adx", 0), "rsi": a.get("rsi", 50),
            "win_rate": round(_asset_win_rate(asset_id)*100, 1),
            "consecutive_losses": _consecutive_losses(asset_id)
        }

        signals_db[asset_id] = data

        # تداول تلقائي
        if has and scan_state.get("auto_trade") and client and bot_status["connected"] and bg_loop:
            if score >= 65:
                try:
                    asyncio.run_coroutine_threadsafe(
                        execute_trade(asset_id, a["signal"], scan_state.get("trade_amount", 1.0), em*60, data, clist),
                        bg_loop
                    )
                except: pass
        return data
    except Exception as e:
        return {"asset": asset_id, "error": str(e)}

# ═══ تنفيذ الصفقة مع التوقيت الذكي ═══
async def execute_trade(asset_id, direction, amount, expiry_secs, sig_data, clist):
    try:
        signals_db[asset_id]["trade_status"] = "executing"
        co = clist[-1]["open"] if clist else 0
        cp = clist[-1]["close"] if clist else 0

        # منطق التوقيت الذكي
        should_wait = True
        if direction == "call" and cp < co: should_wait = False  # استثناء CALL
        if direction == "put" and cp > co: should_wait = False   # استثناء PUT

        if should_wait:
            now = datetime.now()
            wait = 60 - (now.second + now.microsecond/1e6)
            if wait > 1:
                await asyncio.sleep(wait + 0.3)

        status, trade_id = await client.buy(amount, asset_id, direction, expiry_secs)
        if status:
            signals_db[asset_id]["trade_status"] = "executed"
            entry_price = cp
            # انتظار نتيجة الصفقة
            await asyncio.sleep(expiry_secs + 2)
            # حساب النتيجة
            try:
                new_clist = await fetch_candles(asset_id, 60, 5)
                exit_price = new_clist[-1]["close"] if new_clist else entry_price
            except:
                exit_price = entry_price

            won = (direction == "call" and exit_price >= entry_price) or (direction == "put" and exit_price <= entry_price)
            result = "win" if won else "loss"
            payout_pct = 85  # افتراضي
            profit = amount * payout_pct / 100 if won else -amount
            pip_diff = round((exit_price - entry_price) * 10000, 1)

            trade_rec = {
                "id": str(trade_id), "asset": asset_id, "asset_name": ASSET_MAP.get(asset_id, {}).get("name", asset_id),
                "direction": direction, "amount": amount, "entry_price": round(entry_price, 6),
                "exit_price": round(exit_price, 6), "result": result, "profit": round(profit, 2),
                "payout_pct": payout_pct, "pip_diff": pip_diff, "expiry": expiry_secs,
                "score": sig_data.get("score", 0), "time": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            trade_log.append(trade_rec)
            if len(trade_log) > 500: trade_log.pop(0)

            # حفظ في ملف
            try:
                with open(TRADES_FILE, "w") as f: json.dump(trade_log, f, ensure_ascii=False, indent=2)
            except: pass

            # تحديث الذاكرة
            trade_memory[asset_id].append({"result": result, "signal": direction, "score": sig_data.get("score", 0), "time": datetime.now().isoformat()})
            if len(trade_memory[asset_id]) > 200: trade_memory[asset_id].pop(0)
            _save_memory_row(asset_id, direction, sig_data.get("score", 0), result)

            # تبريد بعد الخسارة
            if result == "loss" and _consecutive_losses(asset_id) >= 3:
                asset_cooldown[asset_id] = time.time() + 300  # 5 دقائق تبريد

            # تحديث الرصيد
            try:
                bot_status["balance"] = await client.get_balance()
            except: pass

            print(f"[TRADE] {asset_id} {direction.upper()} → {result.upper()} | ربح: {profit:+.2f}$")
        else:
            signals_db[asset_id]["trade_status"] = "failed"
    except Exception as e:
        print(f"[TRADE_ERR] {asset_id}: {e}")
        signals_db[asset_id]["trade_status"] = "failed"

# ═══ استراتيجية اللستات (تحليل تاريخي مستقبلي) ═══
def analyze_lasts(asset_id):
    """تحليل النمط التاريخي وتوليد إشارات مستقبلية"""
    info = ASSET_MAP.get(asset_id, {"id": asset_id, "name": asset_id})
    try:
        clist = demo_candles(300); mode = "demo"
        if client and bot_status["connected"] and bg_loop:
            try:
                future = asyncio.run_coroutine_threadsafe(fetch_candles(asset_id, 300, 300), bg_loop)
                clist_r = future.result(timeout=12)
                if len(clist_r) > 50: clist = clist_r; mode = "live"
            except: pass

        if len(clist) < 50: return None

        closes = [c["close"] for c in clist]
        # تحليل الأنماط التاريخية
        rsi = calc_rsi(closes)
        aup, adn = calc_aroon(clist, 25)
        ml, sg, ht = calc_macd(closes)
        bb_lo, bb_mid, bb_hi = calc_bb(closes)
        adx = calc_adx(clist)

        # توقع الاتجاه المستقبلي خلال 15-30 دقيقة
        score_up = 0; score_dn = 0
        if rsi < 35: score_up += 3
        elif rsi > 65: score_dn += 3
        if aup > 70: score_up += 2
        elif adn > 70: score_dn += 2
        if ml is not None and len(ml) >= 2 and ml[-1] > sg[-1]: score_up += 2
        elif ml is not None and len(ml) >= 2 and ml[-1] < sg[-1]: score_dn += 2
        cp = closes[-1]
        if bb_lo and cp < bb_lo: score_up += 3
        if bb_hi and cp > bb_hi: score_dn += 3

        direction = "call" if score_up > score_dn else ("put" if score_dn > score_up else None)
        if not direction: return None

        conf = min(92, 55 + max(score_up, score_dn)*5)
        expiry_minutes = 5 if adx >= 25 else 10

        now = datetime.now()
        entry_at = (now + timedelta(minutes=5)).strftime("%H:%M")

        return {
            "asset": asset_id, "asset_name": info["name"],
            "signal": direction, "score": conf,
            "entry_time": entry_at, "expiry_minutes": expiry_minutes,
            "last_price": round(cp, 6), "mode": mode,
            "rsi": round(rsi, 1), "adx": round(adx, 1),
            "aroon_up": aup, "aroon_dn": adn,
            "time": now.strftime("%H:%M:%S"), "type": "last"
        }
    except Exception as e:
        return None

# ═══ حلقة المسح ═══
def scan_loop_thread():
    while True:
        time.sleep(2)
        if not scan_state["active"]: continue
        assets = scan_state.get("selected_assets", [])
        if not assets: continue
        print(f"[{datetime.now().strftime('%H:%M:%S')}] مسح {len(assets)} زوج...")
        for aid in assets:
            if not scan_state["active"]: break
            try: analyze_asset_sync(aid)
            except: pass
            time.sleep(0.1)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] انتهى المسح")
        for _ in range(20):
            if not scan_state["active"]: break
            time.sleep(1)

# ═══ الاتصال بالمنصة ═══
async def switch_account_async(atype):
    global client, bot_status
    if not client or not bot_status["connected"]: return False, "غير متصل"
    try:
        if hasattr(client, 'change_account'): await client.change_account(atype)
        bot_status["account_type"] = atype
        return True, "تم التبديل"
    except Exception as e: return False, str(e)

async def bot_connect():
    global client, bot_status
    try:
        from pyquotex.stable_api import Quotex
        client = Quotex(email=EMAIL, password=PASSWORD, lang="ar")
        ok, reason = await client.connect()
        if ok:
            bot_status["connected"] = True; bot_status["error"] = None
            print("[OK] اتصال ناجح!")
            try: bot_status["balance"] = await client.get_balance()
            except: pass
            await switch_account_async("PRACTICE")
        else: bot_status["error"] = "فشل: " + str(reason); print("[FAIL] " + str(reason))
    except ImportError: bot_status["error"] = "pyquotex غير مثبت — وضع تجريبي"; print("[DEMO] وضع تجريبي")
    except Exception as e: bot_status["error"] = str(e); print("[ERR] " + str(e))

def run_bg_loop():
    global bg_loop
    bg_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bg_loop)
    bg_loop.run_until_complete(bot_connect())
    async def keep_alive():
        while True:
            await asyncio.sleep(30)
            if client and bot_status["connected"]:
                try: bot_status["balance"] = await client.get_balance()
                except: pass
    bg_loop.run_until_complete(keep_alive())

# ═══════════════════════════════════════════
#  HTTP Server
# ═══════════════════════════════════════════
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Accept,X-Token")
        self.send_header("Access-Control-Max-Age", "3600")

    def do_HEAD(self):
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self._cors(); self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        # ─── صفحة HTML ───
        if path in ["/", "/tokyo52.html", "/index.html"]:
            html = None
            sd = os.path.dirname(os.path.abspath(__file__))
            for fn in ["tokyo52.html", "index.html"]:
                for d in [sd, os.getcwd(), os.path.join(sd, '..'), os.path.expanduser('~')]:
                    if not os.path.isdir(d): continue
                    fp = os.path.join(d, fn)
                    if os.path.isfile(fp):
                        try:
                            with open(fp, "r", encoding="utf-8") as f: html = f.read()
                            break
                        except: pass
                if html: break

            if html:
                html = html.replace("const API='http://localhost:8765'", "const API=''")
                html = html.replace("const API = 'http://localhost:8765'", "const API = ''")
                b = html.encode("utf-8")
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self._cors(); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            else:
                self._json({"error": "لم أجد tokyo52.html"}, 404)
            return

        # ─── API ───
        try:
            if path == "/status":
                self._json({**bot_status, "scan_active": scan_state["active"], "auto_trade": scan_state["auto_trade"], "selected_count": len(scan_state["selected_assets"])})
            elif path == "/assets":
                self._json({"assets": ASSETS})
            elif path == "/signals":
                self._json({"signals": list(signals_db.values())})
            elif path == "/trade_log":
                self._json({"trades": list(reversed(trade_log[-100:]))})
            elif path == "/lasts":
                assets = scan_state.get("selected_assets", [])[:20]
                results = []
                for aid in assets:
                    r = analyze_lasts(aid)
                    if r: results.append(r)
                self._json({"lasts": results})
            elif path == "/stats":
                total = len(trade_log)
                wins = sum(1 for t in trade_log if t.get("result") == "win")
                total_profit = sum(t.get("profit", 0) for t in trade_log)
                self._json({"total": total, "wins": wins, "losses": total-wins,
                           "win_rate": round(wins/total*100, 1) if total else 0,
                           "total_profit": round(total_profit, 2)})
            elif path == "/users":
                # للمدير فقط
                user = _get_user(self)
                if user and users_db.get(user, {}).get("role") == "admin":
                    safe = {k: {kk: vv for kk, vv in v.items() if kk != "password"} for k, v in users_db.items()}
                    self._json({"users": safe})
                else:
                    self._json({"error": "غير مصرح"}, 403)
            else:
                self._json({"error": "404"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            cl = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(cl).decode("utf-8")) if cl > 0 else {}

            # ─── تسجيل دخول ───
            if path == "/login":
                uname = body.get("username", "").strip()
                pw = body.get("password", "")
                u = users_db.get(uname)
                if u and u.get("password") == _hash(pw):
                    if not u.get("approved", False):
                        self._json({"success": False, "message": "الحساب قيد المراجعة"}); return
                    token = _new_token(); sessions[token] = uname
                    self._json({"success": True, "token": token, "role": u.get("role", "user"),
                                "first": u.get("first", ""), "last": u.get("last", "")})
                else:
                    self._json({"success": False, "message": "بيانات خاطئة"})

            # ─── تسجيل حساب جديد ───
            elif path == "/register":
                uname = body.get("username", "").strip()
                pw = body.get("password", "")
                first = body.get("first", "").strip()
                last = body.get("last", "").strip()
                email2 = body.get("email", "").strip()
                if not uname or not pw or not first or not last:
                    self._json({"success": False, "message": "جميع الحقول مطلوبة"}); return
                if uname in users_db:
                    self._json({"success": False, "message": "اسم المستخدم موجود"}); return
                users_db[uname] = {"password": _hash(pw), "role": "user", "first": first,
                                   "last": last, "email": email2, "approved": False,
                                   "registered": datetime.now().isoformat()}
                _save_users(users_db)
                self._json({"success": True, "message": "تم التسجيل! انتظر موافقة المدير"})

            # ─── موافقة/رفض مستخدم ───
            elif path == "/approve_user":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح"}, 403); return
                target = body.get("username")
                approved = body.get("approved", True)
                if target in users_db:
                    users_db[target]["approved"] = approved
                    _save_users(users_db)
                    self._json({"success": True})
                else:
                    self._json({"success": False, "message": "المستخدم غير موجود"})

            # ─── تشغيل المسح ───
            elif path == "/start":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح — المدير فقط"}, 403); return
                scan_state["selected_assets"] = [a for a in body.get("assets", []) if a in ASSET_IDS]
                scan_state["auto_trade"] = body.get("auto_trade", False)
                scan_state["trade_amount"] = float(body.get("amount", 1.0))
                scan_state["active"] = True
                self._json({"status": "started", "count": len(scan_state["selected_assets"])})

            elif path == "/stop":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح"}, 403); return
                scan_state["active"] = False
                self._json({"status": "stopped"})

            elif path == "/auto_trade":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح"}, 403); return
                scan_state["auto_trade"] = body.get("enabled", False)
                self._json({"auto_trade": scan_state["auto_trade"]})

            elif path == "/switch_account":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح"}, 403); return
                at = body.get("type", "PRACTICE")
                if bg_loop:
                    future = asyncio.run_coroutine_threadsafe(switch_account_async(at), bg_loop)
                    ok, msg = future.result(timeout=5)
                    self._json({"success": ok, "message": msg, "account_type": at})
                else:
                    self._json({"success": False, "message": "لا يوجد اتصال"})

            elif path == "/lasts_auto":
                user = _get_user(self)
                if not user or users_db.get(user, {}).get("role") != "admin":
                    self._json({"error": "غير مصرح"}, 403); return
                scan_state["lasts_auto"] = body.get("enabled", False)
                self._json({"lasts_auto": scan_state.get("lasts_auto", False)})

            else:
                self._json({"error": "404"}, 404)

        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _json(self, data, code=200):
        try:
            b = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors(); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        except Exception as e:
            print(f"[JSON_ERR] {e}")

# ═══ التشغيل ═══
if __name__ == "__main__":
    print("=" * 55)
    print("  TOKYO 52 — v7.0 ULTIMATE")
    print(f"  http://localhost:{PORT}")
    print("  نظام Triple Gate + تعلم ذاتي + مستخدمين")
    print("=" * 55)

    _load_memory()
    try:
        with open(TRADES_FILE, "r") as f: trade_log.extend(json.load(f))
    except: pass

    t1 = threading.Thread(target=run_bg_loop, daemon=True); t1.start()
    time.sleep(1)
    t2 = threading.Thread(target=scan_loop_thread, daemon=True); t2.start()

    try:
        srv = HTTPServer(("0.0.0.0", PORT), H)
        print(f"[OK] السيرفر يعمل على المنفذ {PORT}")
        srv.serve_forever()
    except OSError as e:
        print(f"[ERR] المنفذ {PORT} مستخدم!")
    except KeyboardInterrupt:
        print("\n[STOP] إيقاف")
