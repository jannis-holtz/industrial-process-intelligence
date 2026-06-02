# Projektlogik: Industrial Process Intelligence Platform

## 1. Zweck des Projekts

Dieses Projekt analysiert reale Purchase-to-Pay-Prozessdaten, um operative Verzögerungen, ineffiziente Prozessvarianten, Bottlenecks und Verbesserungspotenziale zu identifizieren.

Das Ziel ist nicht reines Reporting, sondern Process Intelligence.

Die zentrale Fragestellung lautet:

> Wo verliert der Purchase-to-Pay-Prozess Zeit, welche Prozessmuster verursachen Verzögerungen, und welche Prozessbereiche sollten für Verbesserungsmaßnahmen priorisiert werden?

---

## 2. Fachlicher Kontext

Der analysierte Prozess ist ein Purchase-to-Pay-Prozess. Dieser umfasst typischerweise die Schritte von der Bedarfsmeldung über die Bestellung bis hin zu Wareneingang, Rechnungseingang und Rechnungsfreigabe.

Ein vereinfachter Ablauf sieht wie folgt aus:

Purchase Requisition  
↓  
Purchase Order  
↓  
Goods Receipt  
↓  
Invoice Receipt  
↓  
Invoice Clearing / Payment  

In realen Unternehmensprozessen existieren mehrere Prozessvarianten. Diese Varianten hängen unter anderem davon ab, ob ein Wareneingang erforderlich ist, ob die Rechnung vor oder nach dem Wareneingang eingeht und welche Einkaufsart vorliegt.

Relevante Prozesskategorien im Datensatz sind:

- 3-Way Match, Rechnung vor Wareneingang
- 3-Way Match, Rechnung nach Wareneingang
- 2-Way Match
- Consignment

Diese Kategorien müssen getrennt betrachtet werden, weil sie unterschiedliche fachliche Prozesslogiken und unterschiedliche erwartbare Durchlaufzeiten haben können.

---

## 3. Datengrundlage

Das Projekt basiert auf dem BPI Challenge 2019 Purchase-to-Pay Event Log.

Der Datensatz beschreibt reale Einkaufsprozessdaten eines multinationalen Unternehmens und enthält Ereignisse aus einem Purchase-to-Pay-Prozess.

Die Rohdaten liegen im XES-Format vor. XES ist ein standardisiertes Format für Event Logs im Process-Mining-Kontext.

Die initiale Analyse des Datensatzes ergab:

- 1.595.923 Events
- 251.734 Cases
- 42 verschiedene Aktivitäten
- 628 Ressourcen
- 21 Rohspalten nach Import
- Zeitstempelbereich von 1948-01-26 bis 2020-04-09

Die Rohdaten werden nicht im Repository gespeichert. Stattdessen wird eine reproduzierbare Datenpipeline verwendet, mit der die Rohdaten lokal verarbeitet werden können.

---

## 4. Begriff: Case

Ein Case repräsentiert eine einzelne Einkaufsposition innerhalb eines Einkaufsdokuments.

Beispiel:

case_id = 4507004931_00020

Diese Case-ID besteht aus:

- Einkaufsdokument: 4507004931
- Einkaufsposition: 00020

Fachlich bedeutet das:

> Ein Case ist eine einzelne Einkaufsposition, die durch den Purchase-to-Pay-Prozess läuft.

Die Analyse erfolgt nicht nur auf Ebene einzelner Events, sondern vor allem auf Case-Ebene. Dadurch können Durchlaufzeiten, Prozessvarianten und Abweichungen pro Einkaufsposition bewertet werden.

---

## 5. Begriff: Event

Ein Event ist eine einzelne aufgezeichnete Aktivität innerhalb eines Cases.

Beispiele für Aktivitäten im Datensatz:

- Create Purchase Order Item
- Record Goods Receipt
- Vendor creates invoice
- Record Invoice Receipt
- Clear Invoice
- Remove Payment Block
- Change Quantity
- Record Service Entry Sheet

Jedes Event enthält mindestens folgende Informationen:

- Case-ID
- Aktivität
- Zeitstempel
- Ressource oder ausführender Nutzer beziehungsweise Systemprozess

