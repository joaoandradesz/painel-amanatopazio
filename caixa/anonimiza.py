# -*- coding: utf-8 -*-
"""Gera a versao de demonstracao: mesmos numeros, nomes ficticios.
Troca empresa, pessoas e fornecedores; mantem marcas genericas (bancos,
adquirentes, OTAs, tributos) porque elas nao identificam o cliente."""
import re,sys,os,json,hashlib,unicodedata
AQUI=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.dirname(AQUI)
EMPRESAS=[("AMANA EMPREENDIMENTOS TURISTICOS LTDA","HORIZONTE HOTELARIA LTDA"),
 ("POUSADA TOPAZIO BY AMANA","POUSADA MIRANTE BY HORIZONTE"),("POUSADA TOPAZIO LTDA","POUSADA MIRANTE LTDA"),
 ("Pousada Topázio","Pousada Mirante"),("POUSADA TOPAZIO","POUSADA MIRANTE"),
 ("Grupo Amana e Topázio","Grupo Horizonte e Mirante"),("Grupo Amana / Pousada Topázio","Grupo Horizonte / Pousada Mirante"),
 ("Grupo Amana","Grupo Horizonte"),("Amana · ","Horizonte · "),("Topázio · ","Mirante · "),
 ("Topázio","Mirante"),("TOPAZIO","MIRANTE"),("Topazio","Mirante"),
 ("Amana","Horizonte"),("AMANA","HORIZONTE"),("amana","horizonte"),("topazio","mirante")]
MANTER=["BANCO","SANTANDER","BRADESCO","GETNET","GET NET","BOOKING","EXPEDIA","DECOLAR","AIRBNB","IFOOD",
 "MERCADO PAGO","MERCADOPAGO","EBAZAR","INFINITE","INFINIT","RECEITA FEDERAL","SIMPLES NACIONAL","INSS","FGTS",
 "PREFEITURA","SECRETARIA","CAIXA ECONOMICA","VIVO","CLARO","TIM","OI ","ENERGISA","CELPE","COMPESA","CORREIOS",
 "GOOGLE","META","FACEBOOK","AMAZON","MICROSOFT","OMIE","MAPFRE","PORTO SEGURO","UBER","99","AZUL","GOL","LATAM",
 "CLIENTES DIVERSOS","CLIENTE CONSUMIDOR","SEM TOMADOR","CONSUMIDOR"]
PES=["Ana Beatriz Moraes","Carlos Eduardo Pires","Mariana Lopes Vieira","Rafael Queiroz Lima","Juliana Castro Nunes",
 "Bruno Almeida Rocha","Patrícia Ramos Dias","Felipe Tavares Mendes","Camila Duarte Freitas","Thiago Barreto Cunha",
 "Larissa Amorim Pinto","Gustavo Siqueira Melo","Renata Figueiredo Sá","Diego Martins Couto","Aline Peixoto Braga",
 "Marcelo Fontes Teixeira","Bianca Carvalho Reis","Leonardo Vasques Pinho","Tatiana Guedes Moura","Rodrigo Serra Pacheco",
 "Vanessa Aguiar Prado","Henrique Portela Rios","Sabrina Macedo Leal","Otávio Bastos Correia","Luciana Neves Barbosa"]
EMP=["Aurora Serviços Ltda","Vértice Comércio Ltda","Pedra Clara Distribuidora","Maré Alta Suprimentos Ltda",
 "Boa Vista Manutenção Ltda","Sol Nascente Insumos","Linha Azul Transportes Ltda","Casa Verde Lavanderia",
 "Ponto Norte Tecnologia","Vale Fundo Alimentos Ltda","Ilha Bela Amenidades","Costa Larga Logística Ltda",
 "Nova Era Consultoria","Céu Aberto Energia Ltda","Rota Firme Fretes"]
def chave(n): return int(hashlib.md5(unicodedata.normalize("NFKD",n).encode()).hexdigest()[:8],16)
def generico(n):
    u=n.upper()
    return any(m in u for m in MANTER)
def troca(n):
    if not n or len(n)<4: return n
    u=n.upper()
    if generico(u): return n
    emp=any(t in u for t in (" LTDA","S.A","S/A"," ME"," EIRELI","MEI","COMERCIO","COMÉRCIO","SERVICOS","SERVIÇOS",
            "INDUSTRIA","INDÚSTRIA","DISTRIBUID","TECNOLOGIA","CONSULTORIA","TRANSPORT","AGENCIA","AGÊNCIA","TURISMO"))
    L=EMP if emp else PES
    return L[chave(n)%len(L)]
def anonimiza(html,rotulo):
    i=html.index("const D=");j=html.index("{",i);dep=0
    for k in range(j,len(html)):
        if html[k]=="{":dep+=1
        elif html[k]=="}":
            dep-=1
            if dep==0: fim=k+1;break
    D=json.loads(html[j:fim]); vistos={}
    CH=("nome","p","f","cliente","fornecedor","razao","n")
    def walk(o,ch=None):
        if isinstance(o,dict): return {k:walk(v,k) for k,v in o.items()}
        if isinstance(o,list): return [walk(v,ch) for v in o]
        if isinstance(o,str) and ch in CH and len(o)>4:
            if o not in vistos: vistos[o]=troca(o)
            return vistos[o]
        return o
    D=walk(D)
    s=html[:j]+json.dumps(D,ensure_ascii=False)+html[fim:]
    for a,b in EMPRESAS: s=s.replace(a,b)
    for a,b in ((">amana<",">horizonte<"),(" amana "," horizonte ")," topazio ".__class__ and (" topazio "," mirante ")):
        s=s.replace(a,b)
    s=re.sub(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b","00.000.000/0001-00",s)
    s=re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b","000.000.000-00",s)
    faixa=('<div style="position:fixed;left:0;right:0;bottom:0;z-index:999;background:#0D0F1A;color:#fff;'
      'font-family:\'Plus Jakarta Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:.18em;'
      'text-align:center;padding:7px">DEMONSTRAÇÃO · EMPRESA FICTÍCIA · NÚMEROS REAIS, NOMES SUBSTITUÍDOS</div>')
    s=s.replace("</body>",faixa+"</body>")
    print("  %-14s %d nomes substituidos"%(rotulo,len(vistos)))
    return s
if __name__=="__main__":
    for ent,saida,rot in (("caixa.html","demo/caixa.html","dashboard de caixa"),
                          ("index.html","demo/painel.html","painel mensal")):
        src=open(os.path.join(RAIZ,ent),encoding="utf-8").read()
        open(os.path.join(RAIZ,saida),"w",encoding="utf-8").write(anonimiza(src,rot))
        print("     -> %s"%saida)
