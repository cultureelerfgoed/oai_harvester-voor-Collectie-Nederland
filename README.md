# oai_harvester voor Collectie Nederland

Deze oai_harvester is bedoeld voor **Collectie Nederland**. U harvest OAI-PMH feeds van DCN en vergelijkbare endpoints. U krijgt één valide XML-bestand per run. Optioneel maakt u ook CSV en JSONL met `identifier`, `datestamp` en een EDM-veld.

## Wat u krijgt
- Interactief of via CLI
- Streaming naar één of meerdere XML-bestanden
- Hervatten via .state.json
- Limiet: 1, 100, 1000 of alles
- Bestandsrotatie (nieuw bestand na N records)
- CSV en JSONL export (identifier, datestamp, veld naar keuze)
- Preflight: Identify en metadataPrefix-validatie
- Robuuste HTTP: retries, backoff, Retry-After, gzip/deflate
- Automatische XML-reparatie (invalid chars, losse ampersands)
- Logging naar .log
- Geen externe dependencies

## Snel starten (Collectie Nederland)
```bash
python oai_harvester.py
