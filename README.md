# ML-4-B

## 1 Introduction
### Motivation
- Angebliche 72% Pünktlichkeit der ICEs
- Gefühl immer die falschen ICEs zu erwischen
- Gezielt Zugbindung aufheben (strategisch den falschen Zug buchen)
### Research question
- Lassen sich Verspätungen und Ausfälle der ICEs anhand von Daten über vergangene Zugfahrten und Wetterdaten vorhersagen?
### How is this document structured
### Project tree
```plaintext
ML-4-B
├── data
│   ├── bahn_data
│   ├── streamlit_data
│   └── weather_data
├── src
│   ├── exploration
│   │   ├── exploration.ipynb
│   │   └── weather_exploration.ipynb
│   ├── ml_models
│   │   ├── data_preparation.py
│   │   ├── train.py
│   │   └── xgboost_classifier.py
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
│   └── __init__.py
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
### 3.2. Data Collection
- Keine historischen Daten für Zugfahren über Deutsche Bahn API abrufbar
- Daten aus GitHub von [piebro](https://github.com/piebro/deutsche-bahn-data)
- Wetterdaten über API mit einem Call pro Bahnhof, stündliche Wetterdaten für große Fernverkehrsbahnhöfe

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

#### Fehlerbehandlung

- Ursprünglich: Abbruch bei <168 Datensätzen → Annahme: keine Daten mehr verfügbar  
- Beobachtung: API liefert manchmal zu früh zu wenige Daten  
- Vermutung: verteilte Speicherung → einzelne Datenbanken liefern vorzeitig weniger zurück  
- Lösung: Der Code wartet nun gezielt auf eine **klare Fehlermeldung** der API, bevor er abbricht  
- Ziel: Sicherstellen, dass **alle** verfügbaren Daten abgeholt werden

### 3.3 Data Understanding and Preparation
- Bahn Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/exploration.ipynb)
- Wetter Data exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration/exploration.ipynb)
- Data preparation:
    - Wetterdaten in DataFrame umwandeln
    - Bahndaten und Wetterdaten zusammenführen
    - Feature Engineering: 
        - Wetterdaten in relevante Features umwandeln (z.B. Temperatur, Niederschlag)
        - Zeitstempel in Datetime-Format umwandeln
        - Fehlende Werte behandeln
        - Normalisierung der Daten
        - Weitere Spalten hinzufügen (z.B. Wochentag, Feiertag)
        - Kategorische Variablen in numerische umwandeln
        - Unnötige Spalten entfernen (`train_line_ride_id`, `train_type`)
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
- Possible sources https://algorithmwatch.org/en/ Have a look at the "Automating Society Report"; https://ainowinstitute.org/ Have a look at this website and their publications
- Further Research: What could be next steps for other researchers (specific research questions)
## 6 Conclusion
- Short summary of your findings and outlook
