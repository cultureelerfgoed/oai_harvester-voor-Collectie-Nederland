# Nieuws — oai_harvester v1.1.0 voor Collectie Nederland

Met deze release is er een complete, betrouwbare **OAI-PMH-harvester** beschikbaar voor **Collectie Nederland (DCN)**.  
U gebruikt de tool direct vanaf de commandline, zonder externe Python-pakketten.

## Wat is nieuw
- Interactief gebruik én volledige CLI-ondersteuning.
- Hervatten na onderbreking via `.state.json`.
- Limiet bij start: 1, 100, 1000 of alles (`--max-items`).
- Streaming naar XML met lage geheugendruk.
- Bestandsrotatie bij grote harvests (`--rotate-every`).
- CSV- en JSONL-export met identifier, datestamp en veld naar keuze.
- Preflight-controles:
  - `Identify`
  - validatie van `metadataPrefix`
- Robuuste netwerkafhandeling:
  - retries en backoff
  - respecteert `Retry-After`
  - gzip/deflate ondersteuning
- Automatische XML-reparatie:
  - verwijdert ongeldige control characters
  - herstelt losse `&` naar geldige XML
- Logging naar `.log` met voortgang en fouten.

## Waarom dit handig is
Deze oai_harvester helpt u bij het betrouwbaar ophalen van OAI-PMH-data uit Collectie Nederland.  
U gebruikt de output voor controle, verrijking, analyse of herpublicatie.

De tool is geschikt voor:
- databeheerders
- informatiespecialisten
- ontwikkelaars

## Wat u krijgt
- Eén of meerdere valide XML-bestanden (bij rotatie).
- Optioneel CSV en/of JSONL voor snelle inspectie.
- Herhaalbare runs met behoud van voortgang.
- Inzicht via logbestanden.

## Aanbevolen gebruik
1. Gebruik de officiële DCN-endpoint:  
   `https://prod.dcn.hubs.delving.org/api/oai-pmh/`
2. Start met een kleine limiet (bijv. 100 records).
3. Gebruik `--dump csv` voor snelle controle van identifiers.
4. Gebruik `--rotate-every` bij grote datasets.
5. Controleer `.log` bij fouten of afwijkingen.

## Voorbeeld
```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out \
  --dump beide --edm-field edm:isShownAt \
  --rotate-every 200000
