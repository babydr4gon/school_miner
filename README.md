<h1 align="center">
  <img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/dragon_mine.png" alt="School_miner icon" width="300" height="300"/>
  <br>
  School_Miner
</h1>

<p align="center">
  <a href="https://liberapay.com/Gernot_Sell/donate">
    <img alt="Liberapay donation button" src="https://img.shields.io/badge/liberapay-donate-green">
  </a>
  <a href="https://www.patreon.com/gernotsell?fan_landing=true">
    <img alt="Patreon donation button" src="https://img.shields.io/badge/patreon-donate-green.svg">
  </a>
</p>

Dieses Tool hilft Eltern, Schulwebseiten automatisch nach Keywords (MINT, Ganztag, Montessori, etc.) zu durchsuchen und die pädagogischen Konzepte mit KI zusammenzufassen.

<h1>Installation</h1>

1. **Repository klonen** oder als ZIP herunterladen und entpacken.

2. **Abhängigkeiten installieren:**
   
   ```bash
   pip install -r requirements.txt

3. API-Keys in einer Datei namens .env im gleichen Ordner hinterlegen. Ohne API-Key läuft das Skript auch, liefert aber keine KI-Zusammenfassungen, sondern nur die gefundenen Keywords.
   ```bash
   OPENROUTER_API_KEY=dein_schluessel_hier

4. Schulliste anlegen: Erstelle eine Datei schulen.xlsx. Das Skript erwartet in Spalte A den Namen der Schule und in Spalte C den Ort der Schule.  Wenn diese Daten in anderen Spalten stehen, lässt sich das in den Einstellungen später anpassen.

5. Starten
   ```bash
   python school_miner.py

<h1>Nutzung</h1>

<h3>Die Basis: eine Liste mit Schulen</h3>

Zunächst sollte man eine Liste der Schulen erstellen, über die man Informationen sammeln möchte. In allen Bundesländern gibt es entsprechende Listen, die in der Regel von den Kultusministerien oder von den statistischen Landesämtern gepflegt werden.

Diese Listen muss man für die eigenen Bedürfnisse anpassen: Man könnte also z.B. Städte, die nicht in Frage kommen, löschen und den Rest für die Suche speichern. Oder man lässt die Listen unverändert und scannt damit alle Schulen in einem Bundesland. In jedem Fall bildet diese Liste die Basis. Voreingestellt ist als Name für diese Liste schulen.xlsx.

Das Skript wird für jede der Schulen in dieser Liste nach der offiziellen Webseite suchen. Dort identifiziert es den Schultyp und erkennt bestimmte Keywords. Sobald es diese Dinge gefunden hat, versucht eine KI die gefundenen Informationen zum Konzept oder zu Besonderheiten der Schule in wenigen Sätzen zusammenzufassen. 

Am Ende wird  eine Tabelle mit den Ergebnissen der Suche erstellt. Darin stehen der Name und der Ort der Schule, die gefundenen Keywords, die verwendete Webseite und die Zusammenfassung der KI. Es gibt die Möglichkeit, Fehler, die bei der automatisierten Suche passieren, individuell zu korrigieren. 

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Schulübersicht.jpg" alt="Landkarte" width="650" height="650"/>

Abschließend kann man sich eine Landkarte erstellen lassen. Auf dieser Landkarte sind die Schulen mit Markern eingezeichnet. Klickt man auf einen der Marker, erscheint eine kurze Übersicht: der Name der Schule, die gefundenen Keywords und gegebenenfalls eine KI-Zusammenfassung. 

<h3>Der Ablauf im Detail: vom AutoScan zur Landkarte</h3>

Nach dem Start mit python school_miner.py erscheint ein Auswahlmenü mit insgesamt sieben Möglichkeiten: 
<ol>

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Start.jpg" alt="Hauptmenü" width="650" height="650"/>

<li>AutoScan: die vorbereitete Liste der Schulen wird automatisch, Zeile für Zeile abgearbeitet.</li>

<li>Manuelle Kontrolle: Das Skript geht noch einmal Zeile für Zeile durch die Ergebnisliste. Man kann als Nutzer die jeweiligen Zeilen bestätigen oder neu suchen lassen.</li>

<li>Einzelne Zeile: Hier kann der Nutzer gezielt eine einzelne Schule aus der Ergebnisliste auswählen, wenn er mit dem Suchergebnis zu dieser Schule unzufrieden ist.</li>

<li>Karte erstellen: Hier erstellt das Skript eine Landkarte mit Markierungen für jede Schule auf der Basis der Ergebnisliste.</li>

<li>Sync mit Input-Datei: Das Skript überprüft, wieviele Schulen aus der Quelldatei bereits abgearbeitet wurden.</li>

<li>Einstellungen: Hier kann man die Grundeinstellungen verändern.</li>

<li>Beenden: Beenden des Skripts.
</ol>

<h3>Die Einstellungen</h3>

Das Skript erstellt automatisch eine config.json-Datei. Alle Einstellungen, die man darin vornimmt, überschreiben die Standardeinstellungen im Skript. Es lohnt sich also, hier etwas Zeit und Mühe zu investieren. 

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Settings.jpg" alt="Einstellungen" width="650" height="650"/>

In der config.json-Datei wird unter anderem eine Keywordliste gespeichert. Wie erfolgreich das Suche nach der richtigen Schule ist, hängt nicht zuletzt von der Qualität dieser Keywords ab. Außerdem befinden sich hier die verschiedenen Schultypen und der Prompt für die KI.

Das Skript erwartet als Input-Datei standardmäßig eine Datei mit dem Namen „schulen.xlsx“, die im gleichen Verzeichnis liegt. 

Mit der Sensibilität stellt man ein, wie streng das Skript bei der Kontrolle der gefundenen Webseiten sein soll. Im Modus "Normal" wird nur geschaut, ob Name und Ort der Schule auf der gefundenen Webseite stehen. Das kann in Einzelfällen dazu führen, dass eine völlig falsche Webseite als Grundlage für die Suche genommen wird, nur weil dort zufällig Name und Ort der Schule genannt werden (Stayfriends, Wikipedia, etc.). 

Im Modus "strict" werden weitere Bedingungen genannt, damit eine Webseite als offizielle Webseite der Schule angenommen und gegebenenfalls von der KI ausgewertet wird. 

Die KI-Priorität regelt, in welcher Reihenfolge einzelne KI-Anbieter angesprochen werden. Werden keine KI-API-Keys definiert, läuft das Skript trotzdem weiter - es gibt dann eben keine KI-generierten Zusammenfassungen.

