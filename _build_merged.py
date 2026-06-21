# -*- coding: utf-8 -*-
import re, io

def read(p):
    with io.open(p, encoding='utf-8') as f: return f.read()

dash = read('makromodeller-kritisk-dashboard.html')
expl = read('makromodeller-modellforklaringer.html')
deck = read('makromodeller-teknisk-dypdykk.html')

def between(s, a, b):
    i = s.index(a) + len(a); j = s.index(b, i); return s[i:j]

def style_of(s):
    return between(s, '<style>', '</style>')

def section_by_id(s, sid, tag='section'):
    m = re.search(r'<%s[^>]*id="%s">.*?</%s>' % (tag, sid, tag), s, re.S)
    return m.group(0) if m else ''

def first_svg_in_section(s, sid):
    sec = section_by_id(s, sid, 'section')
    m = re.search(r'<svg.*?</svg>', sec, re.S)
    return m.group(0) if m else ''

def first_table_in_section(s, sid):
    sec = section_by_id(s, sid, 'section')
    m = re.search(r'<table class="tbl".*?</table>', sec, re.S)
    return m.group(0) if m else ''

# ---- styles ----
dash_style = style_of(dash)
expl_style = style_of(expl)

# ---- scripts ----
expl_script = between(expl, '<script>', '</script>')
dash_script = between(dash, '<script>', '</script>')

# ---- explorer body (selector + intro + panel + navfoot + src) ----
expl_body = between(expl, '<body>', '<script>')

# ---- dashboard sections ----
sec = {sid: section_by_id(dash, sid) for sid in
       ['hero','params','olje','oecd','ledger','matrix','synth','paramtable','kilder']}

# ---- deck fragments ----
svg_typology = first_svg_in_section(deck, 's2')
svg_ecosystem = first_svg_in_section(deck, 's3')
tbl_coupling = first_table_in_section(deck, 's12')
tbl_docgrad = first_table_in_section(deck, 's13')

# ---- tax dashboard (scoped + harmonised) ----
tax = read('skattedashboard-2024.html')
tax_style = style_of(tax)
tax_body = between(tax, '<body>', '</body>')

def split_top_rules(css):
    rules=[]; depth=0; start=0
    for i,c in enumerate(css):
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                rules.append(css[start:i+1]); start=i+1
    return rules

def prefix_sel(p, scope):
    s=p.strip()
    if not s: return s
    if s in (':root','html','body'): return scope
    if s=='*': return scope+' *'
    return scope+' '+s

def scope_rule(rule, scope):
    rule=rule.strip()
    if not rule: return ''
    if rule.startswith('@'):
        bi=rule.find('{')
        head=rule[:bi]
        if 'prefers-color-scheme' in head: return ''   # drop dark mode
        inner=rule[bi+1:rule.rfind('}')]
        return head+'{'+''.join(scope_rule(r,scope) for r in split_top_rules(inner))+'}'
    bi=rule.find('{')
    sels=rule[:bi]; body=rule[bi:]
    return ','.join(prefix_sel(p,scope) for p in sels.split(','))+body

tax_css=''.join(scope_rule(r,'.skatt') for r in split_top_rules(tax_style))
harmon={
 '--bg: #FAFAF7':'--bg:#eef1f6',
 '--surface-2: #F1EFE8':'--surface-2:#f4f6f9',
 '--text: #2C2C2A':'--text:#13233a',
 '--text-2: #5F5E5A':'--text-2:#3d5070',
 '--text-3: #888780':'--text-3:#5d6b80',
 '--border: rgba(44, 44, 42, 0.12)':'--border:rgba(19,35,58,.12)',
 '--border-strong: rgba(44, 44, 42, 0.25)':'--border-strong:rgba(19,35,58,.22)',
 '--radius: 8px':'--radius:4px',
 '--radius-lg: 12px':'--radius-lg:6px',
}
for a,b in harmon.items(): tax_css=tax_css.replace(a,b)
tax_css+='\n.skatt h1,.skatt h2,.skatt h3,.skatt h4{font-family:var(--serif)}\n.skatt{padding:0;background:transparent}\n'

co_lotte='''<div class="callout callout-info"><p><strong>Modellkobling:</strong> Slike statiske provenyberegninger er nøyaktig det <a class="xlink" style="cursor:pointer" onclick="goModel('lotte')">LOTTE-modellen →</a> gjør (mikrosimulering av skatt på et utvalg); atferdseffekter krever LOTTE-Arbeid.</p></div>'''
co_oecd='''<div class="callout callout-info"><p><strong>Eksternt blikk:</strong> OECD (2026) anbefaler å redusere formuesskatten til fordel for sterkere eiendoms- og arveskatt — se <a class="xlink" style="cursor:pointer" onclick="goView('data','oecd')">Data &amp; makro → OECD →</a>.</p></div>'''

def inject_after_meta(html, sid, callout):
    idx=html.find('id="%s"'%sid)
    if idx<0: return html
    pend=html.find('</p>', idx)
    if pend<0: return html
    pos=pend+4
    return html[:pos]+'\n'+callout+html[pos:]

