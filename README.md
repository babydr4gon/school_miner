<h1 align="center">
  <img src="https://github.com/babydr4gon/school_miner/blob/assets/images/dragon_mine.png" alt="School_miner icon" width="400" height="400"/>
  <br>
  School_Miner
</h1>


Dieses Tool hilft Eltern, Schulwebseiten automatisch nach Keywords (MINT, Ganztag, Montessori, etc.) zu durchsuchen und die pädagogischen Konzepte mit KI zusammenzufassen.

Eine fast funktionsgleiche Version, die im Browser genutzt werden kann, befindet sich <a href="https://github.com/babydr4gon/school_miner_browser/tree/main">hier</a>. 

<h1>Automatische Installation</h1>

**Vorbereitung:** Auf dem Rechner muss Python installiert sein, mindestens in der Version 3.11. Wer Python auf einem Windows-Rechner nachinstalliert, muss darauf achten, dass der Haken bei "Add Python to PATH" gesetzt ist. Außerdem erwartet das Programm den Browser Google Chrome bzw. Chromium.

**Repository klonen** oder als ZIP herunterladen und entpacken.

**API Key:** Die Datei .env.example in .env umbenennen und API-Keys hinter dem Gleichheitszeichen einfügen.

   ```bash
   OPENROUTER_API_KEY=dein_schluessel_hier
   ```
**Schulliste anlegen:** Eine Liste mit Schulnamen und Adressen herunterladen und unter "schulen.xlsx" abspeichern. Das Skript erwartet, dass sich der Name der Schule in der Spalte A und der Ort in Spalte C befinden. Wer das ändern möchte, muss im Code folgende Angaben anpassen (0 ist A und 2 ist C): 

```bash
"COLUMN_NAME_IDX": 0,
"COLUMN_ORT_IDX": 2,
```


<h1>Manuelle Installation</h1>

**Repository klonen** oder als ZIP herunterladen und entpacken.

**Abhängigkeiten installieren:** Dazu einen Terminal / eine Eingabeaufforderung öffnen und 
   
   ```bash
   pip install -r requirements.txt
   ```
eingeben. Falls es dabei unter Windows Fehlermeldungen gibt, dass die Installation zwar erfolgreich aber "not on PATH" war, muss gegebenenfalls noch eine System-Einstellung verändert werden. Wie das geht, steht <a href="https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/">hier</a>. 


**API-Keys** in einer Datei namens .env im gleichen Ordner hinterlegen. 

```bash
   OPENROUTER_API_KEY=dein_schluessel_hier
   ```

**Schulliste anlegen:** Eine Liste mit Schulnamen und Adressen herunterladen und unter "schulen.xlsx" abspeichern. Das Skript erwartet, dass sich der Name der Schule in der Spalte A und der Ort in Spalte C befinden. Wer das ändern möchte, muss im Code folgende Angaben anpassen (0 ist A und 2 ist C): 

```bash
"COLUMN_NAME_IDX": 0,
"COLUMN_ORT_IDX": 2,
```

<h1>Start</h1>

Auf Windows-Rechnern Doppelklick auf die heruntergeladene Datei "school_miner_cli.bat".  

Auf Linux-Rechnern die Datei "school_miner_startcli.sh" starten. Gegebenenfalls noch ausführbar machen.

Alternativ einen Terminal / eine Eingabeaufforderung starten und in den Ordner wechseln, in dem das Skript liegt. Mit

   ```bash
   python school_miner.py
   ```
   starten.
   
<h1>Nutzung</h1>

<h3>Die Basis: eine Liste mit Schulen</h3>

In allen Bundesländern in Deutschland gibt es Listen mit Namen und Adressen der Schulen. Sie werden  in der Regel von den Kultusministerien oder von den statistischen Landesämtern gepflegt.

Diese Listen muss man für die eigenen Bedürfnisse anpassen, also beispielsweise die Schulen löschen, die geographisch zu weit weg sind. Voreingestellt ist als Name für diese Liste "schulen.xlsx". 