Dadurch kann rekonstruiert werden:

- welche Aktivitäten stattgefunden haben
- in welcher Reihenfolge sie stattgefunden haben
- wann sie stattgefunden haben
- welche Ressource beteiligt war
- welche Prozessvariante ein Case durchlaufen hat

---

## 6. Standardisiertes Event-Log-Modell

Nach dem Import wird das Rohdatenformat in ein standardisiertes analytisches Event-Log-Modell überführt.

Die wichtigsten Zielspalten sind:

- case_id
- activity
- timestamp
- resource
- user
- cumulative_net_worth_eur
- company
- document_type
- purchasing_document
- vendor
- item_type
- item_category
- spend_area
- sub_spend_area
- spend_classification
- source
- gr_based_invoice_verification
- goods_receipt
- item

Für den MVP sind besonders relevant:

- case_id
- activity
- timestamp
- resource
- company
- document_type
- item_category
- vendor

Dieses standardisierte Modell stellt sicher, dass nachgelagerte Analysen unabhängig vom ursprünglichen Rohdatenformat durchgeführt werden können.

---

## 7. Datenpipeline

Die aktuelle Datenpipeline besteht aus folgenden Schritten:

Raw XES Event Log  
↓  
PM4Py Import  
↓  
Pandas DataFrame  
↓  
Standardisierte Spaltennamen  
↓  
Parquet Event Log  
↓  
Case-Level-KPI-Tabelle  
↓  
Bereinigte Business-KPI-Tabelle  
↓  
Dashboard und Analysekomponenten  

Die Umwandlung in Parquet ist bewusst Teil der Architektur. Das XES-Format ist für Process Mining geeignet, aber für wiederholte analytische Verarbeitung und Dashboard-Nutzung zu langsam.

Durch die Parquet-Zwischenschicht wird erreicht:

- schnelleres Laden der Daten
- reproduzierbare Verarbeitung
- klare Trennung von Rohdaten und verarbeiteten Daten
- bessere Nutzbarkeit für KPI-Berechnung und Dashboard-Analysen

---

## 8. Cycle Time

Cycle Time beschreibt die Durchlaufzeit eines Cases vom ersten bis zum letzten aufgezeichneten Event.

Formel:

cycle_time = timestamp des letzten Events - timestamp des ersten Events

Fachliche Interpretation:

> Die Cycle Time zeigt, wie lange eine Einkaufsposition im betrachteten Prozess aktiv war.

Cycle Time ist eine zentrale Kennzahl, um langsame Fälle, ineffiziente Varianten und operative Verzögerungen zu identifizieren.

Die initiale Analyse ergab:

- Average Cycle Time: 71,52 Tage
- Median Cycle Time: 64,04 Tage
- P75 Cycle Time: 98,26 Tage
- P90 Cycle Time: 126,10 Tage
- P95 Cycle Time: 142,30 Tage
- Maximum Cycle Time: 25.670,55 Tage

Der Median ist für die operative Bewertung robuster als der Durchschnitt, weil extreme Ausreißer die Durchschnittswerte verzerren können.

---

## 9. Datenqualität und Ausreißerbehandlung

Die initiale Analyse hat deutliche Zeitstempel-Ausreißer gezeigt.

Relevante Befunde:

- 224 Cases haben eine Cycle Time von mehr als 365 Tagen.
- 318 Events liegen vor dem Jahr 2018.
- 2 Events liegen nach dem Jahr 2019.
- Die maximale Cycle Time liegt bei 25.670,55 Tagen.

Da der betrachtete Prozess fachlich auf Purchase-to-Pay-Vorgänge aus dem Jahr 2018 ausgerichtet ist, müssen solche Ausreißer separat betrachtet werden.

Das Projekt verwendet daher zwei KPI-Sichten:

### Raw KPI View

Die Raw KPI View enthält alle Cases.

Zweck:

- vollständige Transparenz
- Datenqualitätsanalyse
- Ausnahmefallanalyse
- Nachvollziehbarkeit der ursprünglichen Datenlage

### Clean Business KPI View

