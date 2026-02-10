# importy

import argparse
import yaml
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# kontrola struktury katalogów
ROOT = Path(__file__).resolve().parents[2]


def safe_read_csv(path):
    # czytuje CSV bez podnoszenia wyjątku.
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def main():

    # parsowanie argumentów wejściowych
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML config (relative to project root)",
    )
    args = parser.parse_args()

    # wczytanie konfiguracji (ścieżka względem ROOT)
    with open(ROOT / args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    years = cfg.get("years", [])

    # przygotowanie katalogu wyników
    output_dir = ROOT / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # budowa treści raportu (lista linii)
    lines = []
    lines.append(f"# Raport PM2.5 i analiza literatury dla lat {', '.join(map(str, years))}\n\n")
    lines.append("Raport wygenerowany automatycznie.\n\n")

    # dni z przekroczeniem PM2.5
    lines.append("## Dni z przekroczeniem PM2.5\n\n")
    lines.append("| Rok | Miasto | Dni |\n")
    lines.append("|-----|--------|-----|\n")
    for year in years:
        path = ROOT / "results" / "pm25" / str(year) / "data" / "exceedance_days.csv"
        df = safe_read_csv(path)
        if df is None or df.empty:
            continue
        sample = df.sample(n=min(15, len(df)), random_state=42)
        for _, row in sample.iterrows():
            # próbujemy różne klucze/być odporni na formaty
            city = row.get('City') if isinstance(row, dict) else (row.get('city') if 'city' in row else None)
            if city is None:
                # fallback: spróbuj kolumny 'Miejscowość' lub pierwszy element
                city = row.get('Miejscowość', None) if isinstance(row, dict) else (row.get('Miejscowość', '-') if 'Miejscowość' in row else '-')
            # liczba dni - różne możliwe nazwy
            days = None
            for key in ['count', 'value', str(year), 'days', 'days_exceeded']:
                days = row.get(key, None) if isinstance(row, dict) else (row.get(key) if key in row else None)
                if days is not None:
                    break
            if days is None:
                # jako ostateczność pobierz pierwszy element wartości
                vals = list(row.values()) if hasattr(row, "values") else []
                days = vals[0] if vals else '-'
            lines.append(f"| {year} | {city or '-'} | {days} |\n")

    # liczba publikacji (podsumowanie roczne)
    lines.append("\n## Liczba publikacji\n\n")
    lines.append("| Rok | Liczba publikacji |\n")
    lines.append("|-----|-------------------|\n")
    yearly_data = []
    for year in years:
        path = ROOT / "results" / "literature" / str(year) / "summary_by_year.csv"
        df = safe_read_csv(path)
        if df is None:
            continue
        for _, row in df.iterrows():
            lines.append(f"| {int(row.get('year', year))} | {int(row.get('count',0))} |\n")
            yearly_data.append({"year": int(row.get("year", year)), "count": int(row.get("count", 0))})

    # tp 10 czasopism dla każdego roku
    lines.append("\n## Top 10 czasopism\n\n")
    for year in years:
        path = ROOT / "results" / "literature" / str(year) / "top_journals.csv"
        top = safe_read_csv(path)
        if top is None or top.empty:
            continue
        lines.append(f"**Rok {year}**\n\n")
        lines.append("| Czasopismo | Liczba publikacji |\n")
        lines.append("|------------|-------------------|\n")
        for _, row in top.iterrows():
            lines.append(f"| {row.get('journal','-')} | {int(row.get('count',0))} |\n")

    # trend publikacji (wykres)
    if yearly_data:
        yearly_df = pd.DataFrame(yearly_data).drop_duplicates().sort_values("year")
        plt.figure(figsize=(8,5))
        plt.plot(yearly_df["year"], yearly_df["count"], marker="o")
        plt.xlabel("Rok")
        plt.ylabel("Liczba publikacji")
        plt.grid(True)
        plt.savefig(output_dir / "publication_trends.png")
        plt.close()
        lines.append("\n## Trendy w publikacjach\n\n")
        lines.append("![Trendy publikacji](publication_trends.png)\n")

    # przykładowe publikacje (pierwsze 5)
    lines.append("\n## Przykładowe publikacje\n\n")
    for year in years:
        path = ROOT / "results" / "literature" / str(year) / "pubmed_results.csv"
        papers = safe_read_csv(path)
        if papers is None or papers.empty:
            continue
        lines.append(f"**Rok {year}**\n\n")
        for _, row in papers.head(5).iterrows():
            lines.append(f"- {row.get('title','-')} ({row.get('journal','-')})\n")

    # zapis raportu do pliku markdown
    with open(output_dir / "report_task4.md", "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()