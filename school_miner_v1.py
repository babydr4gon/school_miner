"""
SCHUL-SCANNER (National Edition & Strict Mode)
V13.0
"""

import os
import pandas as pd
import json
import time
import warnings
import re
import random
import sys
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import shutil 
import webbrowser
import sys

from openai import OpenAI
from google import genai
from ddgs import DDGS
import folium
from folium import Element
from geopy.geocoders import Nominatim

# Selenium & Webdriver Manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- SETUP & CONFIG ---
warnings.filterwarnings("ignore")
load_dotenv()

CONFIG_FILE = "config.json"

DEFAULT_SCHULTYPEN = ["Grundschule", "Hauptschule", "Realschule", "Gymnasium", "Gesamtschule", "Förderschule", "Berufsschule", "Verbundschule", "Mittelstufenschule", "Oberstufengymnasium"]
DEFAULT_HARD_KEYWORDS = ["MINT", "Sport", "Musik", "Gesellschaftswissenschaften", "Sprachen", "bilingual", "Lernlabor", "Lernloft", "Lernatelier", "sinnstiftend", "themenorientiert", "Makerspace", "Multikultur", "Charakter", "Montessori", "Walldorf", "Jenaplan", "jahrgangsübergreifend", "altersübergreifend", "Ganztag"]

PRIORITY_LINKS_L1 = ["Schulprofil", "Schulprogramm", "Leitbild", "Über uns", "Unsere Schule", "Wir über uns"]
PRIORITY_LINKS_L2 = ["Leitbild", "Konzept", "Pädagogik", "Schwerpunkte", "Ganztag", "Angebote", "AGs", "Förderung"]

DEFAULT_CONFIG = {
    "INPUT_FILE": "schulen.xlsx",
    "OUTPUT_FILE": "schulen_ergebnisse.xlsx",
    "MAP_FILE": "schulen_karte.html",
    "COLUMN_NAME_IDX": 0,
    "COLUMN_ORT_IDX": 2,
    "GEMINI_MODEL": "gemini-2.0-flash-exp", 
    "OPENROUTER_MODEL": "meta-llama/llama-3.3-70b-instruct", 
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "WAIT_TIME": 2.0, 
    "SENSITIVITY": "normal", 
    "SCHULTYPEN_LISTE": DEFAULT_SCHULTYPEN,
    "KEYWORD_LISTE": DEFAULT_HARD_KEYWORDS,
    "AI_PRIORITY": ["openai", "gemini", "groq", "openrouter"],
    "MANUAL_RESUME_IDX": 0,
    "PROMPT_TEMPLATE": (
        "Du bist ein Schul-Analyst. Ich gebe dir Textauszüge von der Webseite.\n"
        "Fasse das pädagogische Konzept zusammen.\n"
        "Ignoriere Navigationstext.\n"
        "Maximal 3 Sätze.\n\n"
        "Text:\n{text}"
    ),
    
    "ERROR_MARKERS": ["Nicht gefunden", "Keine Daten", "KI-Fehler", "QUOTA", "Error", "Zu wenige Infos", "Strict Filter", "Nicht erreichbar"]
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for k, v in loaded.items(): cfg[k] = v
        except: pass
    return cfg

def save_config_to_file(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        print("💾 Config gespeichert.")
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Config: {e}")

CONFIG = load_config()

def open_browser_search(query):
    """
    Versucht, Chrome/Chromium zu öffnen (Linux/Windows).
    Fallback auf Standard-Browser.
    """
    url = f"https://duckduckgo.com/?q={query}"
    
   
    browsers_to_try = []
    if sys.platform.startswith("linux"):
        browsers_to_try = ['chromium-browser', 'chromium', 'google-chrome']
    elif sys.platform.startswith("win"):
        browsers_to_try = ['google-chrome', 'chrome'] 
    
    # Versuch 1: Spezifische Browser
    for b in browsers_to_try:
        try:
            webbrowser.get(b).open(url)
            return
        except: continue
            
    # Versuch 2: Standard-Browser (Fallback)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"   ⚠️ Konnte Browser nicht öffnen: {e}")

# --- API CLIENT SETUP ---
clients = {}
keys = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY"),
    "groq": os.getenv("GROQ_API_KEY")
}
status_flags = {k: bool(v) for k, v in keys.items()}

if status_flags["gemini"]: clients["gemini"] = genai.Client(api_key=keys["gemini"])
if status_flags["openai"]: clients["openai"] = OpenAI(api_key=keys["openai"])
if status_flags["groq"]: clients["groq"] = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=keys["groq"])
if status_flags["openrouter"]:
    clients["openrouter"] = OpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=keys["openrouter"],
        default_headers={"HTTP-Referer": "https://github.com/schul-scanner", "X-Title": "Schul-Scanner"}
    )

