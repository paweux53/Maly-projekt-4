# Projekt 4 

## Opis projektu
Projekt implementuje pipeline w narzędziu **Snakemake**, który integruje dane środowiskowe o stężeniach pyłów PM2.5 z analizą literatury naukowej pobieranej z bazy PubMed.
System automatyzuje proces od pobierania danych, przez transformację (w tym obsługę specyficznych formatów CSV), aż po generowanie zbiorczego raportu Markdown.

## Konfiguracja

Pipeline jest sterowany za pomocą pliku config w, którym są zdefiniowane :
 - lata dla których ma być wykonywana analiza [years],
 - miasta dla których mają być tworzone wykresy [cities],
 - kwestia normalizacji oraz norma dla PM2.5 [pm25],
 - e-mail oraz słowa klucz do wyszukiwania [pubmed]

bazowy config:
```yaml
# lata 
years: [2021, 2024]

# miasta
cities: ['Warszawa', 'Katowice']

# ustawienia dla PM2.5
pm25:

  # normalizacja danych
  normalize: false

  # próg alarmowy dla PM2.5
  threshold: 25

# ustawienia dla PubMed
pubmed:

  # dane wyganae do ściągnięcia danych z PubMed
  email: 'pg459392@students.mimuw.edu.pl'

  # zapytania do PubMed
  queries:

    - 'PM2.5 AND Poland'

    - 'PM2.5 health'

    - 'PM2.5 respiratory diseases'
```
## Struktura wyników 

### PM2.5
```bash
results/pm25/{Year}/
└── data/
    ├── daily_means
    ├── exceedance_days
    └── monthly_means
└── figures/
    ├── pm25_grouped_barplot
    ├── pm25_heatmap
    └── pm25_mean_plot
```
### Literatura
```bash
results/literature/{Year}/
├── pubmed_results
├── summary_by_year
└── top_journals
```
### Raport 
```bash
results/
├── publication_trends.png
└── report_task4.md
```

## Przebieg pipeline'u i kwestia incrementalności

### Należy spojrzeć w generowany automatycznie log znajdujący się w .snakemake.

Jeżeli dla lat 2021 i 2024 odpalimy po raz pierwszy nasz program to w logach zobaczymy na początku np.

```console
job             count
------------  -------
all                 1
pm25_year           2
pubmed_year         2
report_task4        1
total               6
```

Należy zauważyć, że dla pm25_year i pubmed_year nasz skrypt uruchamiany był 2 razy, czyli policzył wymagane wartości.
Kiedy podamy natomiast zestaw lat gdzie jeden rok był już policzony (np: 2019, 2024) to zobaczymy coś takiego:

```console
job             count
------------  -------
all                 1
pm25_year           1
pubmed_year         1
report_task4        1
total               4
```
Czyli skrypt uruchomił się tylko raz - dla nowego niezdefiniowanego wcześniej roku.