Das Skript wird für jede der Schulen in dieser Liste nach der offiziellen Webseite suchen. Dort identifiziert es den Schultyp und erkennt bestimmte Keywords. Sobald es diese Dinge gefunden hat, versucht eine KI die gefundenen Informationen zum Konzept oder zu Besonderheiten der Schule in wenigen Sätzen zusammenzufassen. 

Am Ende wird  eine Tabelle mit den Ergebnissen der Suche erstellt. Darin stehen der Name und der Ort der Schule, die gefundenen Keywords, die verwendete Webseite und die Zusammenfassung der KI. Es gibt die Möglichkeit, Fehler, die bei der automatisierten Suche passieren, individuell zu korrigieren. 

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/assets/images/Karte.jpg" alt="Landkarte" width="650" height="650"/>

Abschließend kann man sich eine Landkarte erstellen lassen. Auf dieser Landkarte sind die Schulen mit Markern eingezeichnet. Klickt man auf einen der Marker, erscheint eine kurze Übersicht: der Name der Schule, die gefundenen Keywords und die KI-Zusammenfassung. 

<h3>Das Hauptmenü</h3>

Nach dem Start erscheint folgende Übersicht:

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/assets/images/Start.jpg" alt="Hauptmenü" width="650" height="650"/>

**AutoScan:** die vorbereitete Liste der Schulen wird automatisch, Zeile für Zeile abgearbeitet.

**Manuelle Kontrolle:** Das Skript geht noch einmal Zeile für Zeile durch die Ergebnisliste. Man kann als Nutzer die jeweiligen Zeilen bestätigen oder einzelne Werte gezielt verändern. Beispielsweise kann man eine neue Webseite angeben, die automatisch neu durchsucht wird. Oder es lassen sich manuell Schultyp bzw. Keywords eintragen.

**Einzelne Zeile:** Hier kann der Nutzer gezielt eine einzelne Schule aus der Ergebnisliste auswählen, wenn er mit dem Suchergebnis zu dieser Schule unzufrieden ist.

**Karte erstellen:** Hier erstellt das Skript eine Landkarte mit Markierungen für jede Schule auf der Basis der Ergebnisliste.

**Sync mit Input-Datei:** Das Skript überprüft, wie viele Schulen aus der Quelldatei bereits abgearbeitet wurden bzw. ob neue Schulen hinzugekommen sind.

**Einstellungen:** Hier kann man die Grundeinstellungen verändern.

**Beenden:** Beenden des Skripts.

<h3>Die manuelle Kontrolle</h3>

Nach dem ersten Durchlauf der Schulliste werden einige Einträge noch unvollständig sein. Mit der manuellen Kontrolle lässt sich hier nacharbeiten. Das Programm sucht nach leeren Stellen in der Ergebnisliste, zeigt die bisher gefundenen Informationen zu einer Schule an und öffnet die bisher gespeicherte Webseite. All diese Dinge kann der Nutzer im Rahmen der manuellen Kontrolle jetzt ändern.

print("\n   [1] Auto-Scan - Aktuell ausgewählte Schule komplett neu scannen")
                print("   [2] Nur KI-Check bei aktuell gewählter Schule wiederholen")
                print("   [3] Neue URL für aktuell gewählte Schule einfügen und scannen")
                print("   [4] Schultyp(en) für aktuell gewählte Schule nachtragen")
                print("   [5] Neue Keywords für aktuell gewählte Schule")
                print("   --------------------------------------------------------")
                print("   [6] Durchsuche Liste nach Schulen ohne Schultyp")
                print("   [7] Durchsuche Liste nach Schulen ohne Keywords")
                print("   [8] Durchsuche Liste nach Schulen ohne KI")

**Auto-Scan - Aktuell ausgewählte Schule komplett neu scannen:**: Im Rahmen der manuellen Kontrolle bedeutet AutoScan, dass der gewählt Eintrag (und nicht etwa die ganze Liste) noch einmal mit den vorgegebenen Einstellungen automatisch gescannt wird. Das ist zum Beispiel dann sinnvoll, wenn eine Webseite beim ersten Durchlauf nicht erreichbar war.

