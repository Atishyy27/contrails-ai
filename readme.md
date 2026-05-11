# Contrails-AI: Media Ingestion & Signal Exploration Prototype

**Developer:** Atishay Jain  
**Project Phase:** Alpha (Heuristic Testing & Dataset Ingestion)

## Project Scope
This is a prototype system designed to automate the discovery and ingestion of deepfake media for forensic analysis. It prioritizes data provenance and high-fidelity signal acquisition over distribution-layer scraping.

## Implementation Details

### 1. Ingestion & Systems Architecture
* **Provenance-First Discovery:** Targets upstream generation hubs (Civitai User Galleries, Discord CDN stubs, HF Spaces) to capture latent lattice artifacts before platform-level H.264/H.265 re-encoding.
* **Concurrent Worker:** `ThreadPoolExecutor` with a 60s I/O timeout to maximize corpus diversity under bandwidth constraints (1 Mbps).
* **Integrity & Deduplication:** SHA-256 content hashing to prevent dataset poisoning through crosspost contamination.

### 2. Heuristic Signal Analysis (Experimental)
The analyzer uses a **Peak-to-Mean Ratio (PMR)** heuristic in the DCT (Discrete Cosine Transform) frequency domain to identify periodic upsampling residuals characteristic of Diffusion Transformers (DiT).

* **Temporal Sampling:** Analyzes a 16-frame sequence per video to calculate mean PMR and inter-frame variance, accounting for temporal inconsistencies.
* **Frequency Gating:** Isolates the high-frequency quadrant to separate stochastic scene entropy from structured generative artifacts.
* **Status:** This is an exploratory heuristic, not a definitive classification head. It serves as a triage layer for the ingestion pipeline.

## Preliminary Observations
Initial tests show a measurable delta in PMR variance between AI-generated animations and low-bitrate "Real" samples (CCTV/Dashcam), though macroblock quantization in social media samples remains a significant confounding variable.

## Unfiltered Realities (Bumps)
* **API Constraints:** Abandoned PRAW due to restrictive training policies; implemented guest-user JSON endpoint ingestion.
* **Hash Collisions:** Identical binaries detected across subreddits (e.g., ID 22/30); implemented automated disk synchronization and duplicate purging.
* **The Texture Trap:** Initial raw HF-mean was biased by natural high-entropy textures; pivoted to PMR to isolate periodic spikes.

---

## Unfiltered Bumps & Hard Truths (The Realness)

* **praw is dead:** Reddit's legal firewall against "model training" killed the official API. Bypassed it using the guest-user `.json` endpoints because it's faster, keyless, and avoids the bot-detection drama.
* **the hash trap:** Hit a `UNIQUE constraint failed` early on because ID 30 was a crosspost of ID 22. Built a sync script to kill the duplicates. If you don't de-duplicate, you're just training your model to memorize the internet.
* **internet is pain:** 1 Mbps in 2026 is an ICPC-level difficulty setting. The 60s timeout was the only way to stay sane. It transformed the project from a "Stalled Downloader" to a "Streamlined Ingester."
* **the texture trap:** Spent an hour wondering why a forest was "more fake" than a deepfake. Realized nature is chaotic and AI is smooth but spiky. PMR fixed the flip.
* **git hygiene:** Almost pushed a 5GB video folder to GitHub. Fixed the `.gitignore` just in time. Codes and metadata stay in Git; raw binaries stay in the Vault.

---

## 🚀 How to Run the Pipeline

### 1. Initialize the Ledger
```bash
python scripts/inti_db.py
```
### 2. Run Discovery (Task 1)
```bash
python src/discovery.py
```
### 3. Bulk Ingest (Task 2)
```bash
python src/ingest.py
```
### 4. Forensic Analysis
```bash
python src/analyze.py
```
### 2. Verify flip
```bash
sqlite3 data/deepfake_vault.db "SELECT category, COUNT(*), AVG(freq_score) FROM media_vault WHERE freq_score IS NOT NULL GROUP BY category;"
```