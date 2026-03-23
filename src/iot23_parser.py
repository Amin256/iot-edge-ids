from __future__ import annotations
from fileinput import filename

import pandas as pd
from pathlib import Path

# Path to selected IoT23 logs
IOT23_SELECTED_DIR = Path(r"C:\Users\Aminb\Documents\Leeds\Year 3\Datasets\IoT23_Selected")
OUTPUT_CSV = Path("data/iot23_processed/iot23_binary_flows.csv")

# Limit malware samples to keep dataset manageable
MAX_MALWARE_ROWS = 1_000_000

# Parses a single IoT-23 log file and extracts relevant features, returning a DataFrame
def parse_log_file(file_path: Path) -> pd.DataFrame:
    print(f"Parsing {file_path.name}")

    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#fields"):
                columns = line.strip().split("\t")[1:]
                break
    
    # We only keep a subset of columns relevant for flow-level analysis and binary classification
    selected_cols = [
    "ts",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "orig_pkts",
    "resp_pkts",
    "orig_ip_bytes",
    "resp_ip_bytes",
    "proto",
    "conn_state",
    "service"
    ]

    dfs = []

    # Read the log file in chunks to handle large files, only keeping selected columns
    chunk_iter = pd.read_csv(
        file_path,
        sep= "\t",
        comment= "#",
        names= columns,
        usecols= lambda c: c in selected_cols,
        chunksize= 200_000,
        engine= "python"
    )

    total_rows = 0

    for chunk in chunk_iter:
        dfs.append(chunk)
        total_rows += len(chunk)

        # If malware file, stop after limit
        if file_path.name.lower().startswith("malware"):
            if total_rows >= MAX_MALWARE_ROWS:
                break

    df = pd.concat(dfs, ignore_index=True)

    # Assign label by scenario type
    if file_path.name.lower().startswith("honeypot"):
        df["binary_label"] = "BENIGN"
    else:
        df["binary_label"] = "MALICIOUS"
    print(f"Rows kept: {len(df):,}")
    return df

def main():
    all_dfs = []
    
    # Parse each selected IoT23 log file
    for file_path in IOT23_SELECTED_DIR.glob("*.log.labeled"):
        df = parse_log_file(file_path)
        capture_name = file_path.name.replace("_conn.log.labeled", "")
        df["capture_name"] = capture_name
        all_dfs.append(df)

    # Combine all parsed DataFrames
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print("\nBefore balancing:")
    print(combined_df["binary_label"].value_counts())
    
    # Save unbalanced dataset (real distribution)
    FULL_OUTPUT_CSV = Path("data/iot23_processed/iot23_full_unbalanced.csv")

    FULL_OUTPUT_CSV.parent.mkdir(parents = True, exist_ok = True)
    combined_df.to_csv(FULL_OUTPUT_CSV, index=False)

    print("\nFull unbalanced dataset saved:")
    print(combined_df["binary_label"].value_counts())

    # Balance dataset by downsampling the majority class (malicious) to match the minority class (benign)
    benign_df = combined_df[combined_df["binary_label"] == "BENIGN"]
    malicious_df = combined_df[combined_df["binary_label"] == "MALICIOUS"]
    malicious_sampled = malicious_df.sample(
        n = len(benign_df),
        random_state = 42
    )

    # Combine balanced dataset
    balanced_df = pd.concat([benign_df, malicious_sampled], ignore_index=True)

    # Shuffle the balanced dataset to mix benign and malicious samples
    balanced_df = balanced_df.sample(frac = 1, random_state = 42).reset_index(drop = True)

    print("\nAfter balancing:")
    print(balanced_df["binary_label"].value_counts())

    # Save final balanced dataset
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    balanced_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nFinal dataset saved: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
