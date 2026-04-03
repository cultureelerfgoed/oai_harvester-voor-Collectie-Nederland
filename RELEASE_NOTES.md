# Release Notes v1.0.0

Deze release levert een complete **oai_harvester** voor **Collectie Nederland**, maar is generiek inzetbaar voor **alle OAI-PMH endpoints**.  
De tool gebruikt uitsluitend de Python-standaardbibliotheek.

## Belangrijk
- Generieke OAI-PMH-harvester (niet gebonden aan één endpoint).
- Hervatten via `.state.json` (inclusief resumptionToken en voortgang).
- Limiet-keuze bij starten: 1, 100, 1000 of alles (`--max-items`).
- Streaming output naar XML (geschikt voor grote datasets).
- Bestandsrotatie na N items (`--rotate-every`).
- Extra export naar CSV en JSONL naast XML.
- Configureerbaar veld voor export (bijv. `edm:isShownAt`, `dc:title`).
- Preflight checks:
  - `Identify`
  - validatie van `metadataPrefix`
- Robuuste netwerkafhandeling:
  - retries en backoff
  - respecteert `Retry-After`
  - gzip/deflate ondersteuning
- Automatische XML-reparatie:
  - verwijdert ongeldige control characters
  - herstelt losse `&` naar geldige XML
- Logging naar `.log`.
- Alleen standaardbibliotheek (geen externe dependencies).

## Scope
Hoewel ontwikkeld voor **Collectie Nederland (DCN)**, werkt deze harvester met:
- elke OAI-PMH 2.0 endpoint
- verschillende metadataformaten (`edm`, `oai_dc`, etc.)
- zowel kleine als zeer grote datasets

## Aanbevolen gebruik
- Begin met limiet 100 voor een snelle check.
- Gebruik `--dump csv` voor snelle controle van identifiers en datestamps.
- Gebruik `--rotate-every` bij grote harvests.
- Controleer `.log`-bestanden bij fouten of onderbrekingen.
- Gebruik voor DCN:
  `https://prod.dcn.hubs.delving.org/api/oai-pmh/`

## Bekende combinaties
- `verb=ListRecords`, `metadataPrefix=edm` of `edm-strict`, optioneel `set=<uw set>`.
- `verb=ListIdentifiers` voor snelle validatie van headers.
- Andere endpoints ondersteunen vaak `oai_dc` als veilige standaard.

## Opmerking
De harvester bevat geen hardcoded endpoint of datamodel.  
U bepaalt zelf:
- de base URL
- het metadataformaat
- de set (optioneel)

Hierdoor is de tool breed inzetbaar binnen en buiten Collectie Nederland.
