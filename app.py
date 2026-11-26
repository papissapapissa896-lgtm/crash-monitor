from flask import Flask, jsonify, request, render_template_string
import sqlite3, os, time

app = Flask(__name__)
DB_PATH = os.getenv('DB_PATH', 'crash_rounds.db')

HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crash Monitor</title>
<style>*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e7eefb;font-family:system-ui,-apple-system,Segoe UI,sans-serif}header{padding:22px 18px;background:#111b2d;border-bottom:1px solid #24344b}h1{font-size:22px;margin:0}small{color:#9eb1cb}.wrap{max-width:900px;margin:auto;padding:16px}.status{padding:14px;border-radius:12px;background:#17243a;margin-bottom:14px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.card{background:#131e31;border:1px solid #26374f;border-radius:14px;padding:16px}.num{font-size:26px;font-weight:700;margin-top:6px}.tablewrap{overflow:auto;margin-top:14px}table{width:100%;border-collapse:collapse;min-width:380px}th,td{text-align:left;padding:11px;border-bottom:1px solid #26374f}th{color:#9eb1cb;font-size:12px}input,button{font:inherit;border-radius:9px;padding:10px;border:1px solid #344963;background:#0e1726;color:#e7eefb;width:100%;margin:5px 0}button{background:#3478f6;border:0;font-weight:600}.form{display:grid;grid-template-columns:1fr 1fr;gap:8px}.notice{color:#ffc86b;font-size:13px;line-height:1.5;margin-top:12px}@media(max-width:480px){.grid{grid-template-columns:1fr}.form{grid-template-columns:1fr}}
</style></head><body><header><h1>Crash Monitor</h1><small>Round history and basic statistics</small></header><main class="wrap"><div class="status" id="status">Checking data source…</div><div class="grid"><div class="card"><small>Rounds stored</small><div class="num" id="total">—</div></div><div class="card"><small>Latest multiplier</small><div class="num" id="latest">—</div></div><div class="card"><small>Average (stored)</small><div class="num" id="avg">—</div></div><div class="card"><small>Highest (stored)</small><div class="num" id="high">—</div></div></div><div class="card" style="margin-top:14px"><b>Add round manually</b><p><small>This is only for manually entered data until a verified live source is connected.</small></p><form class="form" id="add"><input id="mult" type="number" step="0.01" min="1" placeholder="Multiplier (e.g. 2.35)" required><input id="note" placeholder="Optional note"><button type="submit" style="grid-column:1/-1">Save round</button></form></div><div class="card tablewrap"><b>Recent rounds</b><table><thead><tr><th>Time</th><th>Multiplier</th><th>Note</th></tr></thead><tbody id="rows"></tbody></table></div><p class="notice">This dashboard does not predict the next crash multiplier. Live 1xBet data is not connected or verified in this starter package. Do not treat statistics as betting advice.</p></main><script>
async function refresh(){try{const r=await fetch('/api/stats');const d=await r.json();document.getElementById('status').textContent=d.feed_status;document.getElementById('total').textContent=d.count;document.getElementById('latest').textContent=d.latest==null?'—':d.latest.toFixed(2)+'x';document.getElementById('avg').textContent=d.average==null?'—':d.average.toFixed(2)+'x';document.getElementById('high').textContent=d.highest==null?'—':d.highest.toFixed(2)+'x';document.getElementById('rows').innerHTML=d.rounds.map(x=>`<tr><td>${new Date(x.created_at*1000).toLocaleString()}</td><td><b>${Number(x.multiplier).toFixed(2)}x</b></td><td>${(x.note||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}</td></tr>`).join('')}catch(e){document.getElementById('status').textContent='Dashboard API error: '+e}}
document.getElementById('add').addEventListener('submit',async e=>{e.preventDefault();const multiplier=Number(document.getElementById('mult').value);const note=document.getElementById('note').value;const r=await fetch('/api/rounds',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({multiplier,note})});if(r.ok){document.getElementById('mult').value='';document.getElementById('note').value='';refresh()}else alert('Could not save round. Check multiplier value.')});refresh();setInterval(refresh,10000);
</script></body></html>'''

def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS rounds (id INTEGER PRIMARY KEY AUTOINCREMENT, multiplier REAL NOT NULL, note TEXT DEFAULT "", created_at INTEGER NOT NULL)')

@app.get('/')
def home():
    return render_template_string(HTML)


@app.get('/api/health')
def health():
    return jsonify(status='ok', live_feed='not_connected', message='App is running; verified live feed is not configured.')

@app.get('/api/stats')
def stats():
    with db() as c:
        rows = c.execute('SELECT multiplier,note,created_at FROM rounds ORDER BY id DESC LIMIT 100').fetchall()
        count = c.execute('SELECT COUNT(*) FROM rounds').fetchone()[0]
        vals = [float(x['multiplier']) for x in rows]
    return jsonify(count=count, latest=vals[0] if vals else None, average=(sum(vals)/len(vals)) if vals else None, highest=max(vals) if vals else None, rounds=[dict(x) for x in rows], feed_status='⚠️ App running — verified live 1xBet feed is not connected')

@app.post('/api/rounds')
def add_round():
    data = request.get_json(silent=True) or {}
    try:
        m = float(data.get('multiplier'))
        if not (m >= 1 and m < 1000000): return jsonify(error='Multiplier must be >= 1'), 400
    except (TypeError, ValueError):
        return jsonify(error='Invalid multiplier'), 400
    note = str(data.get('note',''))[:200]
    with db() as c:
        c.execute('INSERT INTO rounds(multiplier,note,created_at) VALUES(?,?,?)',(m,note,int(time.time())))
    return jsonify(ok=True), 201


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