Die Clean Business KPI View schließt Cases mit einer Cycle Time über 365 Tagen aus.

Zweck:

- operative Prozesssteuerung
- stabilere Management-KPIs
- realistischere Bottleneck-Analyse
- bessere Vergleichbarkeit von Prozesskategorien

Die ausgeschlossenen Cases werden nicht gelöscht. Sie bleiben im Rohdatenbestand erhalten und können separat als Ausnahmefälle analysiert werden.

---

## 10. KPI-Logik

Die KPI-Berechnung erfolgt auf mehreren Ebenen.

### Dataset-Level KPIs

Diese Kennzahlen beschreiben den Gesamtumfang des Event Logs:

- Anzahl Events
- Anzahl Cases
- Anzahl Aktivitäten
- Anzahl Ressourcen
- Zeitraum der Events

### Case-Level KPIs

Diese Kennzahlen werden pro Case berechnet:

- Startzeitpunkt
- Endzeitpunkt
- Cycle Time in Tagen
- Anzahl Events pro Case
- Anzahl unterschiedlicher Aktivitäten pro Case
- Item Category
- Document Type
- Company
- Vendor

### Prozessbezogene KPIs

Diese Kennzahlen werden für Prozessanalyse und Dashboarding verwendet:

- Average Cycle Time
- Median Cycle Time
- P75 / P90 / P95 Cycle Time
- Anteil langer Cases
- Verteilung nach Item Category
- Verteilung nach Document Type
- Top Activities
- Häufigste Prozessvarianten
- Wartezeiten zwischen Aktivitäten

---

## 11. Prozessvarianten

Eine Prozessvariante beschreibt die konkrete Reihenfolge von Aktivitäten, die ein Case durchlaufen hat.

Beispiel:

Create Purchase Order Item  
→ Record Goods Receipt  
→ Vendor creates invoice  
→ Record Invoice Receipt  
→ Clear Invoice  

Die Variantenanalyse beantwortet unter anderem folgende Fragen:

- Welche Prozesspfade treten am häufigsten auf?
- Welche Varianten haben besonders lange Durchlaufzeiten?
- Welche Varianten enthalten zusätzliche Schleifen oder Korrekturen?
- Welche Varianten unterscheiden sich je nach Item Category?
- Welche Varianten sollten als Standardprozess betrachtet werden?
- Welche Varianten sind potenzielle Abweichungen?

Die Variantenanalyse ist wichtig, weil Durchschnittswerte über alle Cases hinweg oft verdecken, dass verschiedene Prozesspfade unterschiedlich performen.

---

## 12. Bottleneck Detection

Bottleneck Detection analysiert Wartezeiten zwischen aufeinanderfolgenden Aktivitäten.

Für jeden Case werden die Events zeitlich sortiert. Anschließend wird die Zeit zwischen einer Aktivität und der nächsten Aktivität berechnet.

Beispiel:

Record Goods Receipt  
→ Record Invoice Receipt  

waiting_time = timestamp Record Invoice Receipt - timestamp Record Goods Receipt

Die Aggregation erfolgt auf Ebene von Prozessübergängen.

Relevante Kennzahlen pro Übergang:

- durchschnittliche Wartezeit
- mediane Wartezeit
- Anzahl der Vorkommen
- Anteil an der gesamten beobachteten Wartezeit
- betroffene Item Categories

Ein Bottleneck ist fachlich besonders relevant, wenn ein Übergang sowohl häufig auftritt als auch hohe Wartezeiten verursacht.

---

## 13. Rework Detection

Rework beschreibt wiederholte oder rückläufige Prozessmuster, die auf Korrekturen, Nacharbeit oder Prozessinstabilität hindeuten können.

Beispiele für potenzielle Rework-Muster:

- Change Quantity nach Bestellung
- Remove Payment Block
- wiederholte Invoice- oder Goods-Receipt-bezogene Aktivitäten
- mehrfache Änderungen innerhalb eines Cases
- Schleifen in der Aktivitätssequenz

Rework Detection soll nicht jede Wiederholung automatisch als Problem klassifizieren. Manche Wiederholungen sind fachlich zulässig, zum Beispiel bei Teillieferungen oder Teilrechnungen.

