# Nieuws — oai_harvester v1.0.0 voor Collectie Nederland

Met deze release is er nu een complete, betrouwbare **OAI-PMH-harvester** voor **Collectie Nederland (DCN)**.  
De tool werkt zonder externe Python-pakketten en kan direct vanaf de commandline worden gebruikt.

## Wat is nieuw
- Interactieve bediening én commandline-opties.
- Hervatten via `.state.json` na een onderbreking.
- Limietkeuze bij start: 1, 100, 1000 of alles.
- CSV- en JSONL-export naast het XML-bestand.
- Preflight-controles (`Identify` en `ListMetadataFormats`) vóór het harvesten.
- Robuuste netwerkafhandeling met retries, backoff en `Retry-After`.
- Herstel van ongeldige XML (control characters, losse &).
- Bestandsrotatie bij grote harvests.

## Waarom dit handig is
Deze harvester is bedoeld voor databeheerders, informatiespecialisten en ontwikkelaars binnen Collectie Nederland.  
Hij haalt betrouwbare, complete OAI-PMH-data op en maakt die bruikbaar voor controle, verwerking of herpublicatie.

## Aanbevolen gebruik
1. Gebruik altijd de officiële DCN-endpoint:  
   `https://prod.dcn.hubs.delving.org/api/oai-pmh/`
2. Begin met een kleine limiet (100 records) om de instellingen te testen.
3. Gebruik `--dump csv` voor een snelle lijst van identifiers en titels.
4. Bewaar de `.log`-bestanden voor documentatie van de run.

## Voorbeeld
```bash
python oai_harvester.py \
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out --dump beide --edm-field edm:isShownAt