def print_system_status():
    print("\n🔌 SYSTEM-CHECK API KEYS:")
    for service, active in status_flags.items():
        print(f"   • {service.title()}: {'✅' if active else '❌'}")
    print(f"   • Sensibilität: {CONFIG['SENSITIVITY'].upper()}")
    print("-" * 30)

# --- SELENIUM DRIVER ---

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    #service = Service(ChromeDriverManager().install())
    service = Service(executable_path=r'/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(15) # Max 15 Sek Ladezeit
    return driver

# --- DATA MANAGEMENT ---

def load_data():
    data = []
    # Versuch 1: Hauptdatei laden
    if os.path.exists(CONFIG["OUTPUT_FILE"]):
        try: 
            data = pd.read_excel(CONFIG["OUTPUT_FILE"]).to_dict('records')
        except Exception as e: 
            print(f"⚠️ Hauptdatei beschädigt oder leer ({e}). Versuche Backup...")
            
    # Versuch 2: Backup laden, falls Hauptdatei leer/kaputt
    if not data and os.path.exists(CONFIG["OUTPUT_FILE"] + ".bak"):
        try:
            print("🔄 RESTORE: Stelle Daten aus Backup wieder her!")
            shutil.copy(CONFIG["OUTPUT_FILE"] + ".bak", CONFIG["OUTPUT_FILE"])
            data = pd.read_excel(CONFIG["OUTPUT_FILE"]).to_dict('records')
        except Exception as e:
            print(f"❌ Auch Backup konnte nicht geladen werden: {e}")

    return data

def save_data(data):
    try:
        # 1. Sicherheits-Backup der alten Datei erstellen (falls existent)
        if os.path.exists(CONFIG["OUTPUT_FILE"]):
            try:
                shutil.copy(CONFIG["OUTPUT_FILE"], CONFIG["OUTPUT_FILE"] + ".bak")
            except: pass # Wenn Backup fehlschlägt, ist das kein Beinbruch
        
        # 2. Neue Datei schreiben
        pd.DataFrame(data).to_excel(CONFIG["OUTPUT_FILE"], index=False)
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER beim Speichern: {e}")
        # Versuchen, wenigstens das Backup zurückzuspielen, falls der Schreibvorgang die Datei zerstört hat
        if os.path.exists(CONFIG["OUTPUT_FILE"] + ".bak"):
            print("   -> Stelle alte Version wieder her, um Datenverlust zu minimieren.")
            shutil.copy(CONFIG["OUTPUT_FILE"] + ".bak", CONFIG["OUTPUT_FILE"])

def sync_with_source(current_data):
    print("\n🔄 Sync mit Ursprungsdatei...")
    if not os.path.exists(CONFIG["INPUT_FILE"]): 
        print(f"❌ Datei {CONFIG['INPUT_FILE']} fehlt."); return current_data
    try:
        df_raw = pd.read_excel(CONFIG["INPUT_FILE"], header=None)
        existing = {str(d['schulname']).strip() for d in current_data}
        added = 0
        for _, row in df_raw.iterrows():
            if len(row) <= max(CONFIG["COLUMN_NAME_IDX"], CONFIG["COLUMN_ORT_IDX"]): continue
            n = str(row[CONFIG["COLUMN_NAME_IDX"]]).strip()
            if len(n) > 4 and "schule" in n.lower() and "=" not in n and n not in existing:
                current_data.append({
                    'schulname': n, 'ort': str(row[CONFIG["COLUMN_ORT_IDX"]]).strip(),
                    'schultyp': "", 'keywords': "", 
                    'webseite': "Nicht gefunden", 'ki_zusammenfassung': "Keine Daten"
                })
                existing.add(n); added += 1
        if added: save_data(current_data); print(f"✅ {added} neue Schulen.")
        else: print("ℹ️ Keine neuen Einträge.")
    except Exception as e: print(f"❌ Sync-Fehler: {e}")
    return current_data

# --- CRAWLER LOGIC ---

def search_ddg_robust(query, max_retries=3):
    """Sucht URL. Filtert Wikipedia explizit raus."""
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region='de-de', max_results=5, backend="api"))
            
            for res in results:
                url = res['href']
                # FILTER: Keine Wikipedia, keine Facebook/Instagram Seiten wenn möglich
                if "wikipedia.org" in url or "facebook.com" in url or "instagram.com" in url:
                    continue
                return url
        except: time.sleep(1.5)
    return None

def get_selenium_content(driver, url):
    try:
        driver.get(url)
        time.sleep(1.5)
        title = driver.title
        body = driver.find_element(By.TAG_NAME, "body").text
        links = []
        for elem in driver.find_elements(By.TAG_NAME, "a"):
            try: links.append((elem.get_attribute("href"), elem.text.lower()))
            except: continue
        return title, body, links
    except: return "", "", []

