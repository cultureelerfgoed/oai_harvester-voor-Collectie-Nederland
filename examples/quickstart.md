# Quickstart — oai_harvester voor Collectie Nederland

Deze handleiding helpt u snel op weg met de **oai_harvester** voor **Collectie Nederland (DCN)**.  
De tool werkt met de standaard **OAI-PMH API** en is ook bruikbaar voor andere OAI-PMH endpoints.  
Er zijn **geen externe Python-pakketten** nodig.

## 1. Vereisten

- Python 3.9 of hoger
- Internettoegang tot een OAI-PMH endpoint  
  (bijv. https://prod.dcn.hubs.delving.org/api/oai-pmh/)
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

U krijgt vragen over:
- Base URL (bijv. DCN endpoint)
- Verb (`ListRecords` of `ListIdentifiers`)
- metadataPrefix (`edm`, `edm-strict`, `oai_dc`)
- Set (optioneel, bijv. `amsterdam-museum`)
- Limiet (1, 100, 1000 of alles)
- Dump (csv, jsonl, beide of geen)
- Veld (bijv. `edm:isShownAt` of `dc:title`)

## 3. Voorbeeld: 100 records uit Amsterdam Museum

```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out \
  --max-items 100 \
  --dump beide --edm-field edm:isShownAt
```

Resultaat:
- `out/amsterdam.xml`
- `out/amsterdam.csv`
- `out/amsterdam.jsonl`
- `out/amsterdam.log`

## 4. Hervatten bij onderbreking

De harvester maakt een `.state.json`-bestand aan  
(bijv. `amsterdam.xml.state.json`).

Bij herstart:
- u krijgt een vraag om te hervatten
- kies **Y** om door te gaan vanaf het laatste punt

De tool herstelt automatisch de XML-structuur en gaat veilig verder.

## 5. Tips

- Gebruik HTTPS voor DCN:
  https://prod.dcn.hubs.delving.org/api/oai-pmh/
- Begin met kleine limieten (bijv. 100)
- Gebruik `--dump csv` voor snelle controle
- Gebruik `--rotate-every` bij grote datasets
- Controleer `.log` bij fouten of afwijkingen

## 6. Outputoverzicht

| Bestand | Inhoud |
|--------|--------|
| `<naam>.xml` | Volledige OAI-output |
| `<naam>.csv` | Identifiers + gekozen veld |
| `<naam>.jsonl` | Eén record per regel |
| `<naam>.log` | Logbestand |
| `<naam>.xml.state.json` | Alleen bij hervatten |

## 7. Licentie

Vrijgegeven onder de MIT-licentie. Zie `LICENSE`.

---

*Laatste update: oktober 2025 — ontwikkeld voor Collectie Nederland, generiek inzetbaar voor OAI-PMH.*
