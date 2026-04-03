# oai_harvester voor Collectie Nederland

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![No dependencies](https://img.shields.io/badge/dependencies-none-lightgrey)

Een robuuste, generieke **OAI-PMH harvester** voor Collectie Nederland (DCN) en andere OAI-PMH endpoints.  
Werkt volledig met de Python-standaardbibliotheek.

## TL;DR
```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out \
  --dump csv --edm-field edm:isShownAt
```

## Wat u krijgt
- Interactief of via CLI
- Streaming naar XML (grote datasets)
- Hervatten via `.state.json`
- Limiet: 1, 100, 1000 of alles
- Bestandsrotatie (`--rotate-every`)
- CSV en JSONL export
- Configureerbaar veld (EDM/DC)
- Preflight (`Identify`, metadataPrefix check)
- Robuuste HTTP (retries, backoff, Retry-After, gzip/deflate)
- XML-reparatie (control chars, &)
- Logging naar `.log`
- Geen dependencies

## Voorbeeld
```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out \
  --rotate-every 200000
```

## Licentie
MIT