Daher muss Rework im Kontext von Item Category, Document Type und Prozesslogik bewertet werden.

---

## 14. Root Cause Light

Root Cause Light bezeichnet eine erste analytische Ursachenanalyse ohne komplexes Machine Learning.

Ziel ist es, auffällige Muster in langsamen Cases zu identifizieren.

Mögliche Analyseachsen:

- Item Category
- Document Type
- Company
- Vendor
- Spend Area
- Resource
- Aktivitätsanzahl
- Prozessvariante
- Auftreten bestimmter Aktivitäten
- Auftreten bestimmter Übergänge

Beispielfragen:

- Sind lange Cases in bestimmten Item Categories häufiger?
- Treten Verzögerungen bei bestimmten Document Types stärker auf?
- Sind bestimmte Prozessvarianten überdurchschnittlich langsam?
- Sind lange Cases mit bestimmten Aktivitäten oder Prozessübergängen verbunden?
- Haben Cases mit Payment Block längere Durchlaufzeiten?

Root Cause Light ist bewusst analytisch und erklärbar. Es soll eine fachliche Hypothesenbildung unterstützen, ohne Kausalität vorzutäuschen.

---

## 15. Recommendation Layer

Der Recommendation Layer leitet aus den Analyseergebnissen priorisierte Handlungshinweise ab.

Die erste Version ist regelbasiert.

Eine Empfehlung basiert typischerweise auf Kombinationen aus:

- hoher Wartezeit
- hoher Häufigkeit
- hohem Anteil an Gesamtdurchlaufzeit
- auffälliger Item Category
- auffälliger Prozessvariante
- hoher Rework-Wahrscheinlichkeit

Beispielregel:

Wenn ein Prozessübergang häufig vorkommt und eine hohe durchschnittliche Wartezeit aufweist, dann wird dieser Übergang als Verbesserungshebel priorisiert.

Eine Empfehlung sollte enthalten:

- Priorität
- betroffener Prozessbereich
- beobachtetes Problem
- relevante Kennzahl
- fachliche Begründung
- empfohlene Analyse- oder Verbesserungsmaßnahme

Der Recommendation Layer automatisiert keine Managemententscheidung. Er unterstützt die Priorisierung von Verbesserungsmaßnahmen.

---

## 16. Dashboard-Logik

Das Dashboard soll nicht nur Kennzahlen anzeigen, sondern Entscheidungsfragen beantworten.

Geplante Dashboard-Seiten:

### Executive Overview

Zentrale Frage:

> Wie ist der Gesamtzustand des Prozesses?

Inhalte:

- Anzahl Cases
- Anzahl Events
- Median Cycle Time
- Average Cycle Time
- P90 Cycle Time
- Anteil auffälliger Cases
- Data Quality Hinweise
- wichtigste Prozesskategorien

### Cycle Time Analysis

Zentrale Frage:

> Wie verteilt sich die Durchlaufzeit und welche Fälle sind auffällig langsam?

Inhalte:

- Cycle-Time-Verteilung
- Raw-vs-Clean-Vergleich
- Perzentile
- Slowest Cases
- Ausreißerhinweise

### Variant Intelligence

Zentrale Frage:

> Welche Prozesspfade treten auf und welche davon sind ineffizient?

Inhalte:

- häufigste Prozessvarianten
- Cycle Time je Variante
- Event Count je Variante
- Variantenvergleich nach Item Category

### Bottleneck Analysis

Zentrale Frage:

> Welche Prozessübergänge verursachen die größten Wartezeiten?

Inhalte:

- Top Bottleneck Transitions
- durchschnittliche und mediane Wartezeit
- Häufigkeit je Übergang
- Bottleneck Impact Score

### Root Cause Light

Zentrale Frage:

> Welche Faktoren sind mit langen Durchlaufzeiten verbunden?

Inhalte:

- Cycle Time nach Item Category
- Cycle Time nach Document Type
- Cycle Time nach Company
- Cycle Time nach Vendor
- Zusammenhang zwischen Aktivitäten und langen Cases

### Recommendations

Zentrale Frage:

