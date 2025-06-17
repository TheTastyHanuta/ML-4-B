import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from pathlib import Path
from matplotlib.ticker import FuncFormatter

def percent_formatter(x, pos=None):
    return f"{int(x)}%"

# Bins & Labels
BINS = [-np.inf, 0, 5, 10, 15, 30, 60, np.inf]
LABELS = [
    "keine Verspätung",
    "0 - 5 min",
    "5 - 10 min",
    "10 - 15 min",
    "15 - 30 min",
    "30 - 60 min",
    "> 60 min",
]

def compute_all():
    data_dir = "../../../data/bahn_data"
    save_dir = "../../../data/streamlit_data"
    # Read parquet files
    data_dir = Path(data_dir)
    print(f"Reading data from {data_dir}")
    files = sorted(data_dir.glob("*.parquet"))
    df_list = [pd.read_parquet(fp)[["delay_in_min", "station", "is_canceled", "train_type"]] for fp in files]
    df = pd.concat(df_list, ignore_index=True)

    # Calculate statistics
    data_dict = {}
    delay_distributions = {}
    for t in ["all", "ICE", "IC", "RE", "RB", "S"]:
        df_t = df if t == "all" else df[df["train_type"] == t]
        name = "Alle" if t == "all" else t

        data_dict[f"ausgefallen_{t}"] = f"{int(df_t['is_canceled'].mean() * 100)}%"
        df_ok = df_t[~df_t["is_canceled"]]
        data_dict[f"summe_zughalte_{t}"] = len(df_ok)

        md = df_ok["delay_in_min"].mean()
        data_dict[f"durchschnittliche_verspaetung_{t}"] = (
            f"{int(md)}:{int((md - int(md)) * 60):02d}"
        )

        data_dict[f"puenktlich_{t}"] = f"{int((df_ok['delay_in_min'] < 6).mean() * 100)}%"

        hist = pd.cut(df_ok["delay_in_min"], bins=BINS, labels=LABELS)
        delay_distributions[name] = hist.value_counts(normalize=True) * 100

    # Save data_dict to JSON
    if save_dir is not None:
        save_dir = Path(save_dir)
        with open(save_dir / "data.json", "w") as f:
            json.dump(data_dict, f, indent=4)

    # Create bar chart
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(LABELS))
    bar_w = 0.15
    for i, name in enumerate(["Alle", "ICE", "IC", "RE", "RB", "S"]):
        ax1.bar(
            x + i * bar_w,
            delay_distributions[name].values,
            bar_w,
            label=name,
            alpha=0.8,
        )
    ax1.set_xlabel("Durchschnittliche Verspätung [Minuten]")
    ax1.set_ylabel("Prozent aller Züge [%]")
    ax1.set_title("Verteilung von Verspätungen nach Zuggattung")
    ax1.set_xticks(x + 2 * bar_w)
    ax1.set_xticklabels(LABELS, rotation=45, ha="right")
    #ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%")) for some reason this throws an error with caching
    ax1.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # save fig1 as PNG
    if save_dir is not None:
        fig1.savefig(save_dir / "delay_distribution.png", dpi=300, bbox_inches='tight')

    # Create cumulative distribution
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    for t in ["all", "ICE", "IC", "RE", "RB", "S"]:
        df_t = df if t == "all" else df[df["train_type"] == t]
        df_ok = df_t[~df_t["is_canceled"]]
        name = "Alle" if t == "all" else t

        counts = df_ok["delay_in_min"].value_counts().sort_index()
        cum = counts.cumsum() / len(df_ok) * 100
        ax2.plot(cum.index, cum.values, label=name)

    ax2.set_xlabel("Verspätung [Minuten]")
    ax2.set_ylabel("Kumulativer Anteil der Züge [%]")
    ax2.set_title("Kumulative Verteilung der Verspätungen nach Zuggattung")
    ax2.set_xlim(-5, 60)
    #ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%")) for some reason this throws an error with caching
    ax2.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    ax2.yaxis.set_major_locator(MultipleLocator(10))
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    # save fig2 as PNG
    if save_dir is not None:
        fig2.savefig(save_dir / "cumulative_distribution.png", dpi=300, bbox_inches='tight')

compute_all()