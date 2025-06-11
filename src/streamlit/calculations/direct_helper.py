import json
from pathlib import Path
import pandas as pd

FERN_PREFIXES = ["ICE", "IC", "FLX", "NJ", "EC", "HEX", "ES"]
NAH_PREFIXES  = ["S", "RE", "RB"]

base_dir = Path(__file__).parent.parent.parent.parent
data_dir = base_dir / "data" / "streamlit_data"

# Load all direct routes from JSON file
def load_overview(json_path: str = data_dir / "direct_train_overview") -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

# Load route DataFrame from JSON file for specific start and end stations
def load_route_df(
    start: str,
    end: str,
    overview: dict,
    data_dir: str = data_dir / "direct_trains"
) -> pd.DataFrame:
    filename = overview[start][end]
    path = Path(data_dir) / filename
    return pd.read_json(path, orient="records")

# Filter routes based on train type and sample size
def filter_routes(
    df: pd.DataFrame,
    fern: bool = True,
    nah: bool = True,
    min_samples: bool = True,
    sample_threshold: int = 20
) -> pd.DataFrame:
    df2 = df.copy()
    if not fern:
        df2 = df2[~df2["Zug"].str.startswith(tuple(FERN_PREFIXES))]
    if not nah:
        df2 = df2[~df2["Zug"].str.startswith(tuple(NAH_PREFIXES))]
    if min_samples:
        df2 = df2[df2["Stichprobengröße"] >= sample_threshold]
    return df2