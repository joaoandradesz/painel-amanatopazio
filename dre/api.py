# -*- coding: utf-8 -*-
"""Helper do Omie. Credenciais em ~/.omie_<empresa>.json (600), fora do repositorio."""
import json,urllib.request,ssl,os,re,time
CTX=ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
CRED={}
for _e in ("amana","topazio"):
    _p=os.path.expanduser("~/.omie_%s.json"%_e)
    if os.path.exists(_p): CRED[_e]=json.load(open(_p))
def _call(emp,ep,cn,param):
    c=CRED[emp]
    body=json.dumps({"call":cn,"app_key":c["app_key"],"app_secret":c["app_secret"],"param":[param]}).encode()
    req=urllib.request.Request("https://app.omie.com.br/api/v1/%s/"%ep,data=body,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=120,context=CTX) as r: return json.load(r)
    except urllib.error.HTTPError as e: raise RuntimeError(e.read().decode()[:200])
def call(emp,ep,cn,param,tent=6):
    for i in range(tent):
        try: return _call(emp,ep,cn,param)
        except RuntimeError as e:
            m=re.search(r"Aguarde (\d+) segundos",str(e))
            if not m: raise
            time.sleep(int(m.group(1))+3)
    raise RuntimeError("bloqueio persistente")
