# Industrial Process Intelligence Platform

## One-Sentence Pitch

Eine Process-Intelligence-Plattform, die reale Purchase-to-Pay-Eventdaten analysiert, Durchlaufzeiten berechnet, Datenqualitätsprobleme erkennt und die Grundlage für Varianten-, Bottleneck- und Risikoanalysen schafft.

---

## Business Problem

Unternehmen verfügen häufig über große Mengen an Prozessdaten aus ERP-, Einkaufs-, Service- oder Workflow-Systemen. Trotzdem bleiben zentrale operative Fragen oft unbeantwortet:

- Wo verliert der Prozess tatsächlich Zeit?
- Welche Prozessvarianten sind ineffizient?
- Welche Aktivitäten oder Übergänge verursachen Wartezeiten?
- Welche Fälle sind Ausnahmen und verzerren KPIs?
- Welche Verbesserung sollte priorisiert werden?

Klassische Reports zeigen meist nur aggregierte Kennzahlen. Dieses Projekt geht einen Schritt weiter und übersetzt Eventdaten in entscheidungsrelevante Prozessinformationen.

---

## Project Goal

Ziel des Projekts ist der Aufbau eines Process-Intelligence-Prototyps für reale Purchase-to-Pay-Prozessdaten.

Das System soll Process Ownern und Operations-Verantwortlichen helfen, operative Schwachstellen zu erkennen und Verbesserungsmaßnahmen datenbasiert zu priorisieren.

Zentrale Leitfrage:

> Wo verliert der Purchase-to-Pay-Prozess Zeit, warum passiert das, und welcher Prozessbereich sollte zuerst verbessert werden?

---

## Target Users

- Process Owner
- Operations Manager
- Continuous Improvement Teams
- Business Analysts
- Digital Transformation Analysts
- Process Automation Analysts

---

## Data Source

Das Projekt nutzt den BPI Challenge 2019 Purchase-to-Pay Event Log.

Der Datensatz beschreibt reale Einkaufsprozesse eines multinationalen Unternehmens und enthält Events aus einem Purchase-to-Pay-Prozess.

Verwendete Rohdaten:

- Format: XES Event Log
- Prozessdomäne: Purchase-to-Pay
- Events: 1.595.923
- Cases: 251.734
- Aktivitäten: 42
- Ressourcen: 628

Die Rohdaten werden nicht im Repository gespeichert.

---

## Business Context

Der analysierte Purchase-to-Pay-Prozess besteht vereinfacht aus folgenden Schritten:

```text
Purchase Requisition
↓
Purchase Order
↓
Goods Receipt
↓
Invoice Receipt
↓
Invoice Clearing / Payment