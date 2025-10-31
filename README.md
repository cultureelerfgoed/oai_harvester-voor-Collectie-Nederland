# oai_harvester voor Collectie Nederland

Deze oai_harvester is bedoeld voor **Collectie Nederland**. U harvest OAI-PMH feeds van DCN en vergelijkbare endpoints. U krijgt één valide XML-bestand per run. Optioneel maakt u ook CSV en JSONL met `identifier`, `datestamp` en een EDM-veld.

## Wat u krijgt
- Interactief of via CLI.
- Streaming naar één XML-bestand.
- Hervatten via `.state.json`.
- Limietkeuze: 1, 100, 1000 of alles.
- CSV en JSONL naast XML.
- Preflight: `Identify` en controle van `metadataPrefix`.
- Robuuste HTTP: retries, backoff, `Retry-After`, gzip/deflate.
- Geen externe dependencies.

## Snel starten (Collectie Nederland)
```bash
python oai_harvester.py