tax_body=inject_after_meta(tax_body,'scenarier',co_lotte)
tax_body=inject_after_meta(tax_body,'eierskatt',co_oecd)
skatt_view = """<section class="view" id="view-skatt">
<section class="card">
  <div class="eyebrow">Skatteinngang · inntektsåret 2024, oppdatert med 2025-regnskap</div>
  <h2>Fra 3 218 milliarder til 7 milliarder — hvor skattepengene kommer fra</h2>
  <div class="meta-row"><span><b style="color:var(--ok)">✓ Hovedtall verifisert mot SSB 14668, 08231 og 07091</b> (kontrollert juni 2026)</span></div>
  <div class="governing">Hele skattesystemet i ett bilde: fra offentlig forvaltnings 3 218 mrd i totale inntekter, ned gjennom skattesystemet, helt til småbedriftenes selskapsskatt på 7 mrd — 1 av hver 460. krone staten tar inn.</div>
  <div class="subtabs">
    <button class="subtab active" data-sub="oversikt">Oversikt &amp; hierarki</button>
    <button class="subtab" data-sub="eier">Eierskatt</button>
    <button class="subtab" data-sub="smaa">Småbedrifter</button>
    <button class="subtab" data-sub="scenario">Scenarier &amp; historikk</button>
    <button class="subtab" data-sub="perspektiv">Perspektiver: Civita &amp; LO</button>
  </div>

  <!-- ================= SUB: OVERSIKT ================= -->
  <div class="subpanel active" id="sub-oversikt">
    <div class="eyebrow neutral">Det store bildet · offentlige inntekter 2024</div>
    <h3>Selskapsskatten er bare 16 % av inntektene — og petroleum dominerer den</h3>
    <div class="kpis">
      <div class="kpi"><div class="v">3 218 <small>mrd</small></div><div class="l">Offentlig forvaltnings totale inntekter</div></div>
      <div class="kpi"><div class="v">510 <small>mrd</small></div><div class="l">All selskapsskatt (16 % av inntektene)</div></div>
      <div class="kpi"><div class="v">382 <small>mrd</small></div><div class="l">Petroleumsskatt fra ~30 selskap</div></div>
      <div class="kpi"><div class="v">110 <small>mrd</small></div><div class="l">Selskapsskatt fastland (alle størrelser)</div></div>
      <div class="kpi"><div class="v">~7 <small>mrd</small></div><div class="l">Småbedrifter under 10 ansatte</div></div>
      <div class="kpi"><div class="v">593 777</div><div class="l">Antall småbedrifter (90,2 % av alle)</div></div>
      <div class="kpi"><div class="v">~770 000</div><div class="l">Sysselsatte i småbedrifter (43 % av privat sektor)</div></div>
      <div class="kpi"><div class="v">~35 <small>mrd</small></div><div class="l">SMB-segmentet under 100 ansatte</div></div>
    </div>

    <hr class="rule">
    <div class="eyebrow neutral">Hierarkiet · kasse-i-kasse, fra 3 218 mrd til 7 mrd</div>
    <h3>Hver ramme er en del av den ytre</h3>
    <div class="hier">
      <div class="hl hl1"><span class="hlk">Offentlig forvaltning · totale inntekter</span><span class="hlv">3 218 mrd<small>100 %</small></span><div class="hld">Stat + kommuner + fylkeskommuner + folketrygden</div>
        <div class="hl hl2"><span class="hlk">Skatt på inntekt og formue</span><span class="hlv">1 079 mrd<small>33,5 % av total</small></span><div class="hld">Personskatt 558 · petroleumsskatt 382 · selskap fastland 110 · grunnrente 17 · andre 12</div>
          <div class="hl hl3"><span class="hlk">Selskapsskatt fastland</span><span class="hlv">110 mrd<small>10,2 % av forrige</small></span><div class="hld">Store 75 · mellomstore 28 · småbedrifter 7 (triangulert estimat)</div>
            <div class="hl hl4"><span class="hlk">Småbedrifter under 10 ansatte</span><span class="hlv">~7 mrd<small>6,4 % av forrige</small></span><div class="hld">593 777 bedrifter — 1 av hver 460. krone staten tar inn</div></div>
          </div>
        </div>
      </div>
    </div>
    <div class="note" style="margin-top:14px">Til sammenligning: <b>7 mrd</b> ≈ hele NRKs årlige bevilgning (7,2 mrd, 2024). <b>110 mrd</b> ≈ over to forsvarsbudsjetter. Ingen offisiell SSB-tabell krysser skatt med selskapsstørrelse — splitten 75/28/7 er et triangulert estimat, resten er verifiserte tall.</div>

    <hr class="rule">
    <div class="eyebrow neutral">Oppdatering 2025 · foreløpig regnskap (SSB, mars 2026)</div>
    <h3>Petroleumsskatten faller videre; fastland og grunnrente stiger</h3>
    <table class="tbl">
      <thead><tr><th>Post (mrd. kr)</th><th class="num">2024</th><th class="num">2025</th><th class="num">Endring</th></tr></thead>
      <tbody>
        <tr><td>Offentlig forvaltning, totale inntekter</td><td class="num">3 218</td><td class="num">3 264</td><td class="num">+1,4 %</td></tr>
        <tr><td>Offentlig forvaltning, løpende utgifter</td><td class="num">2 441</td><td class="num">2 605</td><td class="num">+6,7 %</td></tr>
        <tr><td>Skatt på inntekt og formue</td><td class="num">1 079</td><td class="num">1 080</td><td class="num">+0,1 %</td></tr>
        <tr><td>Petroleumsskatt total</td><td class="num">382</td><td class="num">343</td><td class="num">−10,2 %</td></tr>
        <tr><td>Selskapsskatt fastland</td><td class="num">110</td><td class="num">115</td><td class="num">+4,5 %</td></tr>
        <tr><td>Grunnrenteskatt (utenom petroleum)</td><td class="num">17,1</td><td class="num">20,5</td><td class="num">+19,9 %</td></tr>
        <tr><td>Merverdiavgift</td><td class="num">387</td><td class="num">401</td><td class="num">+3,7 %</td></tr>
        <tr><td>Avgifter totalt</td><td class="num">528</td><td class="num">548</td><td class="num">+3,7 %</td></tr>
      </tbody>
    </table>
    <div class="tbl-cap">2025 = foreløpig regnskap (SSB 14668, mars 2026). Statsbudsjettet: utgifter 1 953 → 2 101 mrd; netto avsetning til SPU 356 → 184 mrd.</div>

    <hr class="rule">
    <div class="eyebrow neutral">Seks nøkkelinnsikter</div>
    <div class="grid2">
      <div class="box"><h4>1 · Ekstremt skjev pyramide</h4><p style="font-size:13px;margin:0">30 petroleumsselskap betaler ~55 ganger mer selskapsskatt enn 593 777 småbedrifter samlet. Per selskap er forskjellen ~250 millioner ganger.</p></div>
      <div class="box"><h4>2 · Selskapsskatt = toppen av isfjellet</h4><p style="font-size:13px;margin:0">Småbedriftene bidrar med ~7 mrd i selskapsskatt, men ~205 mrd samlet (personskatt, AGA, MVA, eierskatter). Selskapsskatten er bare 4 % av deres totale bidrag.</p></div>
      <div class="box"><h4>3 · Asymmetriske politikknapper</h4><p style="font-size:13px;margin:0">En endring i selskapsskattesatsen treffer ~58 % petroleum. «Selskapsskatt» som knapp er i Norge nesten alltid en petroleumsskatt.</p></div>
      <div class="box"><h4>4 · Eierskatter er små i proveny</h4><p style="font-size:13px;margin:0">Formues- og utbytteskatt utgjør ~63 mrd — under 6 % av skatten på inntekt og formue — men dominerer debatten.</p></div>
      <div class="box"><h4>5 · Konsentrasjon i toppen</h4><p style="font-size:13px;margin:0">De 0,5 % øverste (2 838 personer) betaler 28,6 % av all formuesskatt; flertallet betaler under 25 000 kr/år.</p></div>
      <div class="box"><h4>6 · Boligen er lavt verdsatt</h4><p style="font-size:13px;margin:0">Primærbolig er 26 % av bruttoformuen men har 75 % verdsettelsesrabatt — samme vridning OECD og rentefradrag-debatten peker på.</p></div>
    </div>
  </div>

  <!-- ================= SUB: EIERSKATT ================= -->
  <div class="subpanel" id="sub-eier">
    <div class="eyebrow neutral">Formues- og utbytteskatt · «nullskatteyter»-debatten</div>
    <h3>Små i proveny, store i debatt</h3>
    <p>Formues- og utbytteskatt er de to mest omstridte skattene — og blant de minste. Sammen ~63 mrd (under 6 % av de 1 079 mrd fra inntekt og formue). Det heteste spørsmålet er <em>hvem</em> som faktisk betaler.</p>
    <div class="kpis">
      <div class="kpi"><div class="v">31,8 <small>mrd</small></div><div class="l">Formuesskatt 2024 (NR; skattestat. 31,1)</div></div>
      <div class="kpi"><div class="v">701 482</div><div class="l">Personer som betaler formuesskatt (15,4 %)</div></div>
      <div class="kpi"><div class="v">28,6 %</div><div class="l">Av formuesskatt fra topp 0,5 % (2 838 pers.)</div></div>
      <div class="kpi"><div class="v">~31 <small>mrd</small></div><div class="l">Utbytteskatt (37,84 % effektiv sats)</div></div>
    </div>
    <div class="note" style="margin-top:6px"><b>Kildemerknad.</b> Formuesskatten oppgis med to korrekte SSB-kilder: <b>31,8 mrd</b> = nasjonalregnskapet (tab. 14668, post A1141), <b>~31,1 mrd</b> = skattestatistikkens fastsatte tall som ligger til grunn for tidsserien og betalertabellen (proveny = antall × snitt). Differansen er måleteknisk (~2 %). Fordelingstallene under er beregnet på 31,8-basis.</div>

    <hr class="rule">
    <div class="eyebrow neutral">Hvem betaler formuesskatt?</div>
    <h3>De 0,5 % øverste betaler nesten en tredjedel — flertallet nesten ingenting</h3>
    <table class="tbl">
      <thead><tr><th>Formuesskatt (kr)</th><th class="num">Antall personer</th></tr></thead>
      <tbody>
        <tr><td>1–9 999 (snitt 4 100)</td><td class="num">313 434</td></tr>
        <tr><td>10 000–24 999</td><td class="num">178 023</td></tr>
        <tr><td>25 000–49 999</td><td class="num">105 635</td></tr>
        <tr><td>50 000–99 999</td><td class="num">58 717</td></tr>
        <tr><td>100 000–349 999</td><td class="num">~46 000</td></tr>
        <tr><td>350 000–999 999</td><td class="num">7 193</td></tr>
        <tr><td><b>Over 1 mill. (snitt 3,2 mill.)</b></td><td class="num">2 838</td></tr>
      </tbody>
    </table>
    <div class="note">De 2 838 i toppen har snitt nettoformue <b>296,8 mill. kr</b> og bidrar med ~<b>9,1 mrd</b> = <b>28,6 %</b> av all formuesskatt. Men 70 % av betalerne betaler under 25 000 kr/år. <span class="small">(Kilde: SSB 08231 — alle tre tall verifisert eksakt.)</span></div>

    <hr class="rule">
    <div class="eyebrow neutral">Hva består formuen av?</div>
    <h3>Bruttoformue 8 292 mrd — boligen er stor, men lavt verdsatt</h3>
    <div style="margin:8px 0">
      <div class="dbar"><span class="dlab">Primærbolig</span><div class="track"><div class="fill a" style="width:100%"></div></div><span class="dv">2 186 (26,4 %)</span></div>
      <div class="dbar"><span class="dlab">Verdipapirer (aksjer/fond)</span><div class="track"><div class="fill g" style="width:87%"></div></div><span class="dv">1 900 (22,9 %)</span></div>
      <div class="dbar"><span class="dlab">Bankinnskudd</span><div class="track"><div class="fill" style="width:80%"></div></div><span class="dv">1 757 (21,2 %)</span></div>
      <div class="dbar"><span class="dlab">Sekundærbolig</span><div class="track"><div class="fill a" style="width:44%"></div></div><span class="dv">968 (11,7 %)</span></div>
      <div class="dbar"><span class="dlab">Annen finanskapital</span><div class="track"><div class="fill" style="width:33%"></div></div><span class="dv">~742 (8,9 %)</span></div>
      <div class="dbar"><span class="dlab">Annen eiendom/skog</span><div class="track"><div class="fill a" style="width:16%"></div></div><span class="dv">~354 (4,3 %)</span></div>
      <div class="dbar"><span class="dlab">Næringseiendom/løsøre</span><div class="track"><div class="fill g" style="width:3%"></div></div><span class="dv">62 (0,7 %)</span></div>
    </div>
    <div class="tbl-cap">Kilde: SSB 08815, 2024 (mrd. kr). Primærbolig har 75 % verdsettelsesrabatt opp til 10 mill.; aksjer 20 % rabatt (skattes 80 % av markedsverdi). Det er nettopp denne forskjellen som driver debatten.</div>

    <details class="formula" style="margin-top:18px">
      <summary>Utbytteskatt, historikk og «tilbake til 2020-nivå»-scenariet (vis mer)</summary>
      <div style="margin-top:14px">
        <h4>Utbytteskatt</h4>
        <p style="font-size:13px">Utbytte beskattes hos eieren med effektiv sats <b>37,84 %</b> (22 % × oppjusteringsfaktor 1,72 i 2024). I 2024 mottok <b>368 541 personer</b> utbytte på til sammen <b>85 mrd</b>; beregnet proveny ~<b>31 mrd</b>. Konsentrasjonen er enda sterkere enn for formuesskatt: 75,7 % mottar under 50 000 kr.</p>
        <h4 style="margin-top:14px">Historisk utvikling (skattestatistikk, fastsatt)</h4>
        <table class="tbl" style="font-size:12.5px">
          <thead><tr><th>År</th><th class="num">Betalere</th><th class="num">Proveny (mrd)</th><th>Kontekst</th></tr></thead>
          <tbody>
            <tr><td>2005</td><td class="num">1 175 706</td><td class="num">8,7</td><td>Bredt grunnlag, lave satser</td></tr>
            <tr><td>2014</td><td class="num">~615 000</td><td class="num">13,4</td><td>Solberg — start på reduksjon</td></tr>
            <tr><td>2017</td><td class="num">498 041</td><td class="num">15,3</td><td>Laveste antall betalere</td></tr>
            <tr><td>2020</td><td class="num">572 224</td><td class="num">16,9</td><td>Pandemiåret</td></tr>
            <tr><td>2022</td><td class="num">647 591</td><td class="num">25,9</td><td>Første år med skjerpelse</td></tr>
            <tr><td><b>2024</b></td><td class="num">701 482</td><td class="num">31,1</td><td>Rekordnivå proveny</td></tr>
          </tbody>
        </table>
        <p class="small">Formuesskatt 3,6× høyere enn i 2005; utbytte mottatt: 15 (2007) → 146 (2021, rekord før skattereform) → 85 mrd (2024). NR-serien ligger ~2 % høyere (8,6 → 31,8 mrd).</p>
        <h4 style="margin-top:14px">Scenario: reversering til 2020-nivå</h4>
        <p style="font-size:13px">Statisk provenytap ved å reversere all eierbeskatning til 2020-nivå: <b>~−11,7 mrd/år</b> (formuesskatt ~−6,6 + utbytteskatt ~−5,0). Atferdsjustert (NHH-tolkning/Civita): <b>realistisk 8–11 mrd</b> — lavere enn statisk fordi grunnlaget vokser når satsen kuttes. ~35 % av besparelsen går til de ~10 000 med størst formue/utbytte.</p>
        <div class="note"><b>Eksternt blikk:</b> OECD (2026) anbefaler å redusere formuesskatten til fordel for sterkere eiendoms- og arveskatt — se <a class="xlink" style="cursor:pointer" onclick="goView('data','oecd')">Data &amp; makro → OECD →</a>. Provenyberegningene gjøres i praksis i <a class="xlink" style="cursor:pointer" onclick="goModel('lotte')">LOTTE-modellen →</a>.</div>
      </div>
    </details>
  </div>

  <!-- ================= SUB: SMÅBEDRIFTER ================= -->
  <div class="subpanel" id="sub-smaa">
    <div class="eyebrow neutral">Småbedriftene under 10 ansatte · 90,2 % av alle bedrifter</div>
    <h3>593 777 bedrifter — men bare 7 mrd i selskapsskatt</h3>
    <div class="kpis">
      <div class="kpi"><div class="v">~7 <small>mrd</small></div><div class="l">Selskapsskatt 2024 (0,22 % av off. inntekter)</div></div>
      <div class="kpi"><div class="v">~770 000</div><div class="l">Sysselsatte (43 % av privat sektor)</div></div>
      <div class="kpi"><div class="v">12 000 <small>kr</small></div><div class="l">Snittskatt/bedrift — 2/3 betaler 0 kr</div></div>
      <div class="kpi"><div class="v">1,3</div><div class="l">Snitt ansatte (mest ENK og 1-pers. AS)</div></div>
    </div>

    <hr class="rule">
    <div class="eyebrow neutral">Fordeling innenfor segmentet</div>
    <h3>5–9-ansatte-bedriftene leverer halve skatten med under 7 % av antallet</h3>
    <table class="tbl">
      <thead><tr><th>Størrelse</th><th class="num">Bedrifter</th><th class="num">Sysselsatte</th><th class="num">Selskapsskatt</th><th class="num">Per bedrift</th></tr></thead>
      <tbody>
        <tr><td>0 ansatte (mest holding)</td><td class="num">450 559</td><td class="num">~158 000</td><td class="num">~1,1 mrd</td><td class="num">~2 400 kr</td></tr>
        <tr><td>1–4 ansatte</td><td class="num">102 882</td><td class="num">~309 000</td><td class="num">~2,5 mrd</td><td class="num">~24 000 kr</td></tr>
        <tr><td>5–9 ansatte</td><td class="num">40 336</td><td class="num">~303 000</td><td class="num">~3,5 mrd</td><td class="num">~87 000 kr</td></tr>
        <tr><td><b>Sum &lt; 10 ansatte</b></td><td class="num">593 777</td><td class="num">~770 000</td><td class="num">~7,1 mrd</td><td class="num">~12 000 kr</td></tr>
      </tbody>
    </table>
    <div class="tbl-cap">Antall bedrifter verifisert mot SSB 07091 (eksakt). 0-ansatte-segmentet er overveiende holdingselskap som betaler nesten ingen selskapsskatt pga. fritaksmodellen — beskatning skjer først ved utbytte.</div>

    <hr class="rule">
    <div class="eyebrow neutral">Næringer som dominerer småbedriftssegmentet (SSB 07091)</div>
    <table class="tbl">
      <thead><tr><th>Hovednæring</th><th class="num">Bedrifter</th><th class="num">Andel</th><th>Karakteristikk</th></tr></thead>
      <tbody>
        <tr><td>Faglig/teknisk (M)</td><td class="num">70 838</td><td class="num">12,4 %</td><td>Konsulenter, advokater, arkitekter</td></tr>
        <tr><td>Eiendom (L)</td><td class="num">66 388</td><td class="num">11,6 %</td><td>Domineres av holdingselskap</td></tr>
        <tr><td>Jordbruk/skog/fiske (A)</td><td class="num">64 831</td><td class="num">11,4 %</td><td>Mange ENK på gårdsbruk</td></tr>
        <tr><td>Bygg og anlegg (F)</td><td class="num">64 587</td><td class="num">11,3 %</td><td>Håndverkere, små entreprenører</td></tr>
        <tr><td>Varehandel (G)</td><td class="num">60 082</td><td class="num">10,5 %</td><td>Butikker, nettbutikker</td></tr>
        <tr><td>Helse og sosial (Q)</td><td class="num">46 534</td><td class="num">8,1 %</td><td>Privatpraksis, fysioterapeuter</td></tr>
        <tr><td>Andre næringer</td><td class="num">220 517</td><td class="num">38,7 %</td><td>Kultur, IKT, industri, transport m.m.</td></tr>
        <tr><td><b>Sum</b></td><td class="num">593 777</td><td class="num">100 %</td><td>—</td></tr>
      </tbody>
    </table>

    <hr class="rule">
    <div class="eyebrow neutral">Fullbilde · det skjulte bidraget</div>
    <h3>Selskapsskatten er bare 4 % av småbedriftenes totale bidrag på ~205 mrd</h3>
    <table class="tbl">
      <thead><tr><th>Skatteform</th><th class="num">Estimat</th><th>Hvordan beregnet</th></tr></thead>
      <tbody>
        <tr><td>Selskapsskatt</td><td class="num">~7 mrd</td><td>Triangulert estimat</td></tr>
        <tr><td>Personskatt fra ansatte</td><td class="num">~115 mrd</td><td>770 000 syss. × ~150 000 kr</td></tr>
        <tr><td>Arbeidsgiveravgift</td><td class="num">~50 mrd</td><td>lønnstakere × snittlønn × 14,1 %</td></tr>
        <tr><td>MVA fra omsetning</td><td class="num">~25 mrd</td><td>Andel av samlet MVA</td></tr>
        <tr><td>Eiernes utbytteskatt</td><td class="num">~6 mrd</td><td>Andel fra småbedriftseiere</td></tr>
        <tr><td>Eiernes formuesskatt</td><td class="num">~3 mrd</td><td>Arbeidende kapital</td></tr>
        <tr><td><b>Totalt</b></td><td class="num">~205 mrd</td><td>5–6 % av offentlige inntekter</td></tr>
      </tbody>
    </table>
    <div class="note"><b>Pedagogisk poeng:</b> selskapsskattedebatten gir et misvisende bilde av næringslivets faktiske skatteinnbetalinger — det reelle bidraget kommer fra sysselsetting og eierskap, ikke selskapsskatten. <span class="small">Anslagene er triangulerte (ingen SSB-tabell krysser skatt med selskapsstørrelse).</span></div>

    <hr class="rule">
    <div class="eyebrow neutral">Petroleum vs. småbedrifter — to ytterpunkter</div>
    <table class="tbl">
      <thead><tr><th></th><th class="num">Petroleum (30 selskap)</th><th class="num">Småbedrifter (&lt;10 ans.)</th></tr></thead>
      <tbody>
        <tr><td>Antall selskap</td><td class="num">30</td><td class="num">593 777</td></tr>
        <tr><td>Sysselsatte</td><td class="num">~30 000</td><td class="num">~770 000</td></tr>
        <tr><td>Selskapsskatt</td><td class="num">382 mrd</td><td class="num">~7 mrd</td></tr>
        <tr><td>Skatt per selskap</td><td class="num">12,7 mrd</td><td class="num">~12 000 kr</td></tr>
        <tr><td>Skatt per ansatt</td><td class="num">12,7 mill.</td><td class="num">~9 000 kr</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ================= SUB: SCENARIER & HISTORIKK ================= -->
  <div class="subpanel" id="sub-scenario">
    <div class="eyebrow neutral">Hva skjer hvis selskapsskatten endres? · statisk, før atferd</div>
    <h3>En generell selskapsskatt-endring er først og fremst en petroleumsskatt-endring</h3>
    <div class="grid2">
      <div>
        <div class="box" style="margin-bottom:8px"><h4>22 % → 20 % (kutt) · statisk −19 mrd/år</h4></div>
        <table class="tbl" style="font-size:12.5px">
          <thead><tr><th>Segment</th><th class="num">22 %</th><th class="num">20 %</th><th class="num">Endring</th></tr></thead>
          <tbody>
            <tr><td>Petroleum (ordinær)</td><td class="num">121,0</td><td class="num">110,0</td><td class="num">−11,0</td></tr>
            <tr><td>Store fastland (≥100)</td><td class="num">47,0</td><td class="num">42,7</td><td class="num">−4,3</td></tr>
            <tr><td>Mellomstore (10–99)</td><td class="num">28,0</td><td class="num">25,5</td><td class="num">−2,5</td></tr>
            <tr><td>Småbedrifter (&lt;10)</td><td class="num">7,1</td><td class="num">6,5</td><td class="num">−0,6</td></tr>
            <tr><td>Finans (alt 25 %)</td><td class="num">29,6</td><td class="num">29,6</td><td class="num">0</td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <div class="box" style="margin-bottom:8px"><h4>22 % → 25 % (økning) · statisk +28,5 mrd/år</h4></div>
        <table class="tbl" style="font-size:12.5px">
          <thead><tr><th>Segment</th><th class="num">22 %</th><th class="num">25 %</th><th class="num">Endring</th></tr></thead>
          <tbody>
            <tr><td>Petroleum (ordinær)</td><td class="num">121,0</td><td class="num">137,5</td><td class="num">+16,5</td></tr>
            <tr><td>Store fastland (≥100)</td><td class="num">47,0</td><td class="num">53,4</td><td class="num">+6,4</td></tr>
            <tr><td>Mellomstore (10–99)</td><td class="num">28,0</td><td class="num">31,8</td><td class="num">+3,8</td></tr>
            <tr><td>Småbedrifter (&lt;10)</td><td class="num">7,1</td><td class="num">8,1</td><td class="num">+1,0</td></tr>
            <tr><td>Finans (alt 25 %)</td><td class="num">29,6</td><td class="num">29,6</td><td class="num">0</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="note"><b>Petroleum bærer ~58 %</b> av en hvilken som helst generell satsendring. <b>Modellkobling:</b> slike statiske provenyberegninger er nettopp det <a class="xlink" style="cursor:pointer" onclick="goModel('lotte')">LOTTE-modellen →</a> gjør; atferdseffekter krever LOTTE-Arbeid.</div>

    <hr class="rule">
    <div class="eyebrow neutral">Tidsserie 2020–2025 · verifisert (SSB 14668)</div>
    <h3>Seks ekstraordinære år: pandemi, energikrise, oljerekord, normalisering</h3>
    <div class="matrix-scroll">
    <table class="tbl" style="font-size:12px">
      <thead><tr><th>År</th><th class="num">Total off. innt.</th><th class="num">Skatt innt./formue</th><th class="num">Petroleum</th><th class="num">Selskap fastland</th><th class="num">Grunnrente</th><th class="num">MVA</th></tr></thead>
      <tbody>
        <tr><td>2020</td><td class="num">1 875</td><td class="num">517</td><td class="num">17</td><td class="num">78,0</td><td class="num">3,9</td><td class="num">312</td></tr>
        <tr><td>2021</td><td class="num">2 449</td><td class="num">911</td><td class="num">299</td><td class="num">103,9</td><td class="num">20,9</td><td class="num">339</td></tr>
        <tr><td>2022</td><td class="num">3 618</td><td class="num">1 552</td><td class="num">883</td><td class="num">120,4</td><td class="num">47,1</td><td class="num">372</td></tr>
        <tr><td>2023</td><td class="num">3 192</td><td class="num">1 145</td><td class="num">465</td><td class="num">120,4</td><td class="num">29,0</td><td class="num">378</td></tr>
        <tr><td>2024</td><td class="num">3 218</td><td class="num">1 079</td><td class="num">382</td><td class="num">109,5</td><td class="num">17,1</td><td class="num">387</td></tr>
        <tr><td><b>2025</b></td><td class="num">3 264</td><td class="num">1 080</td><td class="num">343</td><td class="num">114,5</td><td class="num">20,5</td><td class="num">401</td></tr>
      </tbody>
    </table>
    </div>
    <div class="tbl-cap">Mrd. kr. Petroleumsskatten er mest volatil: 17 (2020) → 883 (2022, energikrise) → 343 (2025). Mellom 2021 og 2022 nesten tredoblet den seg; fastlandsselskapsskatten økte bare 16 %.</div>
  </div>

  <!-- ================= SUB: PERSPEKTIVER ================= -->
  <div class="subpanel" id="sub-perspektiv">
    <div class="eyebrow neutral">Politisk kontekst · samme tall, to fortolkninger</div>
    <h3>Tallene er ikke nøytrale i debatten — her er begge sider</h3>
    <p>I juli 2024 viste en SSB-rapport at <b>24 800 personer</b> betalte formuesskatt, men ingen inntektsskatt, i 2022 — av disse <b>230</b> med formue over 50 mill. kr. «Nullskatteyter»-begrepet ble en politisk kampsak. Slik tolker de to sidene de samme tallene:</p>
    <div class="grid2">
      <div class="persp lo">
        <div class="stag">Klassekampen / LO / Vedum</div>
        <h4>«Det finnes velstående nullskatteytere»</h4>
        <p>230 personer med formue over 50 mill. kr betalte ingen inntektsskatt i 2022. Formuesskatten er «siste skanse» som sikrer at de superrike bidrar.</p>
        <p>Formue er ekstremt skjevt fordelt — de 10 % rikeste eier halvparten. Formuesskatten bidrar med 30+ mrd. og motvirker ulikhet.</p>
        <p class="pk">Kilde: Klassekampen 12.07.2024; LO; TV2 «Norges 470 rikeste» (2026).</p>
      </div>
      <div class="persp civita">
        <div class="stag">Civita / Mathilde Fasting</div>
        <h4>«Begrepet er villedende»</h4>
        <p>Av de 24 800 har 22 400 (90 %) formue under 10 mill. — typisk pensjonister lignet med ektefelle. 66 % har så lav pensjon at fradraget fjerner inntektsskatten.</p>
        <p>Av de 500 med formue over 25 mill. som «kun betalte formuesskatt» i 2022, betalte 60 % inntektsskatt i 2021. Permanent nullskatteyter er praktisk talt umulig.</p>
        <p class="pk">Kilde: Civita-notat «Nullskatteytere flest er ikke rike» (2025); SSB; BI.</p>
      </div>
    </div>

    <div class="box" style="margin-top:16px">
      <h4>Seks faktasjekkede påstander</h4>
      <ul class="tight" style="font-size:12.5px;margin:0">
        <li><b>Størrelse:</b> formuesskatt ~31,8 mrd = 1 % av offentlige inntekter, 3 % av skatt på inntekt og formue.</li>
        <li><b>Hvem:</b> 701 482 betaler (15,4 %); 28,6 % av provenyet fra de 0,5 % øverste.</li>
        <li><b>«Bedriftsskatt»?</b> Delvis — 22,9 % av formuen er verdipapirer; resten er bolig, bankinnskudd m.m.</li>
        <li><b>Velstående nullskatteytere?</b> Ja, men få (230 over 50 mill.); de fleste betaler inntektsskatt over tid.</li>
        <li><b>Konkurranseulempe?</b> Ja — utenlandske eiere betaler ikke norsk formues- eller utbytteskatt.</li>
        <li><b>Politikk 2025–26:</b> bunnfradrag 1,76 mill., aksjerabatt 20 %, utbytteskatt 37,84 %; større reform varslet 2027.</li>
      </ul>
    </div>

    <hr class="rule">
    <div class="eyebrow neutral">Reversering til 2020-nivå · hva koster det?</div>
    <h3>Anslagene spriker etter hvor sterke atferdseffekter man tror på</h3>
    <table class="tbl">
      <thead><tr><th>Tilnærming</th><th class="num">Provenytap/år</th><th>Forutsetning</th></tr></thead>
      <tbody>
        <tr><td>Ren statisk beregning</td><td class="num">−11,7 mrd</td><td>Ingen atferdseffekter</td></tr>
        <tr><td>NHH-tolkning (Næss)</td><td class="num">−9,7 mrd</td><td>Begrensede effekter; liten utflytting</td></tr>
        <tr><td>Civita (lavt)</td><td class="num">−8,6 mrd</td><td>Moderate dynamiske effekter</td></tr>
        <tr><td>Civita (høyt)</td><td class="num">−5,7 mrd</td><td>Full dynamikk over 5–10 år</td></tr>
        <tr><td><b>Realistisk anslag</b></td><td class="num">8–11 mrd</td><td>≈ 0,3 % av offentlige inntekter</td></tr>
      </tbody>
    </table>
    <div class="grid2" style="margin-top:14px">
      <div class="persp civita">
        <div class="stag">Pro reversering</div>
        <h4>Civita / Høyre / NHO</h4>
        <p>Reversering koster 7,5–12 mrd. (~0,4 % av inntektene), men frigjør kapital til investeringer og demper utflytting. Norge er ett av få land med både formues- og høy utbytteskatt — konkurranseulempen er strukturell.</p>
        <p>Atferdseffekter gjør faktisk tap mindre enn 11,7 mrd. — trolig 7,5–9 mrd.</p>
      </div>
      <div class="persp lo">
        <div class="stag">Mot reversering</div>
        <h4>LO / Klassekampen / SV</h4>
        <p>Skattekutt for de aller rikeste: ~35 % av besparelsen går til de ~10 000 med størst formue og utbytte. Det er omfordeling oppover, ikke næringsstimulering — pengene kunne gått til velferd.</p>
        <p>Atferdsargumentet er empirisk usikkert: da utbytteskatten økte 2022–23, falt utbyttene bare midlertidig.</p>
      </div>
    </div>

    <details class="formula" style="margin-top:16px">
      <summary>Fire dokumenterte atferdsmekanismer (vis mer)</summary>
      <ul class="tight" style="font-size:12.5px;margin-top:12px">
        <li><b>1 · Utbytte-elastisitet (Civita 0,3–0,5):</b> lavere sats → mer uttak. 2021-utbyttet (146 mrd. vs. 64 året før) viser tilpasning før varslet økning. Gjeninnvinning ~2,5 mrd.</li>
        <li><b>2 · Økt investering (Civita/NyAnalyse/BI):</b> norske eiere tar ut ~dobbelt så mye utbytte som utenlandske for å betale formuesskatt; reversering kan gi 0,5–1,0 mrd. i økt selskapsskatt. NHH er skeptisk.</li>
        <li><b>3 · Utflytting:</b> Civita/Høyre knytter 25–50 utflyttinger (Røkke m.fl.) til skjerpelsen (1–3 mrd./år). NHH (Næss): faktisk tap kun 0,77 mrd. — hovedmotivet var «5-årsregelen», ikke formuesskatten.</li>
        <li><b>4 · Sysselsetting (Frischsenteret, omstridt):</b> økt formuesskatt kan øke sysselsettingen i SMB (humankapital er utenfor grunnlaget). Effekten av reversering er teoretisk usikker.</li>
      </ul>
    </details>

    <div class="note" style="margin-top:16px"><b>Sammenstilling med hovedfunnet.</b> Petroleum styrer det store bildet (382 mrd. fra ~30 selskap). Men eierbeskatningen viser at <b>noen tusen privatpersoner</b> — gründere og bedriftseiere — bidrar med 30+ mrd. i formues- og utbytteskatt direkte fra eierskap i norsk næringsliv, i tillegg til selskapsskatten. <b>Eksternt blikk:</b> OECD (2026) anbefaler å vri fra formuesskatt mot eiendoms- og arveskatt — se <a class="xlink" style="cursor:pointer" onclick="goView('data','oecd')">Data &amp; makro → OECD →</a>.</div>
  </div>

  <div class="src">
    <b>Kilder.</b> SSB tabell 14668 (offentlige inntekter, oppdatert 08.06.2026), 08231 (formuesskatt), 07091 (bedrifter), 08815 (bruttoformue), 10486 (statsregnskap); Statsrekneskapen 2025 (regjeringen.no); DFØ. Hovedtall verifisert mot primærkilde juni 2026. Splitt av selskapsskatt på selskapsstørrelse og samlet småbedriftsbidrag er triangulerte estimater (ingen offisiell tabell krysser skatt med størrelse).
  </div>
</section>
</section>
"""