def find_school_type_in_text(text):
    found = set()
    text_lower = text.lower()
    for st in CONFIG["SCHULTYPEN_LISTE"]:
        if st.lower() in text_lower: found.add(st)
    return list(found)

def validate_page_strict(text):
    """
    Der TÜV-Modus: Prüft, ob es sich wirklich um eine offizielle Schulwebseite handelt.
    Kriterien: Spezielle Phrasen oder Keywords.
    """
    text_sample = text[:10000] # Wir prüfen die ersten 10.000 Zeichen (Performance)
    
    # 1. Hard Keywords (reichen alleine aus)
    triggers = ["leitbild", "konzept", "schulprogramm", "schulprofil", "pädagogik"]
    if any(t in text_sample.lower() for t in triggers):
        return True

    # 2. Satzfragmente (Flexibel mit Regex)
    
    # "Wir sind eine..." (z.B. "Wir sind eine offene Ganztagsschule")
    # \s+ erlaubt beliebige Leerzeichen/Tabs
    if re.search(r"Wir\s+sind\s+eine", text_sample, re.IGNORECASE):
        return True
        
     # "Wir sind eine..." (z.B. "Wir sind eine offene Ganztagsschule")
    # \s+ erlaubt beliebige Leerzeichen/Tabs
    if re.search(r"Unsere\s+ist\s+eine", text_sample, re.IGNORECASE):
        return True
        
     # "Wir sind eine..." (z.B. "Wir sind eine offene Ganztagsschule")
    # \s+ erlaubt beliebige Leerzeichen/Tabs
    if re.search(r"Unsere\s+Schule", text_sample, re.IGNORECASE):
        return True
        
    # "Wir sind eine..." (z.B. "Wir sind eine offene Ganztagsschule")
    # \s+ erlaubt beliebige Leerzeichen/Tabs
    if re.search(r"Wir\s+Schule", text_sample, re.IGNORECASE):
        return True    
    
    # "Wir sind eine..." (z.B. "Wir sind eine offene Ganztagsschule")
    # \s+ erlaubt beliebige Leerzeichen/Tabs
    if re.search(r"Die\s+Schule", text_sample, re.IGNORECASE):
        return True

    # "Die ... ist eine ..." (z.B. "Die Goetheschule ist eine Grundschule")
    # .{0,100}? erlaubt bis zu 100 Zeichen zwischen "Die" und "ist eine" (für Name + Adjektive)
    if re.search(r"Die\s+.{0,100}?\s+ist\s+eine", text_sample, re.IGNORECASE):
        return True
        
    return False

def crawl_and_analyze(driver, school_name, school_ort):
    # 1. URL suchen
    url = search_ddg_robust(f"{school_name} {school_ort} Startseite")
    if not url: return "Nicht gefunden", "", "", ""
    
    print(f"      -> URL: {url}")
    
    # 2. Startseite laden
    title_main, text_main, links_main = get_selenium_content(driver, url)
    if not text_main: return "Nicht erreichbar", "", "", ""
    
    # --- STRICT MODE CHECK ---
    if CONFIG["SENSITIVITY"] == "strict":
        is_valid = validate_page_strict(text_main)
        if not is_valid:
            print("      🛑 Strict Mode: Seite abgelehnt (Kein 'Wir sind eine...' / 'Leitbild' etc.)")
            return url, "", "", "" # Leerer Kontext verhindert KI-Aufruf
        else:
            print("      ✅ Strict Mode: Seite akzeptiert (Offizielle Merkmale gefunden).")
    # -------------------------
    
    # 3. Schultyp auf Startseite suchen
    found_types = find_school_type_in_text(title_main + "\n" + text_main)
    found_kws = set()
    chunks = [f"--- Startseite ---\n{text_main[:2500]}"]
    
    def scan(txt):
        for k in CONFIG["KEYWORD_LISTE"]:
            if re.search(r'\b' + re.escape(k.lower()), txt.lower()): found_kws.add(k)

    scan(text_main)
    
    # 4. Deep Scan (Level 1 & 2)
    domain = urlparse(url).netloc
    
    l1_urls = [h for h, t in links_main if h and domain in urlparse(h).netloc and any(p.lower() in t for p in PRIORITY_LINKS_L1)]
    
    for l1 in list(dict.fromkeys(l1_urls))[:2]:
        print(f"      -> Scan L1: {l1}")
        t1, text1, links1 = get_selenium_content(driver, l1)
        if text1:
            scan(text1)
            chunks.append(f"--- {t1} ---\n{text1[:2500]}")
            if not found_types: found_types.extend(find_school_type_in_text(text1))
            
            l2_urls = [h for h, t in links1 if h and domain in urlparse(h).netloc and any(p.lower() in t for p in PRIORITY_LINKS_L2)]
            for l2 in list(dict.fromkeys(l2_urls))[:2]:
                print(f"         -> Scan L2: {l2}")
                t2, text2, _ = get_selenium_content(driver, l2)
                if text2:
                    scan(text2)
                    chunks.append(f"--- {t2} ---\n{text2[:2500]}")

    schultyp_final = ", ".join(sorted(list(set(found_types))))

    return url, schultyp_final, ", ".join(sorted(list(found_kws))), "\n\n".join(chunks)

