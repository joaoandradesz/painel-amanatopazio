let ENT='consol', SEMINTER=false;
const f=v=>(v==null?'—':Number(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}));
const k=v=>Math.abs(v)>=1000?(v/1000).toFixed(0)+' mil':v.toFixed(0);
const sg=v=>(v>0?'+':(v<0?'−':''))+f(Math.abs(v));
const E=()=>D.ents[ENT];
const itens=()=>E().itens.filter(i=>!(SEMINTER&&/POUSADA TOPAZIO|AMANA EMPREENDIMENTOS/i.test(i.nome)));
function serie(){
  const por={}; itens().forEach(i=>{const a=por[i.d]||(por[i.d]=[0,0]); a[i.lado==='receber'?0:1]+=i.v;});
  let s=E().saldo_hoje; return D.dias.map(d=>{const[e,p]=por[d]||[0,0]; s=Math.round((s+e-p)*100)/100;
    return{d,lbl:d.slice(0,2),dow:['dom','seg','ter','qua','qui','sex','sáb'][new Date(d.split('/').reverse().join('-')+'T12:00').getDay()],ent:e,sai:p,saldo:s};});}
function kpis(S){
  const mn=S.reduce((a,b)=>b.saldo<a.saldo?b:a,S[0]);
  const rec=itens().filter(i=>i.lado==='receber').reduce((a,b)=>a+b.v,0);
  const pag=itens().filter(i=>i.lado==='pagar').reduce((a,b)=>a+b.v,0);
  return{mn,rec,pag,fim:S[S.length-1].saldo};}