produktiv_view = """<section class="view" id="view-produktiv">
<section class="card">
  <div class="eyebrow">Produktivitet · langsiktsdriveren i hele apparatet</div>
  <h2>Produktivitetsdebatten — arbeidsproduktivitet, TFP og Bech Holte-striden</h2>
  <div class="governing">Produktivitet bestemmer levestandarden på lang sikt og er den eksogene driveren i nesten alle modellene. De siste 2–3 årene har det rast en strid om hvor svak den norske utviklingen egentlig er, hvordan den måles, og hvorfor den har falt.</div>
  <div class="subtabs">
    <button class="subtab active" data-sub="maaling">Måling &amp; begreper</button>
    <button class="subtab" data-sub="debatt">Debatten</button>
    <button class="subtab" data-sub="tall">Data &amp; internasjonalt</button>
    <button class="subtab" data-sub="modeller">Kobling til modellene</button>
  </div>

  <!-- ===== SUB: MÅLING ===== -->
  <div class="subpanel active" id="sub-maaling">
    <div class="eyebrow neutral">To mål på produktivitet — og hvorfor de ikke er det samme</div>
    <h3>Arbeidsproduktivitet teller maskiner med; TFP er den «ekte» effektiviteten — og et residual</h3>
    <div class="grid2">
      <div class="box"><h4>Arbeidsproduktivitet</h4><p style="font-size:13px;margin:0">Verdiskaping (bruttoprodukt) per timeverk. Lett å måle — men stiger også når hver arbeider får <b>mer kapital</b> (maskiner, bygg, IKT), uten at effektiviteten i seg selv øker. Det er dette tallet som oftest siteres.</p></div>
      <div class="box accent"><h4>Totalfaktorproduktivitet (TFP)</h4><p style="font-size:13px;margin:0">Solow-residualen: den delen av veksten som <b>ikke</b> forklares av mer arbeid og kapital — teknologi, organisering, effektivitet. Fordi det er et <b>residual</b>, arver det alle målefeil i kapital, kapasitetsutnyttelse og priser. Kjernen i striden.</p></div>
    </div>

    <div class="eq" style="margin-top:14px">
      <span class="c">// vekstregnskap (Solow): produksjon = teknologi × innsatsfaktorer</span><br>
      <span class="v2">Y</span> = <span class="hl">A</span> · F(<span class="v2">K</span>, <span class="v2">L</span>)<br><br>
      <span class="c">// dekomponering av BNP-vekst</span><br>
      vekst <span class="v2">Y</span> = α<sub>K</sub>·vekst <span class="v2">K</span> + α<sub>L</sub>·vekst <span class="v2">L</span> + <span class="hl">vekst A (TFP)</span><br><br>
      <span class="c">// arbeidsproduktivitet = kapitaldybde + TFP</span><br>
      vekst (<span class="v2">Y/L</span>) = α<sub>K</sub>·vekst (<span class="v2">K/L</span>) + <span class="hl">TFP</span>
    </div>
    <div class="eq-cap"><span class="inject"></span>α<sub>K</sub>, α<sub>L</sub> = kapitalens og arbeidets andel av verdiskapingen. TFP framkommer som «det som blir til overs» — derfor er det følsomt for hvordan kapital og timeverk måles.</div>

    <div class="eyebrow neutral" style="margin-top:18px">Hvorfor TFP-fallet ser dramatisk ut — vekstregnskap (illustrativt)</div>
    <svg viewBox="0 0 1000 200" role="img" aria-label="Dekomponering av BNP-vekst, gullalder vs nå">
      <text x="64" y="46" text-anchor="end" font-size="11" font-weight="700" fill="#13233a" font-family="Consolas,monospace">~1995</text>
      <rect x="70" y="32" width="192" height="34" fill="#3a4a8c"/><rect x="262" y="32" width="192" height="34" fill="#9a7b1f"/><rect x="454" y="32" width="336" height="34" fill="#c0552b"/>
      <text x="790" y="54" font-size="11" font-weight="700" fill="#13233a" font-family="Consolas,monospace"> = 3,0 %</text>
      <text x="64" y="124" text-anchor="end" font-size="11" font-weight="700" fill="#13233a" font-family="Consolas,monospace">nå</text>
      <rect x="70" y="110" width="144" height="34" fill="#3a4a8c"/><rect x="214" y="110" width="120" height="34" fill="#9a7b1f"/><rect x="334" y="110" width="48" height="34" fill="#c0552b"/>
      <text x="382" y="132" font-size="11" font-weight="700" fill="#13233a" font-family="Consolas,monospace"> = 1,3 %</text>
      <g font-family="-apple-system,Segoe UI,sans-serif" font-size="11">
        <rect x="70" y="172" width="12" height="12" fill="#3a4a8c"/><text x="88" y="182" fill="#5d6b80">arbeidsinnsats</text>
        <rect x="230" y="172" width="12" height="12" fill="#9a7b1f"/><text x="248" y="182" fill="#5d6b80">kapitaldybde</text>
        <rect x="390" y="172" width="12" height="12" fill="#c0552b"/><text x="408" y="182" fill="#5d6b80">TFP (effektivitet)</text>
      </g>
    </svg>
    <div class="fig-cap">Illustrativt vekstregnskap: det er særlig <b>TFP-leddet</b> (terrakotta) som har krympet. Fordi TFP er et residual, er nettopp dette leddet mest utsatt for målefeil — kjernen i Holm-kritikken.</div>

    <div class="flag">
      <b>Måleproblemene som driver striden.</b> (1) Petroleum/sokkel er ekstremt kapitalintensiv og volatil — derfor måles <b>Fastlands-Norge</b>. (2) I offentlig sektor måles produksjon ofte via innsats, så produktivitetsvekst der blir definitorisk nær null. (3) Kapitalbeholdning, kapasitetsutnyttelse over konjunkturen og prisindekser er vanskelige å måle — og alt slår inn i TFP-residualen.
    </div>
  </div>

  <!-- ===== SUB: DEBATTEN ===== -->
  <div class="subpanel" id="sub-debatt">
    <div class="eyebrow neutral">Striden 2024–2026 · samme tall, ulike fortolkninger</div>
    <h3>Alle er enige om at veksten falt — uenige om hvorfor og hvor mye</h3>
    <p>Martin Bech Holtes «Landet som ble for rikt» (2025) ble en bestselger (60 000+) og utløste en av de mest omstridte økonomidebattene på flere år. Tesen møtte sterk faglig motstand fra tre ulike hold:</p>
    <div class="persp acc" style="margin-bottom:12px">
      <div class="stag">Tesen · Martin Bech Holte (eks-McKinsey)</div>
      <h4>«Landet som ble for rikt» — oljefond-fellen</h4>
      <p>Norge hadde et produktivitetsmirakel ca. 1991–2013, men siden ~2015 nær null vekst. Kapitalproduktiviteten skal ha falt &gt;8 % på 15–20 år. Årsak: landet ble for rikt og selvtilfreds, offentlig sektor blåste seg opp, og kapital ble feilallokert til bolig og lavproduktive tjenester. Metode: Solow/TFP.</p>
    </div>
    <div class="grid3">
      <div class="persp civita"><div class="stag">Målingen · Martin Blomhoff Holm (UiO)</div><h4>«Data som fanden leser bibelen»</h4><p>TFP-beregningene er metodisk svake — «fant en fortelling først, bygde så modeller som bekreftet den». Selve «gullalderen» 1991–2013 er delvis et statistisk artefakt.</p></div>
      <div class="persp teal"><div class="stag">Årsaken · Harald Magnus Andreassen (SB1 Markets)</div><h4>«Grovt og voldsomt feil»</h4><p>Produktivitetsfallet er <b>internasjonalt</b> — det har falt til samme lave nivå i nær alle rike land etter ~2005/2008. Da kan ikke «Norge ble for rikt og lat» være forklaringen.</p></div>
      <div class="persp lo"><div class="stag">Historien · SSB-forskere / BI</div><h4>«Gullalderen har aldri eksistert»</h4><p>1990-tallsveksten skyldtes forskning og nyvinninger (innovasjonsøkosystem som Sintef), ikke bare markedsliberalisering. Gullalderen i Holtes form er en myte.</p></div>
    </div>
    <div class="note" style="margin-top:14px"><b>Hva Bech Holte innrømmet.</b> Etter kritikken erkjente han at han «uttrykte seg sterkere om samlet produktivitetsutvikling enn han hadde grunnlag for», og at han «må gjøre TFP-analysen annerledes» — men holdt fast ved at fallende kapitalproduktivitet er et reelt politikkproblem.</div>
    <div class="grid2" style="margin-top:14px">
      <div class="box"><h4>✓ Felles grunn</h4><p style="font-size:13px;margin:0">Produktivitetsveksten <b>er</b> klart lavere nå enn på 1990- og 2000-tallet. Det er et reelt og viktig problem for norsk levestandard.</p></div>
      <div class="box accent"><h4>✕ Uenigheten</h4><p style="font-size:13px;margin:0"><b>Årsak:</b> norsk særtrekk (oljerikdom) vs. globalt fenomen. <b>Måling:</b> hvor dramatisk fallet er, og om «gullalderen» i det hele tatt er reell.</p></div>
    </div>
  </div>

  <!-- ===== SUB: DATA ===== -->
  <div class="subpanel" id="sub-tall">
    <div class="eyebrow neutral">Hva tallene viser</div>
    <h3>Produktivitetsveksten er omtrent halvert — og det er et internasjonalt mønster</h3>
    <svg viewBox="0 0 1000 210" role="img" aria-label="Arbeidsproduktivitetsvekst Fastlands-Norge over perioder">
      <line x1="70" y1="160" x2="950" y2="160" stroke="#5d6b80" stroke-width="1.2"/>
      <g stroke="#eef1f6"><line x1="70" y1="120" x2="950" y2="120"/><line x1="70" y1="80" x2="950" y2="80"/><line x1="70" y1="40" x2="950" y2="40"/></g>
      <g font-family="Consolas,monospace" font-size="10" fill="#8a97a8"><text x="64" y="163" text-anchor="end">0</text><text x="64" y="123" text-anchor="end">0,5</text><text x="64" y="83" text-anchor="end">1,0</text><text x="64" y="43" text-anchor="end">1,5</text></g>
      <rect x="120" y="32" width="130" height="128" fill="#3a4a8c"/><text x="185" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#3a4a8c" font-family="Consolas,monospace">1,6</text>
      <rect x="340" y="64" width="130" height="96" fill="#3a4a8c"/><text x="405" y="56" text-anchor="middle" font-size="13" font-weight="700" fill="#3a4a8c" font-family="Consolas,monospace">1,2</text>
      <rect x="560" y="96" width="130" height="64" fill="#9aa6c4"/><text x="625" y="88" text-anchor="middle" font-size="13" font-weight="700" fill="#7a86a4" font-family="Consolas,monospace">~0,8</text>
      <rect x="780" y="120" width="130" height="40" fill="#9aa6c4"/><text x="845" y="112" text-anchor="middle" font-size="13" font-weight="700" fill="#7a86a4" font-family="Consolas,monospace">~0,5</text>
      <g font-family="-apple-system,Segoe UI,sans-serif" font-size="10.5" fill="#5d6b80" text-anchor="middle"><text x="185" y="178">1986–2001</text><text x="405" y="178">2001–2016</text><text x="625" y="178">2007–2019</text><text x="845" y="178">2015–2024</text></g>
      <text x="510" y="200" text-anchor="middle" font-size="9.5" font-style="italic" fill="#8a97a8">arbeidsproduktivitetsvekst Fastlands-Norge, %/år · blass = lavere presisjon/illustrativt</text>
    </svg>
    <div class="fig-cap">Kilder: SSB / Samfunnsøkonomisk analyse (de to første periodene er dokumenterte snitt; de to siste er omtrentlige, i tråd med at veksten «mer enn halverte seg» fra 1998–2006 til 2007–2019).</div>

    <table class="tbl" style="margin-top:8px">
      <thead><tr><th>Indikator</th><th class="num">Verdi</th><th>Kilde</th></tr></thead>
      <tbody>
        <tr><td>Arbeidsproduktivitetsvekst, Fastlands-Norge 1986–2001</td><td class="num">1,6 %/år</td><td>SSB</td></tr>
        <tr><td>Samme, 2001–2016</td><td class="num">1,2 %/år</td><td>SSB / Produktivitetskommisjonen (NOU 2015:1)</td></tr>
        <tr><td>Arbeidsproduktivitet, hele økonomien (indeks 2021=1)</td><td class="num">~flat 2023–26</td><td>OECD EO 119</td></tr>
        <tr><td>BNP per innbygger, vekst 2013→2024</td><td class="num">~+10 % totalt</td><td>SSB</td></tr>
        <tr><td>Bygg og anlegg — produktivitet</td><td class="num">fall</td><td>SSB</td></tr>
      </tbody>
    </table>

    <div class="grid2" style="margin-top:14px">
      <div class="box"><h4>«The productivity puzzle»</h4><p style="font-size:13px;margin:0">Produktivitetsveksten falt i nær alle rike land etter finanskrisen 2008 — et internasjonalt fenomen økonomene fortsatt ikke fullt ut forstår. Det er Andreassens hovedpoeng mot en rent norsk forklaring.</p></div>
      <div class="box"><h4>OECDs diagnose (2026)</h4><p style="font-size:13px;margin:0">«Underlying productivity growth has slowed»; Norges forsprang eroderes; PISA-fallet kan redusere langsiktig produktivitet med ~3 %. OECD peker på <b>strukturelle</b> årsaker (regulering, utdanning) — se <a class="xlink" style="cursor:pointer" onclick="goView('data','oecd')">Data &amp; makro → OECD →</a>.</p></div>
    </div>
  </div>

  <!-- ===== SUB: MODELLER ===== -->
  <div class="subpanel" id="sub-modeller">
    <div class="eyebrow neutral">Hvorfor dette er dashbordets dypeste kobling</div>
    <h3>Produktivitet er den eneste driveren som hever trendveksten varig</h3>
    <p>Konjunkturdriverne (rente, oljepengebruk, krone) flytter økonomien <em>rundt</em> trenden. Produktivitet flytter selve trenden — derfor er den eksogen inngang i nær alle modellene:</p>
    <table class="tbl">
      <thead><tr><th>Modell</th><th>Hvordan produktivitet inngår</th></tr></thead>
      <tbody>
        <tr><td><span class="mb econ">KVARTS / MODAG</span></td><td>Tilbudssiden bestemmer langsiktig nivå; produktivitet inngår i frontfags-lønnsdannelsen og bestemmer reallønnsrommet</td></tr>
        <tr><td><span class="mb cge">SNOW / MSG</span></td><td>Teknisk endring (A i CES-funksjonen) er den sentrale langsiktige vekstmotoren</td></tr>
        <tr><td><span class="mb cge">DEMEC</span></td><td>Produktivitet + demografi avgjør om velferdsstaten er bærekraftig (Perspektivmeldingen)</td></tr>
        <tr><td><span class="mb dsge">NEMO</span></td><td>Trendveksten bestemmer potensiell produksjon og den nøytrale realrenten r*</td></tr>
      </tbody>
    </table>
    <div class="note" style="margin-top:14px"><b>Prøv det selv:</b> i <a class="xlink" style="cursor:pointer" onclick="location.hash='#simulator'">Simulatoren →</a> er produktivitetsvekst (0,7 % i dag) den eneste driveren som varig løfter Fastlands-BNP-banen — de andre dør ut når økonomien finner tilbake til trend. Det er nettopp dette tallet hele Bech Holte-debatten dreier seg om.</div>
    <div class="flag"><b>Koblingen til resten av dashbordet.</b> Bech Holtes «oljefond-felle» er en Dutch disease-variant: oljerikdom som svekker produktiviteten i fastlandsøkonomien. Det speiler <a class="xlink" style="cursor:pointer" onclick="goView('data','olje')">oljepengebruk-seksjonen</a> og handlingsregelen, og er en strukturell parallell til essayets kritikk av gjeld og pengeskaping — to fortellinger om hvordan oljeformuen kan forme norsk økonomi.</div>
  </div>

  <div class="src">
    <b>Kilder.</b> Martin Bech Holte (2025): «Landet som ble for rikt», Kagge. Kritikk: Martin Blomhoff Holm (UiO, Økonomisk institutt); Harald Magnus Andreassen (SpareBank 1 Markets); SSB-forskere (VG); Pål Nygaard (BI): «Bech Holte og de mytiske 1990-årene». Data: SSB (produktivitetsberegninger for næringer; bygg/anlegg), Produktivitetskommisjonen (NOU 2015:1), Samfunnsøkonomisk analyse (2025), OECD Economic Outlook 119 og Survey 2026. Vekstregnskaps-figuren er illustrativ; periodetallene 2007–2019 og 2015–2024 er omtrentlige.
  </div>
</section>
</section>
"""