**Nur KI-Check bei aktuell gewählter Schule wiederholen:** Nur das Feld "KI-Zusammenfassung" wird noch einmal bearbeitet, durch eine erneute Abfrage mit den bisher gefundenen Daten und den aktuellen Einstellungen.

<img src="https://github.com/wiemachendiedasnur/school_miner/blob/assets/images/Manuell.jpg" alt="Manuelle Kontrolle" width="650" height="650"/>

**Neue URL für aktuell gewählte Schule einfügen und scannen:** Falls beim ersten Durchlauf eine falsche Webadresse gefunden wurde, lässt sich das hier korrigieren. Anschließend läuft der komplette AutoScan für diesen Eintrag noch einmal durch.

**Schultyp(en) für aktuell gewählte Schule nachtragen:** Hier kann der Schultyp verändert werden.

**Neue Keywords für aktuell gewählte Schule:** Eigene Schlüsselwörter eintragen.

**Durchsuche Liste nach Schulen ohne Schultyp:** Hier kann man die Logik einstellen, nach der bei der manuellen Kontrolle der nächste Eintrag ausgewählt wird. In diesem Fall wird die nächste Schule ausgewählt, bei der in der Ergebnisliste noch kein Schultyp zugeordnet ist und das entsprechende Feld leer ist.

**Durchsuche Liste nach Schulen ohne Schultyp:** Auch hier kann man die Logik einstellen, nach der bei der manuellen Kontrolle der nächste Eintrag ausgewählt wird. In diesem Fall wird die nächste Schule ausgewählt, bei der in der Ergebnisliste noch keine Keywords zugeordnet sind und das entsprechende Feld leer ist.

**Durchsuche Liste nach Schulen ohne KI:** Auch hier kann man die Logik einstellen, nach der bei der manuellen Kontrolle der nächste Eintrag ausgewählt wird. In diesem Fall wird die nächste Schule ausgewählt, bei der in der Ergebnisliste noch kein KI-Eintrag zugeordnet ist und das entsprechende Feld leer ist.

**Skip:** Einen Eintrag überspringen, z.B. weil er zwar unvollständig, aber auch unwichtig ist.

**Reset des Indexes:** Das Programm merkt sich, an welcher Stelle in der Liste die manuelle Kontrolle zuletzt abgebrochen wurde und beginnt beim nächsten Mal genau bei diesem Eintrag. Sollte man aber komplett noch einmal von vorne beginnen wollen, kann man den Merkindex hier auf 0 zurücksetzen.

<h3>Einstellungen</h3>

**Input Datei:** Hier die Quelldatei eintragen. Voreingestellt ist schulen.xlsx

**Schultypen:** Viele Schulformen sind bereits in der Voreinstellung erfasst. In manchen Bundesländern gibt es aber Sonderformen oder besondere Namen für einzelne Schulformen. Dann hier nachtragen.

**Keywords:** Die Schlüsselwörter sind wichtig um auf den Webseiten zentrale Teile herauszufiltern. 

**KI-Priorität:** Die einzelnen KI-Anbieter werden in der hier festgelegten Reihenfolge abgefragt. 

**Prompt Text:** Der Auftrag an die KI-Anbieter mit der zentralen Fragestellung zu den einzelnen Schulen.

**Sensibilität:** Bei der Sensibilität "normal" wird nur geprüft, ob auf einer Webseite der Name und der Ort der Schule enthalten sind. Bei "strict" kommen weitere Bedingungen dazu. Das kann dazu führen, dass manchmal keine Webseite gefunden wird. In anderen Fällen führt "strict" dazu, dass das Skript genauer unterscheiden kann zwischen der echten Schulwebseite und einem Zeitungsartikel über eine Schule.

**Map Pause:** Bei der Erstellung der Landkarte sorgen zu viele Anfragen an den OSM-Server dafür, dass man blockiert wird. Die Pauseneinstellung soll das verhindern. Wenn diese Zeit nicht reicht, einfach erhöhen.

