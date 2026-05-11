"""
TOKYO 52 — v6.2 FIXED
مع إصلاح مشاكل الاتصال والـ CORS
"""
import asyncio, json, threading, time, random, math
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import numpy as np
import os

EMAIL = "x52anasx@gmail.com"
PASSWORD = "anas775312956"

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

signals_db = {}
trade_log = []
bot_status = {"connected": False, "error": None, "balance": None, "account_type": "PRACTICE"}
scan_state = {"active": False, "auto_trade": False, "trade_amount": 1.0, "selected_assets": []}
client = None
bg_loop = None

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

async def fetch_candles(asset_id, tf, target=200):
    if not client or not bot_status["connected"]: return []
    seen = {}; now_ts = int(time.time())
    for attempt in range(5):
        try:
            if attempt == 0: batch = await client.get_candles(asset_id, tf, 0, 100)
            else:
                try: batch = await client.get_candles(asset_id, tf, now_ts - attempt * 100 * tf, 100)
                except: batch = await client.get_candles(asset_id, tf, attempt * 100, 100)
            if not batch: break
            for c in clean_candles(batch):
                if c["time"] not in seen: seen[c["time"]] = c
            if len(seen) >= target: break
            await asyncio.sleep(0.1)
        except: break
    return sorted(seen.values(), key=lambda c: c["time"])

def ema_arr(data, period):
    arr = np.array(data, dtype=float); n = len(arr)
    period = max(1, min(period, n - 1)) if n > 1 else 1
    if n < 2: return arr.copy()
    out = np.zeros(n); out[period - 1] = np.mean(arr[:period]); k = 2.0 / (period + 1)
    for i in range(period, n): out[i] = arr[i] * k + out[i - 1] * (1 - k)
    return out

def calc_rsi(closes, period=14):
    arr = np.array(closes, dtype=float); n = len(arr)
    if n < 6: return 50.0
    p = min(period, n - 1); w = arr[-p * 4:] if n >= p * 4 else arr; d = np.diff(w)
    if len(d) == 0: return 50.0
    g = np.where(d > 0, d, 0.0); l = np.where(d < 0, -d, 0.0)
    pg = min(p, len(g)); ag = np.mean(g[:pg]); al = np.mean(l[:pg])
    for i in range(pg, len(g)): ag = (ag * (pg - 1) + g[i]) / pg; al = (al * (pg - 1) + l[i]) / pg
    return round(100 - 100 / (1 + ag / al), 2) if al > 0 else 100.0

def calc_macd(closes):
    if len(closes) < 35: return None, None, None
    arr = np.array(closes, dtype=float)
    ml = ema_arr(arr, 12) - ema_arr(arr, 26); sg = ema_arr(ml, 9); ht = ml - sg
    s = max(0, min(35, len(ml) - 5)); return ml[s:], sg[s:], ht[s:]

def calc_stoch(clist, kp=14, sm=3):
    n = len(clist)
    if n < 6: return 50.0, 50.0
    kv = []
    for i in range(min(kp, n - 1), n):
        sl = clist[max(0, i - kp + 1):i + 1]; h = max(x["high"] for x in sl); lo = min(x["low"] for x in sl)
        kv.append(100 * (clist[i]["close"] - lo) / (h - lo) if h != lo else 50.0)
    if not kv: return 50.0, 50.0
    d = float(np.mean(kv[-sm:])) if len(kv) >= sm else float(np.mean(kv))
    return round(kv[-1], 2), round(d, 2)

def calc_bb(closes, period=20, mult=2.0):
    if len(closes) < 10: return None, None, None
    arr = np.array(closes[-min(period, len(closes)):], dtype=float)
    mid = float(np.mean(arr)); sd = float(np.std(arr))
    if sd == 0: return mid * 0.998, mid, mid * 1.002
    return mid - mult * sd, mid, mid + mult * sd

def calc_atr(clist, period=14):
    if len(clist) < 3: return 0.001
    c = clist[-min(period * 2, len(clist)):]
    trs = [max(c[i]["high"] - c[i]["low"], abs(c[i]["high"] - c[i - 1]["close"]), abs(c[i]["low"] - c[i - 1]["close"])) for i in range(1, len(c))]
    return float(np.mean(trs)) if trs else 0.001