sim_skatt_tabs = "(function(){document.querySelectorAll('.view').forEach(function(v){var tabs=v.querySelectorAll('.subtab'),pans=v.querySelectorAll('.subpanel');if(!tabs.length)return;tabs.forEach(function(t){t.addEventListener('click',function(){tabs.forEach(function(x){x.classList.remove('active')});t.classList.add('active');var id=t.getAttribute('data-sub');pans.forEach(function(p){p.classList.toggle('active',p.id==='sub-'+id)});});});});})();"

sim_view = """<section class="view" id="view-simulator">
<section class="card">
  <div class="eyebrow">Interaktiv · scenariet settes av deg</div>
  <h2>Scenariosimulator — skru på driverne, se hvor økonomien peker</h2>
  <div class="sim-banner"><b>⚑ Les dette først.</b> Dette er en <b>gjennomsiktig, forenklet emulator</b> kalibrert på de dokumenterte elastisitetene i NEMO, MODAG/NORA og OECD — <b>ikke</b> en kjøring av de faktiske modellene. Den ruller et lite ny-keynesiansk system <b>12 kvartaler (3 år) fram med etterslep</b> og tegner banene — med valgfri endogen rentebane (Taylor-regel). Den viser retning, styrke og <b>tempo</b> i transmisjonen, ikke en presis prognose. Startpunktet er dagens verifiserte verdier (juni 2026).</div>
  <div class="sim-presets" id="sim-presets"></div>
  <div class="sim-grid">
    <div>
      <div class="eyebrow neutral" style="margin-bottom:2px">Driverne · sett verdiene</div>
      <div id="sim-controls"></div>
    </div>
    <div>
      <div class="eyebrow neutral" style="margin-bottom:6px">Bane · 3 år fram, gitt modellene</div>
      <div class="sim-mode" id="sim-mode"></div>
      <div class="sim-charts" id="sim-charts"></div>
      <div class="sim-trans" id="sim-trans"></div>
    </div>
  </div>
  <details class="formula">
    <summary>Slik regner simulatoren — alle koeffisienter (klikk for å vise)</summary>
    <div class="eq">
      <span class="c">// kvartalsvis dynamikk over 12 kvartaler — stilisert ny-keynesiansk system</span><br>
      <span class="c">// produksjonsgap (treg IS, lagget realrente)</span><br>
      yₜ = 0,80·yₜ₋₁ − 0,12·(rₜ₋₁ − r*) + 0,10·Δfisk + 0,045·Δverden + 0,6·Δolje − 0,012·Δkrone<br><br>
      <span class="c">// kjerneinflasjon (treg Phillips: persistens + anker + gap)</span><br>
      πₜ = 0,85·πₜ₋₁ + 0,15·π* + 0,25·yₜ + 0,14·Δlønn − 0,05·Δkrone + 1,2·Δolje − 0,08·Δprod<br><br>
      <span class="c">// pengepolitikk: Taylor-regel med rentegliding (kan slås av)</span><br>
      i*ₜ = r* + π* + 1,5·(πₜ − π*) + 0,5·yₜ ;&nbsp; iₜ = 0,7·iₜ₋₁ + 0,3·i*ₜ<br><br>
      <span class="c">// ledighet (Okun m/ treghet) og realrente</span><br>
      uₜ = 0,5·uₜ₋₁ + 0,5·(4,5 − 0,4·yₜ) ;&nbsp; rₜ = iₜ − πᵉₜ,&nbsp; πᵉₜ = 0,6·πₜ₋₁ + 0,4·π*
    </div>
    <p class="small" style="margin-top:8px">r* = 1 % (nøytral realrente), π* = 2 %. Startverdier = dagens (π₀ = 3,4, y₀ = 0, i₀ = din rente, u₀ = 4,5). Persistensen gir <b>etterslep</b> — renten virker på inflasjonen først etter flere kvartaler. Under Taylor-regelen er <b>rentebanen endogen</b>: den stiger når inflasjonen er over målet og faller når den nærmer seg, omtrent som NEMOs optimering. Fortsatt en forenklet, gjennomsiktig emulator forankret i modellenes dokumenterte parametre — ikke en kjøring av NEMO.</p>
  </details>
  <div class="src">
    <b>Dagens verdier (juni 2026):</b> styringsrente 4,25 % (Norges Bank); oljepengebruk 2,7 % av fondet (OECD/budsjett); Brent ~80 USD/fat; årslønnsvekst ~4,5 %; I-44 ~113,7 (Norges Bank); handelspartnervekst ~1,5 % og produktivitet ~0,7 % (OECD). Utfallenes utgangsverdier: Fastlands-BNP 1,7 %, KPI-JAE 3,4 %, ledighet 4,5 %, produksjonsgap ~0 %, boligprisvekst ~3 % (OECD EO 119 / Norges Bank PPR 2/26).
  </div>
</section>
</section>
"""

