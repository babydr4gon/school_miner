


<h1>Möglichkeit 1:  Geodaten unter Microsoft Excel nutzen </h1>

Excel hat eine eingebaute Funktion namens „Geografie“, die aus Ortsnamen automatisch Längen- und Breitengrade ziehen kann.<br>
<h3>Schritt 1: Vorbereitung</h3>
<ol>
    <li>Markiere deine Liste mit den Ortsnamen.</li>
    <li>Gehe im Menüband auf den Reiter Daten.</li>
    <li>Wähle in der Gruppe „Datentypen“ die Option Geografie aus.
    Hinweis: Excel wandelt die Namen nun in Datensätze um (ein kleines Karten-Symbol erscheint neben dem Namen).</li>
    <li>Klicke auf das kleine Spalten-Symbol (mit dem Plus), das oben rechts an der markierten Zelle erscheint, und wähle Breitengrad (Latitude) und danach Längengrad (Longitude) aus.</li>
</ol>

<h3>Schritt 2: Die Referenzkoordinaten festlegen</h3>
Du brauchst die Koordinaten von deinem Mittelpunkt. Als Beispiel nehmen wir Frankfurt am Main.</br>
<ol>
    • Breitengrad Frankfurt: 50,1109</br>
    • Längengrad Frankfurt: 8,6821</br>
</ol>
Schreibe diese beiden Werte in zwei feste Zellen in deiner Tabelle (z. B. $E$1 für Breite und $F$1 für Länge).</br>

<h3>Schritt 3: Die Entfernung berechnen</h3>
Da die Erde eine Kugel ist, kannst du nicht einfach den Satz des Pythagoras nehmen. Du nutzt stattdessen die Seitenkosinussatz-Formel (eine vereinfachte Form der Haversine-Formel), um die Entfernung in Kilometern zu berechnen.
Erstelle eine neue Spalte „Entfernung (km)“ und nutze folgende Formel (angenommen, der Breitengrad des Ortes steht in B2 und der Längengrad in C2):</br>


$$d = \text{acos}(\sin(\phi_1) \cdot \sin(\phi_2) + \cos(\phi_1) \cdot \cos(\phi_2) \cdot \cos(\Delta\lambda)) \cdot 6371$$

In Excel-Syntax übersetzt sieht das so aus:


=ACOS(SIN(RADIANS($E$1))*SIN(RADIANS(B2))+COS(RADIANS($E$1))*COS(RADIANS(B2))*COS(RADIANS(C2-$F$1)))*6371

• $E$1 / $F$1: Feste Koordinaten von Frankfurt.</br>
• B2 / C2: Koordinaten des jeweiligen Ortes in der Zeile.</br>
• 6371: Der durchschnittliche Erdradius in Kilometern.</br>

<h3>Schritt 4: Filtern</h3>
Jetzt hast du in jeder Zeile die genaue Distanz zu Frankfurt stehen.
    1. Markiere deine Kopfzeile und aktiviere den Filter (Strg + Umschalt + L).
    2. Klicke auf den Pfeil bei „Entfernung (km)“.
    3. Wähle Zahlenfilter -> Kleiner oder gleich... und gib eine Kilometerzahl für den maximalen Radius ein

<h1>Möglichkeit 2: Postleitzahlen und Standardfilter nutzen</h1>

Diese Methode funktioniert sowohl in Excel auch in LibreOffice Calc. Dort einfach den Standardfilter nutzen:
<ol>
    1. Öffne die Datei in Calc.
    2. Markiere die Spalte B (PLZ).
    3. Gehe auf Daten -> Weitere Filter -> Standardfilter.
    4. Stelle ein: Spalte B -> Beginnt mit -> xx. (für xx die beiden ersten Zahlen der gewünschten Postleitzahl.
    5. Nutze den Button Mehr Optionen und füge mit dem Operator ODER weitere Zeilen für andere Postleitzahlen hinzu.
</ol>

<h1>Möglichkeit 3:</h1>
Python. Den folgenden Code speichern und ausführen. Die Quelldatei, die gefiltert werden soll, muss im gleichen Verzeichnis liegen.

```bash
import pandas as pd

file_name = 'schulen.xlsx'
df = pd.read_csv(file_name, header=None)

# Spalten benennen für leichtere Handhabung
# Spalte 0: Name, Spalte 1: PLZ, Spalte 2: Ort
df.columns = ['Name', 'PLZ', 'Ort'] + [f'Col_{i}' for i in range(3, len(df.columns))]

# Filter-Logik: 40km um Frankfurt entspricht grob diesen PLZ-Bereichen:
# 60 (FFM), 61 (Hochtaunus/Wetterau), 63 (Hanau/Offenbach), 
# 64 (Darmstadt/GG), 65 (Wiesbaden/MTK)
ziel_plz_prefix = ('60', '61', '63', '64', '65')

# Filtern
# Wir wandeln die PLZ in Strings um und prüfen den Anfang
filtered_df = df[df['PLZ'].astype(str).str.startswith(ziel_plz_prefix)]

# Ergebnis speichern
filtered_df.to_csv('Schulen_Gefiltert.csv', index=False, header=False)

print(f"Fertig! {len(filtered_df)} Schulen wurden exportiert.")
