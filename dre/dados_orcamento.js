const fs=require("fs"); const s=fs.readFileSync("index.html","utf8");
const i=s.indexOf("const D=");let j=s.indexOf("{",i),dep=0,fim=0;
for(let k=j;k<s.length;k++){if(s[k]==="{")dep++;else if(s[k]==="}"){dep--;if(dep===0){fim=k+1;break;}}}
const D=JSON.parse(s.slice(j,fim));
const mRE=s.match(/RE_NAOOP\s*=\s*(\/[^\n]*?\/[a-z]*);/), mDB=s.match(/function dbucket\(t,g,c,cat\)\{[\s\S]*?\n\}/);
globalThis.RE_NAOOP=eval(mRE[1]); eval("globalThis.dbucket="+mDB[0].replace("function dbucket","function"));
const EB=["receita","deducoes","comercial","custos","pessoaldir","pessoal","admin"];
const R2=v=>Math.round((v||0)*100)/100,f=v=>R2(v).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
const meses=[1,2,3,4,5,6,7,8,9], R={};
for(const m of meses){const T=D.entities.consol.dre[String(m)]||{};
  for(const t in T)for(const g in T[t])for(const c in T[t][g])for(const x of T[t][g][c]){
    if(EB.indexOf(dbucket(t,g,c,x.cat))<0)continue; R[c]=R[c]||meses.map(()=>0); R[c][m-1]=R2(R[c][m-1]+x.v);}}
const L=D.orc.linhas; let os=0,rs=0,oa=0,ra=0; const linhas=[];
const todas=new Set([...Object.keys(L),...Object.keys(R)]);
for(const l of todas){const o=R2((L[l]||[])[8]||0), r=R2((R[l]||[])[8]||0);
  const oA=R2(meses.reduce((a,m)=>a+((L[l]||[])[m-1]||0),0)), rA=R2(meses.reduce((a,m)=>a+((R[l]||[])[m-1]||0),0));
  os+=o;rs+=r;oa+=oA;ra+=rA; if(Math.abs(o)>0.004||Math.abs(r)>0.004) linhas.push({l,o,r,d:R2(r-o)});}
linhas.sort((a,b)=>Math.abs(b.d)-Math.abs(a.d));
console.log("EBITDA set: orcado",f(os),"realizado",f(rs),"var",f(rs-os));
console.log("EBITDA jan-set: orcado",f(oa),"realizado",f(ra),"var",f(ra-oa));
console.log("maiores variacoes de setembro:");
for(const x of linhas.slice(0,10)) console.log("   %s | orc %s | real %s | var %s",x.l.padEnd(42),f(x.o).padStart(13),f(x.r).padStart(13),f(x.d).padStart(13));
fs.writeFileSync("/Users/joaoandrade/painel-amanatopazio/dre/orc2.json",JSON.stringify({os:R2(os),rs:R2(rs),oa:R2(oa),ra:R2(ra),linhas}));