sim_script = r"""
var SIM_P=[
 {id:'rente',name:'Styringsrente',unit:'%',min:0,max:8,step:0.25,base:4.25,ch:'NEMO: realrente vs nøytral r*',tag:'NEMO',cls:'dsge',m:'nemo'},
 {id:'fisk',name:'Oljepengebruk (strukturelt underskudd)',unit:'% av fondet',min:0,max:4,step:0.1,base:2.7,ch:'MODAG/NORA: fiskal multiplikator',tag:'NORA',cls:'dsge',m:'nora'},
 {id:'olje',name:'Oljepris (Brent)',unit:'USD/fat',min:30,max:150,step:1,base:80,ch:'Terms of trade, krone, etterspørsel',tag:'SNOW',cls:'cge',m:'snow'},
 {id:'lonn',name:'Årslønnsvekst (frontfag)',unit:'%',min:1,max:8,step:0.1,base:4.5,ch:'NEMO Phillips + frontfagsmodellen',tag:'NEMO',cls:'dsge',m:'nemo'},
 {id:'krone',name:'Kronekurs (I-44)',unit:'% styrking',min:-20,max:20,step:1,base:0,disp:'krone',ch:'NEMO: valutakurskanal → importpriser',tag:'NEMO',cls:'dsge',m:'nemo'},
 {id:'verden',name:'Vekst hos handelspartnere',unit:'%',min:-2,max:5,step:0.1,base:1.5,ch:'KVARTS/NEMO: eksportetterspørsel',tag:'KVARTS',cls:'econ',m:'kvarts'},
 {id:'prod',name:'Produktivitetsvekst (fastland)',unit:'%',min:-1,max:3,step:0.1,base:0.7,ch:'Trendvekst, langsiktig',tag:'MODAG',cls:'econ',m:'modag'}
];
var simMode='rule';
var SIM_CHARTS=[
 {key:'pi',title:'Kjerneinflasjon (KPI-JAE)',min:0,max:6,target:2.0,color:'#1f6f6b'},
 {key:'rate',title:'Styringsrente',min:0,max:7,color:'#c0552b'},
 {key:'y',title:'Produksjonsgap',min:-4,max:4,target:0,color:'#3a4a8c'},
 {key:'u',title:'Arbeidsledighet',min:2,max:7,color:'#9a7b1f'}
];
var SIM_PRESET=[
 {n:'I dag',reset:true},
 {n:'Rentekutt −1 pp',s:{rente:3.25}},
 {n:'Oljeprisfall',s:{olje:55}},
 {n:'Lønnshopp',s:{lonn:6.5}},
 {n:'Kronesvekkelse −10 %',s:{krone:-10}},
 {n:'Innstramming',s:{rente:5.5,fisk:2.0}}
];
var simState={};
SIM_P.forEach(function(p){simState[p.id]=p.base;});
function simSimulate(s,mode){
 var T=12;
 var dfisk=s.fisk-2.7, doil=(s.olje-80)/80, dwage=s.lonn-4.5, dkrone=s.krone, dworld=s.verden-1.5, dprod=s.prod-0.7;
 var pi=[3.4], y=[0], rate=[s.rente], u=[4.5], g=[1.7];
 for(var t=1;t<=T;t++){
  var pe=0.6*pi[t-1]+0.4*2.0;
  var rr=rate[t-1]-pe;
  var yt=0.80*y[t-1]-0.12*(rr-1.0)+0.10*dfisk+0.045*dworld+0.6*doil-0.012*dkrone;
  var pit=0.85*pi[t-1]+0.15*2.0+0.25*yt+0.14*dwage-0.05*dkrone+1.2*doil-0.08*dprod;
  if(pit<0)pit=0;
  var it;
  if(mode==='rule'){ var istar=1.0+2.0+1.5*(pit-2.0)+0.5*yt; it=0.7*rate[t-1]+0.3*istar; if(it<0)it=0; }
  else { it=s.rente; }
  var ut=0.5*u[t-1]+0.5*(4.5-0.4*yt);
  var gt=1.7+1.0*dprod+0.7*(yt-y[t-1]);
  pi.push(pit); y.push(yt); rate.push(it); u.push(ut); g.push(gt);
 }
 return {pi:pi,rate:rate,y:y,u:u,g:g};
}
function simChart(cfg,base,scen){
 var W=320,H=120,pL=28,pR=10,pT=14,pB=20,n=scen.length;
 function X(i){return pL+(W-pL-pR)*i/(n-1);}
 function Y(v){var vv=Math.max(cfg.min,Math.min(cfg.max,v));return pT+(H-pT-pB)*(1-(vv-cfg.min)/(cfg.max-cfg.min));}
 function path(a){var d='';for(var i=0;i<a.length;i++){d+=(i?'L':'M')+X(i).toFixed(1)+','+Y(a[i]).toFixed(1)+' ';}return d;}
 var s='<svg viewBox="0 0 '+W+' '+H+'" class="simchart">';
 s+='<line x1="'+pL+'" y1="'+(H-pB)+'" x2="'+(W-pR)+'" y2="'+(H-pB)+'" stroke="#d4dae3"/>';
 if(cfg.target!==undefined){var ty=Y(cfg.target);s+='<line x1="'+pL+'" y1="'+ty.toFixed(1)+'" x2="'+(W-pR)+'" y2="'+ty.toFixed(1)+'" stroke="#2f7d4f" stroke-dasharray="4 3" stroke-width="1"/><text x="'+(W-pR)+'" y="'+(ty-3).toFixed(1)+'" text-anchor="end" font-size="8.5" fill="#2f7d4f" font-family="Consolas,monospace">mål '+cfg.target.toFixed(1).replace('.',',')+'</text>';}
 s+='<text x="2" y="'+(pT+4)+'" font-size="8.5" fill="#8a97a8" font-family="Consolas,monospace">'+cfg.max+'</text>';
 s+='<text x="2" y="'+(H-pB)+'" font-size="8.5" fill="#8a97a8" font-family="Consolas,monospace">'+cfg.min+'</text>';
 s+='<path d="'+path(base)+'" fill="none" stroke="#9aa6c4" stroke-width="1.4" stroke-dasharray="4 3"/>';
 s+='<path d="'+path(scen)+'" fill="none" stroke="'+cfg.color+'" stroke-width="2.2"/>';
 var ex=X(n-1),ey=Y(scen[n-1]);
 s+='<circle cx="'+ex.toFixed(1)+'" cy="'+ey.toFixed(1)+'" r="3" fill="'+cfg.color+'"/>';
 s+='<text x="'+(ex-4).toFixed(1)+'" y="'+(ey-6).toFixed(1)+'" text-anchor="end" font-size="10" font-weight="700" fill="'+cfg.color+'" font-family="Consolas,monospace">'+scen[n-1].toFixed(1).replace('.',',')+'</text>';
 var lab=['nå','+1 år','+2 år','+3 år'],pos=[0,4,8,12];
 for(var k=0;k<pos.length;k++){s+='<text x="'+X(pos[k]).toFixed(1)+'" y="'+(H-6)+'" text-anchor="middle" font-size="8.5" fill="#8a97a8" font-family="Consolas,monospace">'+lab[k]+'</text>';}
 s+='</svg>';
 return s;
}
function simFmt(p,v){
 if(p && p.disp==='krone'){ if(Math.abs(v)<0.5) return 'i dag'; return (v>0?'+':'')+Math.round(v)+' %'; }
 var dec = (p && p.step<1)?1:0;
 return v.toFixed(dec).replace('.',',');
}
function simJudge(o,val){
 var d=val-o.base; if(Math.abs(d)<0.05) return 'flat';
 var good;
 if(o.good==='up') good=d>0;
 else if(o.good==='down') good=d<0;
 else if(o.good==='t2') good=Math.abs(val-2)<Math.abs(o.base-2);
 else if(o.good==='t0') good=Math.abs(val)<Math.abs(o.base);
 else return 'flat';
 return good?'good':'bad';
}
function simRenderControls(){
 var c=document.getElementById('sim-controls'); if(!c) return; var h='';
 SIM_P.forEach(function(p){
  h+='<div class="slider-row">'
   +'<div class="slider-head"><div class="slider-name">'+p.name
   +' <span class="mtag mb '+p.cls+'" data-mlink="'+p.m+'" title="Åpne modellen">'+p.tag+'</span>'
   +'<span class="ch">'+p.ch+'</span></div>'
   +'<div class="slider-val"><span id="val-'+p.id+'">'+simFmt(p,simState[p.id])+'</span> '+(p.disp==='krone'?'':p.unit)
   +'<span class="base">i dag: '+simFmt(p,p.base)+(p.disp==='krone'?'':' '+p.unit)+'</span></div></div>'
   +'<input type="range" class="sl" id="sl-'+p.id+'" min="'+p.min+'" max="'+p.max+'" step="'+p.step+'" value="'+simState[p.id]+'">'
   +'</div>';
 });
 c.innerHTML=h;
 SIM_P.forEach(function(p){
  var el=document.getElementById('sl-'+p.id);
  el.addEventListener('input',function(){ simState[p.id]=parseFloat(el.value); document.getElementById('val-'+p.id).textContent=simFmt(p,simState[p.id]); simRenderOutputs(); });
 });
 c.querySelectorAll('[data-mlink]').forEach(function(t){ t.addEventListener('click',function(){ if(typeof goModel==='function') goModel(t.getAttribute('data-mlink')); }); });
}
function simRenderOutputs(){
 var box=document.getElementById('sim-charts'); if(!box) return;
 var scen=simSimulate(simState,simMode);
 var base=simSimulate({rente:4.25,fisk:2.7,olje:80,lonn:4.5,krone:0,verden:1.5,prod:0.7},simMode);
 var h='';
 SIM_CHARTS.forEach(function(c){
  var arrS=scen[c.key], arr0=base[c.key]; var endS=arrS[arrS.length-1], end0=arr0[arr0.length-1];
  var d=endS-end0; var dt=Math.abs(d)<0.05?'≈ referansebane':((d>0?'+':'')+d.toFixed(1).replace('.',',')+' pp vs. ref.');
  h+='<div class="simchart-card"><div class="simchart-head"><span class="simchart-title">'+c.title+'</span>'
   +'<span class="simchart-end" style="color:'+c.color+'">'+endS.toFixed(1).replace('.',',')+' %<span class="simchart-d"> ('+dt+')</span></span></div>'
   +simChart(c,arr0,arrS)+'</div>';
 });
 box.innerHTML=h;
 simTransmission(scen,base);
}
function simTransmission(scen,base){
 var t=document.getElementById('sim-trans'); if(!t) return;
 var n=scen.pi.length-1; var piEnd=scen.pi[n], rateEnd=scen.rate[n];
 var qT=-1; for(var i=0;i<scen.pi.length;i++){ if(Math.abs(scen.pi[i]-2.0)<=0.2){qT=i;break;} }
 var timeStr = qT<0?'<b>ikke innen 3 år</b>':(qT===0?'allerede i dag':('etter ca. '+(qT<4?qT+' kvartaler':(qT/4).toFixed(1).replace('.',',')+' år')));
 var msgs=[];
 var di=simState.rente-4.25, df=simState.fisk-2.7, doil=(simState.olje-80), dw=simState.lonn-4.5, dk=simState.krone, dwo=simState.verden-1.5, dp=simState.prod-0.7;
 if(simMode==='fixed'&&Math.abs(di)>=0.1) msgs.push('rente holdt '+(di>0?'høyere':'lavere'));
 if(Math.abs(df)>=0.1) msgs.push('finanspolitikk '+(df>0?'mer ekspansiv':'strammere'));
 if(Math.abs(doil)>=1) msgs.push('oljepris '+(doil>0?'opp':'ned'));
 if(Math.abs(dw)>=0.1) msgs.push('lønnsvekst '+(dw>0?'opp':'ned'));
 if(Math.abs(dk)>=1) msgs.push('krone '+(dk>0?'sterkere':'svakere'));
 if(Math.abs(dwo)>=0.1) msgs.push('verdensvekst '+(dwo>0?'opp':'ned'));
 if(Math.abs(dp)>=0.1) msgs.push('produktivitet '+(dp>0?'opp':'ned'));
 var modeTxt = simMode==='rule'?('Norges Bank reagerer (Taylor-regel) — renten ender på ca. <b>'+rateEnd.toFixed(1).replace('.',',')+' %</b>'):('renten holdes fast på <b>'+simState.rente.toFixed(2).replace('.',',')+' %</b>');
 var lead='<b>Etter 3 år:</b> kjerneinflasjon ≈ <b>'+piEnd.toFixed(1).replace('.',',')+' %</b> (mål 2,0). Tilbake ved målet '+timeStr+'. '+modeTxt+'.';
 if(msgs.length) lead+=' <span style="color:var(--slate)">Endret: '+msgs.join(', ')+'.</span>';
 if(simMode==='fixed'&&piEnd>2.6) lead+=' <b>Merk:</b> uten renterespons forankres ikke inflasjonen — den blir hengende over målet.';
 t.innerHTML=lead;
}
function simRenderMode(){
 var m=document.getElementById('sim-mode'); if(!m) return;
 m.innerHTML='<button class="preset'+(simMode==='rule'?' reset':'')+'" data-mode="rule">Norges Bank reagerer (Taylor-regel)</button>'
  +'<button class="preset'+(simMode==='fixed'?' reset':'')+'" data-mode="fixed">Hold renten fast</button>';
 m.querySelectorAll('[data-mode]').forEach(function(b){ b.addEventListener('click',function(){ simMode=b.getAttribute('data-mode'); simRenderMode(); simRenderOutputs(); }); });
}
function simApplyPreset(p){
 SIM_P.forEach(function(x){ simState[x.id]=x.base; });
 if(p.s){ for(var k in p.s){ simState[k]=p.s[k]; } }
 simRenderControls(); simRenderOutputs();
}
function simRenderPresets(){
 var pc=document.getElementById('sim-presets'); if(!pc) return; var h='';
 SIM_PRESET.forEach(function(p,i){ h+='<button class="preset'+(p.reset?' reset':'')+'" data-pi="'+i+'">'+p.n+'</button>'; });
 pc.innerHTML=h;
 pc.querySelectorAll('[data-pi]').forEach(function(b){ b.addEventListener('click',function(){ simApplyPreset(SIM_PRESET[parseInt(b.getAttribute('data-pi'))]); }); });
}
simRenderPresets(); simRenderMode(); simRenderControls(); simRenderOutputs();
"""

