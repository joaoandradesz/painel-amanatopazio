# -*- coding: utf-8 -*-
"""Previsto x realizado entre duas rodadas.

A cada rodada guardamos um retrato em caixa/historico/AAAA-MM-DD.json: saldo e
a lista de titulos em aberto da janela, com codigo. Na rodada seguinte, cada
titulo daquele retrato tem um desfecho:

  aconteceu       foi pago/recebido ate hoje
  escorregou      continua em aberto, a data ja passou
  ainda em pe     continua em aberto, mas so vence depois
  valor mudou     foi liquidado por valor diferente do previsto
  sumiu           cancelado ou excluido

E o que NAO estava no retrato e foi liquidado no periodo e 'surpresa' -- o
lancamento que entrou depois. E o indicador que mede a disciplina.
"""
import os,json,datetime
AQUI=os.path.dirname(os.path.abspath(__file__)); HIST=os.path.join(AQUI,"historico")
R2=lambda v: round((v or 0)+0.0,2)
dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()

def salva(D):
    os.makedirs(HIST,exist_ok=True)
    hoje=dt(D["hoje"])
    fim15=(hoje+datetime.timedelta(days=15)).strftime("%d/%m/%Y")
    foto={"data":D["hoje"],"gerado":D["gerado"],"ents":{}}
    for e,x in D["ents"].items():
        foto["ents"][e]={"saldo":R2(sum(c["hoje"] for c in x["contas"])),
            "itens":[{"id":i["id"],"lado":i["lado"],"d":i["d"],"v":i["v"],"nome":i["nome"]}
                     for i in x["itens"] if dt(i["d"])<=dt(fim15)]}
    p=os.path.join(HIST,hoje.strftime("%Y-%m-%d")+".json")
    json.dump(foto,open(p,"w",encoding="utf-8"),ensure_ascii=False)
    return os.path.basename(p)

def anterior(hoje):
    if not os.path.isdir(HIST): return None
    fs=sorted(f for f in os.listdir(HIST) if f.endswith(".json") and f[:10]<hoje.strftime("%Y-%m-%d"))
    return json.load(open(os.path.join(HIST,fs[-1]),encoding="utf-8")) if fs else None

def compara(D):
    """Compara o retrato anterior com o estado de hoje."""
    hoje=dt(D["hoje"]); ant=anterior(hoje)
    if not ant: return None
    ini=dt(ant["data"]); out={"de":ant["data"],"ate":D["hoje"],
        "dias":(hoje-ini).days,"ents":{}}
    for e,x in D["ents"].items():
        velho=(ant["ents"].get(e) or {}).get("itens") or []
        # em aberto = o que ainda vence + o que venceu e nao foi pago
        abertos=set(i["id"] for i in x["itens"])|set((x.get("atrasados") or {}).get("ids") or [])
        desf=x.get("desfecho") or {}
        L={"aconteceu":[],"escorregou":[],"em_pe":[],"mudou":[],"sumiu":[],"surpresa":[]}
        previstos=set()
        for i in velho:
            if dt(i["d"])>hoje: 
                L["em_pe"].append(i); continue      # so vence depois, nao da para cobrar ainda
            previstos.add(i["id"])
            d=desf.get(str(i["id"])) or desf.get(i["id"])
            if d:
                if abs(R2(d["v"])-R2(i["v"]))>0.004:
                    L["mudou"].append({**i,"real":R2(d["v"])})
                else: L["aconteceu"].append(i)
            elif i["id"] in abertos: L["escorregou"].append(i)
            else: L["sumiu"].append(i)
        for cod,d in desf.items():
            try: dd=dt(d["d"])
            except Exception: continue
            if ini<=dd<=hoje and int(cod) not in previstos:
                L["surpresa"].append({"id":cod,"d":d["d"],"v":d["v"],"st":d["st"],
                    "nome":d.get("nome","—"),"lado":d.get("lado","")})
        som=lambda k: R2(sum(y.get("real",y["v"]) for y in L[k]))
        out["ents"][e]={"nome":x["nome"],
            "saldo_ant":(ant["ents"].get(e) or {}).get("saldo"),
            "saldo_hoje":R2(sum(c["hoje"] for c in x["contas"])),
            "n":{k:len(v) for k,v in L.items()},
            "v":{k:som(k) for k in L},
            "listas":{k:sorted(v,key=lambda y:-y.get("real",y["v"]))[:12] for k,v in L.items()}}
        p=out["ents"][e]
        base=p["v"]["aconteceu"]+p["v"]["mudou"]+p["v"]["escorregou"]
        p["acerto"]=round((p["v"]["aconteceu"]+p["v"]["mudou"])/base*100,1) if base else None
        tot=p["v"]["aconteceu"]+p["v"]["mudou"]+p["v"]["surpresa"]
        p["cobertura"]=round((p["v"]["aconteceu"]+p["v"]["mudou"])/tot*100,1) if tot else None
    return out
