
---

## `examples/sample-commands.md`

```markdown
# Sample commands

Alle records, beide dumps:
```bash
python oai_harvester.py --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out amsterdam.xml --dir ./out --dump beide --edm-field dc:title

## Snelle test met 100 items:
python oai_harvester.py --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
  --verb ListRecords --prefix edm --set amsterdam-museum \
  --out test.xml --dir ./out --max-items 100 --dump csv --edm-field edm:isShownAt


---

## `.github/workflows/ci.yml`

Minimalistische CI. Hij valideert alleen dat het script syntactisch OK is. Geen netwerkcalls in CI.

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Syntax check
        run: python -m py_compile oai_harvester.py