function grafico(S){
  const W=1040,H=230,L=64,R=18,T=22,B=40,n=S.length;
  const vs=S.map(x=>x.saldo), lo=Math.min(...vs), hi=Math.max(...vs);
  const pad=(hi-lo)||Math.abs(hi)||1, y0=lo-pad*0.42, y1=hi+pad*0.22;
  const X=i=>L+i*((W-L-R)/(n-1)), Y=v=>T+(y1-v)/(y1-y0)*(H-T-B);
  let g='',rot='';
  for(let i=1;i<=4;i++){const v=y0+(y1-y0)*i/5,y=Y(v);
    g+=`<line x1="${L}" y1="${y}" x2="${W-R}" y2="${y}" stroke="#E5E7EB"/><text x="${L-8}" y="${y+3}" font-size="9" fill="#9CA3AF" text-anchor="end">${k(v)}</text>`;}
  if(y0<0&&y1>0){const yz=Y(0);g+=`<line x1="${L}" y1="${yz}" x2="${W-R}" y2="${yz}" stroke="#DC2626" stroke-width="1.2" stroke-dasharray="4 3"/>`;}
  const pts=S.map((x,i)=>`${X(i).toFixed(1)},${Y(x.saldo).toFixed(1)}`).join(' ');
  let bars='',hot='';
  const mx=Math.max(...S.map(x=>Math.max(x.ent,x.sai)))||1, bw=Math.min(13,(W-L-R)/n*0.34);
  S.forEach((x,i)=>{const cx=X(i);
    if(x.ent){const h=(x.ent/mx)*38;bars+=`<rect x="${cx-bw-1}" y="${H-B-h}" width="${bw}" height="${h}" rx="2" fill="#059669" opacity=".8"/>`;}
    if(x.sai){const h=(x.sai/mx)*38;bars+=`<rect x="${cx+1}" y="${H-B-h}" width="${bw}" height="${h}" rx="2" fill="#DC2626" opacity=".8"/>`;}
    if(i%2===0||i===n-1)rot+=`<text x="${cx}" y="${H-B+16}" font-size="9" fill="#6B7280" text-anchor="middle" font-weight="600">${x.lbl}</text><text x="${cx}" y="${H-B+26}" font-size="7.5" fill="#9CA3AF" text-anchor="middle">${x.dow}</text>`;
    hot+=`<rect class="hot" data-d="${x.d}" x="${cx-((W-L-R)/n)/2}" y="${T}" width="${(W-L-R)/n}" height="${H-T-B}" fill="transparent" style="cursor:pointer"><title>${x.d} · saldo ${f(x.saldo)}</title></rect>`;});
  const mi=S.indexOf(S.reduce((a,b)=>b.saldo<a.saldo?b:a,S[0]));
  const cx=X(mi),cy=Y(S[mi].saldo),bx=Math.min(Math.max(cx-62,L-40),W-R-124);
  return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">
  <defs><linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#F97316" stop-opacity=".28"/><stop offset="100%" stop-color="#F97316" stop-opacity="0"/></linearGradient></defs>
  ${g}<polygon points="${pts} ${X(n-1)},${H-B} ${L},${H-B}" fill="url(#gr)"/>
  <polyline points="${pts}" fill="none" stroke="#F97316" stroke-width="2.4" stroke-linejoin="round"/>
  ${bars}<circle cx="${cx}" cy="${cy}" r="4" fill="#FAFAF7" stroke="#F97316" stroke-width="2.2"/>
  <rect x="${bx}" y="${cy+16}" width="124" height="30" rx="5" fill="#0D0F1A"/>
  <text x="${bx+10}" y="${cy+28}" font-size="7.5" fill="#F97316" font-weight="700" letter-spacing="1">MENOR SALDO</text>
  <text x="${bx+10}" y="${cy+40}" font-size="12" fill="#fff" font-weight="800">${f(S[mi].saldo)}</text>
  ${rot}${hot}</svg>`;}
function calendario(S){
  const dow=new Date(S[0].d.split('/').reverse().join('-')+'T12:00').getDay();
  const mn=S.reduce((a,b)=>b.saldo<a.saldo?b:a,S[0]);
  const mx=Math.max(...S.map(x=>Math.abs(x.ent-x.sai)))||1;
  let h=['DOM','SEG','TER','QUA','QUI','SEX','SÁB'].map(d=>`<div class="hd">${d}</div>`).join('');
  for(let i=0;i<dow;i++)h+='<div></div>';
  S.forEach(x=>{const net=x.ent-x.sai, vz=!x.ent&&!x.sai;
    const bg=net>0?`rgba(5,150,105,${.07+Math.abs(net)/mx*.24})`:(net<0?`rgba(220,38,38,${.07+Math.abs(net)/mx*.24})`:'transparent');
    h+=`<div class="cel${vz?' vz':''}${x.d===mn.d?' mn':''}" style="background:${bg}" ${vz?'':`onclick="abrirDia('${x.d}')"`}>
      <span class="nt ${net>0?'vd':(net<0?'vm':'dim')}">${net?sg(Math.round(net)):'—'}</span>
      <div class="dd">${x.lbl}</div><div class="se">SALDO</div><div class="sl">${f(x.saldo)}</div></div>`;});
  return `<div class="calwrap"><div class="cal">${h}</div></div>`;}
function lista(lado,S){
  const L=itens().filter(i=>i.lado===lado).sort((a,b)=>a.d.split('/').reverse().join('').localeCompare(b.d.split('/').reverse().join(''))||b.v-a.v);
  const tot=L.reduce((a,b)=>a+b.v,0);
  const rows=L.map(i=>`<tr class="bl" data-t="${(i.nome+' '+i.cat+' '+i.d).toLowerCase()}"><td>${i.d.slice(0,5)}</td><td class="l">${i.nome}</td>
    <td style="color:#6B7280;font-size:10.5px">${i.cat||'—'}</td>${ENT==='consol'?`<td style="font-size:10.5px">${i.emp||''}</td>`:''}
    <td class="n ${lado==='receber'?'vd':'vm'}">${f(i.v)}</td></tr>`).join('');
  return `<div class="sec"><h2>${lado==='receber'?'A receber':'A pagar'} · próximos 15 dias</h2>
    <div class="sub">${L.length} títulos em aberto, somando ${f(tot)}</div>
    <input class="busca" placeholder="filtrar por nome, categoria ou data…" oninput="filtrar(this)">
    <table><thead><tr><th>Venc.</th><th>${lado==='receber'?'Cliente':'Fornecedor'}</th><th>Categoria</th>${ENT==='consol'?'<th>Empresa</th>':''}<th class="n">Valor</th></tr></thead>
    <tbody>${rows||'<tr><td colspan="5" style="color:#9CA3AF">nenhum título na janela</td></tr>'}</tbody></table></div>`;}
function filtrar(el){const q=el.value.toLowerCase();
  el.closest('.sec').querySelectorAll('tbody tr.bl').forEach(tr=>{tr.style.display=tr.dataset.t.includes(q)?'':'none';});}
function abrirDia(d){
  const L=itens().filter(i=>i.d===d).sort((a,b)=>b.v-a.v);
  const r=L.filter(i=>i.lado==='receber'),p=L.filter(i=>i.lado==='pagar');
  const S=serie().find(x=>x.d===d);
  const tb=(A,lado)=>A.length?`<table style="margin-bottom:14px"><thead><tr><th>${lado==='receber'?'Cliente':'Fornecedor'}</th><th>Categoria</th>${ENT==='consol'?'<th>Empresa</th>':''}<th class="n">Valor</th></tr></thead><tbody>
    ${A.map(i=>`<tr><td class="l">${i.nome}</td><td style="color:#6B7280;font-size:10.5px">${i.cat||'—'}</td>${ENT==='consol'?`<td style="font-size:10.5px">${i.emp||''}</td>`:''}<td class="n ${lado==='receber'?'vd':'vm'}">${f(i.v)}</td></tr>`).join('')}
    <tr class="tot"><td>Total</td><td></td>${ENT==='consol'?'<td></td>':''}<td class="n">${f(A.reduce((a,b)=>a+b.v,0))}</td></tr></tbody></table>`:'';
  document.getElementById('mtit').textContent=`${d} · ${E().nome}`;
  document.getElementById('mbody').innerHTML=
    `<p style="font-size:12.5px;color:#374151;margin-bottom:12px">Saldo ao fim do dia: <b>${f(S.saldo)}</b> · entra ${f(S.ent)} · sai ${f(S.sai)}</p>`
    +(r.length?'<h2 style="font-size:10px;letter-spacing:.14em;color:#059669;font-weight:700;margin-bottom:6px">RECEBIMENTOS</h2>':'')+tb(r,'receber')
    +(p.length?'<h2 style="font-size:10px;letter-spacing:.14em;color:#DC2626;font-weight:700;margin-bottom:6px">PAGAMENTOS</h2>':'')+tb(p,'pagar');
  document.getElementById('mbg').classList.add('on');}
function fechar(){document.getElementById('mbg').classList.remove('on');}
function setEnt(e){ENT=e;render();}
function toggleInter(){SEMINTER=!SEMINTER;render();}
function render(){
  const x=E(),S=serie(),K=kpis(S);
  document.getElementById('ents').innerHTML=['amana','topazio','consol']
    .map(e=>`<button class="${e===ENT?'on':''}" onclick="setEnt('${e}')">${D.ents[e].nome}</button>`).join('');
  document.getElementById('sub').textContent=
    `${D.meta.hoje} a ${D.meta.fim} · gerado em ${D.meta.gerado} · âncora de conciliação ${D.meta.ancora}`;
  const neg=x.saldo_hoje<0;
  const alerta=neg?`<div class="alert"><span class="tg">Conciliação pendente</span><p>O saldo apurado para <b>${x.nome}</b> está negativo em <b>${f(x.saldo_hoje)}</b>, o que não corresponde à realidade do banco. Há <b>${x.naoconc} lançamentos não conciliados</b> no período e o recebimento intercompany da compra de diárias ainda não foi lançado deste lado. Trate os números desta aba como incompletos até a conciliação de outubro fechar.</p></div>`:'';
  const inter=x.inter?`<label style="font-size:11.5px;color:#374151;display:flex;gap:7px;align-items:center;margin-bottom:12px"><input type="checkbox" ${SEMINTER?'checked':''} onchange="toggleInter()"> ocultar os ${x.inter} títulos intercompany (Amana ↔ Topázio)</label>`:'';
  const contas=x.contas.map(c=>`<tr><td class="l">${c.n}</td><td class="n">${f(c.ini)}</td><td class="n ${c.mov>=0?'vd':'vm'}">${sg(c.mov)}</td><td class="n">${f(c.hoje)}</td><td class="n" style="color:${c.naoconc?'#DC2626':'#9CA3AF'}">${c.naoconc||'—'}</td></tr>`).join('');
  const linhas=S.map(d=>{const net=d.ent-d.sai, vz=!d.ent&&!d.sai;
    return `<tr class="${vz?'':'cl'}${d.d===K.mn.d?' hi':''}" ${vz?'':`onclick="abrirDia('${d.d}')"`}>
      <td class="l">${d.d.slice(0,5)}</td><td style="color:#6B7280;font-size:10.5px">${d.dow}</td>
      <td class="n ${d.ent?'vd':'dim'}">${d.ent?f(d.ent):'—'}</td><td class="n ${d.sai?'vm':'dim'}">${d.sai?f(d.sai):'—'}</td>
      <td class="n ${net>0?'vd':(net<0?'vm':'dim')}">${net?sg(net):'—'}</td><td class="n">${f(d.saldo)}</td></tr>`;}).join('');
  document.getElementById('app').innerHTML=alerta+`
  <div class="kpis">
    <div class="kpi"><div class="e">Caixa hoje</div><div class="v ${x.saldo_hoje<0?'vm':'o'}">${f(x.saldo_hoje)}</div><div class="s">era ${f(x.contas.reduce((a,b)=>a+b.ini,0))} na âncora de ${D.meta.ancora}</div></div>
    <div class="kpi"><div class="e">A receber · 15 dias</div><div class="v vd">${f(K.rec)}</div><div class="s">${itens().filter(i=>i.lado==='receber').length} títulos em aberto</div></div>
    <div class="kpi"><div class="e">A pagar · 15 dias</div><div class="v vm">${f(K.pag)}</div><div class="s">${itens().filter(i=>i.lado==='pagar').length} títulos em aberto</div></div>
    <div class="kpi"><div class="e">Menor saldo</div><div class="v ${K.mn.saldo<0?'vm':''}">${f(K.mn.saldo)}</div><div class="s">em ${K.mn.d} · termina o período em ${f(K.fim)}</div></div>
  </div>
  <div class="sec"><h2>Fluxo de caixa diário</h2><div class="sub">Clique em qualquer dia para ver os títulos. A linha é o saldo; as barras, o que entra e o que sai.</div>
    ${inter}${grafico(S)}</div>
  <div class="sec"><h2>Calendário de caixa</h2><div class="sub">O líquido do dia e o saldo com que a empresa dorme</div>${calendario(S)}</div>
  <div class="sec"><h2>Dia a dia</h2><div class="sub">Clique na linha para abrir os títulos daquele dia</div>
    <table><thead><tr><th>Dia</th><th></th><th class="n">Entradas</th><th class="n">Saídas</th><th class="n">Líquido</th><th class="n">Saldo acumulado</th></tr></thead>
    <tbody>${linhas}<tr class="tot"><td>Total</td><td></td><td class="n vd">${f(K.rec)}</td><td class="n vm">${f(K.pag)}</td><td class="n ${K.rec-K.pag>=0?'vd':'vm'}">${sg(K.rec-K.pag)}</td><td class="n">${f(K.fim)}</td></tr></tbody></table></div>
  <div class="grid2">${lista('receber',S)}${lista('pagar',S)}</div>
  <div class="sec"><h2>Posição por conta</h2><div class="sub">Âncora de ${D.meta.ancora} mais o movimento já conciliado desde então</div>
    <table><thead><tr><th>Conta</th><th class="n">Âncora</th><th class="n">Movimento</th><th class="n">Hoje</th><th class="n">Não conciliados</th></tr></thead>
    <tbody>${contas}<tr class="tot"><td>Total</td><td class="n">${f(x.contas.reduce((a,b)=>a+b.ini,0))}</td><td class="n">${sg(x.contas.reduce((a,b)=>a+b.mov,0))}</td><td class="n">${f(x.saldo_hoje)}</td><td class="n">${x.naoconc||'—'}</td></tr></tbody></table>
    <div class="nota"><b>Vencido e não pago:</b> ${f(x.atrasados.pagar)} a pagar e ${f(x.atrasados.receber)} a receber, em ${x.atrasados.n} títulos fora da janela acima.
    <b>GetNet agendada:</b> ${f(x.getnet.bruto)} brutos em ${x.getnet.n} recebimentos, ${f(Math.abs(x.getnet.taxa))} de taxa — ${f(x.getnet.bruto+x.getnet.taxa)} líquidos, já contratados.
    <br><br>Este painel mostra <b>posição e compromissos</b>, não previsão: enxerga só o que já está lançado no Omie. Em outubro, dos R$ 200.386,32 pagos pela Amana na primeira quinzena, apenas R$ 81.943,07 estavam lançados no dia 30 de setembro — cobertura de <b>41%</b>. Lançar os recorrentes antes do dia 25 fecha 98% dessa lacuna.</div></div>`;
  document.querySelectorAll('.hot').forEach(h=>h.addEventListener('click',()=>abrirDia(h.dataset.d)));}
document.addEventListener('keydown',e=>{if(e.key==='Escape')fechar();});
render();
