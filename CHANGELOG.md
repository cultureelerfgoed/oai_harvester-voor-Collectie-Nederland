# Changelog

## v1.1.0 — Collectie Nederland

### Nieuw
- Volledige OAI-PMH-harvester voor **Collectie Nederland (DCN)** en vergelijkbare endpoints.
- Interactief én via commandline te gebruiken.
- Ondersteuning voor `ListRecords` en `ListIdentifiers` met automatische afhandeling van `resumptionToken`.
- Preflight:
  - `Identify` (repository info, granularity, earliestDatestamp)
  - Validatie van `metadataPrefix` via `ListMetadataFormats`
- Streaming output naar XML (lage geheugendruk, geschikt voor grote datasets).
- Hervatten via `.state.json` (inclusief `resumptionToken`, itemteller en bestandsindex).
- Limietoptie: 1, 100, 1000 of alles (`--max-items`).
- Bestandsrotatie: automatisch nieuw XML-bestand na N items (`--rotate-every`).
- CSV en JSONL export met:
  - `identifier`
  - `datestamp`
  - configureerbaar veld (bijv. `edm:isShownAt`, `dc:title`)
- Logging naar `<naam>.log` met voortgang en HTTP-statussen.
- Automatische output-wrapper voor geldige OAI-PMH XML.

### Technisch
- Alleen Python-stdlib (geen externe dependencies).
- Robuuste HTTP-afhandeling:
  - retries met backoff
  - respecteert `Retry-After` bij 429/503
  - ondersteuning voor gzip en deflate
- XML-verwerking:
  - verwijdering van ongeldige control characters
  - reparatie van losse `&` naar `&amp;`
  - fallback-dump bij parsefouten (`last_response_dump.xml`)
- Veilige state-opslag:
  - atomische writes (`.tmp` → replace)
  - herstelbare en idempotente runs
- Wrapper-herstel bij hervatten:
  - verwijdert closing tags en gaat correct verder schrijven
- EDM-veldextractie met fallback:
  - `edm:isShownAt`
  - fallback naar `edm:isShownBy` of `dc:identifier`
- Compatibel met Python 3.9 en hoger.

### Bekend gedrag
- Sommige DCN-sets leveren geen records voor bepaalde `metadataPrefix`-waarden.  
  Controleer dit met `ListMetadataFormats` of test met `ListSets`.
- Bij “0 items” is de output geldig XML zonder `<record>`-elementen.
- Grote harvests kunnen meerdere outputbestanden genereren bij gebruik van rotatie (`_part2`, `_part3`, ...).
- Bij instabiele endpoints kunnen retries zichtbaar vertragen door backoff.

### Aanbevolen gebruik
- Start met een kleine limiet (bijv. 100) om configuratie te testen.
- Gebruik HTTPS voor DCN:
  `https://prod.dcn.hubs.delving.org/api/oai-pmh/`
- Gebruik `--dump csv` voor snelle controle van identifiers en datestamps.
- Gebruik `--rotate-every` bij grote datasets om bestanden beheersbaar te houden.
- Controleer logs (`.log`) bij fouten of onverwachte resultaten.
