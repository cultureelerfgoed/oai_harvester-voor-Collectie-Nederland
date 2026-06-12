#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete OAI-PMH harvester (stdlib-only) met:
- Interactieve invoer of CLI-opties
- Robust fetch (retries, backoff, gzip/deflate, Retry-After)
- Preflight: Identify + validatie ListMetadataFormats
- Streaming naar één bestand met OAI-conforme wrapper
- Rotatie: nieuw bestand na N items
- Hervatten via .state.json
- Limiet-keuze: 1, 100, 1000 of alles
- CSV/JSONL-dumper: identifier, datestamp, en één EDM-veld

Gebruik:
    python oai_harvester.py
of:
    python oai_harvester.py --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ \
        --verb ListRecords --prefix edm --set amsterdam-museum \
        --out amsterdam.xml --dir ./out --sleep 0.3 --retries 3 \
        --max-items 1000 --rotate-every 200000 --dump beide --edm-field edm:isShownAt
"""

import argparse
import io
import json
import os
import re
import time
import gzip
import zlib
import csv
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Optional, Tuple

# Verwijder ongeldige XML control chars (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F)
INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

# Repareer losse & die geen geldige entity openen, bijv. "A&B" -> "A&amp;B"
AMP_FIX = re.compile(r'&(?![A-Za-z#][A-Za-z0-9]*;)')

# Namespaces
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "edm": "http://www.europeana.eu/schemas/edm/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "ore": "http://www.openarchives.org/ore/terms/",
}

# -----------------------------
# Kleine hulpfuncties
# -----------------------------
def ask_input(prompt_text: str, default: Optional[str] = None) -> str:
    txt = input(f"{prompt_text}{f' [{default}]' if default else ''}: ").strip()
    return txt or (default or "")

def ask_limit_interactive() -> Optional[int]:
    print("Kies limiet: 1, 100, 1000 of alles.")
    ans = input("Limiet [alles]: ").strip().lower()
    if not ans or ans == "alles":
        return None
    if ans in ("1", "100", "1000"):
        return int(ans)
    print("Onbekende keuze. Ik neem 'alles'.")
    return None

def ask_dump_interactive() -> Tuple[str, Optional[str]]:
    print("Extra export? Kies: csv, jsonl, beide of geen.")
    dump_mode = input("Dump [geen]: ").strip().lower() or "geen"
    if dump_mode not in ("csv", "jsonl", "beide", "geen"):
        print("Onbekende keuze. Ik neem 'geen'.")
        dump_mode = "geen"
    edm_field = None
    if dump_mode in ("csv", "jsonl", "beide"):
        edm_field = input("EDM-veld (bijv. edm:isShownAt, edm:isShownBy, dc:title) [edm:isShownAt]: ").strip() or "edm:isShownAt"
    return dump_mode, edm_field

def yes_no(prompt_text: str, default_yes: bool = False) -> bool:
    default = "Y/n" if default_yes else "y/N"
    ans = input(f"{prompt_text} ({default}): ").strip().lower()
    if not ans:
        return default_yes
    return ans in ("y", "yes", "ja", "j")

def clean_xml(s: str) -> str:
    s = INVALID_XML_CHARS.sub("", s)
    return s

def build_url(base: str, params: dict) -> str:
    base = base.rstrip("?")
    return f"{base}?{urllib.parse.urlencode(params)}"

# -----------------------------
# Logging
# -----------------------------
class Logger:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def log(self, msg: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

# -----------------------------
# HTTP ophalen met retries en Retry-After
# -----------------------------
def safe_open_url(req: urllib.request.Request, logger: Logger, retries: int = 3, backoff: float = 1.5) -> Tuple[int, str, bytes, dict]:
    """
    HTTP GET met retries en backoff.
    Respecteert Retry-After bij 429/503.
    Retourneert (status, content_type, raw_bytes, headers_dict).
    """
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req) as resp:
                status = getattr(resp, "status", 200)
                headers = {k: v for k, v in resp.headers.items()}
                ct = headers.get("Content-Type", "")
                ce = headers.get("Content-Encoding", "")
                raw = resp.read()

                # Decompressie (pas ná read)
                if ce.lower() == "gzip":
                    raw = gzip.decompress(raw)
                elif ce.lower() in ("deflate", "zlib"):
                    try:
                        raw = zlib.decompress(raw)
                    except zlib.error:
                        raw = zlib.decompress(raw, -zlib.MAX_WBITS)

                logger.log(f"HTTP {status} | Content-Type: {ct} | Content-Encoding: {ce or 'none'}")
                return status, ct, raw, headers

        except urllib.error.HTTPError as e:
            last_err = e
            status = e.code
            headers = {k: v for k, v in (e.headers or {}).items()}
            retry_after = headers.get("Retry-After")
            wait = backoff * (attempt + 1)
            if status in (429, 503) and retry_after:
                try:
                    wait = max(wait, float(retry_after))
                except ValueError:
                    # Als Retry-After geen seconds is: val terug op backoff
                    pass
            if attempt == retries - 1:
                raise
            logger.log(f"HTTPError {status}: {e.reason}. Wachten {wait:.1f}s en opnieuw proberen...")
            time.sleep(wait)

        except Exception as e:
            last_err = e
            if attempt == retries - 1:
                raise
            wait = backoff * (attempt + 1)
            logger.log(f"Netwerkfout: {e}. Wachten {wait:.1f}s en opnieuw proberen...")
            time.sleep(wait)

    if last_err:
        raise last_err

def fetch_and_parse(url: str, headers: dict, last_resp_path: str, logger: Logger,
                    retries: int, backoff: float) -> Tuple[ET.Element, str]:
    """
    Haal op -> decodeer -> schoon -> parse.
    Bij parsefout: één reparatiepoging met AMP_FIX. Dump ruwe response en stop als het dan nog faalt.
    Retourneert (root_element, text_na_clean/repair).
    """
    req = urllib.request.Request(url, headers=headers)
    status, ct, raw, _ = safe_open_url(req, logger, retries=retries, backoff=backoff)

    # Decodeer en schoon
    text = raw.decode("utf-8", errors="replace")
    text = clean_xml(text)

    # Eerste parsepoging
    try:
        root = ET.fromstring(text)
        return root, text
    except ET.ParseError:
        pass

    # Reparatie: losse & omzetten naar &amp; en opnieuw proberen
    repaired = AMP_FIX.sub("&amp;", text)
    try:
        root = ET.fromstring(repaired)
        logger.log("Waarschuwing: XML gerepareerd (losse & geëscapet).")
        return root, repaired
    except ET.ParseError as e2:
        # Dump voor diagnose
        with open(last_resp_path, "w", encoding="utf-8") as dump:
            dump.write(text)
        raise RuntimeError(f"XML parsefout: {e2}. Ruwe response in {last_resp_path}")

# -----------------------------
# OAI helpers
# -----------------------------
def wrapper_open_tag(verb: str) -> str:
    if verb == "ListRecords":
        return "<OAI-PMH>\n<ListRecords>\n"
    if verb == "ListIdentifiers":
        return "<OAI-PMH>\n<ListIdentifiers>\n"
    return "<OAI-PMH>\n"

def wrapper_close_tag(verb: str) -> str:
    if verb == "ListRecords":
        return "</ListRecords>\n</OAI-PMH>\n"
    if verb == "ListIdentifiers":
        return "</ListIdentifiers>\n</OAI-PMH>\n"
    return "</OAI-PMH>\n"

def ensure_open_wrapper(out_path: str, verb: str, logger: Logger):
    """
    Zorg dat begin-tags aanwezig zijn en strip closing tags bij hervatten.
    """
    open_tag = wrapper_open_tag(verb)
    close_tag = wrapper_close_tag(verb)

    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(open_tag)
        return

    tail_len = min(8192, os.path.getsize(out_path))
    with open(out_path, "rb") as f:
        f.seek(-tail_len, os.SEEK_END)
        tail = f.read().decode("utf-8", errors="ignore")

    idx = tail.rfind(close_tag)
    if idx != -1:
        with open(out_path, "rb+") as f:
            f.seek(-tail_len + idx, os.SEEK_END)
            f.truncate()
        logger.log("Closing tags verwijderd om te hervatten.")

def write_close_wrapper(out_path: str, verb: str):
    with open(out_path, "a", encoding="utf-8") as out:
        out.write(wrapper_close_tag(verb))

def oai_params_first_call(verb: str, metadata_prefix: Optional[str], set_spec: Optional[str]) -> dict:
    params = {"verb": verb}
    if verb in ("ListRecords", "ListIdentifiers"):
        if metadata_prefix:
            params["metadataPrefix"] = metadata_prefix
        if set_spec:
            params["set"] = set_spec
    return params

# -----------------------------
# State (hervatten)
# -----------------------------
def state_path_for(out_path: str) -> str:
    return out_path + ".state.json"

def save_state(path: str, state: dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def load_state(path: str) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def remove_state(path: str):
    if os.path.exists(path):
        os.remove(path)

# -----------------------------
# Preflight: Identify + ListMetadataFormats
# -----------------------------
def preflight_identify(base_url: str, headers: dict, dump_path: str, logger: Logger, retries: int, backoff: float):
    url = build_url(base_url, {"verb": "Identify"})
    logger.log(f"Preflight Identify: {url}")
    root, text = fetch_and_parse(url, headers, dump_path, logger, retries, backoff)
    text = clean_xml(text)
    root = ET.fromstring(text)

    repo = root.find(".//oai:Identify/oai:repositoryName", NS)
    base = root.find(".//oai:Identify/oai:baseURL", NS)
    gran = root.find(".//oai:Identify/oai:granularity", NS)
    earliest = root.find(".//oai:Identify/oai:earliestDatestamp", NS)

    logger.log(f"Identify: repositoryName={repo.text if repo is not None else '?'} | "
               f"baseURL={base.text if base is not None else '?'} | "
               f"granularity={gran.text if gran is not None else '?'} | "
               f"earliestDatestamp={earliest.text if earliest is not None else '?'}")

def preflight_check_metadata_prefix(base_url: str, headers: dict, dump_path: str, logger: Logger,
                                    desired_prefix: str, retries: int, backoff: float):
    url = build_url(base_url, {"verb": "ListMetadataFormats"})
    logger.log(f"Preflight ListMetadataFormats: {url}")
    root, text = fetch_and_parse(url, headers, dump_path, logger, retries, backoff)
    text = clean_xml(text)
    root = ET.fromstring(text)

    prefixes = [el.text.strip() for el in root.findall(".//oai:metadataPrefix", NS) if el.text]
    logger.log(f"Beschikbare metadataPrefix: {', '.join(prefixes) if prefixes else '(geen)'}")
    if desired_prefix not in prefixes:
        raise SystemExit(f"metadataPrefix '{desired_prefix}' niet beschikbaar. Kies een van: {', '.join(prefixes)}")

# -----------------------------
# EDM-veld extractie
# -----------------------------
def resolve_qname(qname: str) -> Tuple[str, dict]:
    if ":" not in qname:
        return qname, NS
    prefix, local = qname.split(":", 1)
    if prefix not in NS:
        return qname, NS
    return f".//{prefix}:{local}", NS

def extract_edm_field_from_record(record_el: ET.Element, edm_field_qname: str) -> str:
    md = record_el.find("oai:metadata", NS)
    if md is None:
        return ""
    xpath, nsmap = resolve_qname(edm_field_qname)
    el = md.find(xpath, nsmap) if xpath.startswith(".//") else md.find(xpath, nsmap)
    if el is not None and el.text:
        return el.text.strip()
    if edm_field_qname == "edm:isShownAt":
        el2 = md.find(".//edm:isShownBy", NS) or md.find(".//dc:identifier", NS)
        if el2 is not None and el2.text:
            return el2.text.strip()
    return ""

# -----------------------------
# Harvest met rotatie, limiet, CSV/JSONL
# -----------------------------
def harvest(base_url: str, verb: str, metadata_prefix: Optional[str], set_spec: Optional[str],
            out_path: str, last_resp_path: str, logger: Logger,
            sleep_between: float = 0.3, retries: int = 3, backoff: float = 1.5,
            max_items: Optional[int] = None, rotate_every: Optional[int] = None,
            dump_mode: str = "geen", edm_field: Optional[str] = None):

    headers = {
        "User-Agent": "OAI-PMH harvester (Python stdlib)",
        "Accept": "application/xml, text/xml;q=0.9, */*;q=0.1",
        "Accept-Encoding": "identity, gzip, deflate",
    }

    # Preflight
    try:
        preflight_identify(base_url, headers, last_resp_path, logger, retries, backoff)
    except Exception as e:
        logger.log(f"Waarschuwing: Identify mislukte: {e}")

    if verb in ("ListRecords", "ListIdentifiers") and metadata_prefix:
        preflight_check_metadata_prefix(base_url, headers, last_resp_path, logger, metadata_prefix, retries, backoff)

    st_path = state_path_for(out_path)
    state = load_state(st_path)

    # Niet-paginerende verbs
    if verb not in ("ListRecords", "ListIdentifiers"):
        params = oai_params_first_call(verb, metadata_prefix, set_spec)
        url = build_url(base_url, params)
        logger.log(f"Ophalen: {url}")
        root, text = fetch_and_parse(url, headers, last_resp_path, logger, retries, backoff)
        text = clean_xml(text)
        root = ET.fromstring(text)
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(wrapper_open_tag(verb))
            out.write(ET.tostring(root, encoding="unicode"))
            out.write("\n")
            out.write(wrapper_close_tag(verb))
        logger.log(f"Klaar. Response opgeslagen in {out_path}")
        remove_state(st_path)
        return

    # Paginerende verbs
    base_name = os.path.splitext(out_path)[0]
    ext = os.path.splitext(out_path)[1] or ".xml"

    def out_path_for_index(idx: int) -> str:
        return f"{base_name}_part{idx}{ext}" if idx > 1 else out_path

    # CSV/JSONL setup
    csv_path = jsonl_path = None
    csv_writer = None
    if dump_mode in ("csv", "beide"):
        csv_path = base_name + ".csv"
    if dump_mode in ("jsonl", "beide"):
        jsonl_path = base_name + ".jsonl"

    def open_csv():
        nonlocal csv_writer
        if csv_path:
            newfile = not os.path.exists(csv_path)
            f = open(csv_path, "a", encoding="utf-8", newline="")
            w = csv.writer(f)
            if newfile:
                w.writerow(["identifier", "datestamp", (edm_field or "edm_field")])
            csv_writer = (f, w)

    def close_csv():
        nonlocal csv_writer
        if csv_writer:
            f, _ = csv_writer
            f.close()
            csv_writer = None

    def write_csv_row(identifier: str, datestamp: str, value: str):
        if csv_writer:
            _, w = csv_writer
            w.writerow([identifier, datestamp, value])

    def write_jsonl_row(identifier: str, datestamp: str, value: str):
        if jsonl_path:
            with open(jsonl_path, "a", encoding="utf-8") as jf:
                jf.write(json.dumps({"identifier": identifier, "datestamp": datestamp, (edm_field or "edm_field"): value}, ensure_ascii=False) + "\n")

    # State init
    if state and state.get("verb") == verb and state.get("out_base") == base_name:
        logger.log(f"Gevonden state: {st_path}")
        logger.log(f"- items={state.get('num_items', 0)}  rotatie_index={state.get('file_index', 1)}")
        if yes_no("Hervatten met bestaande state", default_yes=True):
            num_items = int(state.get("num_items", 0))
            rt = state.get("resumptionToken", "")
            params = {"verb": verb, "resumptionToken": rt} if rt else oai_params_first_call(verb, state.get("metadataPrefix"), state.get("set"))
            file_index = int(state.get("file_index", 1))
            current_out = out_path_for_index(file_index)
        else:
            logger.log("We starten opnieuw en overschrijven output.")
            state = None
            num_items = 0
            file_index = 1
            current_out = out_path_for_index(file_index)
            with open(current_out, "w", encoding="utf-8"):
                pass
            remove_state(st_path)
            params = oai_params_first_call(verb, metadata_prefix, set_spec)
    else:
        num_items = 0
        file_index = 1
        current_out = out_path_for_index(file_index)
        params = oai_params_first_call(verb, metadata_prefix, set_spec)
        state = {
            "base_url": base_url,
            "verb": verb,
            "metadataPrefix": metadata_prefix,
            "set": set_spec,
            "out_base": base_name,
            "file_index": file_index,
            "num_items": 0,
            "resumptionToken": "",
        }
        save_state(st_path, state)

    # Open wrapper en dumpers
    ensure_open_wrapper(current_out, verb, logger)
    if dump_mode in ("csv", "beide"):
        open_csv()

    page = 0
    try:
        while True:
            if max_items is not None and num_items >= max_items:
                logger.log(f"Max-items bereikt ({max_items}). Stoppen.")
                break

            page += 1
            url = build_url(base_url, params)
            logger.log(f"Ophalen: {url}")

            root, text = fetch_and_parse(url, headers, last_resp_path, logger, retries, backoff)
            text = clean_xml(text)
            root = ET.fromstring(text)

            # Selecteer items
            if verb == "ListRecords":
                elements = root.findall(".//oai:record", NS)
            else:
                elements = root.findall(".//oai:header", NS)

            # Schrijf items
            with open(current_out, "a", encoding="utf-8") as out:
                for el in elements:
                    if max_items is not None and num_items >= max_items:
                        break

                    out.write(ET.tostring(el, encoding="unicode"))
                    out.write("\n")

                    header = el.find("./oai:header", NS) if verb == "ListRecords" else el
                    identifier = header.findtext("./oai:identifier", default="", namespaces=NS).strip()
                    datestamp = header.findtext("./oai:datestamp", default="", namespaces=NS).strip()

                    value = ""
                    if verb == "ListRecords" and edm_field:
                        value = extract_edm_field_from_record(el, edm_field)

                    if csv_path:
                        write_csv_row(identifier, datestamp, value)
                    if jsonl_path:
                        write_jsonl_row(identifier, datestamp, value)

                    num_items += 1
                    if num_items % 1000 == 0:
                        logger.log(f"{num_items} items verwerkt...")

            # Rotatie?
            if rotate_every and num_items > 0 and (num_items % rotate_every == 0):
                write_close_wrapper(current_out, verb)
                file_index += 1
                current_out = out_path_for_index(file_index)
                ensure_open_wrapper(current_out, verb, logger)
                logger.log(f"Bestandsrotatie: gestart met {current_out}")

            # Volgende pagina
            rt_el = root.find(".//oai:resumptionToken", NS)
            rt = rt_el.text.strip() if rt_el is not None and rt_el.text else ""
            logger.log(f"Pagina {page}: {len(elements)} items. ResumptionToken {'aanwezig' if rt else 'ontbreekt'}.")

            state.update({
                "file_index": file_index,
                "num_items": num_items,
                "resumptionToken": rt,
            })
            save_state(st_path, state)

            if not rt:
                break

            params = {"verb": verb, "resumptionToken": rt}
            time.sleep(sleep_between)

        write_close_wrapper(current_out, verb)
        remove_state(st_path)
        logger.log(f"Klaar. Totaal {num_items} items opgeslagen."
                   + (f" Laatste bestand: {current_out}" if rotate_every else f" Bestand: {current_out}"))
        if csv_path:
            logger.log(f"CSV: {csv_path}")
        if jsonl_path:
            logger.log(f"JSONL: {jsonl_path}")

    finally:
        if dump_mode in ("csv", "beide"):
            close_csv()

# -----------------------------
# CLI
# -----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Complete OAI-PMH harvester met hervatten, rotatie, limiet en CSV/JSONL-dump.")
    p.add_argument("--url", help="Base URL van OAI-PMH endpoint, bv. https://prod.dcn.hubs.delving.org/api/oai-pmh/")
    p.add_argument("--verb", help="OAI-PMH verb, bv. ListRecords, ListIdentifiers")
    p.add_argument("--prefix", help="metadataPrefix, bv. edm")
    p.add_argument("--set", dest="set_spec", help="set= waarde, bv. amsterdam-museum")
    p.add_argument("--out", help="Bestandsnaam (zonder pad), bv. harvest.xml")
    p.add_argument("--dir", default=".", help="Doelmap")
    p.add_argument("--sleep", type=float, default=0.3, help="Pauze tussen requests (s)")
    p.add_argument("--retries", type=int, default=3, help="Max. retries per request")
    p.add_argument("--backoff", type=float, default=1.5, help="Backoff-factor")
    p.add_argument("--max-items", type=int, default=None, help="Stop na dit aantal items (anders interactief)")
    p.add_argument("--rotate-every", type=int, default=None, help="Start nieuw bestand na N items")
    p.add_argument("--dump", choices=["csv", "jsonl", "beide", "geen"], help="Extra export naast XML")
    p.add_argument("--edm-field", help="EDM-veld, bv. edm:isShownAt, dc:title")
    return p.parse_args()

def main():
    args = parse_args()

    # Interactief invullen waar niets is opgegeven
    base_url = args.url or ask_input("Voer OAI-PMH base URL in", "https://prod.dcn.hubs.delving.org/api/oai-pmh/")
    verb = args.verb or ask_input("Geef verb", "ListRecords")
    metadata_prefix = args.prefix
    if verb in ("ListRecords", "ListIdentifiers", "GetRecord") and not metadata_prefix:
        metadata_prefix = ask_input("Geef metadataPrefix", "edm")
    set_spec = args.set_spec
    if verb in ("ListRecords", "ListIdentifiers") and set_spec is None:
        set_spec = ask_input("Geef set= waarde (of laat leeg)", "amsterdam-museum")

    default_name = f"{verb.lower()}_{(set_spec or 'all')}.xml"
    filename = args.out or ask_input("Geef bestandsnaam (zonder pad)", default_name)
    out_dir = args.dir or ask_input("Geef doelmap (pad)", ".")
    os.makedirs(out_dir, exist_ok=True)

    # Limiet: 1, 100, 1000 of alles (None)
    max_items = args.max_items if args.max_items is not None else ask_limit_interactive()

    # Dump-keuze
    dump_mode = args.dump if args.dump else None
    edm_field = args.edm_field if args.edm_field else None
    if not dump_mode:
        dump_mode, edm_field = ask_dump_interactive()
    if dump_mode in ("csv", "jsonl", "beide") and not edm_field:
        edm_field = "edm:isShownAt"

    out_path = os.path.join(out_dir, filename)
    log_path = os.path.join(out_dir, (os.path.splitext(filename)[0] + ".log"))
    last_resp_path = os.path.join(out_dir, "last_response_dump.xml")
    logger = Logger(log_path)

    logger.log("=== OAI-PMH harvester start ===")
    logger.log(f"URL={base_url} verb={verb} prefix={metadata_prefix or '-'} set={set_spec or '-'}")
    logger.log(f"Output={out_path} Sleep={args.sleep} Retries={args.retries} Backoff={args.backoff} "
               f"MaxItems={max_items or '-'} RotateEvery={args.rotate_every or '-'} Dump={dump_mode} EDM={edm_field or '-'}")

    try:
        harvest(
            base_url=base_url,
            verb=verb,
            metadata_prefix=metadata_prefix,
            set_spec=set_spec,
            out_path=out_path,
            last_resp_path=last_resp_path,
            logger=logger,
            sleep_between=args.sleep,
            retries=args.retries,
            backoff=args.backoff,
            max_items=max_items,
            rotate_every=args.rotate_every,
            dump_mode=dump_mode,
            edm_field=edm_field,
        )
    except Exception as e:
        logger.log(f"Fout: {e}")
        raise
    finally:
        logger.log("=== OAI-PMH harvester einde ===")

if __name__ == "__main__":
    main()
