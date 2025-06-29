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
- Run the `src/init.py` file to transform the data and train all models

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
├── models
├── src
│   ├── data_processing
│   │   ├── transform_bahn.py
│   │   ├── transform_weather.py
│   │   ├── map_weather.py
│   │   └── process_data.py
│   ├── exploration
│   │   ├── exploration.ipynb
│   │   ├── to_csv.py
│   │   └── weather_exploration.ipynb
│   ├── ml_models
│   │   ├── predict.py
│   │   ├── preprocessing.py
│   │   ├── train_lightgbm.py
│   │   ├── train_lightgbm_without.py
│   │   ├── train_xgboost.py
│   │   └── train_xgboost_without.py
│   ├── streamlit
│   │   ├── calulcations
│   │   │   ├── direct_helper.py
│   │   │   ├── direct_trains.py
│   │   │   ├── overview.py 
│   │   │   ├── predict_helper.py
│   │   │   └── worst_stations.py
│   │   ├── pages
│   │   └── main.py
│   ├── weatherdata
│   │   ├── data_scraping
│   │   │   ├── scrapedData
│   │   │   ├── json-schema.json
│   │   │   └── scraping.js
│   │   └── stationsextraction
│   └── init.py
├── requirements.txt
├── README.md
└── LICENSE
```

## 2 Related Work

- Vortrag von [David Kriesel](https://www.dkriesel.com/blog/2019/1229_video_und_folien_meines_36c3-vortrags_bahnmining)
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
  - LightGBM Classifier:
    - Modellarchitektur beschreiben
    - Training der Modelle
    - Evaluation der Modelle und Metriken

### 3.2. Data Collection

#### Bahndaten

- Keine historischen Daten für Zugfahren über Deutsche Bahn API abrufbar
- Daten aus GitHub von [piebro](https://github.com/piebro/deutsche-bahn-data)

#### Wetterdaten

- Wetterdaten über [openweather API](https://openweathermap.org/history)
- Stündliche Wetterdaten für Fernverkehrsbahnhöfe in Deutschland
- API erlaubt es, Daten für das letzte Jahr abzurufen
- JavaScript für das Abrufen der Daten 

### 3.3 Data Understanding and Preparation

- Bahn Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/exploration.ipynb)
  - Informationen jeder Station einer Zugfahrt mit Informationen über die Zugfahrt an dieser Station
  - `Station, Zugnummer, Verspätung, Zugtyp, Zielbahnhof, Abfahrtszeit, Ausfall, Ankunftszeit`
  - ca. 4 Mio. Einträge
  - 107 Fernverkehrsbahnhöfe in Deutschland
- Wetter Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/weather_exploration.ipynb)
  - Stündliche Wetterdaten für Fernverkehrsbahnhöfe in Deutschland
  - `Zeitstempel, Wettertyp, Temperatur, Niederschlag, Windgeschwindigkeit, Luftfeuchtigkeit, Schneefall`
  - ca. 5.564 Einträge pro Bahnhof
  - Insgesamt 375.000 Zeilen
- Data preparation:
  - Wetterdaten von JSON in DataFrame umwandeln
    - Wetterdaten in relevante Features umwandeln (Temperatur, Niederschlag, usw.)
  - Bahndaten transformieren, sodass jede Zeile eine Zugfahrt repräsentiert
    - `ride_id, train_name, station, destination_station, departure_time_origin, day_of_week, hour_of_day, delay_at_destination, canceled, time, weather...`
  - Bahndaten und Wetterdaten zusammenführen in einen DataFrame
  - Feature Engineering:
    - Zeitstempel in Datetime-Format umwandeln
    - Zeilen mit wichtigen fehlenden Werten entfernen
    - Weitere Spalten hinzufügen (Wochentag, Stunde)
    - Unnötige Spalten entfernen (`train_line_ride_id`, `train_type`)
    - Alle Fahrten die nicht ICE oder IC sind entfernen
    - Zielvariable definieren (Verspätung, Ausfall)
  - Daten in Trainings- und Testset aufteilen

### 3.4 Modeling and Evaluation

- XGBoost & LightGBM für Regression und Classification
- Features: 
  - Training mit allen Features: `start_station, end_station, train_name, hour, day_of_week, month, temperature, precipitation, wind_speed, humidity, snow, (delay_minutes)`
  - Training ohne Wetterdaten: `start_station, end_station, train_name, hour, day_of_week, month, (delay_minutes)`
- XGBoost:
  - Training der Modelle auf Trainingsset
  - Evaluation der Modelle auf Testset
- LightGBM:
  - Training der Modelle auf Trainingsset
  - Evaluation der Modelle auf Testset
  - Metriken: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), R² Score für Verspätung und Accuracy, Precision, Recall, F1 Score für Ausfälle
- Hyperparameter Tuning:
  - Grid Search und Random Search für die Optimierung der Hyperparameter (ToDo: noch besser implementieren)

## 4 Results

- Artifacts:
  - Jupyter Notebooks für die Datenexploration
  - Python-Skripte für die Datenverarbeitung und Modelltraining
  - Streamlit App zur Visualisierung der Vorhersagen
  - Trainierte Modelle für die Vorhersage von Verspätungen und Ausfällen
- Libraries:
  - XGBoost und LightGBM für die Modellierung
  - Pandas und NumPy für die Datenverarbeitung
  - Streamlit für die Web-App
- Konzept: 
  - Vorhersage von Verspätungen und Ausfällen von ICEs basierend auf historischen Zugfahrten und Wetterdaten
  - Angabe von Start- und Zielbahnhof, Zugnummer, Datum --> Vorhersage der Verspätung und Ausfallwahrscheinlichkeit
- Ergebnisse:
  - Modelle können Ausfälle mit einer Genauigkeit von ca. 70% vorhersagen
  - Verspätungen können mit einer Genauigkeit von ca. 10 Minuten vorhergesagt werden (Still works in progress)
  - LightGBM genauer als XGBoost
  - Wetterdaten haben einen Einfluss auf die Pünktlichkeit der Züge
  - Modelle können weiter verbessert werden durch:
    - Bessere Datenqualität (mehr historische Daten)
    - Hyperparameter Tuning
- Descriptive Language
  - Die Modelle sind in der Lage, die Pünktlichkeit von ICEs zu prognostizieren, indem sie historische Zugfahrten und Wetterdaten analysieren.
  - Die Genauigkeit der Vorhersagen variiert je nach Modell und Feature-Auswahl.
  - Die Ergebnisse zeigen, dass Wetterbedingungen einen signifikanten Einfluss auf die Pünktlichkeit der Züge haben.
  - Die entwickelten Modelle können als Grundlage für weitere Forschungen und Anwendungen dienen.
  - Die Vorhersagen können Bahnreisenden helfen, ihre Reisen besser zu planen und mögliche Verspätungen zu vermeiden.
  - Die Web-App ermöglicht es Nutzern, die Vorhersagen einfach und intuitiv abzurufen.
  - Die bereitgestellten Daten und Modelle können von der Community genutzt und weiterentwickelt werden.
  - Die Ergebnisse und Modelle sind nicht perfekt und können weiter verbessert werden, insbesondere durch die Integration weiterer Datenquellen und die Optimierung der Hyperparameter.
  - Die Vorhersagen sind als Hilfestellung gedacht und sollten nicht als 100% zuverlässig angesehen werden.
  - Die Modelle sind ein erster Schritt in Richtung einer besseren Planung von Bahnreisen und können in Zukunft weiter verfeinert werden.
  - Die Ergebnisse zeigen, dass es möglich ist, Verspätungen und Ausfälle von ICEs vorherzusagen, jedoch sind die Modelle noch nicht perfekt und benötigen weitere Optimierung.

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