> Welche Verbesserungsmaßnahme sollte zuerst geprüft werden?

Inhalte:

- priorisierte Empfehlungen
- Begründung je Empfehlung
- betroffene Prozessbereiche
- relevante Kennzahlen
- erwarteter Verbesserungshebel

---

## 17. MVP-Scope

Der MVP umfasst die minimal notwendige Funktionalität, um aus Rohdaten erste belastbare Prozessentscheidungen abzuleiten.

Enthalten im MVP:

1. XES-Import
2. Konvertierung nach Parquet
3. Standardisiertes Event-Log-Modell
4. Case-Level-KPI-Berechnung
5. Raw-vs-Clean-KPI-Logik
6. Data Quality Checks
7. Executive Overview
8. Cycle-Time-Analyse
9. Item-Category-Verteilung
10. Erste Dashboard-Version

Nicht enthalten im MVP:

- PyTorch-Modell
- LSTM-Modell
- Transformer-Modell
- Echtzeitmonitoring
- What-if-Simulation
- automatische Prozessoptimierung
- Cloud Deployment
- Microservices
- komplexes Berechtigungssystem

Der MVP fokussiert auf Prozessverständnis, KPI-Stabilität und Entscheidungsfähigkeit.

---

## 18. Version 2: Process Intelligence Layer

Version 2 erweitert den MVP um tiefergehende Prozessanalysen.

Geplante Komponenten:

- Variant Intelligence
- Bottleneck Detection
- Rework Detection
- Root Cause Light
- Recommendation Layer

Ziel von Version 2:

> Der Nutzer soll nicht nur sehen, dass der Prozess langsam ist, sondern erkennen, welche Prozessmuster und Übergänge die Verzögerungen verursachen.

---

## 19. Version 3: Predictive Process Monitoring

Version 3 ergänzt einen Prediction Layer für laufende oder teilweise beobachtete Cases.

Ziel:

> Frühzeitig erkennen, welche Cases wahrscheinlich eine kritische Durchlaufzeit überschreiten werden.

Ein möglicher Use Case ist die Vorhersage, ob ein Case eine Zielgrenze von 120 Tagen überschreiten wird.

Beispiel-Label:

risk_label = 1, wenn cycle_time_days > 120  
risk_label = 0, wenn cycle_time_days <= 120  

Mögliche Eingangsdaten:

- bisherige Aktivitätssequenz
- bisherige Laufzeit
- aktuelle Aktivität
- Item Category
- Document Type
- Company
- Vendor
- Anzahl bisheriger Events
- Auftreten kritischer Aktivitäten
- bisherige Wartezeiten

Möglicher Output:

- Risk Score
- Risikoklasse
- wichtigste erklärende Merkmale
- Empfehlung zur operativen Prüfung

---

## 20. Modellierungslogik für Version 3

Die Modellierung erfolgt gestuft.

### Stufe 1: Regelbasierte Baseline

Beispiel:

- Risiko hoch, wenn bisherige Laufzeit bereits über 90 Tagen liegt.
- Risiko hoch, wenn Payment Block auftritt.
- Risiko hoch, wenn bestimmte Bottleneck-Übergänge aufgetreten sind.

Zweck:

- einfache fachliche Vergleichsbasis
- transparente Entscheidungslogik
- schnelle Bewertung des Mehrwerts komplexerer Modelle

### Stufe 2: Klassisches Machine Learning

Mögliche Modelle:

- Logistic Regression
- Random Forest
- Gradient Boosting

Zweck:

- strukturierte Tabular Features testen
- Performance gegen regelbasierte Baseline vergleichen
- erklärbare Modellmetriken erzeugen

### Stufe 3: PyTorch LSTM

Ein LSTM kann verwendet werden, um Aktivitätssequenzen zu modellieren.

Fachliche Begründung:

> Purchase-to-Pay-Cases bestehen aus geordneten Ereignisfolgen. Ein Sequenzmodell kann Muster in Aktivitätsverläufen lernen, die mit langen Durchlaufzeiten verbunden sind.

Beispielsequenz:

Create Purchase Order Item  
→ Record Goods Receipt  
→ Vendor creates invoice  
→ Record Invoice Receipt  
→ Clear Invoice  