# --- KI ---

def ki_analyse(context_text):
    if not context_text or len(context_text) < 50: return "Keine Daten"
    prompt = CONFIG["PROMPT_TEMPLATE"].format(text=context_text[:15000])

    for provider in CONFIG["AI_PRIORITY"]:
        provider = provider.lower()
        if not status_flags.get(provider, False): continue
        try:
            if provider == "openrouter":
                return "[Llama/Claude]: " + clients["openrouter"].chat.completions.create(model=CONFIG["OPENROUTER_MODEL"], messages=[{"role": "user", "content": prompt}]).choices[0].message.content.strip()
            elif provider == "openai":
                return "[OpenAI]: " + clients["openai"].chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]).choices[0].message.content.strip()
            elif provider == "gemini":
                return "[Gemini]: " + clients["gemini"].models.generate_content(model=CONFIG["GEMINI_MODEL"], contents=prompt).text.strip()
            elif provider == "groq":
                return "[Groq]: " + clients["groq"].chat.completions.create(model=CONFIG["GROQ_MODEL"], messages=[{"role": "user", "content": prompt}]).choices[0].message.content.strip()
        except: continue
    return "KI-Fehler"

# --- MAPPING ---

def generate_map(data):
    print("\n🗺️  Erstelle Landkarte (mit Fallback-Suche)...")
    
    # Wichtig: User-Agent muss eindeutig sein
    geolocator = Nominatim(user_agent=f"schul_scanner_{int(time.time())}")
    
    # Karte zentrieren (Deutschland Mitte)
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6) 
    
    # 1. LEGENDE 
    legend_html = '''
     <div style="position: fixed; bottom: 50px; right: 50px; width: 200px; height: 160px; border:2px solid grey; z-index:9999; font-size:14px; background-color:white; opacity:0.9; padding: 10px;">
     <b>Legende</b><br>
     <i style="color:purple" class="fa fa-map-marker"></i> Begabtenförderung<br>
     <i style="color:blue" class="fa fa-map-marker"></i> Gymnasium<br>
     <i style="color:green" class="fa fa-map-marker"></i> Gesamtschule<br>
     <i style="color:orange" class="fa fa-map-marker"></i> Mix (Gym/HR)<br>
     <i style="color:red" class="fa fa-map-marker"></i> Realschule<br>
     <i style="color:gray" class="fa fa-map-marker"></i> Sonstige/Förder<br>
     </div>
     '''
    m.get_root().html.add_child(Element(legend_html))

    count = 0
    missing_count = 0
    
    print("   (Dieser Schritt kann dauern, um die OSM-Server nicht zu überlasten...)")

    for i, entry in enumerate(data):
        name = entry.get('schulname', ''); ort = entry.get('ort', '')
        
        # Ignoriere Einträge komplett ohne Daten/URL
        if not name or not entry.get('webseite') or entry.get('webseite') == "Nicht gefunden": 
            continue
        
        try:
            # --- GEOCODING STRATEGIE ---
            lat, lon = None, None
            is_approx = False
            
            # Versuch 1: Exakte Suche (Schule + Ort)
            # Wir bereinigen den Namen etwas (z.B. alles in Klammern weg)
            clean_name = re.sub(r"\(.*?\)", "", name).strip()
            query = f"{clean_name}, {ort}, Germany"
            loc = geolocator.geocode(query, timeout=10)
            
            if loc:
                lat, lon = loc.latitude, loc.longitude
            else:
                # Versuch 2: NUR ORT (Fallback)
                # Wenn Schule nicht gefunden, nimm die Stadtmitte
                loc_city = geolocator.geocode(f"{ort}, Germany", timeout=10)
                if loc_city:
                    lat = loc_city.latitude
                    lon = loc_city.longitude
                    # Zufälliger "Jitter" (Verschiebung), damit Marker nicht stapeln
                    # ca. 500m - 1km Umkreis
                    lat += random.uniform(-0.015, 0.015) 
                    lon += random.uniform(-0.015, 0.015)
                    is_approx = True
            
            # Wenn immer noch keine Koordinaten -> Überspringen
            if not lat or not lon:
                print(f"   ❌ Ort nicht gefunden: {ort}")
                missing_count += 1
                continue

            # --- DATEN VORBEREITEN ---
            schultyp = str(entry.get('schultyp', 'Unbekannt'))
            ki = str(entry.get('ki_zusammenfassung', 'Keine Analyse'))
            kw = str(entry.get('keywords', '-'))
            
            # --- FARB-LOGIK ---
            st = schultyp.lower()
            full_text_scan = (ki + " " + kw).lower()
            
            begabung_keywords = ["hochbegabt", "hochbegabte", "begabte", "akzeleration"]
            
            # Zuordnung 
            if any(word in full_text_scan for word in begabung_keywords):
                color = "purple"
            elif "gesamtschule" in st:
                color = "green"
            elif "gymnasium" in st and ("haupt" in st or "real" in st or "verbund" in st):
                color = "orange" 
            elif "gymnasium" in st:
                color = "blue"
            elif "realschule" in st:
                color = "red"
            else:
                color = "gray"
            
            # --- POPUP HTML ---
            # Hinweis hinzufügen, wenn Position nur geschätzt ist
            pos_hint = "<br><i style='color:red; font-size:10px'>(Position geschätzt/Stadtmitte)</i>" if is_approx else ""
            
            html = f"""
            <div style="font-family: Arial; width: 300px;">
                <h4>{name}</h4>
                <p style="color:grey; font-size:11px">{schultyp} {pos_hint}</p>
                <hr>
                <p><b>KW:</b> {kw}</p>
                <div style="max-height:150px;overflow-y:auto;background:#f9f9f9;padding:5px;font-size:11px;border:1px solid #eee;">
                    {ki}
                </div>
                <br>
                <a href="{entry.get('webseite','#')}" target="_blank" style="background-color:#007bff;color:white;padding:3px 8px;text-decoration:none;border-radius:3px;font-size:11px">Webseite</a>
            </div>
            """
            
            # Marker setzen
            icon_type = "info-sign" if not is_approx else "question-sign" # Anderes Icon für geschätzte Position
            folium.Marker(
                [lat, lon], 
                popup=folium.Popup(html, max_width=350), 
                icon=folium.Icon(color=color, icon=icon_type)
            ).add_to(m)
            
            count += 1
            
            # Fortschritt alle 50 Schulen anzeigen
            if count % 50 == 0:
                print(f"   ... {count} Schulen platziert ...")
                
            # WICHTIG: Höflichkeitspause für OSM (sonst blockieren sie dich)
            time.sleep(1.2) 
            
        except Exception as e:
            # Fehler ausgeben, statt pass
            print(f"   ⚠️ Fehler bei {name}: {e}")
            pass

    m.save(CONFIG["MAP_FILE"])
    print(f"\n✅ Karte gespeichert: '{CONFIG['MAP_FILE']}'")
    print(f"   📊 Ergebnis: {count} platziert, {missing_count} ohne Ort.")

