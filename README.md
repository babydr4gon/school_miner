<h1 align="center">
  <img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/dragon_mine.png" alt="School_miner icon" width="250" height="250"/>
  <br>
  School_Miner
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

4. Eine Datei „schulen.xlsx „mit den Spalten Name und Ort als Grundlage für die Suche anlegen.

5. python school_miner.py starten.

<h2>Features</h2>

<h1>Allgemeines</h1>

Zunächst sollte man eine Liste der Schulen erstellen, über die man Informationen sammeln möchte. In allen Bundesländern gibt es entsprechende Listen, die von den Kultusministerien oder von den statistischen Landesämtern gepflegt werden. Das Skript erwartet standardmäßig eine Datei mit dem Namen „schulen.xlsx“, die im gleichen Verzeichnis liegt. Dies kann man aber unter Einstellungen auch individuell verändern.

Anschließend sucht das Skript für jede der Schulen in dieser Liste nach der offiziellen Webseite. Dort sucht es nach dem Schultyp und nach bestimmten Keywords. Sobald es diese Dinge gefunden hat, versucht eine KI die gefundenen Informationen zum Konzept oder zu Besonderheiten der Schule in wenigen Sätzen zusammenzufassen. 

Das Skript erstellt eine Tabelle mit den Ergebnissen der Suche. Darin sind der Name der Schule, die gefundenen Keywords, die verwendete Webseite und die Zusammenfassung der KI gespeichert. Es gibt die Möglichkeit, Fehler, die bei der automatisierten Suche passieren, individuell zu korrigieren. 

Abschließend kann man sich eine Landkarte erstellen lassen. Auf dieser Landkarte sind die Schulen mit Markern eingezeichnet. Klickt man auf einen der Marker, erscheint eine kurze Übersicht: der Name der Schule, die gefundenen Keywords und gegebenenfalls eine KI-Zusammenfassung. 

<h1>Start des Skripts</h1>

Nach dem Start mit python school_miner.py erscheint ein Auswahlmenü mit insgesamt sieben Möglichkeiten: 
1. AutoScan: die vorbereitete Liste der Schulen, über die man mehr wissen möchte, wird automatisch, Zeile für Zeile abgearbeitet.<br>

2. Manuelle Kontrolle: Das Skript geht Zeile für Zeile durch die Ergebnisliste. Man kann als Nutzer die jeweiligen Zeilen bestätigen oder neu suchen lassen.<br>

3. Einzelne Zeile: Hier kann der Nutzer gezielt eine einzelne Schule aus der Ergebnisliste auswählen, wenn er mit dem Suchergebnis zu dieser Schule unzufrieden ist.<br>

4. Karte: Hier erstellt das Skript eine Landkarte mit Markierungen für jede Schule aus der Ergebnisliste.<br>

5: Sync: Das Skript überprüft manuell, wieviele Schulen aus der Quelldatei bereits abgearbeitet wurden.<br>

6: Settings: Hier kann man die Grundeinstellungen verändern. <br>

7: Exit: Beenden des Skripts.<br>

<h1>Einstellungen</h1>

Das Skript erstellt automatisch eine config.json-Datei. Alle Einstellungen, die man darin vornimmt, überschreiben die Standardeinstellungen im Skript. Es lohnt sich also, hier etwas Zeit und Mühe zu investieren. 

In der config.json-Datei wird unter anderem eine Keywordliste gespeichert. Wie erfolgreich das Suche nach der richtigen Schule ist, hängt nicht zuletzt von der Qualität dieser Keywords ab. Außerdem befinden sich hier die verschiedenen Schultypen und der Prompt für die KI.

<h1>Lizenz</h1>
Diese Softare steht unter der GNU GPL v3.0 Lizenz](https://github.com/wiemachendiedasnur/school_miner/blob/main/LICENSE).
