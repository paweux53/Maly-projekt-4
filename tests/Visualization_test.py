import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import math
import seaborn as sns

import pandas as pd

import pytest

from src.pm_2_5.projekt_3.Visualization import *

def test_mean_pm25_plot_returns_figure(monkeypatch): # test dla funkcji mean_pm25_plot

    idx = pd.MultiIndex.from_product(
        [[2015, 2024], range(1, 13)],
        names=["Rok", "Miesiąc"]
    )

    cols = pd.MultiIndex.from_tuples(
        [("S1", "Warszawa"), ("S2", "Katowice")],
        names=["Kod stacji", "Miejscowość"]
    )

    df = pd.DataFrame(10, index=idx, columns=cols)

    result = mean_pm25_plot(df, years=[2015, 2024])

    assert isinstance(result, plt.Figure), "mean_pm25_plot musi zwrócić matplotlib.pyplot.Figure"
    plt.close(result)

def test_heatmap_returns_figure(monkeypatch): # test dla funkcji heatmap

    idx = pd.MultiIndex.from_product(
        [[2015, 2018], range(1, 13)],
        names=["Rok", "Miesiąc"]
    )

    cols = pd.MultiIndex.from_tuples(
        [("S1", "Warszawa"), ("S2", "Kraków")],
        names=["Kod stacji", "Miejscowość"]
    )

    df = pd.DataFrame(25, index=idx, columns=cols)

    result = heatmap(df, years=[2015, 2018])

    assert isinstance(result, plt.Figure), "heatmap musi zwrócić matplotlib.pyplot.Figure"
    plt.close(result)

def test_grouped_barplot_returns_figure(monkeypatch): # test dla funkcji grouped_barplot

    idx = pd.Index([2015, 2024], name="Rok")

    cols = pd.MultiIndex.from_tuples(
        [("S1", "Warszawa"), ("S2", "Kraków"), ("S3", "Katowice"),
         ("S4", "Gdańsk"), ("S5", "Wrocław"), ("S6", "Poznań")],
        names=["Kod stacji", "Miejscowość"]
    )

    df = pd.DataFrame(
        [[5,10,15,20,25,30], [6,11,16,21,26,31]],
        index=idx,
        columns=cols
    )

    result = grouped_barplot(df)

    assert isinstance(result, plt.Figure), "grouped_barplot musi zwrócić matplotlib.pyplot.Figure"
    plt.close(result)