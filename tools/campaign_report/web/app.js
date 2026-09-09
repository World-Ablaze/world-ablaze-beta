"use strict";
async function boot(text) {
  let D = JSON.parse(text);
  if(D.encoding==="gzip-base64") {
    document.getElementById("page-subtitle").textContent="Loading the embedded campaign data…";
    if(typeof DecompressionStream==="undefined")throw new Error("This report requires a browser with gzip DecompressionStream support. Use a recent Chrome, Edge, Firefox, or Safari.");
    const bytes=Uint8Array.from(atob(D.payload),c=>c.charCodeAt(0));
    const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    D=JSON.parse(await new Response(stream).text());
  }
  const snapshots = D.snapshots;
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const finite = n => typeof n === "number" && Number.isFinite(n);
  const names = {GER:"Germany",ENG:"United Kingdom",USA:"United States",SOV:"Soviet Union",JAP:"Japan",ITA:"Italy",FRA:"France",CHI:"China",RAJ:"India",CAN:"Canada",AST:"Australia",NZL:"New Zealand",SAF:"South Africa",POL:"Poland",FIN:"Finland",ROM:"Romania",HUN:"Hungary",BUL:"Bulgaria",BHU:"Bhutan",ETH:"Ethiopia",SPR:"Spain",SWE:"Sweden",NOR:"Norway",SWI:"Switzerland",BEL:"Belgium",HOL:"Netherlands",TUR:"Turkey",MAN:"Manchukuo"};
  const majorColors = {GER:"#476854",ENG:"#547fa6",USA:"#b99654",SOV:"#b96558",JAP:"#91739a",ITA:"#7c986b",FRA:"#6d9e9c"};
  const palette = ["#547f68","#ba975a","#688eae","#ab7166","#897da1","#6fa398","#a4ab69","#6a7c87","#b98797"];
  const familyNames = {armor:"Armor",armour:"Armor",mech:"Mechanized",mot:"Motorized",cav:"Cavalry",foot:"Infantry",infantry:"Infantry",unknown:"Unclassified",fighter:"Fighters",cas:"Close air support",nav_bomber:"Naval bombers",tac_bomber:"Tactical bombers",strat_bomber:"Strategic bombers",heavy_strat_bomber:"Heavy strategic bombers",transport_plane:"Transport",scout_plane:"Reconnaissance",maritime_patrol_plane:"Maritime patrol",cv_fighter:"Carrier fighters",cv_cas:"Carrier close air support",cv_nav_bomber:"Carrier naval bombers",destroyer:"Destroyers",light_cruiser:"Light cruisers",heavy_cruiser:"Heavy cruisers",battleship:"Battleships",battle_cruiser:"Battlecruisers",carrier:"Carriers",submarine:"Submarines",light_tank_equipment:"Light tanks",medium_tank_equipment:"Medium tanks",heavy_tank_equipment:"Heavy tanks",super_heavy_tank_equipment:"Super-heavy tanks",modern_tank_equipment:"Modern tanks",amphibious_tank_equipment:"Amphibious tanks",light_tank_destroyer_equipment:"Light tank destroyers",medium_tank_destroyer_equipment:"Medium tank destroyers",heavy_tank_destroyer_equipment:"Heavy tank destroyers",modern_tank_destroyer_equipment:"Modern tank destroyers",light_tank_artillery_equipment:"Light self-propelled artillery",medium_tank_artillery_equipment:"Medium self-propelled artillery",heavy_tank_artillery_equipment:"Heavy self-propelled artillery",modern_tank_artillery_equipment:"Modern self-propelled artillery",light_tank_aa_equipment:"Light self-propelled AA",medium_tank_aa_equipment:"Medium self-propelled AA",heavy_tank_aa_equipment:"Heavy self-propelled AA",modern_tank_aa_equipment:"Modern self-propelled AA"};
  const resourceNames = {steel:"Steel",aluminium:"Aluminium",rubber:"Rubber",oil:"Oil",tungsten:"Tungsten",chromium:"Chromium",coal:"Coal",iron:"Iron",bauxite:"Bauxite"};
  Object.assign(familyNames,{"?":"Unclassified",sup:"Combat support",light_tank_chassis:"Light tank chassis",medium_tank_chassis:"Medium tank chassis",heavy_tank_chassis:"Heavy tank chassis",super_heavy_tank_chassis:"Super-heavy tank chassis",modern_tank_chassis:"Modern tank chassis",amphibious_tank_chassis:"Amphibious tank chassis",naval_bomber:"Naval bombers",cv_naval_bomber:"Carrier naval bombers",heavy_fighter:"Heavy fighters",interceptor:"Interceptors",jet_fighter:"Jet fighters",jet_tac_bomber:"Jet tactical bombers",jet_strat_bomber:"Jet strategic bombers"});
  const buildingKeys = {civilian_factories:"industrial_complex",military_factories:"arms_factory",dockyards:"dockyard"};
  const fallbackMetrics = {
    manpower_free:{label:"Available manpower",unit:"men",evidence:"DERIVED"},
    divisions:{label:"Deployed divisions",unit:"divisions"}, army_manpower:{label:"Army manpower",unit:"men"},
    ships:{label:"Warships",unit:"ships"}, aircraft:{label:"Aircraft in wings",unit:"aircraft"},
    aircraft_stock:{label:"Aircraft stockpile",unit:"aircraft"}, civilian_factories:{label:"Civilian factories",unit:"levels"},
    military_factories:{label:"Military factories",unit:"levels"},dockyards:{label:"Dockyards",unit:"levels"},
    losses:{label:"Ongoing-war casualties",unit:"men",evidence:"DERIVED"}, stability:{label:"Stability",unit:"%",evidence:"DERIVED"},
    war_support:{label:"War support",unit:"%",evidence:"DERIVED"},stability_base:{label:"Stability (stored base)",unit:"%"},war_support_base:{label:"War support (stored base)",unit:"%"},command_power:{label:"Command power",unit:"points"},
    generals:{label:"Generals",unit:"count",evidence:"DERIVED"},field_marshals:{label:"Field marshals",unit:"count",evidence:"DERIVED"},admirals:{label:"Admirals",unit:"count",evidence:"DERIVED"},army_xp:{label:"Army XP",unit:"points"},navy_xp:{label:"Navy XP",unit:"points"},air_xp:{label:"Air XP",unit:"points"}
  };
  const percentIds = new Set(["stability","war_support","stability_base","war_support_base","mobilised_share"]);
  const catalog = Object.fromEntries([...new Set([...Object.keys(fallbackMetrics),...Object.keys(D.metric_catalog || {})])].map(k => [k,{evidence:"MEASURED",source:"See metric definitions",...(fallbackMetrics[k] || {}),...(D.metric_catalog?.[k] || {})}]));
  for (const [id,m] of Object.entries(catalog)) {
    m.unit = ({men:"men",count:buildingKeys[id]?"levels":id==="divisions"?"divisions":id==="ships"?"ships":id.startsWith("aircraft")?"aircraft":["generals","field_marshals","admirals"].includes(id)?"leaders":"units",percent:"%"})[m.unit] || m.unit;
    if(percentIds.has(id))m.note=[m.note,"Source ratio multiplied by 100 for percentage display."].filter(Boolean).join(" ");
  }
  function metric(id) { return catalog[id] || {label:familyNames[id] || id,unit:"units",evidence:"DERIVED",source:"Aggregated extracted data"}; }
  const labelType = value => familyNames[value] || String(value ?? "Unclassified").replaceAll("_"," ").replace(/^./,c=>c.toUpperCase());
  const labelCountry = tag => names[tag] || tag;
  const allTags = [...new Set(snapshots.flatMap(s => Object.keys(s.countries)))].sort((a,b) => {
    const ai = D.default_tags.indexOf(a), bi = D.default_tags.indexOf(b);
    return (ai < 0 ? 1000 : ai) - (bi < 0 ? 1000 : bi) || labelCountry(a).localeCompare(labelCountry(b),"en");
  });
  const color = tag => majorColors[tag] || palette[Math.max(0, allTags.indexOf(tag)) % palette.length];
  function time(value) { const p = value.split(".").map(Number); return Date.UTC(p[0],p[1]-1,p[2] || 1,p[3] || 0); }
  const times = snapshots.map(s => time(s.date));
  const iso = value => new Date(typeof value === "number" ? value : time(value)).toISOString().slice(0,10);
  const dateFormatter=new Intl.DateTimeFormat("en-GB",{day:"2-digit",month:"short",year:"numeric",timeZone:"UTC"});
  const monthFormatter=new Intl.DateTimeFormat("en-GB",{month:"short",year:"numeric",timeZone:"UTC"});
  const numberFormatters=new Map();
  const dateText = value => dateFormatter.format(new Date(typeof value === "number" ? value : time(value)));
  const shortDate = value => monthFormatter.format(new Date(value));
  const fmt = (n, digits = 0) => {if(!finite(n))return "—";if(!numberFormatters.has(digits))numberFormatters.set(digits,new Intl.NumberFormat("en-GB",{maximumFractionDigits:digits}));return numberFormatters.get(digits).format(n);};
  function compact(n) { if (!finite(n)) return "—"; const a = Math.abs(n); return a >= 1e6 ? `${fmt(n/1e6,1)} M` : a >= 1e3 ? `${fmt(n/1e3,1)} k` : fmt(n,Math.abs(n)<10 ? 1 : 0); }
  const S = {tags:new Set(D.default_tags.filter(t => allTags.includes(t))),from:0,to:snapshots.length-1,at:snapshots.length-1,tab:"overview",force:"land",scope:"controlled",resource:"steel",equipment:"tanks",families:new Set(),unitTypes:new Set(),percent:false,indexed:false,hidden:new Set(),convoy:"month"};
  const tabs = {overview:["Overview","Compare capabilities, follow their evolution, and identify pressures to investigate."],forces:["Forces","Compare force sizes and inspect the composition behind the totals."],industry:["Industry & resources","Track installed industry and the balance of resources."],equipment:["Equipment","Stockpiles, deployed equipment, recorded requests and assigned factories — army, tanks and air."],wars:["Wars & casualties","Follow casualties in the context of the wars included in each observation."],country:["Country status","Stability, war support, command power, and available experience."]};
  const tags = () => allTags.filter(t => S.tags.has(t));
  const current = tag => snapshots[S.at].countries[tag];
  const points = getter => snapshots.slice(S.from,S.to+1).map((snapshot,i) => ({x:times[i+S.from],value:getter(snapshot),file:snapshot.file,date:snapshot.date}));
  const catSum = obj => obj && typeof obj === "object" ? Object.values(obj).filter(finite).reduce((a,b)=>a+b,0) : null;
  function sumKnown(values) { return values.length && values.every(finite) ? values.reduce((a,b)=>a+b,0) : null; }
  function countryValue(country,id) {
    if (!country) return null;
    if (buildingKeys[id]) return finite(country.metrics?.[id]) && country.buildings?.[S.scope] ? country.buildings[S.scope][buildingKeys[id]] ?? 0 : null;
    const v = country.metrics?.[id];
    return finite(v) ? (percentIds.has(id) ? v*100 : v) : null;
  }
  function metricSeries(id) { return tags().map(tag => ({name:labelCountry(tag),color:color(tag),meta:metric(id),points:points(s=>countryValue(s.countries[tag],id))})); }
  function countriesSeries(getter,meta) { return tags().map(tag=>({name:labelCountry(tag),color:color(tag),meta,points:points(s=>getter(s.countries[tag]))})); }
  function badge(evidence) { const e = ["MEASURED","DERIVED","ASSUMED"].includes(evidence) ? evidence : "DERIVED"; return `<span class="badge ${e.toLowerCase()}">${e}</span>`; }
  function download(name,content,type) { const a=document.createElement("a"), url=URL.createObjectURL(new Blob([content],{type})); a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500); }
  function safeCell(value) { const str=String(value ?? ""); const safe=/^[=+@\t\r]/.test(str) || /^-[^\d]/.test(str) ? `'${str}` : str; return `"${safe.replace(/"/g,'""')}"`; }
  function exportCSV(title,headers,rows) { download(`${title.replace(/[^\p{L}\p{N}-]+/gu,"_")}.csv`,"\ufeff"+[headers,...rows].map(row=>row.map(safeCell).join(",")).join("\r\n"),"text/csv;charset=utf-8"); }
  function showTable(title,headers,rows,source="") { $("dialog-title").textContent=title;$("dialog-source").textContent=source;$("dialog-table").innerHTML=`<table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v ?? "—")}</td>`).join("")}</tr>`).join("")}</tbody></table>`;makeSortable($("dialog-table").querySelector("table"));$("data-dialog").showModal(); }
  function heading(title,subtitle="") { const el=document.createElement("div");el.className="section-heading";el.innerHTML=`<h2>${esc(title)}</h2><p>${esc(subtitle)}</p>`;return el; }
  function section(el,title,subtitle="") { el.append(heading(title,subtitle));return grid(); }
  // One panel per selected country, several metrics as series (stability/war support, XP, convoys).
  function countryPanels(g,ids,unit,options={}) { tags().forEach(tag=>{const series=ids.map((id,i)=>({name:metric(id).label,color:palette[i],meta:metric(id),points:points(s=>countryValue(s.countries[tag],id))}));g.append(chart(labelCountry(tag),series,unit,options));}); }
  function grid(parent=$("content")) { const el=document.createElement("div");el.className="grid";parent.append(el);return el; }
  function notice(text,warn=false) {const el=document.createElement("div");el.className=`notice${warn?" warn":""}`;el.textContent=text;return el;}
  function tooltip(event,series,point,display,unit) {
    const box=$("tooltip"), meta=series.meta || {};
    box.innerHTML=`<span>${esc(series.name)} · ${esc(dateText(point.x))}</span><strong>${fmt(display,2)} ${esc(unit)}</strong>${badge(meta.evidence)}<small>${esc(meta.source || "Extracted data")}</small><small>${esc(point.file || "")} ${meta.note?`· ${esc(meta.note)}`:""}</small>`;
    box.hidden=false;const x=event.clientX || event.target.getBoundingClientRect().left,y=event.clientY || event.target.getBoundingClientRect().top;
    box.style.left=`${Math.max(8,Math.min(x+16,innerWidth-box.offsetWidth-12))}px`;box.style.top=`${Math.max(8,Math.min(y+12,innerHeight-box.offsetHeight-12))}px`;
  }
  function chart(title,series,unit,options={}) {
    const card=document.createElement("section");card.className="chart-card";
    const rawSeries=series;
    let indexWarnings=[];
    if(S.indexed && options.indexable !== false) {
      series=series.map(line=>{
        const first=line.points.find(p=>finite(p.value));
        if(!first || first.value===0){indexWarnings.push(line.name);return {...line,points:line.points.map(p=>({...p,value:null}))};}
        return {...line,points:line.points.map(p=>({...p,value:finite(p.value)?p.value/first.value*100:null}))};
      });unit="index, baseline 100";
    }
    const source=[...new Set(rawSeries.map(s=>`${s.meta?.evidence || "DERIVED"} · ${s.meta?.source || "Aggregation"}${s.meta?.note ? ` · ${s.meta.note}` : ""}`))].join(" | ");
    card.innerHTML=`<div class="chart-header"><div><h3>${esc(title)}</h3><p>${esc(unit)}${options.subtitle?` · ${esc(options.subtitle)}`:""}</p></div><div class="chart-tools"><button class="chart-data" aria-label="Data : ${esc(title)}">Data</button><button class="chart-csv" aria-label="CSV : ${esc(title)}">CSV ↗</button></div></div>`;
    const rows=rawSeries.flatMap(s=>s.points.map(p=>[p.date,s.name,p.value ?? "",s.meta?.unit || unit,s.meta?.evidence || "DERIVED",p.file,s.meta?.source || "",s.meta?.note || ""]));
    const headers=["Date","Series","Value before rebasing","Unit","Evidence","Save file","Source","Caveat"];
    card.querySelector(".chart-data").onclick=()=>showTable(title,headers,rows,source);
    card.querySelector(".chart-csv").onclick=()=>exportCSV(title,headers,rows);
    // Legend interaction: a hidden series is dropped from the drawing AND from the axis scale, so the
    // remaining lines get the room. The set is keyed by chart title and series name, survives
    // re-renders, and never hides the last visible series.
    const hiddenKey=name=>`${title}|${name}`,isHidden=line=>S.hidden.has(hiddenKey(line.name));
    let shown=series.filter(line=>!isHidden(line));
    if(!shown.length&&series.length){series.forEach(line=>S.hidden.delete(hiddenKey(line.name)));shown=series;}
    const values=shown.flatMap(s=>s.points.map(p=>p.value)).filter(finite);
    if(!values.length) {card.insertAdjacentHTML("beforeend",`<div class="chart-empty">${indexWarnings.length?"Cannot rebase: initial value is zero or missing.":"No verified data for this selection."}</div>`);if(options.note)card.insertAdjacentHTML("beforeend",`<div class="chart-note">${esc(options.note)}</div>`);return card;}
    const w=720,h=252,pad={l:57,r:15,t:17,b:36},plotW=w-pad.l-pad.r,plotH=h-pad.t-pad.b;
    let min=Math.min(0,...values),max=options.max ?? Math.max(...values);
    if(max===min)max=min+1;else if(!options.max)max+=Math.abs(max-min)*.08;
    // Small integer counts (a handful of vehicles) get integer gridlines, never a 2.2 tick.
    if(!S.indexed&&values.every(Number.isInteger)&&max-min<=12){min=Math.floor(min);max=min+Math.ceil((max-min)/4)*4;}
    const start=times[S.from],end=times[S.to],span=end-start || 86400000;
    const x=v=>pad.l+(end===start?.5:(v-start)/span)*plotW,y=v=>pad.t+plotH-(v-min)/(max-min)*plotH;
    let svg=`<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(title)} : ${esc(unit)}"><title>${esc(title)}</title>`;
    for(let i=0;i<=4;i++){const v=min+(max-min)*i/4;svg+=`<line class="grid-line" x1="${pad.l}" x2="${w-pad.r}" y1="${y(v)}" y2="${y(v)}"/><text text-anchor="end" x="${pad.l-10}" y="${y(v)+3}">${esc(compact(v))}</text>`;}
    if(min<0)svg+=`<line class="zero-line" x1="${pad.l}" x2="${w-pad.r}" y1="${y(0)}" y2="${y(0)}"/>`;
    const tickCount=end===start?1:4;
    for(let i=0;i<tickCount;i++){const t=start+(end-start)*(tickCount===1?.5:i/(tickCount-1));svg+=`<text text-anchor="${i===0?"start":i===tickCount-1?"end":"middle"}" x="${x(t)}" y="${h-9}">${esc(shortDate(t))}</text>`;}
    svg+=`<line class="inspect-line" x1="${x(times[S.at])}" x2="${x(times[S.at])}" y1="${pad.t}" y2="${pad.t+plotH}"/>`;
    const intervals=times.slice(1).map((t,i)=>t-times[i]).sort((a,b)=>a-b),median=intervals[Math.floor(intervals.length/2)] || Infinity;
    const maxGap=median*1.8;
    series.forEach((line,si)=>{
      if(isHidden(line))return;
      let path="",open=false,prev=null;
      line.points.forEach(p=>{if(!finite(p.value)){open=false;return;}if(prev!==null && p.x-prev>maxGap)open=false;path+=`${open?"L":"M"}${x(p.x).toFixed(2)},${y(p.value).toFixed(2)} `;open=true;prev=p.x;});
      svg+=`<path d="${path}" fill="none" stroke="${line.color}" stroke-width="2.2" stroke-linejoin="round"/>`;
      if(values.length<=2000)line.points.forEach((p,pi)=>{if(finite(p.value))svg+=`<circle class="point" data-series="${si}" data-point="${pi}" cx="${x(p.x)}" cy="${y(p.value)}" r="${line.points.length<35?3:1.7}" fill="${line.color}"/><circle class="hit" data-series="${si}" data-point="${pi}" cx="${x(p.x)}" cy="${y(p.value)}" r="7"><title>${esc(line.name)} · ${esc(dateText(p.x))} : ${fmt(p.value,2)} ${esc(unit)}</title></circle>`;});
    });
    svg+="</svg>";
    const anyHidden=series.some(isHidden);
    card.insertAdjacentHTML("beforeend",svg+`<div class="chart-legend">${series.map((s,i)=>`<button type="button" class="legend-item${isHidden(s)?" off":""}" data-series="${i}" aria-pressed="${!isHidden(s)}" title="Click: show or hide · Shift+click: only this series"><i class="chip-dot" style="--color:${s.color}"></i>${esc(s.name)}</button>`).join("")}${anyHidden?`<button type="button" class="legend-item legend-all" data-all="1">show all</button>`:""}</div>`);
    card.querySelectorAll(".legend-item").forEach(b=>b.onclick=e=>{
      if(b.dataset.all){series.forEach(line=>S.hidden.delete(hiddenKey(line.name)));}
      else{const line=series[Number(b.dataset.series)];
        if(e.shiftKey)series.forEach(l=>l===line?S.hidden.delete(hiddenKey(l.name)):S.hidden.add(hiddenKey(l.name)));
        else if(isHidden(line))S.hidden.delete(hiddenKey(line.name));
        else if(shown.length>1)S.hidden.add(hiddenKey(line.name));}
      render();});
    card.querySelectorAll(".hit").forEach(el=>{const si=Number(el.dataset.series),pi=Number(el.dataset.point);el.addEventListener("pointermove",e=>tooltip(e,rawSeries[si],rawSeries[si].points[pi],series[si].points[pi].value,unit));el.addEventListener("pointerleave",()=>$("tooltip").hidden=true);el.addEventListener("click",()=>{S.at=Math.max(S.from,Math.min(S.to,times.indexOf(series[si].points[pi].x)));render();});});
    if(values.length>2000){const drawing=card.querySelector("svg");drawing.addEventListener("pointermove",e=>{const r=drawing.getBoundingClientRect(),px=(e.clientX-r.left)/r.width*w,py=(e.clientY-r.top)/r.height*h;let closest=null,best=Infinity;series.forEach((s,si)=>s.points.forEach((p,pi)=>{if(!finite(p.value))return;const distance=Math.abs(x(p.x)-px)*3+Math.abs(y(p.value)-py);if(distance<best){best=distance;closest={si,pi};}}));if(closest&&best<70){const {si,pi}=closest;tooltip(e,rawSeries[si],rawSeries[si].points[pi],series[si].points[pi].value,unit);}else $("tooltip").hidden=true;});drawing.addEventListener("pointerleave",()=>$("tooltip").hidden=true);}
    if(options.note || indexWarnings.length)card.insertAdjacentHTML("beforeend",`<div class="chart-note">${esc(options.note || "")}${indexWarnings.length?` Cannot rebase: ${esc(indexWarnings.join(", "))}.`:""}</div>`);
    return card;
  }
  function appendMetric(parent,id,options={}) {const m=metric(id);parent.append(chart(m.label,options.series || metricSeries(id),percentIds.has(id)?"%":m.unit,{...options,note:options.note ?? m.note}));}
  // Column sorting for every data table: click a header for ascending, again for descending, a
  // third time for the original order. Numbers sort numerically (formatted "1,234" and "-5" included),
  // anything else alphabetically; missing values ("—" or empty) always sink to the bottom. Rows are
  // moved, not rebuilt, so the handlers attached to their cells (heatmap buttons) survive.
  function makeSortable(table){
    const tbody=table?.tBodies?.[0],head=table?.tHead?.rows?.[0];if(!tbody||!head)return;
    const original=[...tbody.rows],ths=[...head.cells];let state={col:-1,dir:0};
    // A cell may carry a secondary line (the Δ under a snapshot value, the raw key under a variant name):
    // the sort key is its first own text node, the whole text only when there is none (country cell, button).
    const primary=td=>{const node=td&&[...td.childNodes].find(n=>n.nodeType===3?n.textContent.trim():n.tagName!=="SMALL");return ((node||td)?.textContent||"").trim();};
    const key=td=>{const t=primary(td);if(t===""||t==="—")return null;const n=Number(t.replace(/[\s,%+]/g,"").replace(/^−/,"-"));return Number.isFinite(n)?n:t.toLowerCase();};
    const compare=(a,b,dir)=>{if(a.k===null&&b.k===null)return a.idx-b.idx;if(a.k===null)return 1;if(b.k===null)return -1;const na=typeof a.k==="number",nb=typeof b.k==="number";let c=na&&nb?a.k-b.k:na!==nb?(na?-1:1):a.k.localeCompare(b.k,"en",{numeric:true});return c?c*dir:a.idx-b.idx;};
    ths.forEach((th,i)=>{th.classList.add("sortable");th.tabIndex=0;th.setAttribute("role","button");th.title="Sort: ascending, descending, then original order";
      const apply=()=>{state=state.col===i?{col:i,dir:(state.dir+1)%3}:{col:i,dir:1};
        ths.forEach(h=>{h.removeAttribute("aria-sort");h.classList.remove("sort-asc","sort-desc");});
        let rows=original;
        if(state.dir){const dir=state.dir===1?1:-1;th.setAttribute("aria-sort",dir===1?"ascending":"descending");th.classList.add(dir===1?"sort-asc":"sort-desc");rows=original.map((r,idx)=>({r,idx,k:key(r.cells[i])})).sort((x,y)=>compare(x,y,dir)).map(x=>x.r);}
        else state={col:-1,dir:0};
        tbody.replaceChildren(...rows);};
      th.onclick=apply;th.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();apply();}};});
    return table;
  }
  function tablePanel(headers,rows,options={}) {const el=document.createElement("section");el.className="panel";const cls=i=>options.left?.includes(i)?' class="left"':"";el.innerHTML=`<div class="table-scroll"><table><thead><tr>${headers.map((h,i)=>`<th${cls(i)}>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((cell,i)=>`<td${cls(i)}>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;makeSortable(el.querySelector("table"));return el;}
  function countryCell(tag){return `<div class="country-cell"><i class="chip-dot" style="--color:${color(tag)}"></i><div><strong>${esc(labelCountry(tag))}</strong> <span>${esc(tag)}</span></div></div>`;}
  function overview() {
    const el=$("content"),cards=document.createElement("div");cards.className="cards";
    const stats=[["Countries selected",tags().length,"Shared selection across all six tabs"],["Observations",S.to-S.from+1,"Save observations within the time window"],["Period",`${snapshots[S.from].date.split(".")[0]} — ${snapshots[S.to].date.split(".")[0]}`,"Comparison window"],["Inspection",shortDate(times[S.at]),"Cards and compositions at this date"]];
    cards.innerHTML=stats.map((s,i)=>`<div class="stat ${i===0?"accent":""}"><div class="stat-label">${esc(s[0])}</div><div class="stat-value">${esc(s[1])}</div><div class="stat-foot">${esc(s[2])}</div></div>`).join("");el.append(cards);
    el.append(heading("Country snapshot",`Values at ${dateText(times[S.at])} · Δ since ${dateText(times[S.from])}`));
    const ids=["manpower_free","divisions","ships","aircraft","civilian_factories","military_factories","losses"];
    el.append(tablePanel(["Country",...ids.map(id=>metric(id).label)],tags().map(tag=>[countryCell(tag),...ids.map(id=>{
      const value=countryValue(current(tag),id),before=countryValue(snapshots[S.from].countries[tag],id);const delta=finite(value)&&finite(before)?value-before:null;
      return `<span class="metric-value">${fmt(value)}</span><small>${finite(delta)?`Δ ${delta>0?"+":""}${fmt(delta)}`:"Δ —"}${id==="losses"?" · DERIVED":""}</small>`;
    })])));
    el.append(heading("Trends at a glance","One measure per chart · click a point to move the inspection date"));
    const charts=grid();appendMetric(charts,"divisions");appendMetric(charts,"ships");appendMetric(charts,"aircraft");
    el.append(heading("Resource balance","Effective balance at the inspection date · net + unmet demand, what resource@X reads · negative = shortage"));resourceHeatmap(el);
  }
  function controlBar() {const el=document.createElement("div");el.className="inline-controls";$("content").append(el);return el;}
  function segment(bar,choices,currentValue,change){const el=document.createElement("div");el.className="segmented";choices.forEach(([value,label])=>{const b=document.createElement("button");b.textContent=label;b.className=value===currentValue?"selected":"";b.onclick=()=>{change(value);render();};el.append(b);});bar.append(el);}
  function composition(parent,tag,counts,title){const entries=Object.entries(counts || {}).filter(([,n])=>finite(n)).sort((a,b)=>b[1]-a[1]);const total=catSum(counts),el=document.createElement("section");el.className="chart-card";
    let top=entries.slice(0,8);if(entries.length>8)top.push(["Other",entries.slice(8).reduce((s,[,n])=>s+n,0)]);
    el.innerHTML=`<div class="chart-header"><div><h3>${esc(labelCountry(tag))}</h3><p>${esc(title)} · ${fmt(total)} in total</p></div><div class="chart-tools"><button>Detail</button></div></div>${entries.length?`<div class="stack-bar">${top.map(([name,n],i)=>`<span class="stack-segment" style="width:${total?Math.max(0,n/total*100):0}%;background:${palette[i%palette.length]}" title="${esc(labelType(name))} : ${fmt(n)}"></span>`).join("")}</div>${top.map(([name,n],i)=>`<div class="composition-row"><span class="type-name" title="${esc(name)}">${esc(labelType(name))}</span><div class="track"><div class="bar" style="--bar-color:${palette[i%palette.length]};width:${top[0][1]>0?Math.max(0,n/top[0][1]*100):0}%"></div></div><span class="amount">${S.percent&&total?`${fmt(n/total*100,1)} %`:fmt(n)}</span></div>`).join("")}`:`<div class="chart-empty">${counts?"No units recorded.":"Data unavailable."}</div>`}`;
    el.querySelector("button").onclick=()=>showTable(`${labelCountry(tag)} · ${title}`,["Type","Count","Share %"],entries.map(([k,v])=>[labelType(k),v,total?v/total*100:0]),`${snapshots[S.at].file} · ${dateText(times[S.at])}`);parent.append(el);
  }
  function forces(){const el=$("content"),bar=controlBar();segment(bar,[["land","Army"],["sea","Navy"],["air","Air"]],S.force,v=>{S.force=v;S.unitTypes=new Set();});
    const section_=S.force==="land"?"army":S.force==="sea"?"navy":"air",typeWhat=S.force==="land"?"division families":S.force==="sea"?"ship types":"aircraft roles";
    const typeKeys=[...new Set(snapshots.slice(S.from,S.to+1).flatMap(s=>tags().flatMap(t=>Object.keys(s.countries[t]?.[section_]?.types || {}))))].sort((a,b)=>labelType(a).localeCompare(labelType(b),"en"));
    S.unitTypes=new Set([...S.unitTypes].filter(k=>typeKeys.includes(k)));
    if(typeKeys.length)checkPicker(bar,typeKeys,{label:"Types",what:typeWhat,selected:S.unitTypes,apply:v=>S.unitTypes=v,keep:"keepTypePanel"});
    const percent=document.createElement("label");percent.innerHTML=`<input type="checkbox" ${S.percent?"checked":""}> Composition in %`;percent.querySelector("input").onchange=e=>{S.percent=e.target.checked;render();};bar.append(percent);
    // The count metric of the current force is re-summed from the picked types, so the curve
    // answers the same question as the composition below it; the other charts have no type split.
    const countId=S.force==="land"?"divisions":S.force==="sea"?"ships":"aircraft",typeList=[...S.unitTypes].map(labelType).join(", ");
    const typed=S.unitTypes.size?{subtitle:`${typeList} only`,series:tags().map(tag=>({name:labelCountry(tag),color:color(tag),
      meta:{...metric(countId),evidence:"DERIVED",source:`${section_}/types, picked keys summed`,note:`Selected ${typeWhat} only: ${typeList}.`},
      points:points(s=>{const c=s.countries[tag];return finite(c?.metrics?.[countId])?catSum(pickedTypes(c[section_]?.types)):null;})}))}:{};
    const charts=grid();if(S.force==="land"){appendMetric(charts,"divisions",typed);appendMetric(charts,"army_manpower");}else if(S.force==="sea"){appendMetric(charts,"ships",typed);appendMetric(charts,"dockyards");appendMetric(charts,"admirals",{indexable:false});}else{appendMetric(charts,"aircraft",typed);appendMetric(charts,"aircraft_stock");}
    if(S.unitTypes.size)el.append(notice(`Type filter: ${typeList}. The "${metric(countId).label}" curve, the compositions, their shares and the template table below cover the selected types only; the other trend charts stay at the country total.`));
    el.append(heading("Force composition",dateText(times[S.at])));const comps=grid();tags().forEach(tag=>{const c=current(tag),available=finite(c?.metrics?.[S.force==="land"?"divisions":S.force==="sea"?"ships":"aircraft"]);composition(comps,tag,available?pickedTypes(c?.[section_]?.types):null,S.force==="land"?"Divisions by family":S.force==="sea"?"Ships by type":"Aircraft by role");});
    if(S.force==="land"){
      el.append(heading("Division templates","Composition at the inspection date"));
      const rows=tags().flatMap(tag=>(current(tag)?.army?.templates || []).filter(t=>unitTypePicked(t.family)).map(t=>[countryCell(tag),esc(t.name || t.id),esc(labelType(t.family)),fmt(t.count),fmt(t.manpower)]));
      if(rows.length)el.append(tablePanel(["Country","Template","Family","Divisions","Men present"],rows));
      el.append(notice("Counts describe commanded units. Foreign manpower contributions and expeditionary forces require reconciliation before country totals can be combined."));
      countryPanels(section(el,"Generals and field marshals","Unit leaders the country holds at each save, one panel per country"),["generals","field_marshals"],"leaders",{indexable:false});
    }else if(S.force==="air")el.append(notice("Aircraft in wings and in stockpiles are counted separately. These charts do not measure nominal airbase capacity."));
  }
  function resourceKeys(){return [...new Set(tags().flatMap(t=>Object.keys(current(t)?.resources || {})))].sort((a,b)=>(resourceNames[a]||a).localeCompare(resourceNames[b]||b,"en"));}
  function resourceHeatmap(parent){const keys=resourceKeys();if(!keys.length){parent.append(notice("No resource ledger at this date."));return;}
    const panel=tablePanel(["Country",...keys.map(k=>resourceNames[k]||k)],tags().map(tag=>[countryCell(tag),...keys.map(key=>{const v=current(tag)?.resources?.[key]?.effective;const cls=!finite(v)?"heat-missing":v<0?"heat-issue":"heat-clear";return `<button data-resource="${esc(key)}" class="heat-cell ${cls}" ${v<0?`style="background:rgba(186,98,74,${Math.min(.5,.09+Math.log10(1+Math.abs(v))*.07)})"`:""} title="${esc(resourceNames[key]||key)} · shortfall · ${fmt(v,1)}">${fmt(v,1)}</button>`;})]));
    panel.querySelectorAll("[data-resource]").forEach(b=>b.onclick=()=>{S.resource=b.dataset.resource;S.tab="industry";render();});parent.append(panel);
  }
  function refineryBuildings(c){return finite(c?.metrics?.civilian_factories)?c?.buildings?.[S.scope]:null;}
  function refineryCard(parent,tag){const c=current(tag),buildings=refineryBuildings(c),el=document.createElement("section");el.className="chart-card";const groups=[["Synthetic",["synthetic_refinery"]],["Steel",["steel_refinery","hydro_steel_refinery"]],["Aluminium",["aluminium_refinery","hydro_aluminium_refinery"]]];
    const rows=groups.map(([name,keys])=>{const active=buildings?keys.reduce((s,k)=>s+(buildings[k]||0),0):null,inactive=buildings?keys.reduce((s,k)=>s+(buildings[`${k}_inactive`]||0),0):null;return {name,active,inactive,total:active+inactive};});const max=Math.max(1,...rows.map(r=>r.total));
    el.innerHTML=`<div class="chart-header"><div><h3>${esc(labelCountry(tag))}</h3><p>Refinery levels · ${S.scope==="controlled"?"controlled states":"owned states"}</p></div></div>${rows.map(r=>`<div class="refinery-row"><span>${r.name}</span><div class="stack-bar"><span style="width:${r.active/max*100}%;background:#597d63"></span><span style="width:${r.inactive/max*100}%;background:#c6cdbf"></span></div><small>${fmt(r.active)} / ${fmt(r.inactive)}</small></div>`).join("")}<div class="chart-legend"><span><i class="chip-dot" style="--color:#597d63"></i>Active</span><span><i class="chip-dot" style="--color:#c6cdbf"></i>Inactive</span></div><details class="refinery-details"><summary>Hydroelectric variants and building detail</summary>${Object.entries(buildings || {}).filter(([k])=>k.includes("refinery")).map(([k,v])=>`<div class="key-value"><span>${esc(k)}</span><span>${fmt(v)}</span></div>`).join("") || "No buildings recorded."}</details>`;parent.append(el);
  }
  function industry(){const el=$("content"),bar=controlBar();segment(bar,[["controlled","Controlled states"],["owned","Owned states"]],S.scope,v=>S.scope=v);
    el.append(notice("Buildings show installed levels in the selected states. This is not the number of usable factories after occupation, damage, trade, and allocation."));
    const charts=grid();appendMetric(charts,"civilian_factories");appendMetric(charts,"military_factories");appendMetric(charts,"dockyards");
    const refineryMeta={unit:"levels",evidence:"DERIVED",source:"states/*/buildings/*refinery*/level",note:"Five building definitions, with active and inactive levels counted separately."};
    charts.append(chart("Inactive refineries",countriesSeries(c=>{const b=refineryBuildings(c);return b?Object.entries(b).filter(([k])=>k.includes("refinery")&&k.endsWith("_inactive")).reduce((s,[,v])=>s+v,0):null;},refineryMeta),"levels"));
    el.append(heading("Refineries: active / inactive",dateText(times[S.at])));const refs=grid();tags().forEach(t=>refineryCard(refs,t));
    el.append(heading("Resources","Effective balance (net + unmet demand) · negative = shortage · click a cell to select a resource"));resourceHeatmap(el);
    const keys=resourceKeys();if(!keys.length)return;
    if(!keys.includes(S.resource))S.resource=keys[0];
    const controls=controlBar(),label=document.createElement("label");label.innerHTML=`Resource <select aria-label="Resource">${keys.map(k=>`<option value="${esc(k)}" ${S.resource===k?"selected":""}>${esc(resourceNames[k]||k)}</option>`).join("")}</select>`;label.querySelector("select").onchange=e=>{S.resource=e.target.value;render();};controls.append(label);
    const rg=grid();for(const [key,title] of [["produced","Domestic production"],["effective","Effective balance"],["deficit","Unmet demand"],["imported","Imports"],["exported","Actual exports"],["available","Available"]]){
      const source=key==="effective"?"resources/to_use[0] + resources/to_use[2]":`resources/${key==="deficit"?"to_use[2]":key==="available"?"to_use[0]":key}`;
      rg.append(chart(`${resourceNames[S.resource]||S.resource} · ${title}`,countriesSeries(c=>c?.resources?.[S.resource]?.[key] ?? null,{unit:"units",evidence:key==="effective"?"DERIVED":"MEASURED",source}),"units"));
    }
  }
  // Registry entries without a `name` are the base chassis; the game displays their localised key.
  const variantName=v=>(v.name&&v.name!==v.definition)?v.name:((D.equipment_names||{})[v.definition]||v.name||v.definition||v.id);
  const domainOf={army:"army",tanks:"armor",air:"air",trains:"rail"},domainLabel={army:"Army equipment",tanks:"Tanks and derivatives",air:"Aircraft",trains:"Trains"};
  const familyPicked=k=>S.families.size===0||S.families.has(k);
  function equipmentFamilies(country){const fs=country?.equipment?.families;if(!fs)return [];const d=domainOf[S.equipment];return Object.entries(fs).filter(([k,f])=>f.domain===d&&familyPicked(k)).map(([,f])=>f);}
  function equipmentVariants(country){const d=domainOf[S.equipment];return (country?.equipment?.variants || []).filter(v=>v.domain===d&&familyPicked(v.family));}
  const unitTypePicked=k=>S.unitTypes.size===0||S.unitTypes.has(k);
  const pickedTypes=counts=>counts?Object.fromEntries(Object.entries(counts).filter(([k])=>unitTypePicked(k))):counts;
  // Additive checkbox dropdown: several keys add up, none checked = all. `only` isolates one row.
  function checkPicker(bar,keys,{label,what,selected,apply,keep}){const box=document.createElement("div");box.className="family-filter";const picked=keys.filter(k=>selected.has(k));
    box.innerHTML=`<label>${esc(label)}</label><button type="button" class="family-toggle" aria-expanded="false">${esc(picked.length?picked.length===1?labelType(picked[0]):`${picked.length} selected`:`All ${what.toLowerCase()}`)} <span>⌄</span></button><div class="family-panel" hidden><div class="family-actions"><button type="button" data-act="all">All</button><button type="button" data-act="none">Clear</button></div><div class="family-options">${keys.map(k=>`<div class="family-row"><label><input type="checkbox" value="${esc(k)}" ${selected.has(k)?"checked":""}> <span>${esc(labelType(k))}</span></label><button type="button" class="only-btn" data-only="${esc(k)}" title="Select only ${esc(labelType(k))}">only</button></div>`).join("")}</div></div>`;
    const panel=box.querySelector(".family-panel"),toggle=box.querySelector(".family-toggle");toggle.onclick=e=>{e.stopPropagation();panel.hidden=!panel.hidden;toggle.setAttribute("aria-expanded",String(!panel.hidden));};
    panel.onclick=e=>e.stopPropagation();
    panel.querySelectorAll("input").forEach(input=>input.onchange=()=>{const next=new Set(selected);if(input.checked)next.add(input.value);else next.delete(input.value);S[keep]=true;apply(next);render();});
    panel.querySelectorAll("[data-only]").forEach(b=>b.onclick=()=>{S[keep]=true;apply(new Set([b.dataset.only]));render();});
    panel.querySelectorAll("[data-act]").forEach(b=>b.onclick=()=>{S[keep]=true;apply(new Set(b.dataset.act==="all"?keys:[]));render();});
    if(S[keep]){panel.hidden=false;toggle.setAttribute("aria-expanded","true");S[keep]=false;}
    document.addEventListener("click",()=>{panel.hidden=true;toggle.setAttribute("aria-expanded","false");},{once:true});bar.append(box);}
  function familyPicker(bar,keys,what){checkPicker(bar,keys,{label:"Families",what,selected:S.families,apply:v=>S.families=v,keep:"keepFamilyPanel"});}
  function equipmentSum(country,key){if(!country?.equipment)return null;const values=equipmentFamilies(country);if(values.length)return sumKnown(values.map(v=>v[key]));if(["production_per_day","training_need","deficit"].includes(key))return null;return finite(country.metrics?.[["stock","stock_deficit","active_factories"].includes(key)?"aircraft_stock":"divisions"])?0:null;}
  function equipment(){const el=$("content"),bar=controlBar();segment(bar,[["army","Army"],["tanks","Tanks"],["air","Air"],["trains","Trains"]],S.equipment,v=>{S.equipment=v;S.families=new Set();});
    const d=domainOf[S.equipment],air=S.equipment==="air",rail=S.equipment==="trains",what=domainLabel[S.equipment];
    const keys=[...new Set(snapshots.slice(S.from,S.to+1).flatMap(s=>tags().flatMap(t=>Object.entries(s.countries[t]?.equipment?.families || {}).filter(([,f])=>f.domain===d).map(([k])=>k))))].sort();
    S.families=new Set([...S.families].filter(k=>keys.includes(k)));
    familyPicker(bar,keys,what);
    el.append(notice(rail?"Stockpiles are signed. Trains never enter a division: nothing is deployed and no reinforcement request is recorded for them, so no shortfall is derived. Their factories share the same military lines as army, tank and aircraft equipment. Daily output and the railway capacity they serve are not computed.":air?"Stockpiles are signed. Aircraft serve in wings, not divisions: the save records no reinforcement request for them, so no shortfall is derived; wings come from the strategic_air section. Daily output is not computed.":"Stockpiles are signed. Reinforcement requests are recorded by compatible family; they cannot be attributed to individual variants. Shortfall = recorded reinforcement requests - stock (DERIVED): requests may include equipment already in transit, so it is pressure, not a certified shortage. Training requirement and daily output are not computed.",true));
    // Captured or received stock explains a family a country never produced (SOV medium tank
    // destroyers after Germany's collapse): say it beside the charts instead of leaving a puzzle.
    const foreignLines=tags().map(tag=>{const vs=equipmentVariants(current(tag));const total=sumKnown(vs.map(v=>Math.max(0,v.stock ?? 0))),foreign=sumKnown(vs.filter(v=>v.creator&&v.creator!==tag).map(v=>Math.max(0,v.stock ?? 0)));return total>0&&foreign/total>=.5?`${labelCountry(tag)}: ${fmt(foreign)} of ${fmt(total)} in stock (${Math.round(foreign/total*100)} %) were built by other countries (captured or received), factories assigned ${fmt(equipmentSum(current(tag),"active_factories"))}.`:null;}).filter(Boolean);
    if(foreignLines.length)el.append(notice(`Foreign-built stock at ${dateText(times[S.at])} — ${foreignLines.join(" ")}`));
    const meta=(key,unit="equipment")=>({unit,evidence:"DERIVED",source:key==="stock"?"production/equipments → variant registry":key==="active_factories"?"production/military_lines":air&&key==="deployed"?"strategic_air/TAG/air_wing_pool/air_wings/equipment → variant registry":`units/division → equipment/${key}`,note:air&&key==="deployed"?"Aircraft listed in wings with their variant amounts, aggregated by airframe family.":"Aggregated by equipment-definition family."});
    const g=grid();
    const charts=rail?[["stock","Train stockpile","trains"],["active_factories","Factories assigned to trains","factories"]]:air?[["stock","Aircraft stockpile","aircraft"],["deployed","Aircraft in wings","aircraft"],["active_factories","Factories assigned to aircraft","factories"]]:[["stock",`${what}: stockpile`,"equipment"],["deployed",`${what}: in divisions`,"equipment"],["reinforcement_need","Recorded reinforcement requests","equipment"],["active_factories",`Factories assigned to ${what.toLowerCase()}`,"factories"]];
    for(const [key,title,unit] of charts){const m=meta(key,unit);g.append(chart(title,countriesSeries(c=>equipmentSum(c,key),m),unit,{note:m.note}));}
    if(air){
      // Roles come from the airframe families of the current selection, so both compositions follow the family filter.
      const byRole=(country,key)=>{const out={};for(const f of equipmentFamilies(country)){if(!finite(f[key]))continue;const role=f.role||"unknown";out[role]=(out[role]||0)+f[key];}return Object.keys(out).length?out:null;};
      const sg=section(el,"Stockpile by role",`At ${dateText(times[S.at])} · signed stock of the selected families grouped by airframe role`);tags().forEach(tag=>composition(sg,tag,byRole(current(tag),"stock"),labelCountry(tag)));
      const dg=section(el,"Deployed by role",`At ${dateText(times[S.at])} · aircraft in wings of the selected families grouped by airframe role`);tags().forEach(tag=>composition(dg,tag,byRole(current(tag),"deployed"),labelCountry(tag)));
    }
    // Three numbers per production line: requested (the line asks), active (the engine assigned) and
    // damaged (assigned factories currently damaged). A line omits a field at its default 0.
    const linesSum=(c,key)=>{if(!c?.equipment)return null;return equipmentVariants(c).flatMap(v=>v.production_lines||[]).reduce((a,l)=>a+(l[key]||0),0);};
    const lineMeta=(key,note)=>({unit:"factories",evidence:"MEASURED",source:`production/military_lines/${key}`,note});
    const fg=section(el,"Factories requested, assigned and damaged","Per country · what the lines ask for, what they received, and how much of that is currently damaged");
    tags().forEach(tag=>{const series=[["requested_factories","Requested (theoretical)",lineMeta("requested_factories","Factories the lines of the selected family ask for.")],["active_factories","Assigned (practical)",lineMeta("active_factories","Factories the engine actually assigned; a queued line without the field counts 0.")],["damaged_factories","Assigned but damaged",lineMeta("damaged_factories","Assigned factories currently damaged (bombing, sabotage, occupation); the field is omitted when 0.")]].map(([key,name,meta],i)=>({name,color:i===2?"#a8483d":palette[i],meta,points:points(s=>linesSum(s.countries[tag],key))}));fg.append(chart(labelCountry(tag),series,"factories",{indexable:false}));});
    if(!air&&!rail){
      // Stock and recorded demand on one panel per country, with the shortfall between them.
      const shortfallMeta={unit:"equipment",evidence:"DERIVED",source:"max(0, reinforcement requests - stock)",note:"Requests may include equipment already in transit: pressure, not a certified shortage."};
      const shortfall=c=>{const need=equipmentSum(c,"reinforcement_need"),stock=equipmentSum(c,"stock");return finite(need)&&finite(stock)?Math.max(0,need-stock):null;};
      const sd=section(el,"Stock versus recorded demand","Per country · signed stock, recorded reinforcement requests, and the shortfall between them");
      tags().forEach(tag=>{const series=[["stock","Stock (signed)",meta("stock")],["reinforcement_need","Recorded reinforcement requests",meta("reinforcement_need")],["shortfall","Shortfall",shortfallMeta]].map(([key,name,m],i)=>({name,color:palette[i],meta:m,points:points(s=>key==="shortfall"?shortfall(s.countries[tag]):equipmentSum(s.countries[tag],key))}));sd.append(chart(labelCountry(tag),series,"equipment",{indexable:false,note:shortfallMeta.note}));});
    }
    el.append(heading("Variants at the inspection date",dateText(times[S.at])));
    const variants=tags().flatMap(tag=>equipmentVariants(current(tag)).map(v=>({tag,...v})));
    const controls=controlBar(),search=document.createElement("input"),origin=document.createElement("select");search.type="search";search.placeholder="Filter variants…";search.setAttribute("aria-label","Search variants");search.style.cssText="padding:8px;border:1px solid var(--line);border-radius:6px";origin.setAttribute("aria-label","Variant origin");origin.innerHTML='<option value="all">All origins</option><option value="domestic">Domestic designs</option><option value="foreign">Foreign designs</option>';controls.append(search,origin);
    const holder=document.createElement("div");el.append(holder);
    const columns=["Country","Variant","Family","Creator","Stock",air?"In wings":"Deployed","Factories"];
    const redraw=()=>{const query=search.value.toLowerCase();const filtered=variants.filter(v=>(`${variantName(v)} ${v.name} ${v.definition} ${v.creator} ${v.family}`).toLowerCase().includes(query)&&(origin.value==="all"||(origin.value==="domestic"?v.creator===v.tag:v.creator&&v.creator!==v.tag)));holder.replaceChildren(tablePanel(columns,filtered.map(v=>[countryCell(v.tag),`${esc(variantName(v))}<small>${esc(v.definition || "")}</small>`,esc(labelType(v.family)),esc(v.creator || "—"),fmt(v.stock,1),fmt(v.deployed,1),fmt(v.active_factories)])));if(!filtered.length)holder.append(notice("No variants in this selection."));};search.oninput=redraw;origin.onchange=redraw;redraw();
    const rawButton=document.createElement("button");rawButton.textContent="Inspect recorded production lines";rawButton.onclick=()=>showTable(`Recorded ${what.toLowerCase()} production lines`,["Country","Variant","Active factories","Requested factories","produced (raw)","speed (raw)","cost (raw)"],variants.flatMap(v=>(v.production_lines||[]).map(line=>[labelCountry(v.tag),variantName(v),line.active_factories,line.requested_factories,line.produced,line.speed,line.cost])),`${snapshots[S.at].file} · MEASURED: production/military_lines. The units and time basis of produced/speed/cost are not certified; these fields are not presented as daily output.`);controls.append(rawButton);
  }
  // Convoy-loss ledger: each save carries a rolling 24-month window of (month, killer, owner, convoys)
  // records; the selected period is stitched month by month, the latest save covering a month wins,
  // and a month no selected save covers stays uncovered (never 0).
  const monthIndex=date=>{const p=date.split(".").map(Number);return p[0]*12+p[1]-1;};
  const monthLabel=m=>`${Math.floor(m/12)}.${String(m%12+1).padStart(2,"0")}`;
  function convoyLedger(){const first=monthIndex(snapshots[S.from].date)-1,last=monthIndex(snapshots[S.to].date)-1,byMonth=new Map();
    for(const s of snapshots.slice(S.from,S.to+1)){const w=s.convoy_window;if(!w||!s.convoy_losses)continue;for(let m=Math.max(w[0],first);m<=Math.min(w[1],last);m++)byMonth.set(m,[]);for(const r of s.convoy_losses){if(byMonth.has(r[0]))byMonth.get(r[0]).push(r);}}
    return {first,last,byMonth,covered:byMonth.size,total:last-first+1};}
  function lostInLastMonth(s,tag){if(!s.convoy_losses||!s.convoy_window)return null;const m=monthIndex(s.date)-1;if(m<s.convoy_window[0]||m>s.convoy_window[1])return null;return s.convoy_losses.filter(r=>r[0]===m&&r[2]===tag).reduce((a,r)=>a+r[3],0);}
  function shareTable(ledger,side){const other=side===2?1:2;return tags().map(tag=>{const sums=new Map();let total=0;for(const rows of ledger.byMonth.values())for(const r of rows){if(r[side]!==tag)continue;total+=r[3];sums.set(r[other],(sums.get(r[other])||0)+r[3]);}
      const parts=[...sums.entries()].sort((a,b)=>b[1]-a[1]).map(([t,n])=>`${esc(labelCountry(t))} ${Math.round(n/total*100)} % (${fmt(n)})`);return [countryCell(tag),fmt(total),parts.length?parts.join(", "):"—"];});}
  function convoyWar(el){const ledger=convoyLedger();el.append(heading("Convoy war",`Losses ledger stitched over ${monthLabel(ledger.first)} → ${monthLabel(ledger.last)} · ${ledger.covered} of ${ledger.total} months covered by a selected save`));
    if(!ledger.covered){el.append(notice("No convoy-loss ledger in the selected saves."));return;}
    el.append(notice("MEASURED sunk_convoys_history: one record per month, attacker and victim. Each save keeps only the last 24 complete months, so a month outside every selected save's window is uncovered, not zero. Convoy counts are the convoy pool (owned) and WA telemetry (free); in use is their difference.",true));
    const bar=controlBar();segment(bar,[["month","Losses in the last month"],["cumulative","Cumulative losses"]],S.convoy,v=>S.convoy=v);el.append(bar);
    const g=grid();const ledgerMeta={unit:"convoys",evidence:"MEASURED",source:"sunk_convoys_history (last complete month before the save)",note:"Convoys this country lost in the last complete month before each save, all attackers combined."};
    if(S.convoy==="month")g.append(chart("Convoys lost in the last complete month",tags().map(tag=>({name:labelCountry(tag),color:color(tag),meta:ledgerMeta,points:points(s=>lostInLastMonth(s,tag))})),"convoys",{note:ledgerMeta.note,indexable:false}));
    else appendMetric(g,"convoys_lost_cumulative",{indexable:false});
    appendMetric(g,"convoy_kills",{indexable:false});appendMetric(g,"convoys_pool",{indexable:false});appendMetric(g,"convoys_in_use",{indexable:false});
    el.append(heading("Losses by attacker",`Selected countries as victims · ${monthLabel(ledger.first)} → ${monthLabel(ledger.last)}`));el.append(tablePanel(["Victim","Convoys lost","Attackers (share of the victim's losses)"],shareTable(ledger,2),{left:[2]}));
    el.append(heading("Kills by victim",`Selected countries as attackers · same period`));el.append(tablePanel(["Attacker","Convoys sunk","Victims (share of the attacker's kills)"],shareTable(ledger,1),{left:[2]}));}
  function wars(){const el=$("content");el.append(notice("DERIVED — casualty direction follows the losses.py reader. Totals include the wars present at each date. When a war relation disappears, the total can fall; this does not represent negative casualties.",true));const g=grid();appendMetric(g,"losses");appendMetric(g,"army_manpower");appendMetric(g,"divisions");
    el.append(heading("Current war relations",dateText(times[S.at])));const rows=tags().flatMap(tag=>(current(tag)?.wars || []).map(w=>[countryCell(tag),esc(labelCountry(w.enemy)),esc(w.start_date || "—"),fmt(w.losses),badge("DERIVED")]));el.append(tablePanel(["Country","Opponent","Start","Attributed casualties suffered","Evidence"],rows));
    const changes=[];for(let i=Math.max(1,S.from);i<=S.to;i++)for(const tag of tags()){
      const before=snapshots[i-1].countries[tag],after=snapshots[i].countries[tag];if(!before||!after)continue;const newIds=new Set((after.wars||[]).map(w=>w.id));for(const w of before.wars||[])if(!newIds.has(w.id))changes.push([esc(dateText(times[i])),esc(labelCountry(tag)),esc(labelCountry(w.enemy)),fmt(w.losses),"Relation disappeared; final value unknown"]);
    }
    if(changes.length){el.append(heading("Changes in coverage","Last observed counter, not a verified final total at peace"));el.append(tablePanel(["Observation","Country","Opponent","Last value","Interpretation"],changes));}
    convoyWar(el);
  }
  function country(){const el=$("content");
    const mg=section(el,"Mobilisation","Share of the population the conscription law makes recruitable, beside the free manpower pool");appendMetric(mg,"mobilised_share",{indexable:false});appendMetric(mg,"manpower_free");
    const changes=tags().flatMap(tag=>{let previous;return snapshots.slice(S.from,S.to+1).flatMap(s=>{const law=s.countries[tag]?.conscription_law;if(!law||law===previous){if(law)previous=law;return [];}const row=[countryCell(tag),dateText(s.date),esc(labelType(previous||"—")),esc(labelType(law)),fmt(s.countries[tag]?.metrics?.manpower)];previous=law;return [row];});});
    if(changes.length)el.append(tablePanel(["Country","First save with the law","From","To","Pool at that save"],changes,{left:[2,3]}));
    countryPanels(section(el,"Stability and war support","Displayed values rebuilt from the stored base plus spirits, advisors, dynamic modifiers, party popularity, war posture and penalties (DERIVED; see the metric definitions)"),["stability","war_support"],"%",{max:100,indexable:false});
    countryPanels(section(el,"Available experience","Army, navy, and air experience in points"),["army_xp","navy_xp","air_xp"],"points",{indexable:false});
    countryPanels(section(el,"Command and political power","Stored balances at each save, in points, one panel per country"),["command_power","political_power"],"points",{indexable:false});
    appendMetric(section(el,"Economy fatigue","WA economic fatigue variable, in points"),"economy_fatigue",{indexable:false});
    countryPanels(section(el,"Convoys","Owned pool, free (WA telemetry) and in use, one panel per country"),["convoys_pool","convoys_free","convoys_in_use"],"convoys",{indexable:false});
  }
  function renderCountries(){const q=$("country-search").value.toLowerCase();$("country-options").innerHTML=allTags.filter(t=>`${t} ${labelCountry(t)}`.toLowerCase().includes(q)).map(t=>`<label><input type="checkbox" value="${esc(t)}" ${S.tags.has(t)?"checked":""}><i class="chip-dot" style="--color:${color(t)}"></i><span class="country-name">${esc(labelCountry(t))}</span><span class="country-tag">${esc(t)}</span><button type="button" class="only-tag" data-tag="${esc(t)}" title="Select only ${esc(labelCountry(t))}">only</button></label>`).join("");$("country-options").querySelectorAll("input").forEach(input=>input.onchange=()=>{if(input.checked)S.tags.add(input.value);else S.tags.delete(input.value);render();});$("country-options").querySelectorAll(".only-tag").forEach(button=>button.onclick=e=>{e.preventDefault();e.stopPropagation();S.tags=new Set([button.dataset.tag]);render();});}
  function renderQuality(){const allIssues=[...new Set([...D.warnings,...snapshots.slice(S.from,S.to+1).flatMap(s=>[...(s.warnings || []),...tags().flatMap(t=>s.countries[t]?.issues || [])])])];
    $("quality-count").textContent=`${allIssues.length} note${allIssues.length>1?"s":""} · metric sources`;
    $("quality-content").innerHTML=`<h3>Coverage and caveats</h3><ul>${allIssues.map(w=>`<li>${esc(w)}</li>`).join("")}</ul><p>Missing data is shown as “—”. Lines do not bridge missing values or gaps longer than 1.8 times the median observation interval. Aggregated classifications are DERIVED; source counts remain available. Save dates are observations, not the exact dates of every event.</p><div class="table-scroll"><table><thead><tr><th>Metric</th><th>Evidence</th><th>Source</th><th>Caveat</th></tr></thead><tbody>${Object.entries(catalog).map(([k,m])=>`<tr><td>${esc(m.label)}</td><td>${badge(m.evidence)}</td><td><code>${esc(m.source)}</code></td><td>${esc(m.note || "")}</td></tr>`).join("")}</tbody></table></div><h3>Reproducibility</h3><p>Campaign: <code>${esc(D.campaign.id)}</code><br>Definitions and extractors: <code>${esc(D.dependencies_sha256)}</code><br>Schema ${esc(D.schema_version)} · no LLM calls in generation.</p>`;makeSortable($("quality-content").querySelector("table"));
  }
  let renderedTab=null;
  function render(){
    // An in-page control (resource select, scope, armor filter, heatmap cell) re-renders the whole
    // tab; keep the reader where they were unless the tab itself changed.
    const sameTab=renderedTab===S.tab,scrollY=window.scrollY;
    $("tooltip").hidden=true;$("page-title").textContent=tabs[S.tab][0];$("page-subtitle").textContent=tabs[S.tab][1];
    $("nav").innerHTML=Object.entries(tabs).map(([id,[name]],i)=>`<button class="nav-button ${id===S.tab?"active":""}" data-tab="${id}" ${id===S.tab?'aria-current="page"':""}><span class="nav-number">0${i+1}</span>${esc(name)}</button>`).join("");$("nav").querySelectorAll("button").forEach(b=>b.onclick=()=>{S.tab=b.dataset.tab;history.replaceState(null,"",`#${S.tab}`);render();});
    $("country-toggle").innerHTML=`<span>${tags().length} countries selected</span><span>⌄</span>`;
    $("selected-chips").innerHTML=tags().map(t=>`<span class="chip"><i class="chip-dot" style="--color:${color(t)}"></i>${esc(t)}</span>`).join("");
    $("date-from").value=iso(times[S.from]);$("date-to").value=iso(times[S.to]);$("range-from").value=S.from;$("range-to").value=S.to;
    $("inspect-date").min=S.from;$("inspect-date").max=S.to;$("inspect-date").value=S.at;$("inspect-label").textContent=dateText(times[S.at]);
    $("content").replaceChildren();if(!tags().length)$("content").innerHTML='<div class="empty"><strong>Select at least one country</strong>Use the country filter to restore the seven majors.</div>';else({overview,forces,industry,equipment,wars,country}[S.tab])();
    renderCountries();renderQuality();
    if(renderedTab!==null)window.scrollTo(0,sameTab?scrollY:0);renderedTab=S.tab;
  }
  function setWindow(from,to){S.from=Math.max(0,Math.min(snapshots.length-1,from));S.to=Math.max(S.from,Math.min(snapshots.length-1,to));S.at=Math.max(S.from,Math.min(S.to,S.at));document.querySelectorAll("[data-period]").forEach(b=>b.classList.remove("selected"));render();}
  for(const id of ["range-from","range-to","inspect-date"]){$(id).min=0;$(id).max=snapshots.length-1;$(id).step=1;}
  for(const id of ["date-from","date-to"]){$(id).min=iso(times[0]);$(id).max=iso(times[times.length-1]);}
  $("range-from").oninput=e=>setWindow(Number(e.target.value),Math.max(S.to,Number(e.target.value)));
  $("range-to").oninput=e=>setWindow(Math.min(S.from,Number(e.target.value)),Number(e.target.value));
  $("inspect-date").oninput=e=>{S.at=Number(e.target.value);render();};
  $("date-from").onchange=e=>{if(!e.target.value)return;const t=Date.parse(e.target.value+"T00:00:00Z"),found=times.findIndex(x=>x>=t),i=found<0?times.length-1:found;setWindow(i,Math.max(i,S.to));};
  $("date-to").onchange=e=>{if(!e.target.value)return;const t=Date.parse(e.target.value+"T23:59:59Z"),i=Math.max(0,times.findLastIndex(x=>x<=t));setWindow(Math.min(i,S.from),i);};
  document.querySelectorAll("[data-period]").forEach(b=>b.onclick=()=>{const date=new Date(times[times.length-1]);if(b.dataset.period!=="all")date.setUTCMonth(date.getUTCMonth()-Number(b.dataset.period));const from=b.dataset.period==="all"?0:Math.max(0,times.findIndex(t=>t>=date.getTime()));S.at=times.length-1;setWindow(from,times.length-1);b.classList.add("selected");});
  $("country-toggle").onclick=()=>{const expanded=$("country-panel").hidden;$("country-panel").hidden=!expanded;$("country-toggle").setAttribute("aria-expanded",String(expanded));if(expanded)$("country-search").focus();};
  document.onclick=e=>{if(!e.target.closest(".country-filter")){$("country-panel").hidden=true;$("country-toggle").setAttribute("aria-expanded","false");}};
  document.onkeydown=e=>{if(e.key==="Escape"){$("country-panel").hidden=true;$("country-toggle").setAttribute("aria-expanded","false");$("tooltip").hidden=true;}};
  $("country-search").oninput=renderCountries;$("major-tags").onclick=()=>{S.tags=new Set(D.default_tags.filter(t=>allTags.includes(t)));render();};$("all-tags").onclick=()=>{S.tags=new Set(allTags);render();};$("no-tags").onclick=()=>{S.tags.clear();render();};
  $("indexed").onchange=e=>{S.indexed=e.target.checked;render();};$("close-dialog").onclick=()=>$("data-dialog").close();$("download-json").onclick=()=>download(`campaign_${D.campaign.id.slice(0,8)}.json`,JSON.stringify(D),"application/json");
  $("campaign-id").textContent=`CAMPAIGN ${D.campaign.id.slice(0,8).toUpperCase()}`;$("coverage-label").textContent=`${snapshots[0].date.split(".")[0]} — ${snapshots[snapshots.length-1].date.split(".")[0]}`;$("sample-label").textContent=`${snapshots.length} saves · ${allTags.length} countries`;
  $("build-info").textContent=`Generated on ${new Date(D.generated_at).toLocaleDateString("en-GB")} · schema ${D.schema_version}`;
  if(location.hash==="#armor"){S.tab="equipment";S.equipment="tanks";}
  if(tabs[location.hash.slice(1)])S.tab=location.hash.slice(1);
  window.onhashchange=()=>{if(tabs[location.hash.slice(1)]){S.tab=location.hash.slice(1);render();}};
  // Import: another campaign.json from this generator replaces the data for this session only.
  $("import-json").onclick=()=>{$("import-file").value="";$("import-file").click();};
  $("import-file").onchange=async e=>{const file=e.target.files[0];if(!file)return;const text=await file.text();let parsed;
    try{parsed=JSON.parse(text);}catch(err){alert(`Not a JSON file: ${err.message}`);return;}
    if(parsed.schema_version!==D.schema_version||!Array.isArray(parsed.snapshots)||!parsed.snapshots.length||!parsed.campaign?.id){alert(`Not a campaign.json from this generator (schema ${D.schema_version} with snapshots and a campaign id expected).`);return;}
    $("page-subtitle").textContent=`Loading ${file.name}…`;location.hash="";await boot(text);};
  render();
}
boot(document.getElementById("report-data").textContent).catch(error=>{document.getElementById("page-title").textContent="Report could not be loaded";document.getElementById("page-subtitle").textContent=error.message;console.error(error);});
