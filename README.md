# oai_harvester voor Collectie Nederland

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![No dependencies](https://img.shields.io/badge/dependencies-none-lightgrey)

# OAI-harvester voor Collectie Nederland

Met deze Python-tool haal je metadata op uit Collectie Nederland
en andere OAI-PMH-bronnen. Je kunt de harvester interactief gebruiken
of instellingen meegeven via de opdrachtregel.

De harvester bewaart records als XML. Daarnaast kun je een CSV-
of JSONL-bestand maken met de identifier, wijzigingsdatum en
één gekozen metadataveld.

## Mogelijkheden

- Records ophalen met `ListRecords`.
- Identifiers ophalen met `ListIdentifiers`.
- Interactief een beschikbare set kiezen.
- Vooraf de bron en het metadataformaat controleren.
- Het aantal opgehaalde items beperken.
- Voortgang bewaren voor hervatten na een onderbreking.
- XML-uitvoer over meerdere bestanden verdelen.
- Aanvullend exporteren naar CSV, JSONL of beide.
- HTTP-verzoeken opnieuw proberen bij fouten.
- Uitvoering vastleggen in een logbestand.

De harvester gebruikt alleen de Python-standaardbibliotheek.
Voor het uitvoeren hoef je geen extra pakketten te installeren.

## Vereisten

- Python 3.9 of nieuwer.
- Toegang tot een OAI-PMH-endpoint.
- Schrijfrechten in de uitvoermap.

Download deze repository of kloon haar:

```text
git clone https://github.com/cultureelerfgoed/oai_harvester-voor-Collectie-Nederland.git
cd oai_harvester-voor-Collectie-Nederland
```

## Snel beginnen

Start de interactieve invoer:

```text
python oai_harvester.py
```

Het script vraagt om de bron, het type verzoek, het metadataformaat,
de set, de bestandsnaam, een eventuele limiet en de exportkeuze.

Bekijk alle opdrachtregelopties met:

```text
python oai_harvester.py --help
```

## Voorbeeld: maximaal 100 records

Dit voorbeeld gebruikt het endpoint en de set uit de bestaande
projectvoorbeelden. Controleer of die beschikbaar zijn bij de bron.

```text
python oai_harvester.py --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ --verb ListRecords --prefix edm --set amsterdam-museum --out amsterdam.xml --dir ./out --max-items 100 --dump csv --edm-field dc:title
```

De opdracht schrijft XML, een CSV met titels en een logbestand
naar de map `out`.

Gebruik voor een nieuwe harvest een nieuwe bestandsnaam of uitvoermap.
Bestaande XML-, CSV- en JSONL-bestanden kunnen worden aangevuld.

## Alle records ophalen

Laat `--max-items` weg. Het script vraagt dan om een limiet.
Kies `alles`.

```text
python oai_harvester.py --url https://prod.dcn.hubs.delving.org/api/oai-pmh/ --verb ListRecords --prefix edm --set amsterdam-museum --out amsterdam.xml --dir ./out --dump geen
```

Ook bij gebruik van opdrachtregelopties kan het script invoer vragen,
bijvoorbeeld voor ontbrekende instellingen of het hervatten van een
bestaande harvest. De huidige versie is daarom niet in alle situaties
geschikt voor uitvoering zonder toezicht.

## Instellingen

| Optie | Functie | Standaard |
|---|---|---|
| `--url` | Basis-URL van het OAI-PMH-endpoint | Interactieve invoer |
| `--verb` | Type verzoek, bijvoorbeeld `ListRecords` | Interactieve invoer |
| `--prefix` | Metadataformaat, bijvoorbeeld `edm` | Interactieve invoer waar nodig |
| `--set` | Selectie van een set | Interactieve setkeuze |
| `--out` | Bestandsnaam voor XML | Interactieve invoer |
| `--dir` | Uitvoermap | Huidige map |
| `--max-items` | Maximumaantal items | Interactieve keuze |
| `--dump` | `csv`, `jsonl`, `beide` of `geen` | Interactieve keuze |
| `--edm-field` | Metadataveld voor aanvullende export | `edm:isShownAt` |
| `--sleep` | Pauze tussen vervolgpagina's, in seconden | `0.3` |
| `--retries` | Maximumaantal HTTP-pogingen per verzoek | `3` |
| `--backoff` | Basis voor de wachttijd tussen mislukte pogingen | `1.5` |
| `--rotate-every` | Instelling voor verdeling over XML-bestanden | Uitgeschakeld |

De interactieve limietkeuze biedt `1`, `100`, `1000` en `alles`.
Via `--max-items` kun je een ander positief geheel getal opgeven.

## Uitvoerbestanden

Bij `--out amsterdam.xml` kunnen deze bestanden ontstaan:

| Bestand | Inhoud |
|---|---|
| `amsterdam.xml` | Opgehaalde XML-records of headers |
| `amsterdam_part2.xml` | Vervolgdeel bij bestandsrotatie |
| `amsterdam.csv` | Aanvullende CSV-export |
| `amsterdam.jsonl` | Aanvullende JSONL-export |
| `amsterdam.log` | Uitvoeringslog |
| `amsterdam.xml.state.json` | Voortgang voor hervatten |
| `last_response_dump.xml` | Diagnostische uitvoer bij een niet-herstelbare XML-parsefout |

De XML-export bundelt opgehaalde items in een eigen wrapper.
Het bestand is geen ongewijzigde kopie van de afzonderlijke
OAI-PMH-antwoorden van de server.

## CSV- en JSONL-export

De aanvullende export bevat per item:

- de OAI-identifier;
- de OAI-datestamp;
- één gekozen metadataveld.

Voorbeelden van velden zijn:

- `dc:title`
- `dc:identifier`
- `edm:isShownAt`
- `edm:isShownBy`

Gebruik `--dump beide` om zowel CSV als JSONL te schrijven.

De export neemt alleen de tekst van het eerste gevonden element over.
Herhaalde waarden en URI's in attributen zoals `rdf:resource`
worden niet volledig geëxporteerd.

Bij `ListIdentifiers` ontbreken metadata-elementen.
Het gekozen metadataveld blijft dan leeg.

Gebruik de XML-uitvoer wanneer je de volledige opgehaalde metadata
nodig hebt.

## Hervatten

Tijdens het ophalen bewaart het script de voortgang in een
`.state.json`-bestand. Daarin staan onder meer de itemteller,
het bestandsdeel en het resumption token voor een volgende pagina.

Start na een onderbreking met dezelfde bron, instellingen,
bestandsnaam en uitvoermap. Als het script een passende state vindt,
vraagt het of je wilt hervatten.

Houd rekening met deze grenzen:

- Voortgang wordt per pagina opgeslagen.
- Bij een onderbreking tijdens het schrijven kan hervatten duplicaten opleveren.
- Hervatten werkt alleen zolang de bron het opgeslagen token accepteert.
- Bij normale afronding verwijdert het script het statebestand.
- Ook stoppen op `--max-items` verwijdert het statebestand.

Een beperkte proefharvest is daardoor geen hervatbare eerste stap
van een volledige harvest. Gebruik voor de volledige harvest
een nieuwe uitvoermap of bestandsnaam.

## Bestandsrotatie

Met bijvoorbeeld `--rotate-every 200000` kun je XML-uitvoer over
meerdere bestanden verdelen.

De huidige code controleert de rotatie na een volledige pagina.
Een nieuw bestand ontstaat alleen wanneer de totale itemteller
op dat moment exact deelbaar is door de ingestelde waarde.

De optie garandeert dus geen vast maximumaantal records per bestand.
CSV en JSONL blijven elk in één bestand staan.

## Netwerk- en XML-verwerking

De harvester:

- probeert mislukte HTTP-verzoeken opnieuw;
- gebruikt oplopende wachttijden;
- verwerkt een numerieke `Retry-After` bij HTTP 429 en 503;
- ondersteunt gzip- en deflate-compressie;
- verwijdert ongeldige XML-controlekarakters;
- probeert bij een parsefout losse ampersands te herstellen.

Deze verwerking kan de ontvangen tekst aanpassen.
De export is daarom geen bytegetrouw bronarchief.

## Grenzen van de huidige versie

- Paginering is uitgewerkt voor `ListRecords` en `ListIdentifiers`.
- De interactieve setkeuze leest alleen de eerste `ListSets`-pagina.
- Er zijn geen `--from`- en `--until`-opties voor datumselectie.
- Er is geen identifieroptie voor een volledig `GetRecord`-verzoek.
- CSV en JSONL bevatten slechts één geselecteerd metadataveld.
- De code behandelt OAI-PMH-foutmeldingen in XML niet expliciet als fout.

Controleer daarom na een harvest het logbestand, de uitvoer
en het verwachte aantal records. Een normale afsluiting alleen
bewijst niet dat de volledige gewenste dataset is opgehaald.

## Projectbestanden

| Pad | Inhoud |
|---|---|
| `oai_harvester.py` | Harvester en opdrachtregelinterface |
| `examples/` | Snelstart en voorbeeldopdrachten |
| `tests/` | Basistests voor import en CLI-help |
| `.github/workflows/ci.yml` | Automatische controles |
| `CHANGELOG.md` | Wijzigingsgeschiedenis |
| `CONTRIBUTING.md` | Bijdragen aan het project |
| `SECURITY.md` | Beveiligingsinformatie |
| `LICENSE` | MIT-licentie |

## Bijdragen

Lees [CONTRIBUTING.md](CONTRIBUTING.md) voordat je wijzigingen indient.

De huidige tests controleren of het script bestaat, kan worden
geïmporteerd en helptekst geeft. Ze testen geen volledige harvest
of het hervatten na een onderbreking.

## Licentie en maker

Ontwikkeld door Joop Vanderheiden.

De software valt onder de [MIT-licentie](LICENSE).
De licentie van de software bepaalt niet de gebruiksvoorwaarden
van de opgehaalde metadata. Raadpleeg daarvoor de betreffende bron.
