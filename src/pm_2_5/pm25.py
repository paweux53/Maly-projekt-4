# importy

from html import parser
from projekt_3.DownloadClean import *
from projekt_3.Analysis import *
from projekt_3.Visualization import *

from pathlib import Path
import yaml
import argparse

# kontrola struktury katalogów
ROOT_DIR = Path(__file__).resolve().parents[2] 

def main():

    # parsowanie argumentów
    parser = argparse.ArgumentParser(description='Analiza danych PM2.5')

    parser.add_argument("--config", type=str, default="config/task4.yaml",
                         help="Ścieżka do pliku konfiguracyjnego YAML") 

    parser.add_argument('--years' , type=int, nargs='+',
                         help='Lata do analizy danych PM2.5 (np. --years 2021 2024)')

    args = parser.parse_args()  

    # wczytanie yaml
    config_path = ROOT_DIR / args.config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # określenie Zmiennych globalnych
    CITIES = config['cities']
    YEARS = args.years 

    # określenie katalogów
    results = ROOT_DIR / 'results' / 'PM_2.5' / str(YEARS)
    results.mkdir(parents=True, exist_ok=True)

    data = results / 'data'
    data.mkdir(parents=True, exist_ok=True)

    plots = results / 'plots'
    plots.mkdir(parents=True, exist_ok=True)

    # pobieranie danych + czyszczenie + mapowanie
    df = prepare_common_data(YEARS)

    # analiza danych i zapis do csv

    df_monthly_mean = monthly_mean(df, YEARS)
    df_monthly_mean.to_csv(data / 'pm25_monthly_mean.csv')

    df_daily_mean = daily_mean(df)
    df_daily_mean.to_csv(data / 'pm25_daily_mean.csv')

    df_days_above_norm = days_above_norm(df)
    df_days_above_norm.to_csv(data / 'pm25_days_above_norm.csv')

    # wizualizacja danych i zapis wykresów do png
    
    mean_pm25_plot = mean_pm25_plot(df_monthly_mean, YEARS)
    mean_pm25_plot.savefig(plots / 'pm25_mean_pm25_plot.png')

    heatmap = heatmap(df_monthly_mean, YEARS)
    heatmap.savefig(plots / 'pm25_heatmap.png')

    grouped_barplot = grouped_barplot(df_days_above_norm)
    grouped_barplot.savefig(plots / 'pm25_grouped_barplot.png')












