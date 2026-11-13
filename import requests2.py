
import requests

base_url = "https://rce.adlibhosting.com/harvest/oai.ashx"

for verb in ["Identify", "ListMetadataFormats", "ListSets"]:
    print(f"\n=== {verb} ===", flush=True)

    try:
        response = requests.get(
            base_url,
            params={"verb": verb},
            timeout=30
        )
        print("URL:", response.url)
        print("HTTP:", response.status_code)
        print("Antwoord:")
        print(response.text[:3000])
    except requests.RequestException as e:
        print("FOUT:", e)
