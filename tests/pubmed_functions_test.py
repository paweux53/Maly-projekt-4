import pytest
from src.PubMed.pubmed import extract_authors, strip_xml


def test_extract_authors():
    article = {
        "AuthorList": [
            {"LastName": "Kowalski", "ForeName": "Jan"},
            {"LastName": "Nowak", "ForeName": "Anna"},
        ]
    }

    result = extract_authors(article)

    assert result == "Jan Kowalski; Anna Nowak"


def test_extract_authors_empty():
    article = {"AuthorList": []}
    result = extract_authors(article)
    assert result == ""

def test_strip_xml():
    text = 'Effects of <math><mi>PM</mi><msub><mn>2.5</mn></msub></math>'
    assert strip_xml(text) == "Effects of PM2.5"

def test_strip_xml_none():
    text = 'Effects of PM2.5'
    assert strip_xml(text) == "Effects of PM2.5"






