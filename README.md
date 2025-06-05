# ML-4-B

## 1 Introduction

### Motivation

- Angebliche 72% Pünktlichkeit der ICEs
- Gefühl immer die falschen ICEs zu erwischen
- Gezielt Zugbindung aufheben (strategisch den falschen Zug buchen)
- Verspätungen und Ausfälle der ICEs vorhersagen

### Research question

- Lassen sich Verspätungen und Ausfälle der ICEs anhand von Daten über vergangene Zugfahrten und Wetterdaten vorhersagen?
- Welche Faktoren beeinflussen die Pünktlichkeit der ICEs?
- Wie kann die Vorhersagegenauigkeit weiter verbessert werden?

### Goal

- Entwicklung eines Modells zur Vorhersage von Verspätungen und Ausfällen der ICEs
- Entwicklung einer Web-App zur Visualisierung der Vorhersagen
- Bereitstellung der Daten und Modelle für die Community

### Target audience

- Bahnreisende, die ihre Reise besser planen möchten
- Entwickler, die an der Vorhersage von Verspätungen und Ausfällen interessiert sind
- Forscher, die an der Analyse von Zugfahrten und Wetterdaten interessiert sind

### How to use this repository

- Clone the repository
- Install the required packages via `pip install -r requirements.txt`
- Run the Jupyter notebooks in the `src/exploration` folder to explore the data
- Run the Python scripts in the `src/ml_models` folder to train the models
- Run the Streamlit app in the `src/streamlit` folder to visualize the predictions
- Use the `data` folder to store your own data or keep ours

### How is this document structured