def calc_adx(clist, period=14):
    if len(clist) < 16: return 15.0
    c = clist[-min(60, len(clist)):]
    pdm, mdm, trl = [], [], []
    for i in range(1, len(c)):
        h, lo, ph, pl, pc = c[i]["high"], c[i]["low"], c[i - 1]["high"], c[i - 1]["low"], c[i - 1]["close"]
        trl.append(max(h - lo, abs(h - pc), abs(lo - pc))); up = h - ph; dn = pl - lo
        pdm.append(up if up > dn and up > 0 else 0); mdm.append(dn if dn > up and dn > 0 else 0)
    def wld(a, p):
        p = min(p, len(a))
        if p == 0: return [0]
        s = sum(a[:p]); o = [s]
        for v in a[p:]: s = s - s / p + v; o.append(s)
        return o
    at, pd, md = wld(trl, period), wld(pdm, period), wld(mdm, period); dx = []
    for a, p, m in zip(at, pd, md):
        if a == 0: dx.append(0); continue
        pi, mi = 100 * p / a, 100 * m / a; s = pi + mi
        dx.append(100 * abs(pi - mi) / s if s else 0)
    return round(float(np.mean(dx[-10:])), 2) if len(dx) >= 10 else 15.0

def calc_williams_r(clist, period=14):
    if len(clist) < period: return -50.0
    sl = clist[-period:]; h = max(x["high"] for x in sl); l = min(x["low"] for x in sl)
    return round((h - clist[-1]["close"]) / (h - l) * -100, 2) if h != l else -50.0

def calc_cci(clist, period=20):
    if len(clist) < period: return 0.0
    sl = clist[-period:]; tp = [(x["high"] + x["low"] + x["close"]) / 3 for x in sl]
    avg = np.mean(tp); mad = np.mean([abs(x - avg) for x in tp])
    return round((tp[-1] - avg) / (0.015 * mad), 2) if mad else 0.0

def find_pivots(clist, w=4):
    hs, ls, n = [c["high"] for c in clist], [c["low"] for c in clist], len(clist)
    pk, tr = [], []
    for i in range(w, n - w):
        if all(hs[i] >= hs[i - j] for j in range(1, w + 1)) and all(hs[i] >= hs[i + j] for j in range(1, w + 1)): pk.append((i, hs[i]))
        if all(ls[i] <= ls[i - j] for j in range(1, w + 1)) and all(ls[i] <= ls[i + j] for j in range(1, w + 1)): tr.append((i, ls[i]))
    return pk, tr

def calc_sr(clist):
    pk, tr = find_pivots(clist, 4); cur = clist[-1]["close"]
    nr = min(p[1] for p in pk[-8:] if p[1] > cur) if any(p[1] > cur for p in pk[-8:]) else cur * 1.005
    ns = max(t[1] for t in tr[-8:] if t[1] < cur) if any(t[1] < cur for t in tr[-8:]) else cur * 0.995
    ds = round((cur - ns) / cur * 100, 4) if cur else 0
    dr = round((nr - cur) / cur * 100, 4) if cur else 0
    return round(ns, 6), round(nr, 6), ds, dr

def trend_score(clist):
    if len(clist) < 25: return 0
    pk, tr = find_pivots(clist, 3); s = 0
    if len(pk) >= 2: s += 2 if pk[-1][1] > pk[-2][1] * 1.0002 else (-2 if pk[-1][1] < pk[-2][1] * 0.9998 else 0)
    if len(tr) >= 2: s += 2 if tr[-1][1] > tr[-2][1] * 1.0002 else (-2 if tr[-1][1] < tr[-2][1] * 0.9998 else 0)
    return s

def candle_patterns(clist):
    v = 0
    if len(clist) < 4: return v
    atr = calc_atr(clist, 14); bt = atr * 0.2
    bd = lambda c: abs(c["close"] - c["open"])
    su = lambda c: c["high"] - max(c["close"], c["open"])
    sl = lambda c: min(c["close"], c["open"]) - c["low"]
    L = clist[-1]
    if sl(L) > bd(L) * 2.2 and su(L) < bd(L) * 0.4 and bd(L) > bt: v += 3
    if su(L) > bd(L) * 2.2 and sl(L) < bd(L) * 0.4 and bd(L) > bt: v -= 3
    if len(clist) >= 2:
        P, C = clist[-2], clist[-1]
        if P["close"] < P["open"] and C["close"] > C["open"] and C["open"] < P["close"] and C["close"] > P["open"] and bd(C) > bd(P) * 1.1: v += 4
        if P["close"] > P["open"] and C["close"] < C["open"] and C["open"] > P["close"] and C["close"] < P["open"] and bd(C) > bd(P) * 1.1: v -= 4
    return v

def detect_div(clist, rsi):
    if len(clist) < 30: return 0
    n = min(40, len(clist)); pr = [c["close"] for c in clist[-n:]]; h = n // 2
    pe, pl, re = np.mean(pr[:h]), np.mean(pr[h:]), calc_rsi(pr[:h])
    if pl > pe * 1.001 and rsi < re - 6: return -3
    if pl < pe * 0.999 and rsi > re + 6: return +3
    return 0

