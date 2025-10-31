# Sample commands — oai_harvester voor Collectie Nederland

Kopieer en plak één van de onderstaande voorbeelden. Kies de variant voor uw shell (Bash of PowerShell).

> Let op: dit bestand bevat **alleen voorbeeldcommando’s**.  
> Het CI-voorbeeld hoort in `.github/workflows/ci.yml` en niet in deze file.

---

## Bash (Linux/macOS, of Git Bash op Windows)

### 1) Alle records, met CSV én JSONL
```bash
python oai_harvester.py   --url https://prod.dcn.hubs.delving.org/api/oai-pmh/   --verb ListRecords --prefix edm --set amsterdam-museum   --out amsterdam.xml --dir ./out --dump beide --edm-field dc:title
```

### 2) Snelle test met 100 items (CSV-dump)
```bash
python oai_harvester.py   --url https://prod.dcn.hubs.delving.org/api/oai-pmh/   --verb ListRecords --prefix edm --set amsterdam-museum   --out test.xml --dir ./out --max-items 100 --dump csv --edm-field edm:isShownAt
```

### 3) Alleen identifiers (snelle header-check)
```bash
python oai_harvester.py   --url https://prod.dcn.hubs.delving.org/api/oai-pmh/   --verb ListIdentifiers --prefix edm --set amsterdam-museum   --out amsterdam_ids.xml --dir ./out --max-items 100
```

### 4) Zonder setfilter, minimale record-check (1 item)
```bash
python oai_harvester.py   --url https://prod.dcn.hubs.delving.org/api/oai-pmh/   --verb ListRecords --prefix edm   --out all_edm.xml --dir ./out --max-items 1
```

### 5) Grote run met bestandsrotatie (per 200.000 items)
```bash
python oai_harvester.py   --url https://prod.dcn.hubs.delving.org/api/oai-pmh/   --verb ListRecords --prefix edm --set amsterdam-museum   --out amsterdam.xml --dir ./out --rotate-every 200000 --dump beide --edm-field dc:title
```

---

## PowerShell (Windows)

Gebruik de **backtick** (\`) als regel-afbreking, of zet alles op één regel.

### 1) Alle records, met CSV én JSONL
```powershell
python oai_harvester.py `
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ `
  --verb ListRecords --prefix edm --set amsterdam-museum `
  --out amsterdam.xml --dir ./out --dump beide --edm-field dc:title
```

### 2) Snelle test met 100 items (CSV-dump)
```powershell
python oai_harvester.py `
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ `
  --verb ListRecords --prefix edm --set amsterdam-museum `
  --out test.xml --dir ./out --max-items 100 --dump csv --edm-field edm:isShownAt
```

### 3) Alleen identifiers (snelle header-check)
```powershell
python oai_harvester.py `
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ `
  --verb ListIdentifiers --prefix edm --set amsterdam-museum `
  --out amsterdam_ids.xml --dir ./out --max-items 100
```

### 4) Zonder setfilter, minimale record-check (1 item)
```powershell
python oai_harvester.py `
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ `
  --verb ListRecords --prefix edm `
  --out all_edm.xml --dir ./out --max-items 1
```

### 5) Grote run met bestandsrotatie (per 200.000 items)
```powershell
python oai_harvester.py `
  --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ `
  --verb ListRecords --prefix edm --set amsterdam-museum `
  --out amsterdam.xml --dir ./out --rotate-every 200000 --dump beide --edm-field dc:title
```

---

## Notities
- Gebruik **HTTPS** voor DCN: `https://prod.dcn.hubs.delving.org/api/oai-pmh/`.
- Twijfelt u aan de setnaam? Run eerst `verb=ListSets` (interactief) of laat `--set` weg voor een snelle check.
- `edm` en `edm-strict` zijn de meest gebruikte `metadataPrefix`-waarden binnen Collectie Nederland.
- Voor Windows **CMD** (niet PowerShell) gebruikt u het caret-teken (`^`) voor regelafbreking.
