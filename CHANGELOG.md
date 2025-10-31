# Changelog

## v1.0.0 — Collectie Nederland

### Nieuw
- Volledige OAI-PMH-harvester voor **Collectie Nederland (DCN)**.
- Interactief én via commandline te gebruiken.
- Ondersteuning voor `ListRecords` en `ListIdentifiers` met `resumptionToken`.
- Preflight: `Identify` en controle van `metadataPrefix`.
- Hervatten via `.state.json`.
- Limietprompt: 1, 100, 1000 of alles.
- CSV/JSONL-dump met `identifier`, `datestamp` en EDM-veld.
- Rotatie naar nieuwe bestanden na N items.
- Logging naar `<naam>.log`.

### Technisch
- Alleen Python-stdlib, geen afhankelijkheden.
- Retry/backoff + `Retry-After` + gzip/deflate-decompressie.
- XML-reparatie (control characters en losse `&`).
- Veilige state-updates en herstelbare runs.
- Compatibel met Python 3.9 en hoger.

### Bekend gedrag
- Sommige DCN-sets leveren geen records voor bepaalde `metadataPrefix`-waarden.  
  Controleer dit met `ListMetadataFormats` of test eerst met `ListSets`.
- Bij “0 items” is de output geldig XML maar zonder `<record>`-elementen.

### Aanbevolen
- Start met kleine limiet (100).
- Gebruik altijd HTTPS voor DCN (`https://prod.dcn.hubs.delving.org/api/oai-pmh/`).
- Gebruik `--dump csv` voor snelle controle van identifiers.