Das LSTM verarbeitet solche Sequenzen und gibt eine Risikowahrscheinlichkeit aus.

### Stufe 4: Optionaler Transformer-Vergleich

Ein Transformer-Modell kann optional als Vergleichsexperiment eingesetzt werden.

Der Einsatz ist nur gerechtfertigt, wenn:

- genügend Daten für robuste Modellierung vorhanden sind,
- das Modell besser als Baseline und LSTM performt,
- die zusätzliche Komplexität fachlich erklärbar bleibt,
- die Ergebnisse für den Nutzer interpretierbar sind.

Der Transformer ist nicht Kern des Projekts, sondern ein optionaler Benchmark.

---

## 21. Modellbewertung

Für den Prediction Layer sind folgende Bewertungsdimensionen relevant:

### Technische Metriken

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC
- Confusion Matrix

### Fachliche Metriken

- Wie viele kritische Cases werden früh erkannt?
- Wie viele False Positives erzeugt das Modell?
- Ist der Risk Score für Process Owner interpretierbar?
- Verbessert das Modell die Priorisierung gegenüber einer einfachen Regel?
- Ist die Modellleistung stabil über verschiedene Item Categories?

Ein Modell wird nur als sinnvoll bewertet, wenn es gegenüber der Baseline einen klaren Mehrwert zeigt.

---

## 22. Grenzen des Projekts

Das Projekt ist ein analytischer Prototyp und kein produktives Enterprise-System.

Aktuelle Grenzen:

- keine Live-Anbindung an ein ERP-System
- keine Echtzeitdaten
- keine Benutzerverwaltung
- keine produktive Zugriffskontrolle
- keine automatische Prozessänderung
- keine garantierte Kausalitätsanalyse
- keine vollständige fachliche Validierung durch den ursprünglichen Prozessowner
- keine produktive Modellüberwachung

Diese Grenzen sind bewusst dokumentiert, um die Ergebnisse realistisch einzuordnen.

---

## 23. Qualitäts- und Sicherheitsprinzipien

Das Projekt folgt grundlegenden Qualitäts- und Sicherheitsprinzipien:

- Rohdaten werden nicht ins Repository committed.
- Verarbeitete Daten werden reproduzierbar erzeugt.
- Rohdaten und verarbeitete Daten sind getrennt.
- Keine API-Keys oder Secrets im Code.
- Keine unnötige Cloud-Abhängigkeit.
- Keine unsichere dynamische Codeausführung.
- Keine Verwendung von eval().
- Lokale Analyse statt unnötiger Infrastruktur.
- Modularer Aufbau der Python-Dateien.
- KPI-Logik soll testbar sein.
- Datenqualitätsprobleme werden transparent dokumentiert.

---

## 24. Erfolgskriterien

Der MVP ist erfolgreich, wenn folgende Fragen beantwortet werden können:

1. Wie viele Cases und Events enthält der Prozess?
2. Wie lange dauert ein Case typischerweise?
3. Wie stark unterscheiden sich Average und Median Cycle Time?
4. Welche Datenqualitätsprobleme beeinflussen die KPIs?
5. Welche Item Categories dominieren den Prozess?
6. Welche Cases sind auffällig langsam?
7. Welche KPI-Sicht ist für operative Steuerung geeignet?

Version 2 ist erfolgreich, wenn zusätzlich beantwortet werden kann:

1. Welche Prozessvarianten treten am häufigsten auf?
2. Welche Varianten sind besonders langsam?
3. Welche Übergänge verursachen die höchsten Wartezeiten?
4. Welche Aktivitäten deuten auf Rework hin?
5. Welche Verbesserungsmaßnahme sollte priorisiert geprüft werden?

Version 3 ist erfolgreich, wenn zusätzlich beantwortet werden kann:

1. Welche laufenden Cases haben ein erhöhtes Risiko für kritische Durchlaufzeit?
2. Schlägt das Vorhersagemodell eine einfache Baseline messbar?
3. Ist der Risk Score fachlich interpretierbar?
4. Unterstützt die Prediction eine konkrete operative Priorisierung?