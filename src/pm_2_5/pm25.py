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

    # parsowanie argumentów wejściowych
    parser = argparse.ArgumentParser(description='Analiza danych PM2.5')
    parser.add_argument("--config", type=str, default="config/task4.yaml",
                         help="Ścieżka do pliku konfiguracyjnego YAML") 
    parser.add_argument('--year' , type=int, help='Rok do analizy danych PM2.5 (np. --year 2024)')

    args = parser.parse_args()  

    # wczytanie yaml
    config_path = ROOT_DIR / args.config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    YEAR = args.year
    if YEAR is None:
        raise SystemExit("Provide --year YEAR")

    # katalogi wynikowe per-year
    results = ROOT_DIR / 'results' / 'pm25' / str(YEAR)
    data_dir = results / 'data'
    plots_dir = results / 'figures'
    data_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # pobieranie danych + czyszczenie + mapowanie dla pojedynczego roku
    df = prepare_common_data([YEAR])

    # analiza danych i zapis do csv
    df_monthly_mean = monthly_mean(df, [YEAR])
    df_monthly_mean.to_csv(data_dir / 'monthly_means.csv')

    df_daily_mean = daily_mean(df)
    df_daily_mean.to_csv(data_dir / 'daily_means.csv')

    df_days_above_norm = days_above_norm(df)
    df_days_above_norm.to_csv(data_dir / 'exceedance_days.csv')

    # wizualizacje -> funkcje teraz zwracają fig
    fig1 = mean_pm25_plot(df_monthly_mean, [YEAR])
    fig1.savefig(plots_dir / 'pm25_mean_plot.png')
    fig1.clf()

    fig2 = heatmap(df_monthly_mean, [YEAR])
    fig2.savefig(plots_dir / 'pm25_heatmap.png')
    fig2.clf()

    fig3 = grouped_barplot(df_days_above_norm)
    fig3.savefig(plots_dir / 'pm25_grouped_barplot.png')
    fig3.clf()


if __name__ == "__main__":
    main()












