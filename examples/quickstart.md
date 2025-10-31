# Quickstart — oai_harvester voor Collectie Nederland

Deze korte handleiding helpt u om snel aan de slag te gaan met de **oai_harvester** voor **Collectie Nederland (DCN)**.  
De tool werkt direct met de standaard **OAI-PMH API** van DCN en vereist **geen externe Python-pakketten**.

## 1. Vereisten

- Python 3.9 of hoger
- Internettoegang tot `https://prod.dcn.hubs.delving.org/api/oai-pmh/`
- Schrijfrechten in uw uitvoermap (standaard `./out`)

## 2. Interactieve start

Maak eventueel een map `out/`:

```bash
mkdir out
```

Start de harvester:

```bash
python oai_harvester.py
```

U krijgt dan vragen over:
- **Base URL** (meestal `https://prod.dcn.hubs.delving.org/api/oai-pmh/`)
- **Verb** (`ListRecords` of `ListIdentifiers`)
- **metadataPrefix** (`edm`, `edm-strict`, of `oai_dc`)
- **Set** (bijv. `amsterdam-museum`)
- **Limiet** (1, 100, 1000 of alles)
- **Dump** (csv, jsonl, beide of geen)
- **EDM-veld** (bijv. `edm:isShownAt`)

## 3. Voorbeeld: 100 records uit Amsterdam Museum

```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out \
  --max-items 100 --dump beide --edm-field edm:isShownAt
```

Resultaat:
- `out/amsterdam.xml` (XML-records)
- `out/amsterdam.csv` en `out/amsterdam.jsonl`
- `out/amsterdam.log` (logbestand)

## 4. Hervatten bij onderbreking

De harvester maakt een `.state.json`-bestand aan (bijv. `amsterdam.xml.state.json`).  
Bij herstart wordt gevraagd of u wilt hervatten. Antwoord met **Y** om verder te gaan waar u gebleven was.

## 5. Tips

- Gebruik altijd HTTPS voor DCN (`https://prod.dcn.hubs.delving.org/api/oai-pmh/`).
- Test met kleine limieten (`100`) voordat u grote runs start.
- Gebruik `--dump csv` voor snelle controles van identifiers.
- Bewaar `.log`-bestanden bij productieruns.

## 6. Outputoverzicht

| Bestand | Inhoud |
|----------|---------|
| `<naam>.xml` | Volledige OAI-output |
| `<naam>.csv` | Identifiers en één EDM-veld |
| `<naam>.jsonl` | Eén record per regel |
| `<naam>.log` | Log met details |
| `<naam>.xml.state.json` | Alleen aanwezig bij hervatten |

## 7. Licentie

Vrijgegeven onder de **MIT-licentie**. Zie `LICENSE.md`.

---
*Laatste update: oktober 2025 — ontwikkeld voor gebruik binnen Collectie Nederland (DCN).*