def analyze(clist):
    closes = [c["close"] for c in clist]; n = len(closes)
    res = {"signal": None, "score": 0, "gate1": 0, "gate2": 0, "gate3": 0, "reasons": [], "entry_type": "", "expiry_minutes": 2, "entry_method": "انتظار", "no_signal": ""}
    g1 = 0
    if n >= 12:
        arr = np.array(closes, dtype=float)
        e9, e21, e50 = ema_arr(arr, min(9, n-1)), ema_arr(arr, min(21, n-1)), ema_arr(arr, min(50, n-1))
        if e9[-1] > e21[-1] > e50[-1]: g1 += 3
        elif e9[-1] < e21[-1] < e50[-1]: g1 -= 3
        elif e9[-1] > e21[-1]: g1 += 1
        elif e9[-1] < e21[-1]: g1 -= 1
        if n >= 10:
            sl2 = (e9[-1] - e9[-6]) / abs(e9[-6]) * 100 if e9[-6] != 0 else 0
            if sl2 > 0.03: g1 += 1
            elif sl2 < -0.03: g1 -= 1
    g1 += trend_score(clist); adx = calc_adx(clist); res["gate1"] = g1
    g2 = 0; rsi = calc_rsi(closes)
    if rsi < 25: g2 += 4
    elif rsi < 35: g2 += 3
    elif rsi < 42: g2 += 2
    elif rsi > 75: g2 -= 4
    elif rsi > 65: g2 -= 3
    elif rsi > 58: g2 -= 2
    sk, _ = calc_stoch(clist)
    if sk < 15: g2 += 4
    elif sk < 30: g2 += 2
    elif sk > 85: g2 -= 4
    elif sk > 70: g2 -= 2
    ml, sg, ht = calc_macd(closes)
    if ml is not None and len(ml) >= 3:
        if ml[-2] <= sg[-2] and ml[-1] > sg[-1]: g2 += 4
        elif ml[-2] >= sg[-2] and ml[-1] < sg[-1]: g2 -= 4
        elif ml[-1] > sg[-1]: g2 += 1
        else: g2 -= 1
    wr = calc_williams_r(clist)
    if wr < -82: g2 += 3
    elif wr > -18: g2 -= 3
    cci = calc_cci(clist)
    if cci < -130: g2 += 2
    elif cci > 130: g2 -= 2
    g2 += detect_div(clist, rsi); res["gate2"] = g2
    g3 = 0; cp = closes[-1]
    bb_lo, bb_mid, bb_hi = calc_bb(closes)
    if bb_mid:
        if cp < bb_lo: g3 += 4
        elif cp < bb_lo * 1.001: g3 += 3
        elif cp > bb_hi: g3 -= 4
        elif cp > bb_hi * 0.999: g3 -= 3
    try:
        _, _, ds, dr = calc_sr(clist)
        if ds < 0.12: g3 += 4
        elif ds < 0.25: g3 += 3
        if dr < 0.12: g3 -= 4
        elif dr < 0.25: g3 -= 3
    except: pass
    g3 += candle_patterns(clist); res["gate3"] = g3
    def gd(v, t=2): return 1 if v >= t else (-1 if v <= -t else 0)
    d1, d2, d3 = gd(g1), gd(g2), gd(g3)
    gs = [d for d in [d1, d2, d3] if d != 0]; ca = sum(1 for d in gs if d > 0); pu = sum(1 for d in gs if d < 0)
    if ca >= 2: dir2, agr = "call", ca
    elif pu >= 2: dir2, agr = "put", pu
    else: res["no_signal"] = "توافق غير كافي"; return res
    ds2 = 1 if dir2 == "call" else -1
    base = 70 if agr >= 3 else (64 if agr == 2 and adx >= 20 else 60)
    conf = int(min(96, base + min(10, max(0, g1 * ds2 * 1.2)) + min(12, max(0, g2 * ds2)) + min(10, max(0, g3 * ds2 * 1.2)) + (4 if adx >= 28 else 2 if adx >= 20 else 0)))
    et = "GOLD" if agr >= 3 else ("SILVER" if agr == 2 else "BRONZE")
    em = 2 if agr >= 3 else 3
    co = clist[-1]["open"]
    meth = "انتظار إغلاق الشمعة"
    if dir2 == "call" and cp < co: meth = "دخول فوري"
    elif dir2 == "put" and cp > co: meth = "دخول فوري"
    stren = "استثنائية" if conf >= 85 else ("قوية جداً" if conf >= 75 else ("قوية" if conf >= 65 else "جيدة"))
    res.update({"signal": dir2, "score": conf, "strength": stren, "entry_type": et, "expiry_minutes": em, "expiry_seconds": em * 60, "entry_method": meth, "agreeing_gates": agr})
    return res