# --- MENU HELPERS ---

def manage_list_setting(key_name, display_name):
    while True:
        current_list = CONFIG[key_name]
        print(f"\n⚙️ {display_name} ({len(current_list)} Einträge)")
        print(f"   Auszug: {', '.join(current_list[:5])}...")
        print("   [+] Hinzufügen | [-] Löschen | [*] Neu schreiben | [B] Zurück")
        opt = input("   👉 Aktion: ").strip().lower()
        if opt == "b": break
        elif opt == "+":
            add = input("   Neuer Eintrag (Komma für mehrere): ")
            new_items = [x.strip() for x in add.split(",") if x.strip()]
            CONFIG[key_name] = list(set(current_list + new_items))
        elif opt == "-":
            for idx, val in enumerate(current_list): print(f"   {idx+1}: {val}")
            rem = input("   Nummer zum Löschen: ").strip()
            if rem.isdigit():
                idx = int(rem) - 1
                if 0 <= idx < len(current_list): CONFIG[key_name].pop(idx)
        elif opt == "*":
            if input("   ⚠️ Sicher? (j/n): ").lower() == "j":
                new_full = input("   Neue Liste (kommagetrennt): ")
                CONFIG[key_name] = [x.strip() for x in new_full.split(",") if x.strip()]
        save_config_to_file(CONFIG)