ADD_CSS = """
/* ===== merged shell ===== */
.topnav{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.96);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line);padding:0 18px}
.topnav-inner{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:4px;height:54px;overflow-x:auto;white-space:nowrap}
.topnav .brand{font-family:var(--serif);font-weight:600;font-size:15px;margin-right:12px;padding-right:14px;border-right:1px solid var(--line);color:var(--ink)}
.topnav a{font-size:13px;font-weight:600;color:var(--slate);text-decoration:none;padding:8px 12px;border-radius:6px;cursor:pointer;border:0;background:none;font-family:var(--sans)}
.topnav a:hover{color:var(--ink);background:var(--mist)}
.topnav a.active{color:#fff;background:var(--ink)}
main{max-width:1180px;margin:0 auto;padding:24px 18px 90px}
.view{display:none}
.view.active{display:block}
.view .wrap{max-width:none!important;margin:0!important;padding:0!important}
.selector{position:static!important;top:auto!important;background:transparent!important;border:0!important;padding:6px 0 2px!important;backdrop-filter:none!important}
.xlink{cursor:pointer;text-decoration:underline;text-underline-offset:2px}
.xlink:hover{filter:brightness(.9)}
.doc{font-family:var(--mono);font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:3px}
.doc-g{background:#e2f0e8;color:#2f7d4f}.doc-y{background:#f6efd9;color:#b8860b}.doc-r{background:#f6e0e0;color:#b23b3b}
.suite-head{padding:4px 0 14px}
.suite-head .kick{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:8px}
.suite-head h1{font-family:var(--serif);font-weight:600;font-size:30px;line-height:1.14;margin-bottom:8px}
.suite-head p{font-size:16px;color:var(--ink-soft);max-width:84ch}
.entry-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:8px 0 0}
.entry{border:1px solid var(--line);border-left-width:3px;border-radius:6px;padding:14px 16px;cursor:pointer;background:var(--paper);transition:.12s}
.entry:hover{border-color:var(--ink-soft);transform:translateY(-2px);box-shadow:0 3px 10px rgba(19,35,58,.06)}
.entry.e1{border-left-color:var(--indigo)}.entry.e2{border-left-color:var(--accent)}
.entry.e3{border-left-color:var(--teal)}.entry.e4{border-left-color:var(--gold)}.entry.e5{border-left-color:#7F77DD}.entry.e7{border-left-color:var(--gold)}
.entry h4{font-family:var(--serif);font-size:15px;margin-bottom:4px;color:var(--ink)}
.entry p{font-size:12px;margin:0;color:var(--slate);line-height:1.4}
.deckwrap{background:var(--paper);border:1px solid var(--line);border-radius:3px;padding:24px 30px;margin:0 0 22px;position:relative}
.deckwrap::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--ink);border-radius:2px 0 0 2px}
.deckwrap h3{font-family:var(--serif);font-size:18px;margin:0 0 6px}
.entry.e6{border-left-color:#1f6f6b}
/* ===== simulator ===== */
.sim-banner{background:var(--accent-soft);border:1px solid #ecd3c7;border-radius:6px;padding:11px 15px;font-size:12.5px;color:#7a3a20;margin:0 0 18px}
.sim-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:24px}
@media(max-width:880px){.sim-grid{grid-template-columns:1fr}}
.sim-presets{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.preset{font-family:var(--sans);font-size:12px;font-weight:600;padding:6px 12px;border-radius:20px;border:1px solid var(--line);background:var(--paper);color:var(--ink-soft);cursor:pointer}
.preset:hover{border-color:var(--ink-soft);color:var(--ink)}
.preset.reset{background:var(--ink);color:#fff;border-color:var(--ink)}
.slider-row{padding:12px 0;border-bottom:1px solid var(--line-soft)}
.slider-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:8px}
.slider-name{font-size:13.5px;font-weight:600;color:var(--ink)}
.slider-name .ch{display:block;font-size:11px;color:var(--slate);font-weight:400;margin-top:2px}
.slider-val{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--accent);white-space:nowrap;text-align:right}
.slider-val .base{display:block;font-size:10px;color:var(--slate);font-weight:400}
input[type=range].sl{width:100%;-webkit-appearance:none;appearance:none;height:5px;border-radius:3px;background:var(--mist-2);outline:none;margin:2px 0}
input[type=range].sl::-webkit-slider-thumb{-webkit-appearance:none;width:17px;height:17px;border-radius:50%;background:var(--accent);cursor:pointer;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.25)}
input[type=range].sl::-moz-range-thumb{width:17px;height:17px;border-radius:50%;background:var(--accent);cursor:pointer;border:2px solid #fff}
.mtag{font-family:var(--mono);font-size:9.5px;font-weight:700;padding:1px 6px;border-radius:3px;cursor:pointer;text-decoration:underline;text-underline-offset:2px;margin-left:6px}
.out-card{border:1px solid var(--line);border-radius:7px;padding:13px 15px;margin-bottom:11px;background:var(--paper)}
.out-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.out-name{font-size:13px;font-weight:600;color:var(--ink)}
.out-val{font-family:var(--serif);font-size:23px;font-weight:600;color:var(--ink);line-height:1;white-space:nowrap}
.out-delta{font-family:var(--mono);font-size:12px;font-weight:700;margin-left:7px}
.out-delta.bad{color:var(--bad)} .out-delta.good{color:var(--ok)} .out-delta.flat{color:var(--slate)}
.out-meta{font-size:11px;color:var(--slate);margin-top:3px}
.out-track{height:7px;border-radius:4px;background:var(--mist-2);margin-top:10px;position:relative;overflow:visible}
.out-fill{position:absolute;top:0;bottom:0;left:0;border-radius:4px;background:var(--indigo);transition:width .18s}
.out-basemark{position:absolute;top:-2px;bottom:-2px;width:2px;background:var(--ink)}
.sim-trans{background:var(--teal-soft);border:1px solid #cfe5e3;border-radius:6px;padding:12px 14px;font-size:12.5px;color:#13332f;margin-top:6px;line-height:1.5}
.formula{margin-top:20px}
.formula summary{cursor:pointer;font-size:12.5px;font-weight:600;color:var(--ink-soft)}
.sim-mode{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.sim-charts{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:560px){.sim-charts{grid-template-columns:1fr}}
.simchart-card{border:1px solid var(--line);border-radius:7px;padding:8px 10px 4px;background:var(--paper)}
.simchart-head{display:flex;justify-content:space-between;align-items:baseline;gap:6px;margin-bottom:2px}
.simchart-title{font-size:11.5px;font-weight:600;color:var(--ink)}
.simchart-end{font-family:var(--mono);font-size:12px;font-weight:700;white-space:nowrap}
.simchart-d{font-size:9.5px;color:var(--slate);font-weight:400}
svg.simchart{width:100%;height:auto;display:block}
/* ===== skatt: subtabs, hierarki, fordelingsbarer ===== */
.subtabs{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 20px;border-bottom:1px solid var(--line)}
.subtab{font-family:var(--sans);font-size:13px;font-weight:600;padding:9px 15px;border:0;background:none;color:var(--slate);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px}
.subtab:hover{color:var(--ink)}
.subtab.active{color:var(--ink);border-bottom-color:var(--accent)}
.subpanel{display:none}
.subpanel.active{display:block}
.hier{margin:8px 0}
.hl{border:1px solid var(--line);border-left-width:3px;border-radius:6px;padding:12px 14px;overflow:hidden}
.hl1{border-left-color:var(--ink);background:var(--mist-2)}
.hl2{border-left-color:var(--indigo);background:var(--indigo-soft);margin-top:11px}
.hl3{border-left-color:var(--gold);background:var(--gold-soft);margin-top:11px}
.hl4{border-left-color:var(--accent);background:var(--accent-soft);margin-top:11px}
.hl .hlk{font-weight:600;color:var(--ink);font-size:13px}
.hl .hlv{float:right;font-family:var(--serif);font-weight:600;color:var(--ink);font-size:15px}
.hl .hlv small{font-family:var(--mono);font-size:10px;color:var(--slate);font-weight:400;margin-left:4px}
.hl .hld{font-size:11.5px;color:var(--slate);margin-top:4px;clear:both}
.dbar{display:grid;grid-template-columns:165px 1fr 128px;gap:10px;align-items:center;margin:7px 0;font-size:12.5px}
.dbar .dlab{color:var(--ink-soft)}
.dbar .track{height:14px;background:var(--mist-2);border-radius:3px;overflow:hidden}
.dbar .fill{height:100%;border-radius:3px;background:var(--indigo)}
.dbar .fill.g{background:var(--gold)} .dbar .fill.a{background:var(--accent)} .dbar .fill.t{background:var(--teal)}
.dbar .dv{font-family:var(--mono);text-align:right;color:var(--ink);white-space:nowrap}
@media(max-width:620px){.dbar{grid-template-columns:120px 1fr 96px;font-size:11.5px}}
.persp{border:1px solid var(--line);border-left-width:3px;border-radius:6px;padding:14px 16px;background:var(--paper)}
.persp.civita{border-left-color:var(--indigo);background:var(--indigo-soft)}
.persp.lo{border-left-color:var(--gold);background:var(--gold-soft)}
.persp.acc{border-left-color:var(--accent);background:var(--accent-soft)}
.persp.teal{border-left-color:var(--teal);background:var(--teal-soft)}
.persp .stag{font-family:var(--mono);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--slate);margin-bottom:4px}
.persp h4{font-size:14px;margin:0 0 8px;color:var(--ink)}
.persp p{font-size:12.5px;margin:0 0 8px}
.persp .pk{font-size:10.5px;color:var(--slate);margin-bottom:0}
"""