def demo_candles(count=250):
    rng = random.Random(int(time.time() * 1000) % 9999999); price = 1.0 + rng.random() * 50; bv = 0.0005
    segs = [('up', 25, 2.0), ('down', 20, 1.5), ('up', 30, 2.5), ('sideways', 15, 1.0), ('down', 25, 2.0), ('up', 20, 1.8)]
    out = []; si = 0; sp = 0
    for i in range(count):
        while si < len(segs) - 1 and sp >= segs[si][1]: si += 1; sp = 0
        t, _, s = segs[si]; v = bv * s
        tr = v * 0.35 * (1 if t == 'up' else -1 if t == 'down' else 0); ns = v * (0.6 if t != 'sideways' else 0.3)
        ch = tr + (rng.random() - 0.5) * ns * 2; op = price; price += ch
        out.append({"open": op, "close": price, "high": max(op, price) + rng.random() * v * 0.2, "low": min(op, price) - rng.random() * v * 0.2, "time": int(time.time()) - count + i}); sp += 1
    return out

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
        a = analyze(clist); now = datetime.now(); em = a.get("expiry_minutes", 2)
        secs = 60 - now.second; et = datetime.fromtimestamp(now.timestamp() + secs).strftime("%H:%M:%S")
        score = a.get("score", 0); has = a.get("signal") is not None
        data = {"asset": asset_id, "asset_name": info["name"], "asset_cat": info["cat"], "time": now.strftime("%H:%M:%S"), "signal": a.get("signal"), "score": score, "strength": a.get("strength", ""), "reasons": a.get("reasons", []), "gate1": a.get("gate1", 0), "gate2": a.get("gate2", 0), "gate3": a.get("gate3", 0), "entry_type": a.get("entry_type", ""), "expiry_minutes": em, "expiry_seconds": em * 60, "entry_time": et, "seconds_to_entry": secs, "last_price": round(clist[-1]["close"], 6), "mode": mode, "has_signal": has, "strong_signal": has and score >= 75, "no_signal_reason": a.get("no_signal", ""), "trade_status": "signal_only", "entry_method": a.get("entry_method", "انتظار"), "agreeing_gates": a.get("agreeing_gates", 0)}
        signals_db[asset_id] = data
        return data
    except Exception as e: return {"asset": asset_id, "error": str(e)}

