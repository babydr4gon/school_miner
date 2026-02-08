"""
SCHUL-SCANNER (Community Edition)
Ein Tool zur automatisierten Analyse von Schul-Webseiten mittels KI.
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

# Externe Bibliotheken
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
DEFAULT_HARD_KEYWORDS = ["MINT", "Sport", "Musik", "Gesellschaftswissenschaften", "Sprachen", "bilingual", "Lernlabor", "Lernloft", "Lernatelier", "sinnstiftend", "sinnstiftende Zusammenhänge", "themenorientiert", "themenorientiertes Lernen", "Makerspace", "Maker", "Multikultur", "multikulturell", "multikulturelles", "Charakter", "charakterliche Entwicklung", "Montessoripädagogik", "Montessori", "Walldorf", "Walldorfpädagogik", "Jenaplan", "jahrgangsübergreifend", "altersübergreifend", "Altersgruppen", "Gruppenarbeit", "Bezugsgruppe"]

PRIORITY_LINKS_L1 = ["Schulprofil", "Schulprogramm", "Leitbild", "Über uns", "Unsere Schule", "Wir über uns"]
PRIORITY_LINKS_L2 = ["Leitbild", "Konzept", "Pädagogik", "Schwerpunkte", "Ganztag", "Angebote", "AGs", "Förderung"]

DEFAULT_CONFIG = {
    "INPUT_FILE": "schulen.xlsx",
    "SHEET_NAME": "Schulverzeichnis",
    "OUTPUT_FILE": "schulen_ergebnisse.xlsx",
    "MAP_FILE": "schulen_karte.html",
    "COLUMN_NAME_IDX": 0,
    "COLUMN_ORT_IDX": 2,
    "GEMINI_MODEL": "gemini-2.0-flash-exp", 
    "OPENROUTER_MODEL": "meta-llama/llama-3.3-70b-instruct", 
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "WAIT_TIME": 2.0, 
    "SCHULTYPEN_LISTE": DEFAULT_SCHULTYPEN,
    "KEYWORD_LISTE": DEFAULT_HARD_KEYWORDS,
    "AI_PRIORITY": ["openrouter", "gemini", "openai", "groq"],
    "PROMPT_TEMPLATE": (
        "Du bist ein Schul-Analyst. Ich gebe dir Textauszüge von der Webseite.\n"
        "Fasse das pädagogische Konzept zusammen.\n"
        "Ignoriere Navigationstext.\n"
        "Maximal 3 Sätze.\n\n"
        "Text:\n{text}"
    ),
    "ERROR_MARKERS": ["Nicht gefunden", "Keine Daten", "KI-Fehler", "QUOTA", "Error"]
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
    except: pass

CONFIG = load_config()

clients = {}
status_flags = {"gemini": bool(os.getenv("GEMINI_API_KEY")), "openai": bool(os.getenv("OPENAI_API_KEY")), "openrouter": bool(os.getenv("OPENROUTER_API_KEY")), "groq": bool(os.getenv("GROQ_API_KEY"))}

if status_flags["gemini"]: clients["gemini"] = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
if status_flags["openai"]: clients["openai"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if status_flags["groq"]: clients["groq"] = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
if status_flags["openrouter"]:
    clients["openrouter"] = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={"HTTP-Referer": "https://github.com/schul-scanner", "X-Title": "Schul-Scanner"})

# --- SELENIUM DRIVER ---

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(25)
    return driver

# --- DATA ---

def load_data():
    if os.path.exists(CONFIG["OUTPUT_FILE"]):
        try: return pd.read_excel(CONFIG["OUTPUT_FILE"]).to_dict('records')
        except: pass
    return []

def save_data(data):
    try: pd.DataFrame(data).to_excel(CONFIG["OUTPUT_FILE"], index=False)
    except Exception as e: print(f"❌ Fehler beim Speichern: {e}")

def sync_with_source(current_data):
    print("\n🔄 Sync mit Ursprungsdatei...")
    if not os.path.exists(CONFIG["INPUT_FILE"]): return current_data
    try:
        df_raw = pd.read_excel(CONFIG["INPUT_FILE"], sheet_name=CONFIG["SHEET_NAME"], header=None)
        existing = {str(d['schulname']).strip() for d in current_data}
        added = 0
        for _, row in df_raw.iterrows():
            if len(row) <= max(CONFIG["COLUMN_NAME_IDX"], CONFIG["COLUMN_ORT_IDX"]): continue
            n = str(row[CONFIG["COLUMN_NAME_IDX"]]).strip()
            if len(n) > 5 and "schule" in n.lower() and "=" not in n and n not in existing:
                current_data.append({
                    'schulname': n, 'ort': str(row[CONFIG["COLUMN_ORT_IDX"]]).strip(),
                    'schultyp': "", 'keywords': "", 
                    'webseite': "Nicht gefunden", 'ki_zusammenfassung': "Keine Daten"
                })
                existing.add(n); added += 1
        if added: save_data(current_data); print(f"✅ {added} neue Schulen.")
    except: pass
    return current_data

# --- SEARCH ---

def search_ddg_robust(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region='de-de', max_results=3, backend="api"))
            if results: return results[0]['href']
        except: time.sleep(1.5)
    return None

# --- CRAWLER LOGIC ---

def get_selenium_content(driver, url):
    """Lädt Seite und gibt Titel, Text und Links zurück"""
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

def check_hessen_db_fallback(driver, name, ort):
    print("      ⚠️ Homepage gab keinen Schultyp -> Versuche Hessen-DB Fallback...")
    query = f"site:schul-db.bildung.hessen.de {name} {ort}"
    url = search_ddg_robust(query)
    if url:
        _, text, _ = get_selenium_content(driver, url)
        return ", ".join(sorted(find_school_type_in_text(text)))
    return ""

def crawl_and_analyze(driver, school_name, school_ort):
    url = search_ddg_robust(f"{school_name} {school_ort} Startseite")
    if not url: return "Nicht gefunden", "", "", ""
    
    print(f"      -> URL: {url}")
    
    title_main, text_main, links_main = get_selenium_content(driver, url)
    if not text_main: return "Nicht erreichbar", "", "", ""
    
    # Prio 1: Startseite Schultyp
    found_types = find_school_type_in_text(title_main + "\n" + text_main)
    found_kws = set()
    chunks = [f"--- Startseite ---\n{text_main[:2500]}"]
    
    def scan(txt):
        for k in CONFIG["KEYWORD_LISTE"]:
            if re.search(r'\b' + re.escape(k.lower()), txt.lower()): found_kws.add(k)

    scan(text_main)
    
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
    if not schultyp_final:
        schultyp_final = check_hessen_db_fallback(driver, school_name, school_ort)

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
    print("\n🗺️  Erstelle Landkarte...")
    geolocator = Nominatim(user_agent="schul_scanner_v11_1")
    m = folium.Map(location=[50.6, 9.0], zoom_start=9)
    
    legend_html = '''
     <div style="position: fixed; bottom: 50px; right: 50px; width: 180px; height: 110px; border:2px solid grey; z-index:9999; font-size:14px; background-color:white; opacity:0.9; padding: 10px;">
     <b>Legende</b><br><i style="color:green" class="fa fa-map-marker"></i> Grundschule<br><i style="color:orange" class="fa fa-map-marker"></i> Verbund/Hybrid<br><i style="color:blue" class="fa fa-map-marker"></i> Weiterführend<br></div>
     '''
    m.get_root().html.add_child(Element(legend_html))

    count = 0
    for entry in data:
        name = entry.get('schulname', ''); ort = entry.get('ort', '')
        if not name or "Keine Daten" in str(entry.get('ki_zusammenfassung')): continue
        try:
            loc = geolocator.geocode(f"{name}, {ort}, Germany", timeout=5)
            if loc:
                schultyp = entry.get('schultyp', 'Unbekannt')
                ki = entry.get('ki_zusammenfassung', '')
                kw = entry.get('keywords', '-')
                is_grund = "Grundschule" in schultyp
                has_others = any(x in schultyp for x in ["Haupt", "Real", "Gym", "Förder", "Verbund", "Mittel"])
                color = "orange" if (is_grund and has_others) else ("green" if is_grund else "blue")
                html = f"""<div style="font-family: Arial; width: 300px;"><h4>{name}</h4><p style="color:grey">{schultyp}</p><hr><p><b>KW:</b> {kw}</p><div style="max-height:150px;overflow-y:auto;background:#f9f9f9;padding:5px;font-size:11px">{ki}</div><br><a href="{entry.get('webseite','#')}" target="_blank">Webseite</a></div>"""
                folium.Marker([loc.latitude, loc.longitude], popup=folium.Popup(html, max_width=350), icon=folium.Icon(color=color, icon="info-sign")).add_to(m)
                count += 1
                time.sleep(1.0)
        except: pass
    m.save(CONFIG["MAP_FILE"])
    print(f"✅ Karte gespeichert ({count} Schulen)")

# --- MENU HELPERS ---

def manage_list_setting(key_name, display_name):
    """Hilfsfunktion für Listen-Management (Keywords, Schultypen)"""
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
            CONFIG[key_name] = list(set(current_list + new_items)) # Duplikate vermeiden
            print(f"   ✅ {len(new_items)} hinzugefügt.")
            
        elif opt == "-":
            print("\n   --- Liste ---")
            for idx, val in enumerate(current_list):
                print(f"   {idx+1}: {val}")
            rem = input("   Nummer zum Löschen: ").strip()
            if rem.isdigit():
                idx = int(rem) - 1
                if 0 <= idx < len(current_list):
                    removed = current_list.pop(idx)
                    CONFIG[key_name] = current_list
                    print(f"   🗑️ '{removed}' gelöscht.")
                    
        elif opt == "*":
            conf = input("   ⚠️ Sicher? Ganze Liste überschreiben? (j/n): ")
            if conf.lower() == "j":
                new_full = input("   Neue Liste (kommagetrennt): ")
                CONFIG[key_name] = [x.strip() for x in new_full.split(",") if x.strip()]
                print("   ✅ Liste neu erstellt.")
        
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
        print("6: Zurück zum Hauptmenü")
        
        c = input("👉 Wahl: ").strip()
        
        if c == "1": CONFIG["INPUT_FILE"] = input("Datei: ")
        elif c == "2": manage_list_setting("SCHULTYPEN_LISTE", "Schultypen")
        elif c == "3": manage_list_setting("KEYWORD_LISTE", "Keywords")
        elif c == "4": 
            inp = input("Neue Reihenfolge (kommagetrennt, z.B. openai,gemini): ")
            if inp: CONFIG["AI_PRIORITY"] = [x.strip().lower() for x in inp.split(",")]
        elif c == "5":
            print(f"\nAktueller Prompt:\n{CONFIG['PROMPT_TEMPLATE']}")
            new_p = input("Neuer Text (Enter = behalten): ")
            if len(new_p) > 10: CONFIG["PROMPT_TEMPLATE"] = new_p
        elif c == "6": 
            save_config_to_file(CONFIG)
            break
        
        save_config_to_file(CONFIG)

# --- RUNNERS ---

def run_auto_scan(data):
    print(f"\n🤖 AUTO-SCAN V11.1 | KI: {', '.join(CONFIG['AI_PRIORITY'])}")
    print("ℹ️ Drücke STRG+C, um zu pausieren und ins Menü zurückzukehren.")
    
    driver = get_driver()
    try:
        for i, entry in enumerate(data):
            # Check, ob wir abbrechen sollen (falls STRG+C genau hier gedrückt wird)
            # Python wirft KeyboardInterrupt, das fangen wir unten ab.
            
            if entry.get('ki_zusammenfassung') not in ["", "Keine Daten", None] and entry.get('schultyp') != "": continue 
            print(f"\n[{i+1}/{len(data)}] {entry['schulname']}...")
            
            url, typ, kw, ctx = crawl_and_analyze(driver, entry['schulname'], entry['ort'])
            
            entry['webseite'] = url
            entry['schultyp'] = typ
            entry['keywords'] = kw
            
            print(f"      -> Typ: {typ if typ else '-'}")
            print(f"      -> KW:  {kw if kw else '-'}")

            if (typ or kw) and ctx:
                print("      🧠 Kontext gefunden -> KI...")
                entry['ki_zusammenfassung'] = ki_analyse(ctx)
            else:
                entry['ki_zusammenfassung'] = "Keine relevanten Daten gefunden"
            
            save_data(data)
            
    except KeyboardInterrupt:
        print("\n\n🛑 PAUSE! Scan wird unterbrochen...")
        print("   Speichere Daten...")
        save_data(data)
        time.sleep(1)
        print("   Zurück zum Menü.")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        save_data(data)
    finally:
        driver.quit()

def run_manual_review(data):
    print("\n🕵️ MANUELLE KONTROLLE")
    driver = None
    try:
        for entry in data:
            if any(m in str(entry.get('ki_zusammenfassung', '')) for m in CONFIG["ERROR_MARKERS"]):
                print(f"\n🏫 {entry['schulname']} ({entry.get('ki_zusammenfassung')})")
                webbrowser.open(f"https://duckduckgo.com/?q={entry['schulname']} {entry['ort']}")
                c = input("1=Neue URL | 2=Skip | 3=Exit: ").strip()
                if c == "1":
                    if not driver: driver = get_driver()
                    u = input("URL: ").strip()
                    if u.startswith("http"):
                        entry['webseite'] = u
                        t, text, links = get_selenium_content(driver, u)
                        entry['schultyp'] = ", ".join(find_school_type_in_text(text))
                        entry['ki_zusammenfassung'] = ki_analyse(text[:15000])
                    save_data(data)
                elif c == "3": break
    except KeyboardInterrupt:
        print("\n🛑 Abbruch durch User.")
    finally:
        if driver: driver.quit()

def run_single_edit(data):
    print("\n✏️ EINZELNE ZEILE")
    row = input("👉 Zeilennummer: ").strip()
    if not row.isdigit(): return
    idx = int(row) - 2
    if 0 <= idx < len(data):
        e = data[idx]
        print(f"Gewählt: {e['schulname']}")
        print("1. Auto-Scan")
        print("2. URL manuell")
        c = input("👉 Wahl: ").strip()
        driver = get_driver()
        try:
            if c == "1":
                url, typ, kw, ctx = crawl_and_analyze(driver, e['schulname'], e['ort'])
                e['webseite'] = url; e['schultyp'] = typ; e['keywords'] = kw
                if ctx: e['ki_zusammenfassung'] = ki_analyse(ctx)
            elif c == "2":
                u = input("URL: ").strip()
                if u.startswith("http"):
                    e['webseite'] = u
                    t, text, _ = get_selenium_content(driver, u)
                    if text: e['ki_zusammenfassung'] = ki_analyse(text[:15000])
            save_data(data)
        finally:
            driver.quit()

def main():
    while True:
        data = load_data()
        if not data and os.path.exists(CONFIG["INPUT_FILE"]): data = sync_with_source([])
        if data:
            for d in data:
                if 'schultyp' not in d: d['schultyp'] = ""
                if 'keywords' not in d: d['keywords'] = ""
            save_data(data)

        done = sum(1 for x in data if str(x.get('ki_zusammenfassung')) not in ["Keine Daten", "Keine relevanten Daten gefunden", ""])
        print(f"\n--- SCANNER V11.1 (Komfort-Edition) | Fertig: {done}/{len(data)} ---")
        print("1️⃣ Auto-Scan | 2️⃣ Manuelle Kontrolle | 3️⃣ Einzelne Zeile")
        print("4️⃣ Karte | 5️⃣ Sync | 6️⃣ Settings | 7️⃣ Exit")
        
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
            print("\n(Im Hauptmenü: Zum Beenden '7' wählen)")
            continue

if __name__ == "__main__":
    main()