def menu_settings():
    global CONFIG
    while True:
        print("\n⚙️ EINSTELLUNGEN")
        print(f"1: Input Datei    [{CONFIG['INPUT_FILE']}]")
        print(f"2: Schultypen     ({len(CONFIG['SCHULTYPEN_LISTE'])})")
        print(f"3: Keywords       ({len(CONFIG['KEYWORD_LISTE'])})")
        print(f"4: KI-Priorität   {CONFIG['AI_PRIORITY']}")
        print(f"5: Prompt Text")
        print(f"6: Sensibilität   [{CONFIG['SENSITIVITY'].upper()}]")
        print("7: Zurück")
        
        c = input("👉 Wahl: ").strip()
        if c == "1": CONFIG["INPUT_FILE"] = input("Datei: ")
        elif c == "2": manage_list_setting("SCHULTYPEN_LISTE", "Schultypen")
        elif c == "3": manage_list_setting("KEYWORD_LISTE", "Keywords")
        elif c == "4": 
            inp = input("Neue Reihenfolge: ")
            if inp: CONFIG["AI_PRIORITY"] = [x.strip().lower() for x in inp.split(",")]
        elif c == "5":
            print(f"\nPrompt:\n{CONFIG['PROMPT_TEMPLATE']}")
            new_p = input("Neuer Text (Enter = behalten): ")
            if len(new_p) > 10: CONFIG["PROMPT_TEMPLATE"] = new_p
        elif c == "6":
            print("\nModus wählen:")
            print("  normal = Akzeptiert alle gefundenen Seiten")
            print("  strict = Prüft auf 'Wir sind eine...' / 'Leitbild' etc.")
            new_s = input(f"  Aktuell: {CONFIG['SENSITIVITY']} -> Neu (normal/strict): ").strip().lower()
            if new_s in ["normal", "strict"]: CONFIG["SENSITIVITY"] = new_s
        elif c == "7": save_config_to_file(CONFIG); break
        save_config_to_file(CONFIG)

# --- RUNNERS ---

def run_auto_scan(data):
    print(f"\n🤖 AUTO-SCAN V13.1 (Safe Mode) | Sensibilität: {CONFIG['SENSITIVITY'].upper()}")
    print("ℹ️ Drücke STRG+C, um zu pausieren.")
    
    driver = get_driver()
    unsaved_changes = False # Merken, ob wir was zu speichern haben
    
    try:
        for i, entry in enumerate(data):
            # Überspringe bereits bearbeitete Einträge
            if entry.get('ki_zusammenfassung') not in ["", "Keine Daten", None] and entry.get('schultyp') != "": 
                continue 
            
            print(f"\n[{i+1}/{len(data)}] {entry['schulname']}...")
            
            url, typ, kw, ctx = crawl_and_analyze(driver, entry['schulname'], entry['ort'])
            
            entry['webseite'] = url; entry['schultyp'] = typ; entry['keywords'] = kw
            unsaved_changes = True

            print(f"      -> Typ: {typ if typ else '-'}")
            print(f"      -> KW:  {kw if kw else '-'}")

            if (typ or kw) and ctx:
                if CONFIG["SENSITIVITY"] == "strict" and not ctx:
                    entry['ki_zusammenfassung'] = "Zu wenige Infos (Strict Filter)"
                else:
                    print("      🧠 Kontext gefunden -> KI...")
                    entry['ki_zusammenfassung'] = ki_analyse(ctx)
            else:
                entry['ki_zusammenfassung'] = "Zu wenige Infos (Strict Filter)" if CONFIG["SENSITIVITY"] == "strict" else "Keine relevanten Daten gefunden"
            
            # SICHERHEITS-UPDATE: Nur alle 10 Schulen speichern (oder bei der allerletzten)
            if (i + 1) % 10 == 0:
                print("      💾 Zwischenspeicherung (Backup & Save)...")
                save_data(data)
                unsaved_changes = False
            
    except KeyboardInterrupt:
        print("\n🛑 PAUSE durch Benutzer! Speichere Fortschritt...")
        save_data(data)
        unsaved_changes = False
    finally:
        if unsaved_changes: # Falls beim Absturz/Ende noch was offen war
            print("💾 Letzte Änderungen werden gespeichert...")
            save_data(data)
        if driver: driver.quit()

