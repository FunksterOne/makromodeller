# Makromodell-apparatet — samlet dashbord

Et interaktivt, pedagogisk dashbord om **norske makroøkonomiske modeller**, en kritisk faktasjekk av essayet «Skapt av ingenting», og det løpende makrobildet for norsk økonomi. Bygget som én selvstendig HTML-fil uten eksterne avhengigheter.

**Live:** https://makromodeller.vercel.app/

## Innhold (8 faner)

1. **Oversikt** — tese, totaldom, metodefamilier og økosystemkart
2. **Modellapparatet** — dyp gjennomgang av KVARTS, MODAG, NEMO, NORA, SNOW/MSG, DEMEC, MOSART, LOTTE, NAM med alle parametre
3. **Kritisk analyse** — 24 påstander fra essayet vurdert (riktig/delvis/feil), koblet til modellene
4. **Data & makro** — nøkkeltall, BNP-utvikling, oljepengebruk, OECD-blikk og parameterregister (underfaner)
5. **Skatteinngang** — fra 3 218 mrd til 7 mrd, eierskatt, småbedrifter, scenarier og Civita/LO-perspektiver (underfaner)
6. **Produktivitet** — arbeidsproduktivitet vs TFP, Bech Holte-debatten, data og modellkobling (underfaner)
7. **Simulator** — interaktiv scenario-simulator med dynamisk 3-årsbane og endogen rentebane (Taylor-regel)
8. **Kilder** — samlet kildeapparat

## Kilder og verifisering

Alle bærende tall er kontrollert mot primærkilde (juni 2026): Norges Bank (styringsrente, PPR 2/26, valutakurser), NBIM (fondsverdi), SSB (nasjonalregnskap 09189, pengemengde 10945, offentlige inntekter 14668, formuesskatt 08231, bedrifter 07091, bruttoformue 08815), Finanstilsynet, OECD (Survey 2026, Economic Outlook 119) og IMF.

Stiliserte figurer, triangulerte estimater og simulatorens reduserte-form-emulator er merket som sådan i selve dashbordet.

## Bygging

Dashbordet settes sammen fra tre kildefiler av et byggeskript:

```bash
python _build_merged.py   # → makromodeller-samlet-dashboard.html (= index.html)
python _og_gen.py         # → og.png (krever Pillow)
```

Kildefiler: `makromodeller-teknisk-dypdykk.html`, `makromodeller-kritisk-dashboard.html`, `makromodeller-modellforklaringer.html` og skatteinnholdet (`skattedashboard-2024.html`).

## Forbehold

«Dom» i den kritiske analysen er en faktasjekk og vurdering av intern konsistens, ikke en politisk vurdering. Simulatoren er en gjennomsiktig emulator kalibrert på modellenes dokumenterte elastisiteter — ikke en kjøring av NEMO/KVARTS.
