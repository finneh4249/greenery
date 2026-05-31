# 🌿 Greenery

> **Get that green.** An automated commit generator designed to keep your GitHub contribution graph vibrant, active, and fully customizable.

---

## 🚀 Overview

`Greenery` is a developer tool that automatically simulates daily code activity on GitHub. It operates by generating commits containing random or dynamically structured programming "fortunes" to a dedicated repository. It includes:
- **Programmatic Fortune Generator**: Generates infinite, unique, and humorous developer fortunes without using external LLM APIs.
- **Deterministic Seeded Mode**: Creates deterministic output based on date or seed for repeatable runs.
- **Automated Cron Execution**: Pre-packaged shell scripts to sync and run seamlessly in the background.
- **Git History Backfilling**: Backdates commits to fill your timeline history.

---

## 🤔 Why?

For some reason, recruiters, companies, and open-source contributors place a disproportionate emphasis on the number of green squares on a GitHub profile, treating it as a primary metric of productivity.

In reality, contribution graphs mean literally nothing about your actual skill or capability as a software engineer. This tool highlights that absurdity by giving you a beautiful, fully automated green wall with zero effort.

---

## 🛠️ Repository Architecture

| File | Purpose |
| :--- | :--- |
| [`fortune.py`](file:///mnt/storage/Documents/greenery/fortune.py) | The core fortune generator script. |
| [`backfill.py`](file:///mnt/storage/Documents/greenery/backfill.py) | Backfills your commit graph with history back to a specified date. |
| [`committed.sh`](file:///mnt/storage/Documents/greenery/committed.sh) | Local script wrapper executing the commit cycles. |
| [`push.sh`](file:///mnt/storage/Documents/greenery/push.sh) | Execution script that commits and pushes to remote repository. |
| [`cron.txt`](file:///mnt/storage/Documents/greenery/cron.txt) | Reference crontab entry for automating daily activity. |

---

## 💻 Getting Started

### 1. Daily Fortune Generator

You can run `fortune.py` to generate randomized programming wisdom:

```bash
python3 fortune.py
```

#### CLI Options
- `-sn <length>` / `-n <length>`: Constrain the output string to a maximum number of characters.
- `-s <seed>` / `--seed <seed>`: Seed the generator for deterministic, reproducible fortunes.
- `-c <count>` / `--count <count>`: Generate multiple fortunes at once.

**Example (Deterministic Execution):**
```bash
python3 fortune.py --seed "my_custom_seed"
```

### 2. Auto-commit Setup

`committed.sh` runs a random number of commits locally:
```bash
bash committed.sh
```

To schedule this automatically, set up the cron job defined in `cron.txt` by running:
```bash
crontab -e
```
Add the following line (configured for 4:20 PM daily):
```text
20 16 * * * bash ~/greenery/push.sh
```

### 3. Backfilling Contribution History

To fill in missing spots in your historical graph, use `backfill.py`. It loops from a historical start date up to the current date and generates commits using random times during the day:
```bash
python3 backfill.py
```

> [!WARNING]
> Backdating git commits modifies history. Be sure to run this in a dedicated repository to avoid polluting important project histories.
