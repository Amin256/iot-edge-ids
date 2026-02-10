# Converting pcap files to csv form for machine learning models
from __future__ import annotations

from pathlib import Path
import pandas as pd
from scapy.all import rdpcap

# This script reads a PCAP file and extracts basic packet-level features into a CSV format.
def pcap_to_packet_features(pcap_path: Path) -> pd.DataFrame:
    packets = rdpcap(str(pcap_path))

    rows: list[dict] = []
    # Loop through each packet and extract features if it's an IP packet
    for pkt in packets:
        if pkt.haslayer("IP"):
            ip = pkt["IP"]
            rows.append(
                # Extracting timestamp, source/destination IPs, protocol, and packet length
                {
                    "timestamp": float(pkt.time),
                    "src_ip": str(ip.src),
                    "dst_ip": str(ip.dst),
                    "protocol": int(ip.proto),
                    "packet_length": int(len(pkt)),
                }
            )

    return pd.DataFrame(rows)

# Main function to execute the conversion process
def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    pcap_path = repo_root /"data"/"raw"/"normal_traffic_01.pcap"
    out_csv = repo_root /"data"/"processed"/"normal_traffic_01_packet_features.csv"
    
    # Check if the PCAP file exists before processing
    if not pcap_path.exists():
        raise FileNotFoundError(f"PCAP not found: {pcap_path}")
    
    # Convert the PCAP to a DataFrame of packet features
    df = pcap_to_packet_features(pcap_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    print(f"[+] IP packets extracted: {len(df)}")
    print(f"[+] Saved: {out_csv}")

if __name__ == "__main__":
    main()
