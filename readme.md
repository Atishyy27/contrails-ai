# Contrails-AI: Forensic Ingestion & Signal Extraction Pipeline

**Developer:** Atishay Jain  
**Role:** Forensic Data Engineer (Pilot Phase)  
**Objective:** Solving the 2026 Deepfake Ingestion Crisis through Signal-Aware Discovery and Mathematical Quantization.

---

## The Engineering Manifesto

In 2026, scraping "Deepfakes" from social media is a fool's errand. Platforms like X and YouTube perform aggressive H.264 macroblock quantization that acts as a "low-pass filter," effectively sandblasting the delicate forensic fingerprints left by generative models. 

**Contrails-AI** is built on the philosophy that a dataset is only as good as its Signal-to-Noise Ratio (SNR). We don't just "download files." We hunt for **Latent Lattice Artifacts** using a multi-threaded, collision-aware pipeline that treats every pixel as a frequency coordinate.

---

## Task 1: Source Intelligence (Targeting the Zero-Day)

Task 1 was to identify where the "Forensic Gold" lives. We moved upstream from the "Distribution Layer" (Social Media) to the "Generation Hubs" (Raw Model Outputs).

### The Primary Target List
* **Civitai Video Vault:** The epicenter for Flux.1 and LTX-Video fine-tunes. We target the "User Gallery" because these are often raw renders that preserve the high-frequency upsampling lattice identified in **Rombach (2022)**.
* **Hugging Face Trending Spaces:** The lab where LivePortrait and Hedra v2 signatures land first. Monitoring these allows us to capture "Zero-Day" artifacts before they are "cleaned" by platform CDNs.
* **Discord Master-Copy CDNs:** By scraping `cdn.discordapp.com` links from Kling and Luma showcase servers, we bypass the compression slop of the Discord UI feed, getting the closest thing to a "Bit-Perfect" fake.
* **r/CCTV & r/Dashcam (The Domain Gap):** A critical addition. We need to establish a baseline for low-bitrate, high-grain stochastic noise to ensure our detector doesn't hallucinate "AI" every time it sees a grainy security camera.

---

## Task 2: Multi-threaded Ingestion (High-Velocity Engineering)

Building a pipeline on a **1 Mbps bottleneck** is a constraint-driven optimization problem. We implemented a "Greedy Filter" approach to ensure the 200-vid volume target was met without the script hanging.

### 1. Concurrency via `ThreadPoolExecutor`
We utilize parallel I/O streams to maximize our limited bandwidth. Instead of waiting for one heavy 4K file to finish, the script processes multiple small, high-signal samples simultaneously.

### 2. The 60-Second Kill-Switch
If a download exceeds 60 seconds, it is likely a high-resolution, long-form video that will choke the network. The script terminates the process, deletes the fragment, and moves to the next ID. This prioritizes **Corpus Diversity** over individual file size.

### 3. SHA-256 Collision Logic
Reddit and Discord are feedback loops of crossposted content. To prevent **Data Leakage** (training and testing on the same binary), every file is hashed. If a hash already exists, the script purges the redundant binary and cleans the SQLite ledger.

---

## The Science: Frequency-Domain Feature Extraction

This is the project's unique value proposition. We do not use a "Guessing Machine" (CNN/ViT). we use the **Discrete Cosine Transform (DCT)** to mathematically prove artificiality.

### 1. From Energy to Structure
Initially, we measured raw High-Frequency energy. However, nature videos (trees, grass) are high-entropy and have more raw energy than smooth AI faces.
* **Real Average:** 1.16
* **Animation Average:** 0.92  
*(The Texture Trap: Nature is "noisier" than AI)*.

### 2. The PMR Pivot (Peak-to-Mean Ratio)
We realized that AI noise is **Periodic** (a mathematical grid), while natural noise is **Stochastic** (random grain). In the DCT domain, a grid manifests as a "Spike."

We isolate the extreme high-frequency quadrant ($HF$) and calculate the ratio between the single highest energy peak and the average noise floor:

$$PMR = \frac{\max(HF_{quadrant})}{\mu(HF_{quadrant}) + \epsilon}$$

### 3. The Papers that Built the Math
* **Rombach et al. (2022) [Latent Diffusion]:** Taught us that generating in a compressed latent space and upsampling back to pixels *guarantees* a lattice artifact. 
* **Peebles & Xie (2023) [Scalable DiT]:** Explained the "Patch-based" nature of Sora/Kling. We look for the frequency spikes occurring at those $16 \times 16$ or $8 \times 8$ patch boundaries.
* **Liu & Choi (2026) [Frequency-Aware Fusion]:** Provided the logic for using the frequency spectrum as a "Gate" to filter out low-freq "Scene Content" and focus purely on "Generative Residuals."
* **FasterDiT (2024):** Defined our Bitrate requirement. If Bitrate $< 500kbps$, the PMR signal is considered "Forensically Dead."

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