def run_manual_review(data):
    # Lade aktuellen Startpunkt aus der Config
    start_idx = CONFIG.get("MANUAL_RESUME_IDX", 0)
    
    # Falls der Index ungültig ist (z.B. Liste wurde kleiner), auf 0 setzen
    if start_idx >= len(data): start_idx = 0

    print(f"\n🕵️ MANUELLE KONTROLLE (Lückenfüller)")
    print(f"ℹ️  Start bei Zeile {start_idx + 1} von {len(data)}.")
    if start_idx > 0:
        print(f"   (Nutze Option [7], um wieder ganz von vorne zu beginnen)")
    
    driver = None
    found_count = 0
    
    try:
        for i in range(start_idx, len(data)):
            entry = data[i]
            
            # Index für den nächsten Start merken & speichern
            CONFIG["MANUAL_RESUME_IDX"] = i
            # Wir speichern die Config nur alle paar Einträge oder beim Skip/Edit, 
            # um die Festplatte zu schonen.
            
            # --- TRIGGER LOGIK ---
            ki_text = str(entry.get('ki_zusammenfassung', ''))
            typ_text = str(entry.get('schultyp', ''))
            keyw_text = str(entry.get('keywords', ''))
            is_error_ki = any(m in ki_text for m in CONFIG["ERROR_MARKERS"])
            is_empty_ki = len(ki_text) < 10
            is_empty_typ = len(typ_text) < 3
            
            if not is_error_ki and not is_empty_ki and not is_empty_typ:
                continue

            found_count += 1
            
            
            # --- 3. ANZEIGE ---
            print(f"\n[{i+1}/{len(data)}] 🏫 {entry['schulname']} ({entry['ort']})")
            print(f"   URL:  {entry.get('webseite', 'N/A')}")
            print(f"   Typ:  {typ_text if len(typ_text) > 2 else '❌ FEHLT'}")
            print(f"   Keywords:  {keyw_text if len(keyw_text) > 2 else '❌ FEHLT'}")
            
            # Statusanzeige für KI-Text
            if any(m in ki_text for m in CONFIG["ERROR_MARKERS"]):
                print(f"   KI:   ⚠️ {ki_text}")
            elif len(ki_text) < 10:
                print("   KI:   ❌ FEHLT / LEER")
            else:
                print(f"   KI:   {ki_text[:50]}...")
            
            #Browser zur Kontrolle öffnen    
            open_browser_search(f"{entry['schulname']} {entry['ort']} Startseite")
            
            # --- 4. INTERAKTION ---
            while True:
                print("\n   [1] Auto-Scan (Komplett neu suchen)")
                print("   [2] KI-Check wiederholen (Bypass Strict Filter)")
                print("   [3] URL Paste (Link manuell setzen)")
                print("   [4] Typ manuell nachtragen")
                print("   [5] Keywords manuell nachtragen")
                print("   [6] Skip (Diesen Eintrag überspringen)")
                print("   [7] Reset des Indexes. Suche beginnt wieder oben in der Liste)")
                print("   [8] Exit (Zurück zum Menü)")
                
                c = input("   👉 Wahl: ").strip()
                
                if c == "1":
                    if not driver: driver = get_driver()
                    url, typ, kw, ctx = crawl_and_analyze(driver, entry['schulname'], entry['ort'])
                    entry['webseite'] = url; entry['schultyp'] = typ; entry['keywords'] = kw
                    entry['ki_zusammenfassung'] = ki_analyse(ctx) if ctx else "Nicht gefunden"
                    save_data(data); break 

                elif c == "2":
                    curr = entry.get('webseite', '')
                    u = input("   🔗 URL (Enter = behalten): ").strip()
                    target_url = u if u.startswith("http") else curr
                    if target_url and target_url != "Nicht gefunden":
                        if not driver: driver = get_driver()
                        t, text, _ = get_selenium_content(driver, target_url)
                        entry['ki_zusammenfassung'] = ki_analyse(text[:15000]) if text else "Inhalt leer"
                        save_data(data)
                    break

                elif c == "3": # URL Paste (Via Deep-Scan)
                    u = input("   🔗 URL eingeben: ").strip()
                    if u.startswith("http"):
                        if not driver: driver = get_driver()
                        
                        print(f"   🤖 Starte Deep-Scan für: {u}")
                        # Wir übergeben die URL direkt als erstes Argument.
                        # Die Funktion erkennt "http" und überspringt die Google-Suche,
                        # führt aber das volle Programm (Validierung + Unterseiten-Scan) durch.
                        url, typ, kw, ctx = crawl_and_analyze(driver, u, entry['ort'])
                        
                        # Ergebnisse übernehmen
                        entry['webseite'] = url
                        
                        # Nur überschreiben, wenn auch was gefunden wurde, sonst behalten was da war
                        if typ: entry['schultyp'] = typ
                        if kw: entry['keywords'] = kw
                        
                        if ctx:
                            print("   🧠 Kontext gefunden (Startseite + Unterseiten). Sende an KI...")
                            entry['ki_zusammenfassung'] = ki_analyse(ctx)
                            print("   ✅ Analyse erfolgreich.")
                        else:
                            print("   ⚠️ URL geladen, aber 'crawl_and_analyze' hat keine Inhalte validiert.")
                            print("      (Möglicherweise hat der Strict-Filter den Ort nicht im Impressum gefunden)")
                            entry['ki_zusammenfassung'] = "Inhalt abgelehnt (Strict Filter)"
                        
                        save_data(data)
                    break
                elif c == "4":
                    new_typ = input(f"   ✍️ Typ ({entry.get('schultyp')}): ").strip()
                    if new_typ: entry['schultyp'] = new_typ
                    
                    save_data(data); break
                
                elif c == "5":
                    new_kw = input(f"Keywords ({entry.get('keywords')}): ").strip()
                    if new_kw: entry['keywords'] = new_kw
                    
                    save_data(data); break

                elif c == "6": # SKIP
                    print("   ⏭️ Merke Position und gehe weiter...")
                    save_config_to_file(CONFIG) # Position sichern
                    break
                
                elif c == "8": # EXIT
                    save_config_to_file(CONFIG)
                    return 

                elif c == "7": # RESET
                    CONFIG["MANUAL_RESUME_IDX"] = 0
                    save_config_to_file(CONFIG)
                    print("   ♻️ Index zurückgesetzt. Beim nächsten Start geht es bei 1 los.")

        # Wenn wir am Ende der Liste angekommen sind
        print("\n✅ Ende der Liste erreicht.")
        CONFIG["MANUAL_RESUME_IDX"] = 0
        save_config_to_file(CONFIG)

    except KeyboardInterrupt:
        save_config_to_file(CONFIG)
        print("\n🛑 Pause. Position gespeichert.")
    finally:
        if driver: driver.quit()


