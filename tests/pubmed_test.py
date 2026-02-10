import pandas as pd
from pathlib import Path
import tempfile
import os

def test_pubmed_determinism():
    # przykład: wczytaj istniejący CSV z wynikami
    csv_path = Path("results/literature/2024/pubmed_results.csv")
    
    if not csv_path.exists():
        # pomija jeśli nie ma danych
        import pytest
        pytest.skip("pubmed_results.csv nie istnieje")
    
    df = pd.read_csv(csv_path)
    
    # sprawdzenie podstawowej struktury
    assert "pmid" in df.columns, "Brakuje kolumny 'pmid'"
    assert "title" in df.columns, "Brakuje kolumny 'title'"
    assert "year" in df.columns, "Brakuje kolumny 'year'"
    assert "journal" in df.columns, "Brakuje kolumny 'journal'"
    
    # sprawdzenie, że rokiem jest 2024 
    assert (df["year"] == 2024).all(), "Wszystkie rekordy powinny mieć year=2024"
    
    # sprawdzenie: PMID powinny być unikalne (brak duplikatów z tego samego źródła)
    assert df["pmid"].is_unique, "PMID powinny być unikalne"
    
    # sprawdzenie: tytuły nie mogą być puste
    assert (df["title"].str.len() > 0).all(), "Tytuły nie mogą być puste"


def test_pubmed_aggregations():
    
    journals_path = Path("results/literature/2024/top_journals.csv")
    summary_path = Path("results/literature/2024/summary_by_year.csv")
    
    if not journals_path.exists() or not summary_path.exists():
        import pytest
        pytest.skip("Agregatowe pliki nie istnieją")
    
    journals_df = pd.read_csv(journals_path, index_col=0)
    summary_df = pd.read_csv(summary_path, index_col=0)
    
    # top_journals ma kolumnę 'count'
    assert "count" in journals_df.columns, "top_journals.csv musi mieć kolumnę 'count'"
    assert len(journals_df) <= 10, "top_journals musi mieć max 10 wierszy"
    
    # summary_by_year ma 'count'
    assert "count" in summary_df.columns, "summary_by_year.csv musi mieć kolumnę 'count'"
    assert summary_df["count"].sum() > 0, "Suma publikacji powinna być > 0"