def scan_loop_thread():
    while True:
        time.sleep(2)
        if not scan_state["active"]: continue
        assets = scan_state.get("selected_assets", [])
        if not assets: continue
        print("[" + datetime.now().strftime("%H:%M:%S") + "] مسح " + str(len(assets)) + " زوج...")
        for aid in assets:
            if not scan_state["active"]: break
            try: analyze_asset_sync(aid)
            except: pass
            time.sleep(0.15)
        print("[" + datetime.now().strftime("%H:%M:%S") + "] انتهى المسح")
        for _ in range(25):
            if not scan_state["active"]: break
            time.sleep(1)

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
    except ImportError: bot_status["error"] = "pyquotex غير مثبت"; print("[DEMO] وضع تجريبي")
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
#  HTTP Server — يعمل في Main Thread
# ═══════════════════════════════════════════
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Accept")
        self.send_header("Access-Control-Max-Age", "3600")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._cors()
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        # ─── صفحة الويب ───
        if path == "/" or path == "/tokyo52.html" or path == "/index.html":
            html = None
            sd = os.path.dirname(os.path.abspath(__file__))
            search_dirs = [sd, os.getcwd(), os.path.join(sd, '..'), os.path.expanduser('~')]
            
            for fn in ["tokyo52.html", "index.html", "bot_macd.html"]:
                for d in search_dirs:
                    if not os.path.isdir(d): continue
                    fp = os.path.join(d, fn)
                    if os.path.isfile(fp):
                        try:
                            with open(fp, "r", encoding="utf-8") as f:
                                html = f.read()
                            print(f"[HTML] وجدت: {fp}")
                            break
                        except Exception as e:
                            print(f"[ERROR] خطأ في قراءة {fp}: {e}")
                if html: break

            if html:
                # استبدال رابط API
                html = html.replace("const API='http://localhost:8765'", "const API=''")
                html = html.replace("const API = 'http://localhost:8765'", "const API = ''")
                html = html.replace('const API="http://localhost:8765"', 'const API=""')
                b = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._cors()
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            else:
                error_html = f"""
                <html dir='rtl' lang='ar'>
                <head><meta charset='utf-8'></head>
                <body style='background:#050508;color:#ff3366;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;direction:rtl'>
                <div style='text-align:center;max-width:500px;padding:20px'>
                    <h1 style='color:#00ff41'>TOKYO 52</h1>
                    <p style='color:#ff6b6b;font-size:16px;margin:20px 0'>❌ لم أجد ملف tokyo52.html</p>
                    <p style='color:#888;font-size:14px;line-height:1.8'>
                        اسم الملف يجب أن يكون: <code style='background:#111;padding:4px 8px'>tokyo52.html</code><br>
                        المسارات المطلوبة:<br>
                        - {sd}<br>
                        - {os.getcwd()}<br>
                        - {os.path.join(sd, '..')}<br>
                        <br>
                        ضع ملف HTML في أي من المسارات السابقة وأعد تحميل الصفحة
                    </p>
                    <script>
                        // محاولة تحديث كل 2 ثانية
                        setTimeout(() => location.reload(), 2000);
                    </script>
                </div>
                </body>
                </html>
                """.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._cors()
                self.end_headers()
                self.wfile.write(error_html)
            return

        # ─── API Endpoints ───
        try:
            if path == "/status":
                self._json(bot_status)
            elif path == "/assets":
                self._json({"assets": ASSETS})
            elif path == "/signals":
                self._json({"signals": list(signals_db.values())})
            elif path == "/trade_log":
                self._json({"trades": trade_log})
            else:
                self._json({"error": "404 Not Found"}, 404)
        except Exception as e:
            print(f"[API ERROR] {path}: {e}")
            self._json({"error": str(e)}, 500)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            cl = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(cl).decode("utf-8")) if cl > 0 else {}

            if path == "/start":
                scan_state["selected_assets"] = [a for a in body.get("assets", []) if a in ASSET_IDS]
                scan_state["auto_trade"] = body.get("auto_trade", False)
                scan_state["trade_amount"] = body.get("amount", 1.0)
                scan_state["active"] = True
                print(f"[SCAN] بدء مسح {len(scan_state['selected_assets'])} زوج")
                self._json({"status": "started", "count": len(scan_state["selected_assets"])})

            elif path == "/stop":
                scan_state["active"] = False
                print("[SCAN] إيقاف المسح")
                self._json({"status": "stopped"})

            elif path == "/auto_trade":
                scan_state["auto_trade"] = body.get("enabled", False)
                print(f"[AUTO_TRADE] {'تفعيل' if scan_state['auto_trade'] else 'تعطيل'}")
                self._json({"auto_trade": scan_state["auto_trade"]})

            elif path == "/switch_account":
                at = body.get("type", "PRACTICE")
                if bg_loop:
                    future = asyncio.run_coroutine_threadsafe(switch_account_async(at), bg_loop)
                    ok, msg = future.result(timeout=5)
                    print(f"[ACCOUNT] تبديل إلى {at}: {msg}")
                    self._json({"success": ok, "message": msg, "account_type": at})
                else:
                    self._json({"success": False, "message": "لا يوجد اتصال"})

            else:
                self._json({"error": "404"}, 404)

        except Exception as e:
            print(f"[POST ERROR] {path}: {e}")
            self._json({"error": str(e)}, 500)

    def _json(self, data, code=200):
        try:
            b = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        except Exception as e:
            print(f"[JSON ERROR] {e}")

# ═══ التشغيل ═══
if __name__ == "__main__":
    print("=" * 50)
    print("  TOKYO 52 — v6.2 FIXED")
    print("  http://localhost:" + str(PORT))
    print("=" * 50)

    # تشغيل bg_loop في thread منفصل
    t1 = threading.Thread(target=run_bg_loop, daemon=True)
    t1.start()
    time.sleep(1)

    # تشغيل حلقة المسح في thread منفصل
    t2 = threading.Thread(target=scan_loop_thread, daemon=True)
    t2.start()

    # تشغيل HTTP server في الـ main thread
    try:
        srv = HTTPServer(("0.0.0.0", PORT), H)
        print(f"[OK] السيرفر يعمل — افتح: http://localhost:{PORT}")
        print("=" * 50)
        srv.serve_forever()
    except OSError as e:
        print(f"[ERR] المنفذ {PORT} مستخدم!")
        print("اكتب في الكونسول: netstat -ano | findstr 8765")
        print("ثم أغلق البرنامج الذي يستخدم المنفذ")
    except KeyboardInterrupt:
        print("\nايقاف")