- [1 Introduction](#1-introduction)
- [2 Related Work](#2-related-work)
- [3 Methodology](#3-methodology)
  - [3.1 General Methodology](#31-general-methodology)
  - [3.2 Data Collection](#32-data-collection)
  - [3.3 Data Understanding and Preparation](#33-data-understanding-and-preparation)
  - [3.4 Modeling and Evaluation](#34-modeling-and-evaluation)
- [4 Results](#4-results)
- [5 Discussion](#5-discussion)
- [6 Conclusion](#6-conclusion)

### Project tree

```plaintext
ML-4-B
├── data
│   ├── bahn_data
│   │   └── processed
│   ├── streamlit_data
│   └── weather_data
├── src
│   ├── data_processing
│   │   ├── transform_bahn.py
│   │   ├── transform_weather.py
│   │   └── map_weather.py
│   ├── exploration
│   │   ├── exploration.ipynb
│   │   ├── to_csv.py
│   │   └── weather_exploration.ipynb
│   ├── ml_models
│   │   ├── data_preparation.py
│   │   ├── train.py
│   │   └── predict.py
│   ├── streamlit
│   │   ├── calulcations
│   │   │   ├── overview.py 
│   │   │   └── direct_train.py
│   │   ├── pages
│   │   └── Home.py
│   ├── weatherdata
│   │   ├── data_scraping
│   │   │   ├── scrapedData
│   │   │   ├── json-schema.json
│   │   │   └── scraping.js
│   │   ├── stationsextraction
│   │   └── testing
│   └── process_data.py
├── requirements.txt
├── README.md
└── LICENSE
```

## 2 Related Work

- [David Kriesel](https://www.dkriesel.com/blog/2019/1229_video_und_folien_meines_36c3-vortrags_bahnmining)
- Projekt von [Theo Döllmann](https://gitlab.com/bahnvorhersage/bahnvorhersage)
- [Bahnvorhersagen.de](https://bahnvorhersage.de/blog)

## 3 Methodology

### 3.1 General Methodology

- Suche auf GitHub und GitLab nach bereits existierenden Projekten
- Theo Döllmann's Projekt angeschaut und nach Optimierungsmöglichkeiten gesucht --> Wetterdaten können auch Einfluss auf Verspätungen haben
- [Data Collection](#32-data-collection):
  - Wetterdaten über API
  - Bahndaten über GitHub
- [Data Understanding and Preparation](#33-data-understanding-and-preparation)
  - Explorative Datenanalyse (EDA) durchführen
  - Feature Engineering
  - Datenbereinigung und Normalisierung
  - Daten zusammenführen:
    - Wetterdaten und Bahndaten zusammenführen
    - Relevante Features auswählen
    - Zielvariable definieren (Verspätung)
    - Daten in Trainings- und Testset aufteilen
- [Modeling and Evaluation](#34-modeling-and-evaluation)
  - XGBoost Classifier:
    - Modellarchitektur beschreiben
    - Training der Modelle
    - Evaluation der Modelle und Metriken

### 3.2. Data Collection

#### Bahndaten

- Keine historischen Daten für Zugfahren über Deutsche Bahn API abrufbar
- Daten aus GitHub von [piebro](https://github.com/piebro/deutsche-bahn-data)
- Wetterdaten über API mit einem Call pro Bahnhof, stündliche Wetterdaten für große Fernverkehrsbahnhöfe

#### Wetterdaten

- Wetterdaten über [openweather API](https://openweathermap.org/history)
- Stündliche Wetterdaten für Fernverkehrsbahnhöfe in Deutschland
- API erlaubt es, Daten für das letzte Jahr abzurufen
- JavaScript für das Abrufen der Daten geschrieben

#### Donnerstag, 22.05.2025

- **Ziel:** Über eine API stündliche Wetterdaten aus der Vergangenheit für alle 107 Fernverkehrsbahnhöfe in Deutschland abrufen  
- Die API erlaubt es, genau 1 Jahr in die Vergangenheit zurückzugehen  
- Pro Anfrage erhalten wir 168 Datensätze = 7 Tage stündliche Wetterdaten  
- Um ein Jahr abzudecken: 52 Anfragen pro Bahnhof  
- Insgesamt: **5.564 API-Anfragen** (52 × 107)

#### So funktioniert der Code jetzt

- Holt für jeden Bahnhof Daten in 7-Tages-Schritten  
- Genau 168 Einträge pro Anfrage  
- Zuordnung der Bahnhöfe über `city_ID` gemäß API-Dokumentation  
- Pro Bahnhof werden die Daten separat gespeichert  
- Der Code merkt sich automatisch den letzten Stand und setzt dort bei erneutem Lauf fort  

#### (( Fehlerbehandlung

- Ursprünglich: Abbruch bei <168 Datensätzen → Annahme: keine Daten mehr verfügbar  
- Beobachtung: API liefert manchmal zu früh zu wenige Daten  
- Vermutung: verteilte Speicherung → einzelne Datenbanken liefern vorzeitig weniger zurück  
- Lösung: Der Code wartet nun gezielt auf eine **klare Fehlermeldung** der API, bevor er abbricht  
- Ziel: Sicherstellen, dass **alle** verfügbaren Daten abgeholt werden
))

### 3.3 Data Understanding and Preparation

- Bahn Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/exploration.ipynb)^
  - Informationen zu Zugfahrten, Verspätungen und Ausfällen pro Station einer Zugfahrt seit 2025
  - `Station, Zugnummer, Verspätung, Zugtyp, Zielbahnhof, Abfahrtszeit, Ausfall, Ankunftszeit`
  - ca. 3 Mio. Einträge
  - 107 Fernverkehrsbahnhöfe in Deutschland
- Wetter Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/weather_exploration.ipynb)
  - Stündliche Wetterdaten für Fernverkehrsbahnhöfe in Deutschland
  - `Zeitstempel, Wettertyp, Temperatur, Niederschlag, Windgeschwindigkeit, Luftfeuchtigkeit, Schneefall`
  - ca. 5.564 Einträge pro Bahnhof
  - Insgesamt 375.000 Zeilen
  - Daten von [openweather API](https://openweathermap.org/history)
- Data preparation:
  - Wetterdaten von JSON in DataFrame umwandeln
  - Bahndaten und Wetterdaten zusammenführen
  - Feature Engineering:
    - Wetterdaten in relevante Features umwandeln (z.B. Temperatur, Niederschlag)
    - Zeitstempel in Datetime-Format umwandeln
    - Fehlende Werte behandeln
    - Normalisierung der Daten
    - Weitere Spalten hinzufügen (Wochentag, Stunde)
    - Kategorische Variablen in numerische umwandeln
    - Unnötige Spalten entfernen (`train_line_ride_id`, `train_type`, `arrival_time`, `departure_time`)
    - Alle Fahrten die nicht ICE sind entfernen
  - Feature Selection:
    - Relevante Features auswählen (z.B. Temperatur, Niederschlag, Wochentag, Feiertag)
    - Zielvariable definieren (z.B. Verspätung, Ausfall)
  - Daten in Trainings- und Testset aufteilen

### 3.4 Modeling and Evaluation

- Describe the model architecture(s) you selected
- XGBoost Classifier
- Describe how you train your models
- Describe how you evaluate your models/ which metrics you use

## 4 Results

- Describe what artifacts you have build
- Describe the libraries and tools you use
- Describe the concept of your app
- Describe the results you achieve by applying your trained models on unseen data
- Descriptive Language (no judgement, no discussion in this section -> just show what you built)

## 5 Discussion

- Now its time to discuss your results/ artifacts/ app
- Show the limitations : e.g. missing data, limited training ressources/ GPU availability in Colab, limitaitons of the app
- Discuss your work from an ethics perspective:
- Dangers of the application of your work (for example discrimination through ML models)
- Transparency
- Effects on society and environment
- Possible sources <https://algorithmwatch.org/en/> Have a look at the "Automating Society Report"; <https://ainowinstitute.org/> Have a look at this website and their publications
- Further Research: What could be next steps for other researchers (specific research questions)

## 6 Conclusion

- Short summary of your findings and outlook
