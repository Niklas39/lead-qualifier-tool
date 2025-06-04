import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_google_urls_from_serpapi(query, api_key, max_results=50):
    search_url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "google",
        "api_key": api_key,
        "num": 50,
        "hl": "de",
        "gl": "de"
    }
    res = requests.get(search_url, params=params)
    if res.status_code != 200:
        return [], f"SerpAPI Fehler: {res.text}"

    data = res.json()
    links = [r.get("link") for r in data.get("organic_results", []) if r.get("link")]
    return links, None

# Streamlit App-Konfiguration
st.set_page_config(page_title="Lead-Scraper & Qualifier", layout="centered")
st.title("🔍 Lead Scraper & Qualifier für Cold Calling")

# Eingabe des OpenAI-Keys
openai_api_key = st.text_input("🧠 Dein OpenAI API Key", type="password")

# Moduswahl
modus = st.radio("🔍 Wähle Eingabemethode", ["Manuell (URLs einfügen)", "Google-Suche über SerpAPI"])

# URL-Eingabe
urls = []
if modus == "Manuell (URLs einfügen)":
    urls_input = st.text_area("🌐 Füge hier deine Website-URLs ein (eine pro Zeile):")
    if urls_input:
        urls = [line.strip() for line in urls_input.strip().splitlines() if line.strip()]
else:
    SERP_API_KEY = st.text_input("🔎 Dein SerpAPI Key", type="password")
    suchbegriff = st.text_input("🔎 Dein Google-Suchbegriff (z. B. 'kostenloses Erstgespräch Coach site:.de')")
    if suchbegriff and SERP_API_KEY:
        urls, error = get_google_urls_from_serpapi(suchbegriff, SERP_API_KEY)
        if error:
            st.error(error)
        else:
            st.success(f"{len(urls)} URLs von Google geladen.")
            st.write(urls)

# Start-Button
start = st.button("🚀 Analyse starten")

# GPT-Funktion

def analyze_lead_with_gpt(api_key, url, website_text):
    prompt = f"""
    Du bist ein Lead-Qualifizierer. Prüfe die Website {url} auf folgende Kriterien:
    1. Online-Coach oder Agentur im DACH-Raum?
    2. Funnelstruktur (z. B. Calendly, Call-to-Action)?
    3. Hinweise auf Setter-/Closer-Struktur? (z. B. Team, Karriere, Vertrieb)
    4. Umsatz-Hinweise (z. B. Testimonials, Preise, Anzahl Kunden)?
    5. Firmennamen und Telefonnummer aus Impressum falls vorhanden.
    Am Ende: Ist die Seite geeignet für Cold Calling? (Ja/Nein + Begründung)
    Website-Inhalt: {website_text}
    """

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei GPT: {e}"

# Website-Inhalte holen
def scrape_website_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        return f"Fehler beim Laden der Seite: {e}"

# Hauptlogik starten
if start:
    if not openai_api_key:
        st.warning("Bitte trage deinen OpenAI API Key ein.")
    elif not urls:
        st.warning("Bitte gib URLs ein oder führe eine Google-Suche aus.")
    else:
        result_list = []

        with st.spinner("Analysiere Websites..."):
            for url in urls:
                website_text = scrape_website_text(url)
                gpt_analysis = analyze_lead_with_gpt(openai_api_key, url, website_text)
                result_list.append({"Website": url, "Analyse": gpt_analysis})

        df = pd.DataFrame(result_list)
        st.success("Analyse abgeschlossen!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Ergebnisse als CSV herunterladen",
            data=csv,
            file_name="lead_analyse_ergebnisse.csv",
            mime="text/csv"
        )
