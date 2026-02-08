<h1 align="center">
  <img src="src/contents/icons/com.github.wwmm.easyeffects.svg" alt="Easy Effects icon" width="150" height="150"/>
  <br>
  School_Miner (Eltern-Edition)
</h1>

<p align="center">
  <a href="https://github.com/sponsors/wwmm">
    <img alt="GitHub Sponsors donation button" src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&link=https://github.com/sponsors/wwmm">
  </a>
  <a href="https://liberapay.com/Gernot_Sell/donate">
    <img alt="Liberapay donation button" src="https://img.shields.io/badge/liberapay-donate-green">
  </a>
  <a href="https://www.patreon.com/gernotsell?fan_landing=true">
    <img alt="Patreon donation button" src="https://img.shields.io/badge/patreon-donate-green.svg">
  </a>
</p>

Dieses Tool soll Eltern helfen, Schulwebseiten automatisch nach Keywords (MINT, Ganztag, etc.) zu durchsuchen und die pädagogischen Konzepte mittels KI zusammenzufassen.

<h2>Installation:</h2>

1. Repository klonen.

2. pip install -r requirements.txt ausführen.

3. .env Datei erstellen und API-Keys eintragen (z.B. OPENROUTER_API_KEY=...).

4. schulen.xlsx mit den Spalten Name und Ort anlegen.

5. python school_miner.py starten.

<h2>Hinweise zur Nutzung</h2>

Das Skript erstellt automatisch eine config.json-Datei. Dort wird unter anderem eine Keywordliste gespeichert. Wie erfolgreich das Suche nach der richtigen Schule ist, hängt nicht zuletzt von der Qualität dieser Keywords ab.

## License

School_miner ist unter der GNU General Public License, Version 3 or folgende, lizensiert.
Hier die [Lizenz](https://github.com/wiemachendiedasnur/school_miner/main/LICENSE).