def run_single_edit(data):
    print("\n✏️ EINZELNE ZEILE BEARBEITEN")
    row = input("👉 Zeilennummer (aus Excel/Liste): ").strip()
    if not row.isdigit(): return
    idx = int(row) - 2 # Header ist Zeile 1, Index start bei 0 -> -2 ist meist korrekt bei Excel
    
    if 0 <= idx < len(data):
        e = data[idx]
        print(f"\nGewählt: {e['schulname']} ({e['ort']})")
        print(f"URL: {e.get('webseite')}")
        print(f"Typ: {e.get('schultyp')}")
        print(f"Keywords:{e.get('keywords')}")
        
        
        # Browser öffnen
        open_browser_search(f"{e['schulname']} {e['ort']}")

        print("\n[1] Auto-Scan")
        print("[2] URL manuell eingeben")
        print("[3] Daten manuell editieren (Typ/Keywords)")
        print("[4] Zurück")
        
        c = input("👉 Wahl: ").strip()
        driver = None
        
        try:
            if c == "1" or c == "2":
                driver = get_driver() # Brauchen wir nur hier

            if c == "1":
                url, typ, kw, ctx = crawl_and_analyze(driver, e['schulname'], e['ort'])
                e['webseite'] = url; e['schultyp'] = typ; e['keywords'] = kw
                if ctx: e['ki_zusammenfassung'] = ki_analyse(ctx)
                
            elif c == "2":
                u = input("URL: ").strip()
                if u.startswith("http"):
                    e['webseite'] = u
                    t, text, _ = get_selenium_content(driver, u)
                    e['schultyp'] = ", ".join(find_school_type_in_text(text))
                    if text: e['ki_zusammenfassung'] = ki_analyse(text[:15000])

            elif c == "3":
                new_typ = input(f"Schultyp ({e.get('schultyp')}): ").strip()
                if new_typ: e['schultyp'] = new_typ
                
                # Keywords anpassen
                new_kw = input(f"Keywords ({e.get('keywords')}): ").strip()
                if new_kw: e['keywords'] = new_kw
                
                print("💾 Daten aktualisiert.")

            save_data(data)
            
        finally:
            if driver: driver.quit()
    else:
        print("❌ Ungültige Zeilennummer.")

def main():
    print_system_status()
    while True:
        data = load_data()
        if not data and os.path.exists(CONFIG["INPUT_FILE"]): data = sync_with_source([])
        if data:
            for d in data:
                if 'schultyp' not in d: d['schultyp'] = ""
                if 'keywords' not in d: d['keywords'] = ""
            save_data(data)

        done = sum(1 for x in data if str(x.get('ki_zusammenfassung')) not in ["Keine Daten", "Keine relevanten Daten gefunden", "", "Zu wenige Infos (Strict Filter)"])
        print(f"\n--- SCANNER V13.0 (National/Strict) | Fertig: {done}/{len(data)} ---")
        print("1️⃣ Auto-Scan")
        print("2️⃣ Manuelle Kontrolle")
        print("3️⃣ Einzelne Zeile")
        print("4️⃣ Karte erstellen")
        print("5️⃣ Sync mit Input-Datei")
        print("6️⃣ Einstellungen")
        print("7️⃣ Beenden")
        
        try:
            c = input("\n👉 Wahl: ").strip()
            if c == "1": run_auto_scan(data)
            elif c == "2": run_manual_review(data)
            elif c == "3": run_single_edit(data)
            elif c == "4": generate_map(data)
            elif c == "5": data = sync_with_source(data)
            elif c == "6": menu_settings()
            elif c == "7": break
        except KeyboardInterrupt:
            print("\n(Im Hauptmenü: '7' zum Beenden)")

if __name__ == "__main__":
    main()
