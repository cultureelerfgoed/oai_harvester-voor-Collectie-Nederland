# Release Notes v1.0.0

Deze release levert een complete **oai_harvester** voor **Collectie Nederland** zonder externe dependencies.

## Belangrijk
- Hervatten via `.state.json`.
- Limiet-keuze bij starten: 1, 100, 1000 of alles.
- Extra export naar CSV en JSONL naast XML.
- Preflight checks: `Identify` en validatie van `metadataPrefix`.
- Robuuste netwerkafhandeling met retries, backoff, `Retry-After` en gzip/deflate.
- Streaming naar één geldig XML-bestand met wrapper.
- Bestandsrotatie na N items.
- Alleen standaardbibliotheek.

## Aanbevolen gebruik
- Begin met limiet 100 voor een snelle check.
- Gebruik `--dump csv` om snel een controlelijst te maken.
- Bewaar de `.log`-bestanden bij grote runs.
- Gebruik de DCN-endpoint: `https://prod.dcn.hubs.delving.org/api/oai-pmh/`.

## Bekende combinaties
- `verb=ListRecords`, `metadataPrefix=edm` of `edm-strict`, optioneel `set=<uw set>`.
- `verb=ListIdentifiers` voor een snelle header-check.
