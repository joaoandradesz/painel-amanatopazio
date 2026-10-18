# -*- coding: utf-8 -*-
"""Reconstroi o retrato de uma data passada, para o de-para ter com o que
comparar ja na primeira rodada. Um titulo entrava no retrato daquela data se
ja existia nela (data_registro/emissao <= corte) e vencia nos 15 dias
seguintes. E o mesmo criterio do backtest."""
import sys,os,json,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from coleta_dash import EMP,nomes,titulos
import historia
R2=lambda v: round((v or 0)+0.0,2)
dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()
def existia(t,corte):
    for k in ("data_registro","data_emissao","data_entrada"):
        v=t.get(k)
        if v and len(v)==10:
            try:
                if dt(v)<=corte: return True
            except Exception: pass
    return False
if __name__=="__main__":
    CORTE=dt(sys.argv[1]); FIM=CORTE+datetime.timedelta(days=15)
    SALDO=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
    foto={"data":CORTE.strftime("%d/%m/%Y"),"gerado":"reconstruído em %s"%datetime.date.today().strftime("%d/%m/%Y"),
          "reconstruido":True,"ents":{}}
    for emp,cfg in EMP.items():
        NM=nomes(emp); itens=[]
        for lado,ep,cn,raiz in (("receber","financas/contareceber","ListarContasReceber","conta_receber_cadastro"),
                                ("pagar","financas/contapagar","ListarContasPagar","conta_pagar_cadastro")):
            for t in titulos(emp,ep,cn,raiz):
                v=t.get("data_vencimento") or ""
                if len(v)!=10: continue
                try: d=dt(v)
                except Exception: continue
                if not (CORTE<d<=FIM): continue
                if (t.get("status_titulo") or "").upper()=="CANCELADO": continue
                if not existia(t,CORTE): continue
                itens.append({"id":t.get("codigo_lancamento_omie"),"lado":lado,"d":v,
                              "v":R2(t.get("valor_documento")),"nome":NM.get(t.get("codigo_cliente_fornecedor"),"—")})
        foto["ents"][emp]={"saldo":R2(SALDO.get(emp,sum(cfg["ancora"].values()))),"itens":itens}
        print("  %-8s %d titulos no retrato de %s"%(emp,len(itens),CORTE.strftime("%d/%m")))
    os.makedirs(historia.HIST,exist_ok=True)
    p=os.path.join(historia.HIST,CORTE.strftime("%Y-%m-%d")+".json")
    json.dump(foto,open(p,"w",encoding="utf-8"),ensure_ascii=False)
    print("gravado",p)
