
# importy

import argparse
import re
import yaml
from Bio import Entrez
import pandas as pd
from pathlib import Path

# kontrola struktury katalogów
ROOT_DIR = Path(__file__).resolve().parents[2]


# funkcje pomocnicze 

def extract_authors(article):
    # Ekstrakcja listy autorów z obiektu artykułu PubMed.
    authors = []
    for author in article.get("AuthorList", []):
        last = author.get("LastName")
        fore = author.get("ForeName")
        if last and fore:
            authors.append(f"{fore} {last}")
    return "; ".join(authors)


def strip_xml(text):
    # Usuwa tagi XML/HTML z pola tekstowego 
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", text)


# główna logika programu 
def main():

    # parsowanie argumentów wejściowych
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    # wczytanie pliku konfiguracyjnego 
    config_path = ROOT_DIR / args.config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    year = args.year

    # ustawienie adresu email dla Entrez (wymagane przez NCBI)
    Entrez.email = config["pubmed"]["email"]

    # katalog wyjściowy dla wyników
    output_dir = ROOT_DIR / "results" / "literature" / str(year)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []

    # wykonaj zapytania z konfiguracji i pobierz metadane
    for query in config["pubmed"]["queries"]:
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            mindate=str(year),
            maxdate=str(year),
            datetype="pdat",
            retmax=config["pubmed"].get("max_results", 100),
        )

        result = Entrez.read(handle)
        ids = result.get("IdList", [])

        if not ids:
            continue

        fetch = Entrez.efetch(
            db="pubmed",
            id=",".join(ids),
            rettype="xml",
            retmode="xml",
        )
        papers = Entrez.read(fetch)

        # iteracja po artykułach i budowa rekordów
        for p in papers.get("PubmedArticle", []):
            citation = p["MedlineCitation"]
            article = citation["Article"]
            records.append(
                {
                    "pmid": str(citation["PMID"]),
                    "title": strip_xml(article.get("ArticleTitle", "")),
                    "year": year,
                    "journal": article["Journal"]["Title"],
                    "authors": extract_authors(article),
                }
            )

    # zapis wyników do ramki danych + pliki CSV
    df = pd.DataFrame(records)
    df.to_csv(output_dir / "pubmed_results.csv", index=False)

    # top 10 czasopism
    top_journals = df.groupby("journal").size().sort_values(ascending=False).head(10)
    top_journals = top_journals.to_frame()
    top_journals.rename(columns={0: "count"}, inplace=True)
    top_journals.to_csv(output_dir / "top_journals.csv")

    # podsumowanie wg roku
    yearly = df.groupby("year").size()
    yearly = yearly.to_frame()
    yearly.rename(columns={0: "count"}, inplace=True)
    yearly.to_csv(output_dir / "summary_by_year.csv")


if __name__ == "__main__":
    main()