# ===== assemble =====
head = """<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Makromodell-apparatet — samlet dashbord</title>
<meta name="description" content="Norske makroøkonomiske modeller — apparat, kritikk, data, skatt, produktivitet og en interaktiv simulator. Verifisert mot SSB, Norges Bank, NBIM og OECD (2026).">
<meta property="og:type" content="website">
<meta property="og:title" content="Norske makroøkonomiske modeller — på ett sted">
<meta property="og:description" content="Modellverket, faktasjekken og en interaktiv simulator. 8 faner, verifisert mot SSB, Norges Bank, NBIM og OECD.">
<meta property="og:url" content="https://makromodeller.vercel.app/">
<meta property="og:image" content="https://makromodeller.vercel.app/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="nb_NO">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Norske makroøkonomiske modeller — på ett sted">
<meta name="twitter:description" content="Modellverket, faktasjekken og en interaktiv simulator — verifisert mot SSB, Norges Bank og OECD.">
<meta name="twitter:image" content="https://makromodeller.vercel.app/og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='5' fill='%2313233a'/%3E%3Crect x='4' y='4' width='4' height='24' fill='%23c0552b'/%3E%3Cpath d='M11 23L16 14L20 18L27 8' stroke='%231f6f6b' stroke-width='2.6' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<style>
""" + expl_style + "\n/* ===== dashboard styles ===== */\n" + dash_style + "\n" + ADD_CSS + """
</style>
</head>
<body>
"""

topnav = """
<div class="topnav"><div class="topnav-inner">
  <span class="brand">Makromodell-apparatet</span>
  <a data-v="oversikt">Oversikt</a>
  <a data-v="modeller">Modellapparatet</a>
  <a data-v="kritikk">Kritisk analyse</a>
  <a data-v="data">Data &amp; makro</a>
  <a data-v="produktiv">Produktivitet</a>
  <a data-v="skatt">Skatteinngang</a>
  <a data-v="simulator">Simulator</a>
  <a data-v="kilder">Kilder</a>
</div></div>
<main>
"""

oversikt = """
<section class="view" id="view-oversikt">
  <div class="suite-head">
    <div class="kick">Samlet dashbord · tre lag i ett verk</div>
    <h1>Norske makroøkonomiske modeller — apparat, kritikk og data på ett sted</h1>
    <p>Dette samler tre arbeider: det tekniske dypdykket i modellapparatet, den dype modell-utforskeren, og den kritiske analysen av essayet «Skapt av ingenting» holdt opp mot data og OECDs landrapport. Bruk toppmenyen — eller klikk en modell i kritikken for å hoppe rett til forklaringen.</p>
    <div class="entry-grid">
      <div class="entry e1" onclick="location.hash='#modeller'"><h4>Modellapparatet →</h4><p>KVARTS, MODAG, NEMO, NORA, SNOW, DEMEC, MOSART, LOTTE, NAM — dypt forklart med alle parametre og figurer.</p></div>
      <div class="entry e2" onclick="location.hash='#kritikk'"><h4>Kritisk analyse →</h4><p>24 påstander vurdert (riktig/delvis/feil), koblet til modellene som faktisk svarer.</p></div>
      <div class="entry e3" onclick="location.hash='#data'"><h4>Data &amp; makro →</h4><p>Rentebane, inflasjonsbane, oljepengebruk og OECDs framskrivinger — verifisert mot primærkilde.</p></div>
      <div class="entry e7" onclick="location.hash='#produktiv'"><h4>Produktivitet →</h4><p>Arbeidsproduktivitet vs TFP, Bech Holte-debatten, og hvorfor dette er langsiktsdriveren i modellene.</p></div>
      <div class="entry e5" onclick="location.hash='#skatt'"><h4>Skatteinngang →</h4><p>Hvor skattepengene kommer fra: 3 218 mrd → 7 mrd, eierskatt, scenarier og tidsserie (SSB).</p></div>
      <div class="entry e6" onclick="location.hash='#simulator'"><h4>Simulator →</h4><p>Sett driverne selv (rente, oljepengebruk, oljepris, lønn …) og se hvor økonomien peker, gitt modellenes elastisiteter.</p></div>
      <div class="entry e4" onclick="location.hash='#kilder'"><h4>Kilder →</h4><p>Samlet kildeapparat for etterprøving.</p></div>
    </div>
  </div>
""" + sec['hero'].replace('<section class="card" id="hero">','<section class="card">') + """
  <div class="deckwrap">
    <div class="eyebrow neutral">Kart 1 · fire metodefamilier etter tidshorisont og teorigrad</div>
    <h3>Slik er modellparken ordnet</h3>
    """ + svg_typology + """
    <div class="fig-cap">Posisjonering etter brukshorisont (x) og grad av mikrofundering/teoristruktur (y). Boblestørrelse ≈ detaljeringsgrad. Fra det tekniske dypdykket.</div>
  </div>
  <div class="deckwrap">
    <div class="eyebrow neutral">Kart 2 · datafundament, modeller, produkter, brukere</div>
    <h3>Økosystemet: hvordan modellene mater hverandre</h3>
    """ + svg_ecosystem + """
    <div class="fig-cap">Heltrukne piler = data-/leveranseflyt; stiplet oransje = modell-til-modell-kobling. Nasjonalregnskapet er navet.</div>
  </div>
  <div class="deckwrap">
    <div class="eyebrow neutral">Syntese · koblingene mellom modellene</div>
    <h3>Ingen kjører isolert, men ingen er teknisk fusjonert</h3>
    """ + tbl_coupling + """
  </div>
  <div class="deckwrap">
    <div class="eyebrow neutral">Etterprøvbarhet · dokumentasjonsgrad</div>
    <h3>Hvor godt kan en skeptiker faktisk kontrollere hver modell?</h3>
    """ + tbl_docgrad + """
  </div>
</section>
"""

modeller = '<section class="view" id="view-modeller">\n' + expl_body + '\n</section>\n'

kritikk = '<section class="view" id="view-kritikk">\n' + sec['ledger'] + '\n' + sec['matrix'] + '\n' + sec['synth'] + '\n</section>\n'

bnp_card = """<section class="card">
  <div class="eyebrow neutral">BNP-utvikling · nasjonalregnskap (SSB 09189) + OECD-anslag</div>
  <h2>Fastlands-BNP er det relevante målet — petroleum gjør total-BNP volatil</h2>
  <div class="governing">Norsk vekst er moderat: etter COVID-fallet (2020) og gjeninnhentingen (2021–22) har Fastlands-BNP vokst 0,6–1,7 % i året. OECD venter ~1,7 % (2026) og ~1,5 % (2027) — i tråd med den svake produktivitetstrenden.</div>
  <div class="kpis">
    <div class="kpi"><div class="v">4 398 <small>mrd</small></div><div class="l">Fastlands-BNP 2025 (løpende priser)</div></div>
    <div class="kpi"><div class="v">5 511 <small>mrd</small></div><div class="l">Total BNP 2025 (inkl. petroleum)</div></div>
    <div class="kpi"><div class="v">1,7 %</div><div class="l">Fastlands-BNP volumvekst 2025 (SSB)</div></div>
    <div class="kpi"><div class="v">~1,7 / 1,5 %</div><div class="l">OECD-anslag Fastlands-BNP 2026 / 2027</div></div>
  </div>

  <div class="eyebrow neutral" style="margin-top:16px">Volumvekst, %/år — total BNP vs Fastlands-BNP (2015–2027)</div>
  <svg viewBox="0 0 1000 250" role="img" aria-label="BNP-volumvekst 2015-2027, total og Fastlands-Norge">
    <g stroke="#eef1f6" stroke-width="1"><line x1="70" y1="30" x2="960" y2="30"/><line x1="70" y1="70" x2="960" y2="70"/><line x1="70" y1="110" x2="960" y2="110"/><line x1="70" y1="190" x2="960" y2="190"/></g>
    <line x1="70" y1="150" x2="960" y2="150" stroke="#5d6b80" stroke-width="1.2"/>
    <g font-family="Consolas,monospace" font-size="10" fill="#8a97a8"><text x="64" y="33" text-anchor="end">6</text><text x="64" y="73" text-anchor="end">4</text><text x="64" y="113" text-anchor="end">2</text><text x="64" y="153" text-anchor="end">0</text><text x="64" y="193" text-anchor="end">−2</text></g>
    <line x1="849" y1="30" x2="849" y2="210" stroke="#d4dae3" stroke-dasharray="3 3"/>
    <text x="853" y="40" font-size="9.5" fill="#8a97a8" font-style="italic">anslag (OECD) →</text>
    <polyline points="70,110 144,124 218,96 293,128 367,120 441,178 515,68 589,68 664,142 738,122 812,128 886,124 960,126" fill="none" stroke="#9aa6c4" stroke-width="1.6"/>
    <polyline points="70,116 144,130 218,102 293,108 367,96 441,204 515,56 589,46 664,132 738,138 812,116" fill="none" stroke="#1f6f6b" stroke-width="2.6"/>
    <polyline points="812,116 886,116 960,120" fill="none" stroke="#1f6f6b" stroke-width="2.6" stroke-dasharray="5 4"/>
    <g fill="#1f6f6b" font-family="Consolas,monospace" font-size="10" font-weight="700">
      <circle cx="441" cy="204" r="3"/><text x="441" y="219" text-anchor="middle">−2,7</text>
      <circle cx="589" cy="46" r="3"/><text x="589" y="40" text-anchor="middle">5,2</text>
      <circle cx="738" cy="138" r="3"/><text x="730" y="151" text-anchor="end">0,6</text>
      <circle cx="812" cy="116" r="3"/><text x="812" y="110" text-anchor="middle">1,7</text>
      <circle cx="960" cy="120" r="3.5"/><text x="958" y="113" text-anchor="end">1,5</text>
    </g>
    <g font-family="-apple-system,Segoe UI,sans-serif" font-size="10" fill="#8a97a8" text-anchor="middle"><text x="70" y="240">2015</text><text x="218" y="240">2017</text><text x="367" y="240">2019</text><text x="515" y="240">2021</text><text x="664" y="240">2023</text><text x="812" y="240">2025</text><text x="960" y="240">2027</text></g>
    <g font-family="-apple-system,Segoe UI,sans-serif" font-size="11"><rect x="600" y="223" width="12" height="11" fill="#1f6f6b"/><text x="618" y="232" fill="#5d6b80">Fastlands-BNP</text><rect x="742" y="227" width="14" height="3" fill="#9aa6c4"/><text x="762" y="232" fill="#5d6b80">Total BNP (inkl. petroleum)</text></g>
  </svg>
  <div class="fig-cap">Kilde: SSB tabell 09189 (volumendring, faste priser) for 2015–2025; OECD Economic Outlook 119 for 2026–2027 (stiplet). Total-BNP (grå) svinger mer enn Fastlands-BNP fordi olje-/gassproduksjon og -priser slår inn.</div>

  <div class="matrix-scroll" style="margin-top:12px">
    <table class="tbl" style="font-size:12px">
      <thead><tr><th>Volumvekst (%)</th><th class="num">’20</th><th class="num">’21</th><th class="num">’22</th><th class="num">’23</th><th class="num">’24</th><th class="num">’25</th><th class="num">’26*</th><th class="num">’27*</th></tr></thead>
      <tbody>
        <tr><td>Total BNP</td><td class="num">−1,4</td><td class="num">4,1</td><td class="num">4,1</td><td class="num">0,4</td><td class="num">1,4</td><td class="num">1,1</td><td class="num">~1,3</td><td class="num">~1,2</td></tr>
        <tr><td><b>Fastlands-BNP</b></td><td class="num">−2,7</td><td class="num">4,7</td><td class="num">5,2</td><td class="num">0,9</td><td class="num">0,6</td><td class="num">1,7</td><td class="num">1,7</td><td class="num">1,5</td></tr>
      </tbody>
    </table>
  </div>
  <div class="tbl-cap">*2026–2027 = OECD-anslag. SSB-tall til og med 2025 (foreløpig regnskap).</div>

  <div class="note" style="margin-top:14px"><b>Les sammen med resten.</b> Det svake 2024-året (Fastlands-BNP +0,6 %) og den moderate trenden (~1,5 %) er kjernen i <a class="xlink" style="cursor:pointer" onclick="location.hash='#produktiv'">produktivitetsdebatten →</a> — lav produktivitetsvekst gir lav trend-BNP. BNP per innbygger steg bare ~10 % fra 2013 til 2024. I <a class="xlink" style="cursor:pointer" onclick="location.hash='#simulator'">Simulatoren →</a> er Fastlands-BNP-vekst (1,7 % i dag) ett av utfallene.</div>

  <div class="src"><b>Kilder.</b> SSB tabell 09189 «Makroøkonomiske hovedstørrelser» (volumendring og løpende priser, oppdatert mai 2026); OECD Economic Outlook 119 (Fastlands-BNP-anslag 2026–2027). Nivåtall i løpende priser: total BNP 5 511 mrd, Fastlands-BNP 4 398 mrd (2025).</div>
</section>
"""

