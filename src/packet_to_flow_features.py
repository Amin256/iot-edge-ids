# Script to convert packet-level features to flow-level features.
from __future__ import annotations

from pathlib import Path
import pandas as pd

# Reads the packet-level features CSV and turns them into flow-level features.
def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    in_csv = repo_root /"data"/"processed"/"normal_traffic_01_packet_features.csv"
    out_csv = repo_root /"data"/"processed"/"normal_traffic_01_flow_features.csv"

    if not in_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_csv}")

    df = pd.read_csv(in_csv)

    # Ensure numeric timestamp
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors = "coerce")
    df = df.dropna(subset = ["timestamp"])
    # Define a time window (60 seconds) to group packets into flows
    WINDOW_S = 60

    df["time_bin"] = (df["timestamp"] // WINDOW_S).astype(int)

    group_cols = ["src_ip", "dst_ip", "protocol", "time_bin"]
    # Aggregate packet features into flow features
    agg = df.groupby(group_cols).agg(
        start_time = ("timestamp", "min"),
        end_time = ("timestamp", "max"),
        packet_count = ("packet_length", "size"),
        total_bytes = ("packet_length", "sum"),
        mean_pkt_len = ("packet_length", "mean"),
        std_pkt_len = ("packet_length", "std"),
        min_pkt_len = ("packet_length", "min"),
        max_pkt_len = ("packet_length", "max"),
    ).reset_index()

    # Calculate flow duration and rates, handling zero-duration flows to avoid division by zero
    agg["duration_s"] = (agg["end_time"] - agg["start_time"]).clip(lower = 0.0)
    agg["packets_per_s"] = agg["packet_count"] / agg["duration_s"].replace(0.0, 1.0)
    agg["bytes_per_s"] = agg["total_bytes"] / agg["duration_s"].replace(0.0, 1.0)

    # Fill NaN values in std_pkt_len with 0.0 (occurs when packet_count is 1)
    agg["std_pkt_len"] = agg["std_pkt_len"].fillna(0.0)

    out_csv.parent.mkdir(parents = True, exist_ok = True)
    agg.to_csv(out_csv, index = False)

    print(f"[+] Input packets: {len(df):,}")
    print(f"[+] Output flows: {len(agg):,}")
    print(f"[+] Saved: {out_csv}")

if __name__ == "__main__":
    main()
