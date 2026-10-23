const fs=require("fs"); const s=fs.readFileSync("index.html","utf8");
const i=s.indexOf("const D=");let j=s.indexOf("{",i),dep=0,fim=0;
for(let k=j;k<s.length;k++){if(s[k]==="{")dep++;else if(s[k]==="}"){dep--;if(dep===0){fim=k+1;break;}}}
const D=JSON.parse(s.slice(j,fim));
const mRE=s.match(/RE_NAOOP\s*=\s*(\/[^\n]*?\/[a-z]*);/), mDB=s.match(/function dbucket\(t,g,c,cat\)\{[\s\S]*?\n\}/);
globalThis.RE_NAOOP=eval(mRE[1]); eval("globalThis.dbucket="+mDB[0].replace("function dbucket","function"));
const R2=v=>Math.round((v||0)*100)/100;
function casc(e,m){const T=(D.entities[e].dre||{})[m]||{};const b={};
  for(const t in T)for(const g in T[t])for(const c in T[t][g])for(const x of T[t][g][c]){const k=dbucket(t,g,c,x.cat);b[k]=R2((b[k]||0)+x.v);}
  const G=k=>R2(b[k]||0);
  const rl=R2(G("receita")+G("deducoes")), lb=R2(rl+G("custos")+G("pessoaldir"));
  const eb=R2(lb+G("comercial")+G("admin")+G("pessoal")), rf=R2(G("recfin")+G("despfin"));
  const res=R2(Object.values(b).reduce((a,v)=>a+v,0));
  return {rb:G("receita"),ded:G("deducoes"),rl,cus:G("custos"),pdir:G("pessoaldir"),lb,
          com:G("comercial"),adm:G("admin"),pind:G("pessoal"),eb,rf,ll:R2(eb+rf),
          inv:G("investimentos"),recnop:G("recnaoop"),nop:R2(G("naoop")+G("emprestimo")),res};}
function linhas(e,m,co){const T=(D.entities[e].dre||{})[m]||{};const o=[];
  for(const t in T)for(const g in T[t])for(const c in T[t][g])for(const x of T[t][g][c]) o.push({t,g,c,cat:x.cat,v:x.v});
  return o;}
const out={casc:{},linhas:{},contas:{},com:D.com,orc:D.orc,resumo:D.resumo};
for(const e of ["amana","topazio","consol"]) for(const m of ["8","9","T"]) out.casc[e+"_"+m]=casc(e,m);
for(const e of ["amana","topazio","consol"]) out.linhas[e+"_9"]=linhas(e,"9");
for(const e of ["amana","topazio","consol"]) out.linhas[e+"_8"]=linhas(e,"8");
for(const e of ["amana","topazio","consol"]) out.contas[e]=((D.entities[e].dfc||{})["9"]||{}).contas||[];
for(const e of ["amana","topazio","consol"]) out["dfc_"+e]=Object.fromEntries(["8","9"].map(m=>[m,{res:(D.entities[e].dfc[m]||{}).resultado,si:(D.entities[e].dfc[m]||{}).saldo_inicial,ac:(D.entities[e].dfc[m]||{}).acumulado}]));
fs.writeFileSync("/Users/joaoandrade/painel-amanatopazio/dre/dados_rel.json",JSON.stringify(out));
console.log("consol set:",JSON.stringify(out.casc.consol_9));
console.log("consol ago:",JSON.stringify(out.casc.consol_8));
console.log("amana set:",JSON.stringify(out.casc.amana_9));
console.log("topazio set:",JSON.stringify(out.casc.topazio_9));
