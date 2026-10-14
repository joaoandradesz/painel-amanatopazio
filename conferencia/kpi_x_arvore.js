// A DRE desenha a arvore; os KPIs, os graficos e as matrizes leem D.resumo.
// Este teste usa o dbucket DA PROPRIA PAGINA para garantir que os dois contam
// a mesma coisa -- se divergirem, o numero de cima nao bate com a tabela.
const fs=require("fs"); const arq=process.argv[2]||"index.html";
const s=fs.readFileSync(arq,"utf8");
const i=s.indexOf("const D=");let j=s.indexOf("{",i),dep=0,fim=0;
for(let k=j;k<s.length;k++){if(s[k]==="{")dep++;else if(s[k]==="}"){dep--;if(dep===0){fim=k+1;break;}}}
const D=JSON.parse(s.slice(j,fim));
const mRE=s.match(/RE_NAOOP\s*=\s*(\/[^\n]*?\/[a-z]*);/), mDB=s.match(/function dbucket\(t,g,c,cat\)\{[\s\S]*?\n\}/);
globalThis.RE_NAOOP=eval(mRE[1]); eval("globalThis.dbucket="+mDB[0].replace("function dbucket","function"));
const EB=["receita","deducoes","comercial","custos","pessoaldir","pessoal","admin"];
const R2=v=>Math.round((v||0)*100)/100, f=v=>R2(v).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
let bad=0,tot=0;
for(const e of ["amana","topazio","consol"]){const ent=D.entities[e];
  for(const m of Object.keys(D.resumo[e])){ if(!ent.dre[m])continue; const b={};
    for(const t of Object.keys(ent.dre[m]))for(const g of Object.keys(ent.dre[m][t]))for(const c of Object.keys(ent.dre[m][t][g]))
      for(const x of ent.dre[m][t][g][c]){const k=dbucket(t,g,c,x.cat);b[k]=(b[k]||0)+x.v;}
    const eb=R2(EB.reduce((a,k)=>a+(b[k]||0),0)), rb=R2(b["receita"]||0); tot+=2;
    if(Math.abs(eb-R2(D.resumo[e][m].ebitda))>0.02){bad++;console.log("  EBITDA ",e,m,"arvore",f(eb),"x KPI",f(D.resumo[e][m].ebitda));}
    if(Math.abs(rb-R2(D.resumo[e][m].rb))>0.02){bad++;console.log("  RECEITA",e,m,"arvore",f(rb),"x KPI",f(D.resumo[e][m].rb));}}}
console.log(`${arq}: ${tot} comparacoes KPI x arvore, ${bad} divergencias`);
process.exit(bad?1:0);
