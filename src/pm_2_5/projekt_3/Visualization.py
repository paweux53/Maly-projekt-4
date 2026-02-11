import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import math
import seaborn as sns
import pandas as pd

def mean_pm25_plot(df, years):
    # Wybieram odpowiednie miasta
    df_waw = df.xs('Warszawa', level='Miejscowość', axis=1)
    df_kat = df.xs('Katowice', level='Miejscowość', axis=1)
    
    df_waw_mean = df_waw.mean(axis=1)
    df_kat_mean = df_kat.mean(axis=1)

    # Filter available years from the data
    available_years = sorted(df_waw_mean.index.get_level_values('Rok').unique())
    years_to_plot = [y for y in years if y in available_years]
    
    if not years_to_plot:
        raise ValueError(f"No requested years {years} found in data. Available: {available_years}")
    
    fig = plt.figure(figsize=(10,6))
    ax = fig.gca()
    
    for year in years_to_plot:
        waw_data = df_waw_mean.xs(year, level='Rok')
        kat_data = df_kat_mean.xs(year, level='Rok')
        
        ax.plot(waw_data.index, waw_data.values, label=f"Warszawa {year}", marker='o')
        ax.plot(kat_data.index, kat_data.values, label=f"Katowice {year}", marker='s')
    
    ax.set_xlabel("Miesiąc", fontsize=14)
    ax.set_ylabel("Średnie PM2.5", fontsize=14)
    ax.set_title("Trend miesięcznych stężeń PM2.5 (Warszawa vs Katowice)", fontsize=18)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xticks(range(1, 13))
    fig.tight_layout()
    return fig


def heatmap(df, years):
    # grupowanie po mieście 
    matrix_dict = {}
    
    # Iteruj po miastach w DataFrame
    for city in df.columns.get_level_values('Miejscowość').unique():
        df_city = df.xs(city, level='Miejscowość', axis=1)
        
        # Unstack to create Year x Month matrix
        matrix = df_city.unstack(level='Miesiąc')
        
        # Flatten MultiIndex columns to single level
        if isinstance(matrix.columns, pd.MultiIndex):
            matrix.columns = matrix.columns.get_level_values(-1)
        
        # Remove duplicate columns by keeping only unique months
        matrix = matrix.loc[:, ~matrix.columns.duplicated(keep='first')]
        
        available_years = sorted(matrix.index.unique())
        years_to_plot = [y for y in years if y in available_years]
        
        if years_to_plot:
            # Reindex rows only, keep existing columns
            matrix = matrix.reindex(index=years_to_plot)
            matrix_dict[city] = matrix
    
    # ustalenie globalnego maksima i minima
    global_min = df.min().min()
    global_max = df.max().max()
    
    # Custom mapa kolorów 
    custom_cmap = LinearSegmentedColormap.from_list(
        "PM2.5",
        [
            (0.0,  "green"),
            (0.15, "yellow"),
            (0.25, "orange"),
            (0.40, "red"),
            (0.60, "black"),
            (1.00, "purple"),
        ]
    )
    
    cities = list(matrix_dict.keys())
    n_cities = len(cities)
    
    # układ siatki
    ncols = 5
    nrows = math.ceil(n_cities / ncols)
    
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(15, 9),
        constrained_layout=True
    )
    axes = axes.flatten()
    
    for i, city in enumerate(cities):
        ax = axes[i]
        im = ax.imshow(
            matrix_dict[city],
            aspect='auto',
            cmap=custom_cmap,
            vmin=global_min,
            vmax=global_max
        )

        # upewnienie się że oś x i y będzie wyglądać odpowiednio
        ax.set_title(city, fontsize=10)
        ax.set_xticks(range(12))
        ax.set_xticklabels(range(1, 13), fontsize=8)
        available_years = sorted(matrix_dict[city].index.unique())
        ax.set_yticks(range(len(available_years)))
        ax.set_yticklabels(available_years, fontsize=8)

        # Podpisanie osi wykresu 
        ax.set_xlabel("Miesiąc", fontsize=8)
        ax.set_ylabel("Rok", fontsize=8)
    
    # usunięcie pustych paneli (jeśli < 20 miast)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    # wspólna colorbar
    cbar = fig.colorbar(
        im,
        ax=axes,
        orientation="vertical",
        fraction=0.02,
        pad=0.02
    )
    cbar.set_label("PM2.5 [µg/m³]")
    
    # nazwanie wykresu
    fig.suptitle(
        "Średnie miesięczne stężenia PM2.5 w miastach (2015, 2018, 2021, 2024)",
        fontsize=16
    )
    return fig


def grouped_barplot(df):
    # Get available years dynamically
    available_years = sorted(df.index.unique())
    if not available_years:
        raise ValueError("No data available in dataframe")
    
    # Use the latest available year instead of hardcoded 2024
    year_to_plot = available_years[-1]
    df_year = df.loc[year_to_plot]
    
    # 3 stacje z najmniejszą liczbą dni
    bottom3 = df_year.nsmallest(3)
    
    # 3 stacje z największą liczbą dni
    top3 = df_year.nlargest(3)
    
    # Lista interesujących stacji
    stations_of_interest = bottom3.index.tolist() + top3.index.tolist()
    
    # Wybieramy tylko interesujące stacje 
    df_plot = df[stations_of_interest]
    
    df_plot_flat = df_plot.copy()
    df_plot_flat.columns = [f"{kod}_{miasto}" for kod, miasto in df_plot_flat.columns]
    
    df_plot_reset = df_plot_flat.reset_index()  # teraz 'Rok' jest kolumną
    
    # Przekształcenie formatu
    df_plot_long = df_plot_reset.melt(id_vars='Rok', var_name='station', value_name='days_exceeded')

    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(10,6))
    ax = fig.gca()
    
    sns.barplot(data=df_plot_long, x='station', y='days_exceeded', hue='Rok', ax=ax)
    
    ax.set_xlabel('Station')
    ax.set_ylabel('Number of days exceeded')
    ax.set_title('Dni przekraczające normę dzienną według stacji i roku')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Year')
    
    fig.tight_layout()
    return fig
