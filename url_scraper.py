import streamlit as st
import requests
import pandas as pd

# Funktion zur Google-Suche via SerpAPI
def get_google_urls_from_serpapi(query, api_key, max_results=50):
    search_url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "google",
        "api_key": api_key,
        "num": max_results,
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
st.set_page_config(page_title="URL Finder für Google", layout="centered")
st.title("🔗 Google URL-Scraper über SerpAPI")

# Eingabefelder
serp_api_key = st.text_input("🔑 Dein SerpAPI Key", type="password")
suchbegriff = st.text_input("🔎 Dein Google-Suchbegriff (z. B. 'kostenloses Erstgespräch Coach site:.de')")

# Scraping starten
if st.button("🚀 50 URLs abrufen"):
    if not serp_api_key or not suchbegriff:
        st.warning("Bitte gib sowohl den SerpAPI Key als auch den Suchbegriff ein.")
    else:
        with st.spinner("Hole URLs von Google..."):
            urls, error = get_google_urls_from_serpapi(suchbegriff, serp_api_key)
            if error:
                st.error(error)
            elif not urls:
                st.warning("Keine URLs gefunden.")
            else:
                df = pd.DataFrame({"Gefundene URLs": urls})
                st.success(f"{len(urls)} URLs gefunden!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Als CSV herunterladen",
                    data=csv,
                    file_name="google_urls.csv",
                    mime="text/csv"
                )
