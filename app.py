import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Streamlit App-Konfiguration
st.set_page_config(page_title="Lead-Scraper & Qualifier", layout="centered")
st.title("🔍 Lead Scraper & Qualifier für Cold Calling")

# Eingabe des API-Keys
openai_api_key = st.text_input("🔑 Dein OpenAI API Key", type="password")

# Eingabe der URLs
urls_input = st.text_area("🌐 Füge hier deine Website-URLs ein (eine pro Zeile):")

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
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response['choices'][0]['message']['content']
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
    elif not urls_input.strip():
        st.warning("Bitte füge mindestens eine URL ein.")
    else:
        urls = [line.strip() for line in urls_input.strip().splitlines() if line.strip()]
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
