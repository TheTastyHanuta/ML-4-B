# ML-4-B

## 1 Introduction
### Motivation
- Angebliche 72% Pünktlichkeit der ICEs
- Gefühl immer die falschen ICEs zu erwischen
- Gezielt Zugbindung aufheben (strategisch den falschen Zug buchen)
### Research question
- Lassen sich Verspätungen und Ausfälle der ICEs anhand von Daten über vergangene Zugfahrten und Wetterdaten vorhersagen?
### How is this document structured
## 2 Related Work
- [David Kriesel](https://www.dkriesel.com/blog/2019/1229_video_und_folien_meines_36c3-vortrags_bahnmining)
- Projekt von [Theo Döllmann](https://gitlab.com/bahnvorhersage/bahnvorhersage)
- [Bahnvorhersagen.de](https://bahnvorhersage.de/blog)
## 3 Methodology
### 3.1 General Methodology
- Suche auf GitHub und GitLab nach bereits existierenden Projekten
### 3.2. Data Collection
- Keine Historischen Daten für Zugfahren über Deutsche Bahn API abrufbar
- Daten aus GitHub von [piebro](https://github.com/piebro/deutsche-bahn-data)
- Wetterdaten über API mit einem Call pro Bahnhof, stündliche Wetterdaten für große Fernverkehrsbahnhöfe
### 3.3 Data Understanding and Preparation
- Date exploration über [Jupyter Notebook](https://github.com/TheTastyHanuta/ML-4-B/blob/main/src/exploration.ipynb)
### 3.4 Modeling and Evaluation
- Describe the model architecture(s) you selected
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