<h1>Tipps und Tricks </h1>

Schulwebseiten zu scannen ist eine Herausforderung. Viele dieser Seiten sind entweder veraltet oder ziemlich zusammengestückelt. Deshalb muss man, wenn man erfolgreich Informationen sammeln will, etwas Zeit und Mühe investieren. Dazu folgende Ideen:

**Mit einer kleinen Testliste anfangen:** Es hat sich bewährt, zunächst höchstens 10 Schulen als Quelle zu nehmen und das Programm ein paar Mal mit verschiedenen Keywords und einem individuell gestalteten Prompt durchlaufen zu lassen. Sehr unterschiedlich wirkt es sich beispielsweise aus, die Sensibilität von "strict" auf "normal" zu stellen. Dann tauchen zwar plötzlich vielleicht ein paar Zeitungsberichte in der Suche auf, aber da stehen manchmal auch ganz interessante Sachen über die gesuchte Schule drin. Die Keywordliste zu erweitern kann dafür sorgen, dass das Skript auf Unterseiten der Schulhomepage Dinge findet, die sonst verloren gegangen wären.

**Einen guten Prompt formulieren:** Es lohnt sich sicher, hier etwas Arbeit reinzustecken und mehrere unterschiedliche Versionen zu vergleichen. Es kann helfen, zunächst einen sehr allgemeinen Prompt zu formulieren, bei dem vielleicht einfach nur nach Besonderheiten der Schule gefragt wird. Im zweiten Schritt probiert man dann einen Prompt, der sehr genau auf den eigenen Fokus bei der Schulsuche hin geschrieben ist. Stück für Stück nähert man sich so einem Prompt an, der individuell auf den eigenen Bedarf zugeschnitten, aber gleichzeitig auch für größere Listen geeignet ist.

**Den Index in der config.json nutzen:** Manchmal hat man Pech und in der Ergebnisliste gibt es einen längeren Abschnitt ohne vernünftige Ergebnisse. Über mehrere Zeilen hinweg hat das Programm möglicherweise keine oder keine guten Daten geliefert. Wenn man nun den Autoscan wieder bei 0 startet, werden andere Ergebnisse wieder überschrieben und sind verloren. In diesem Fall kann man besser ganz unten in der config.json den Wert "AUTO_RESUME_IDX" auf die Zeile stellen, bei der man wieder anfangen möchte. Wenn die fehlenden Zeilen abgearbeitet sind, einfach das Programm mit Strg + C unterbrechen.

**Eine andere KI ausprobieren:** Das Programm bietet die Möglichkeit, zwischen unterschiedlichen KI-Anbietern und Modellen zu wechseln. Dabei können sehr unterschiedliche Antworten herauskommen.

**Viele beige Marker auf der Landkarte:** Wahrscheinlich sind viele Schulen noch ohne Schultyp und werden dann den anderen Farben nicht zugeordnet. Da hilft nur eine manuelle Kontrolle oder ein ganz neuer Autoscan.

<h1>Deinstallation</h1>

Wer das Programm über die beiliegenden Start-Skripte (.bat für Windows oder .sh für Linux) genutzt hat, muss einfach nur den gesamten Projektordner löschen.

Fortgeschrittene Nutzer, die das Programm manuell über das Terminal installiert haben: Wer die Module händisch ohne virtuelle Umgebung installiert hat, bei dem liegen diese im globalen Python-Ordner des Systems. Um sie zu entfernen, einen Terminal in diesem Ordner öffnen und folgenden Befehl eingeben, und zwar bevor der Projektordner gelöscht wird:

  ```bash
  pip uninstall -r requirements.txt -y
   ```

<h1>Kauf mir einen Kaffee! </h1>
Wem diese Arbeit gefallen hat oder wer einfach nur einen Nutzen von dem Programm hat, der darf mir gerne einen Kaffee kaufen :-). Ich freue mich darüber.

<p align="center">
  <a href="https://www.buymeacoffee.com/gernotzumc2" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 90px !important;width: 324px !important;"></a>
 </p>