data_header = """<section class="card">
  <div class="eyebrow neutral">Data &amp; makro · verifisert mot primærkilde (juni 2026)</div>
  <h2>Det løpende makrobildet</h2>
  <div class="governing">Nøkkeltallene, BNP-utviklingen, oljepengebruken, OECDs eksterne blikk og det fulle parameterregisteret — verifisert mot Norges Bank, SSB, NBIM og OECD.</div>
  <div class="subtabs">
    <button class="subtab active" data-sub="nokkeltall">Nøkkeltall</button>
    <button class="subtab" data-sub="bnp">BNP &amp; vekst</button>
    <button class="subtab" data-sub="olje">Oljepengebruk</button>
    <button class="subtab" data-sub="oecd">OECD-blikk</button>
    <button class="subtab" data-sub="param">Parameterregister</button>
  </div>
</section>
"""
data_view = ('<section class="view" id="view-data">\n' + data_header
  + '<div class="subpanel active" id="sub-nokkeltall">\n' + sec['params'] + '\n</div>\n'
  + '<div class="subpanel" id="sub-bnp">\n' + bnp_card + '\n</div>\n'
  + '<div class="subpanel" id="sub-olje">\n' + sec['olje'] + '\n</div>\n'
  + '<div class="subpanel" id="sub-oecd">\n' + sec['oecd'] + '\n</div>\n'
  + '<div class="subpanel" id="sub-param">\n' + sec['paramtable'] + '\n</div>\n'
  + '</section>\n')

kilder = """<section class="view" id="view-kilder">
<section class="card">
  <div class="eyebrow neutral">Kildeapparat · samlet for hele dashbordet</div>
  <h2>Kilder og etterprøving</h2>
  <div class="governing">Alle bærende tall er kontrollert mot primærkilde i juni 2026. Stiliserte figurer, triangulerte estimater og simulatorens emulator er merket som sådan både her og der de opptrer.</div>

  <div class="eyebrow neutral">Artikkelen som vurderes</div>
  <ul class="tight" style="margin-bottom:16px">
    <li>Thomas Rosseland Wiborg-Thune (2026): «Skapt av ingenting: Gjeldsbyrden i rike Norge», eksternt innlegg, publisert 20.06.2026.</li>
  </ul>

  <div class="eyebrow neutral">Verifiserte data (kontrollert juni 2026)</div>
  <table class="tbl">
    <thead><tr><th>Kilde</th><th>Brukt til</th><th>Status</th></tr></thead>
    <tbody>
      <tr><td>Norges Bank — styringsrente (IR-serien)</td><td>4,25 % i dag; rentehistorikk 2021–2026</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>Norges Bank — Pengepolitisk rapport 2/26 (18.06.2026)</td><td>Rentebane og inflasjonsbane (KPI/KPI-JAE) til 2029; komiteens vurdering</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>Norges Bank — valutakurser (EXR: I-44, USD)</td><td>Importveid kronekurs (~113,7) og USD/NOK</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>NBIM — fondsverdi</td><td>SPU 21 286 mrd per 31.12.2025</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 10945 — Pengemengden M1/M2/M3</td><td>M2/M3 3 183/3 193 mrd (des. 2024) → 3 566/3 576 mrd (apr. 2026); M3 +8,4 % å/å</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 14668 — Offentlig forvaltnings inntekter</td><td>Skatteaggregater 2020–2025 (oppdatert 08.06.2026)</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 08231 — Formuesskatt etter intervaller</td><td>701 482 betalere; 2 838 i toppen; 296,8 mill / 9,1 mrd</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 07091 — Bedrifter etter størrelse</td><td>593 777 småbedrifter (90,2 %)</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 08815 — Bruttoformue</td><td>Formuessammensetning 8 292 mrd</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>SSB tabell 10486 — Statsregnskapet</td><td>Statsbudsjett-tall 2024–2025</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>Finanstilsynet — Boliglånsundersøkelsen 2024</td><td>Gjeldsgrad nye boliglån 323 %</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>Utlånsforskriften — FOR-2020-12-09-2648 (Lovdata)</td><td>Gjeldsgrad-tak 5×, belåningsgrad 90 % (endret 01.01.2025)</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>OECD (2026) — <i>Economic Surveys: Norway 2026</i></td><td>Eksternt blikk; DOI 10.1787/5cc02644-en</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>OECD — <i>Economic Outlook</i> nr. 119 (DSD_EO@DF_EO)</td><td>Framskrivinger for Norge 2023–2027</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>IMF</td><td>Husholdningsgjeld ~100 % av BNP</td><td><span class="chip ok">✓</span></td></tr>
      <tr><td>Nasjonalbudsjettet 2026 (Meld. St. 1 (2025–2026))</td><td>Oljepengebruk / strukturelt underskudd, handlingsregelen</td><td><span class="chip ok">✓</span></td></tr>
    </tbody>
  </table>

  <div class="eyebrow neutral" style="margin-top:22px">Pengeteori og reformforslag</div>
  <ul class="tight" style="margin-bottom:16px">
    <li>McLeay, Radia &amp; Thomas (2014): «Money creation in the modern economy», Bank of England Quarterly Bulletin 2014 Q1.</li>
    <li>Benes &amp; Kumhof (2012): «The Chicago Plan Revisited», IMF Working Paper WP/12/202.</li>
    <li>Jordà, Schularick &amp; Taylor: kreditt, boligpriser og finansielle sykluser.</li>
    <li>Milton Friedman: regelstyring vs. skjønn; Simons &amp; Fisher: Chicago-planen (1933).</li>
    <li>Hayek og Mises: østerriksk konjunkturteori (presentert som omstridt, ikke konsensus).</li>
  </ul>

  <div class="grid2">
    <div>
      <div class="eyebrow neutral">Modellapparatet · SSB</div>
      <ul class="tight">
        <li>Haakonsen (2015): «KVARTS i praksis V», Notater 2015/21; Biørn, Jensen &amp; Reymert (1987).</li>
        <li>Boug &amp; Dyvi (red.) (2008): MODAG, SØS 111; Boug, Cappelen &amp; Eika (2017), Rapporter 2017/9.</li>
        <li>Johansen (1960); Rosnes, Bye &amp; Fæhn (2019): SNOW, Notater 2019/1; Fæhn mfl. (2020), Rapporter 2020/23.</li>
        <li>Holmøy &amp; Strøm (2013): DEMEC-relatert, <i>Handbook of CGE Modeling</i>.</li>
        <li>Fredriksen &amp; Knudsen (2025): MOSART 7.5, Notater 2025/04.</li>
        <li>Hansen, Lian, Nesbakken &amp; Thoresen (2008): LOTTE, Rapporter 2008/36.</li>
      </ul>
    </div>
    <div>
      <div class="eyebrow neutral">Modellapparatet · Norges Bank, FIN, akademisk</div>
      <ul class="tight">
        <li>Gerdrup, Kravik, Paulsen &amp; Robstad (2017): «Documentation of NEMO», Staff Memo 8/2017; Kravik mfl. (2019); Brubakk mfl. (2006), SM 6/2006.</li>
        <li>Aursland, Frankovic, Birol &amp; Saxegaard (2020): «State-dependent fiscal multipliers in NORA», <i>Economic Modelling</i> 93.</li>
        <li>Bårdsen, Eitrheim, Jansen &amp; Nymoen (2005): <i>The Econometrics of Macroeconomic Modelling</i>, OUP (NAM).</li>
        <li>Norges Bank Memo 1/2022 (pengepolitikk-prosessen); Perspektivmeldingen 2017 og 2024.</li>
      </ul>
    </div>
  </div>

  <div class="flag" style="margin-top:18px">
    <b>Metode og forbehold.</b> «Dom» i den kritiske analysen er en faktasjekk + vurdering av intern konsistens, ikke en politisk vurdering. Modellparametrene er fra primærdokumentasjonen der de er offentlige, ellers oppgitt som typiske størrelser for klassen og merket. Formuesskatten oppgis med to korrekte SSB-kilder (31,8 mrd nasjonalregnskap / ~31,1 mrd skattestatistikk). Splitt av selskapsskatt på selskapsstørrelse og samlet småbedriftsbidrag er triangulerte estimater. Scenario-simulatoren er en gjennomsiktig emulator kalibrert på modellenes elastisiteter — ikke en kjøring av NEMO/KVARTS.
  </div>

  <div class="deckwrap" style="margin-top:18px">
    <h3>Originaldokumentene</h3>
    <p style="font-size:13px;color:var(--ink-soft)">Dette dashbordet slår sammen tre filer. Originalene beholdes urørt: <span class="term">makromodeller-teknisk-dypdykk.html</span> (det fulle dypdykket — 14 lysbilder, egnet for utskrift/PowerPoint), <span class="term">makromodeller-kritisk-dashbord.html</span> og <span class="term">makromodeller-modellforklaringer.html</span>.</p>
  </div>
</section>
</section>
"""

router = """
<script>
/* ===== router + cross-linking ===== */
const NAMEMAP={KVARTS:'kvarts',MODAG:'modag',NEMO:'nemo',NORA:'nora',SNOW:'snow',MSG:'snow',DEMEC:'demec',MOSART:'mosart',LOTTE:'lotte',NAM:'nam'};
function showView(v){
  if(!document.getElementById('view-'+v)) v='oversikt';
  document.querySelectorAll('.view').forEach(s=>s.classList.toggle('active',s.id==='view-'+v));
  document.querySelectorAll('.topnav a').forEach(a=>a.classList.toggle('active',a.dataset.v===v));
}
function goModel(id){
  var i=(typeof MODELS!=='undefined')?MODELS.findIndex(function(m){return m.id===id}):-1;
  location.hash='#modeller/'+id;
}
function route(){
  var h=location.hash.replace(/^#/,'');var p=h.split('/');var v=p[0];var sub=p[1];
  if(!v){showView('oversikt');return;}
  if(!document.getElementById('view-'+v)){return;} /* ukjent hash = intern ankerlenke: la nettleseren scrolle */
  showView(v);
  if(v==='modeller'&&sub&&typeof MODELS!=='undefined'){var i=MODELS.findIndex(function(m){return m.id===sub});if(i>=0&&typeof renderModel==='function')renderModel(i);}
  window.scrollTo({top:0,behavior:'smooth'});
}
function goView(v,anchor){location.hash='#'+v;if(anchor){setTimeout(function(){var el=document.getElementById(anchor);if(!el)return;var panel=el.closest?el.closest('.subpanel'):null;if(panel){var sub=panel.id.replace(/^sub-/,'');var vw=document.getElementById('view-'+v);if(vw){vw.querySelectorAll('.subtab').forEach(function(t){t.classList.toggle('active',t.getAttribute('data-sub')===sub)});vw.querySelectorAll('.subpanel').forEach(function(p){p.classList.toggle('active',p===panel)});}}el.scrollIntoView({behavior:'smooth',block:'start'});},90);}}
window.addEventListener('hashchange',route);
document.querySelectorAll('.topnav a').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();location.hash='#'+a.dataset.v;});});
function wireLinks(){
  function key(t){return (t||'').trim().split(/[\\s/,.]+/)[0].toUpperCase();}
  document.querySelectorAll('#view-kritikk .mb').forEach(function(b){
    var id=NAMEMAP[key(b.textContent)];
    if(id){b.classList.add('xlink');b.title='\\u00c5pne '+key(b.textContent)+'-modellen';b.addEventListener('click',function(){goModel(id);});}
  });
  document.querySelectorAll('#view-kritikk .mx thead th').forEach(function(th){
    var raw=(th.firstChild&&th.firstChild.nodeType===3)?th.firstChild.textContent:th.textContent;
    var id=NAMEMAP[key(raw)];
    if(id){th.classList.add('xlink');th.title='\\u00c5pne modellen';th.addEventListener('click',function(){goModel(id);});}
  });
}
wireLinks();
route();
</script>
</body>
</html>
"""

out = head + topnav + oversikt + modeller + kritikk + data_view + produktiv_view + skatt_view + sim_view + kilder + "</main>\n" \
      + '<script>\n' + expl_script + '\n</script>\n' \
      + '<script>\n(function(){\n' + dash_script + '\n})();\n</script>\n' \
      + '<script>\n(function(){\n' + sim_script + '\n})();\n</script>\n' \
      + '<script>\n' + sim_skatt_tabs + '\n</script>\n' \
      + router

with io.open('makromodeller-samlet-dashboard.html','w',encoding='utf-8') as f:
    f.write(out)

# validation
import os
print('OK bytes', os.path.getsize('makromodeller-samlet-dashboard.html'))
for k,v in sec.items():
    print('section',k,'len',len(v))
print('svg_typology',len(svg_typology),'svg_ecosystem',len(svg_ecosystem),'tbl_coupling',len(tbl_coupling),'tbl_docgrad',len(tbl_docgrad))
print('expl_script',len(expl_script),'dash_script',len(dash_script),'expl_body',len(expl_body))
print('views in out:', out.count('class="view"'))
print('has goModel:', 'function goModel' in out, '| has MODELS:', 'const MODELS' in out, '| has CLAIMS:', 'CLAIMS' in out)
