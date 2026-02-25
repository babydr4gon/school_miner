<h1 align="center">
  <img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/dragon_mine.png" alt="School_miner icon" width="400" height="400"/>
  <br>
  School_Miner
</h1>


Dieses Tool hilft Eltern, Schulwebseiten automatisch nach Keywords (MINT, Ganztag, Montessori, etc.) zu durchsuchen und die pädagogischen Konzepte mit KI zusammenzufassen.

Eine fast funktionsgleiche Version, die im Browser genutzt werden kann, befindet sich <a href="https://github.com/babydr4gon/school_miner_browser/tree/main">hier</a>. 

<h1>Automatische Installation</h1>

**Vorbereitung:** Auf dem Rechner muss Python und der Browser Google Chrome bzw Chromium installiert sein. Wer Python auf einem Windows-Rechner nachinstalliert, muss darauf achten, dass der  Haken bei "Add Python to PATH" gesetzt ist.

**Repository klonen** oder als ZIP herunterladen und entpacken.

**API Key:** Die Datei .env.example in .env umbenennen und API-Keys hinter dem Gleichheitszeichen einfügen.  Ohne API-Key läuft das Skript auch, liefert aber keine KI-Zusammenfassungen, sondern nur die gefundenen Keywords.
   ```bash
   OPENROUTER_API_KEY=dein_schluessel_hier
   ```
**Schulliste anlegen:** Eine Liste mit Schulnamen und Adressen herunterladen und unter "schulen.xlsx" abspeichern. Das Skript erwartet, dass sich der Name der Schue in der Spalte A und der Ort in Spalte C befinden. Wer das ändern möchte, muss im Code folgende Angaben anpassen (0 ist A und 2 ist C): 

```bash
"COLUMN_NAME_IDX": 0,
"COLUMN_ORT_IDX": 2,
```

**Start:** Auf Windows-Rechnern, Doppelklick auf die heruntergeladene Datei "school_miner_cli.bat". 

Auf Linux-Rechnern, im Terminal eingeben:

   ```bash
   python school_miner.py
   ```

<h1>Manuelle Installation</h1>

**Repository klonen** oder als ZIP herunterladen und entpacken.

**Abhängigkeiten installieren:**

Dazu einen Terminal / eine Eingabeaufforderung öffnen und 
   
   ```bash
   pip install -r requirements.txt
   ```
eingeben. Falls es dabei unter Windows Fehlermeldungen gibt, dass die Installation zwar erfolgreich aber "not on PATH" war, muss gegebenenfalls noch eine System-Einstellung verändert werden. Wie das geht, steht <a href="https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/">hier</a>. 


**API-Keys** in einer Datei namens .env im gleichen Ordner hinterlegen. Ohne API-Key läuft das Skript auch, liefert aber keine KI-Zusammenfassungen, sondern nur die gefundenen Keywords.
   ```bash
   OPENROUTER_API_KEY=dein_schluessel_hier
   ```

**Schulliste anlegen:** Eine Liste mit Schulnamen und Adressen herunterladen und unter "schulen.xlsx" abspeichern. Das Skript erwartet, dass sich der Name der Schue in der Spalte A und der Ort in Spalte C befinden. Wer das ändern möchte, muss im Code folgende Angaben anpassen (0 ist A und 2 ist C): 

```bash
"COLUMN_NAME_IDX": 0,
"COLUMN_ORT_IDX": 2,
```

**Starten:**
   Einen Terminal / eine Eingabeaufforderung starten und in den Ordner wechseln, in dem das Skript liegt, z.B.:
   unter Windows
   ```bash
   cd Ein_Ordner\ein_Unterordner\...
   ```
   oder unter Linux
   ```bash
   cd Ein_Ordner/ein_Unterordner/ ...
   ```
   Dann das Skript starten mit

   ```bash
   python school_miner.py
   ```
   
<h1>Nutzung</h1>

<h3>Die Basis: eine Liste mit Schulen</h3>

Zunächst sollte man eine Liste der Schulen erstellen, über die man Informationen sammeln möchte. In allen Bundesländern gibt es entsprechende Listen, die in der Regel von den Kultusministerien oder von den statistischen Landesämtern gepflegt werden.

Diese Listen muss man für die eigenen Bedürfnisse anpassen, also beispielsweise die Schulen rauslöschen, die geographisch zu weit weg sind. Voreingestellt ist als Name für diese Liste "schulen.xlsx". 

Das Skript wird für jede der Schulen in dieser Liste nach der offiziellen Webseite suchen. Dort identifiziert es den Schultyp und erkennt bestimmte Keywords. Sobald es diese Dinge gefunden hat, versucht eine KI die gefundenen Informationen zum Konzept oder zu Besonderheiten der Schule in wenigen Sätzen zusammenzufassen. 

Am Ende wird  eine Tabelle mit den Ergebnissen der Suche erstellt. Darin stehen der Name und der Ort der Schule, die gefundenen Keywords, die verwendete Webseite und die Zusammenfassung der KI. Es gibt die Möglichkeit, Fehler, die bei der automatisierten Suche passieren, individuell zu korrigieren. 

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Karte.jpg" alt="Landkarte" width="650" height="650"/>

Abschließend kann man sich eine Landkarte erstellen lassen. Auf dieser Landkarte sind die Schulen mit Markern eingezeichnet. Klickt man auf einen der Marker, erscheint eine kurze Übersicht: der Name der Schule, die gefundenen Keywords und die KI-Zusammenfassung. 

<h3>Nach dem Start</h3>

Es erscheint ein Auswahlmenü mit insgesamt sieben Möglichkeiten: 

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Start.jpg" alt="Hauptmenü" width="650" height="650"/>

**AutoScan:** die vorbereitete Liste der Schulen wird automatisch, Zeile für Zeile abgearbeitet.

**Manuelle Kontrolle:** Das Skript geht noch einmal Zeile für Zeile durch die Ergebnisliste. Man kann als Nutzer die jeweiligen Zeilen bestätigen oder einzelne Werte gezielt verändern. Beispielsweise kann man eine neue Webseite angeben, die automatisch neu durchsucht wird. Oder es lassen sich manuell Schultyp bzw. Keywords eintragen.

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/main/images/Manuell.jpg" alt="Manuelle Kontrolle" width="650" height="650"/>

**Einzelne Zeile:** Hier kann der Nutzer gezielt eine einzelne Schule aus der Ergebnisliste auswählen, wenn er mit dem Suchergebnis zu dieser Schule unzufrieden ist.

**Karte erstellen:** Hier erstellt das Skript eine Landkarte mit Markierungen für jede Schule auf der Basis der Ergebnisliste.

**Sync mit Input-Datei:** Das Skript überprüft, wieviele Schulen aus der Quelldatei bereits abgearbeitet wurden.

**Einstellungen:** Hier kann man die Grundeinstellungen verändern.

**Beenden:** Beenden des Skripts.

<h1>Zu guter Letzt: </h1>
Wem diese Arbeit gefallen hat oder wer einfach nur einen Nutzen von dem Programm hat, der darf mir gerne einen Kaffee kaufen :-). Ich freue mnich darüber.

<p align="center">
  <a href="https://www.buymeacoffee.com/gernotzumc2" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 90px !important;width: 324px !important;"></a>
 </p>


