import os
from pathlib import Path
import pandas as pd
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
OUT_CSV = Path(__file__).parent / "miner_dataset.csv"

MINER_LOG_FILENAME = "/tmp/ebpfangel_miner.log"

def parse_log(log_path: Path):
    stats = {}  # pid -> dict
    files_per_pid = defaultdict(set)

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 跳过说明行、表头
            if line.startswith("Printing file") or line.startswith("TS "):
                continue
            if line.startswith("Running from kernel directory"):
                continue

            parts = line.split()
            if len(parts) < 8:
                continue

            try:
                ts = int(parts[0])
                pid = int(parts[1])
            except ValueError:
                continue

            comm = parts[2]
            etype = parts[3]   # Open / Create / Delete / Encrypt
            flag = parts[4]
            patt = parts[5]
            thresh = parts[6]
            filename = " ".join(parts[7:])

            if pid not in stats:
                stats[pid] = {
                    "pid": pid,
                    "label": 0,  # 默认认为是 normal
                    "total_events": 0,
                    "open_count": 0,
                    "create_count": 0,
                    "delete_count": 0,
                    "encrypt_count": 0,
                    "min_ts": ts,
                    "max_ts": ts,
                }

            s = stats[pid]
            s["total_events"] += 1
            s["min_ts"] = min(s["min_ts"], ts)
            s["max_ts"] = max(s["max_ts"], ts)

            if etype == "Open":
                s["open_count"] += 1
            elif etype == "Create":
                s["create_count"] += 1
            elif etype == "Delete":
                s["delete_count"] += 1
            elif etype == "Encrypt":
                s["encrypt_count"] += 1

            files_per_pid[pid].add(filename)

            # 关键：只要某个 PID 访问过 miner 日志文件，就把它标成 1
            if filename == MINER_LOG_FILENAME:
                s["label"] = 1

    rows = []
    for pid, s in stats.items():
        total = max(s["total_events"], 1)
        duration = max(s["max_ts"] - s["min_ts"], 1)

        row = {
            "pid": pid,
            "label": s["label"],
            "total_events": s["total_events"],
            "open_count": s["open_count"],
            "create_count": s["create_count"],
            "delete_count": s["delete_count"],
            "encrypt_count": s["encrypt_count"],
            "unique_files": len(files_per_pid[pid]),
            "open_ratio": s["open_count"] / total,
            "delete_ratio": s["delete_count"] / total,
            "encrypt_ratio": s["encrypt_count"] / total,
            "events_per_ts": total / duration,
        }
        rows.append(row)

    return rows

def main():
    # 把所有 normal_*.log 和 miner_*.log 都吃进来
    logs = sorted(LOGS_DIR.glob("normal_*.log")) + sorted(LOGS_DIR.glob("miner_*.log"))
    if not logs:
        raise RuntimeError("No normal_*.log or miner_*.log found under logs/")

    all_rows = []
    for p in logs:
        print("Parsing log:", p)
        all_rows.extend(parse_log(p))

    df = pd.DataFrame(all_rows)

    print("Dataset shape:", df.shape)
    print(df["label"].value_counts())

    df.to_csv(OUT_CSV, index=False)
    print("Saved dataset to:", OUT_CSV)

if __name__ == "__main__":
    main()
