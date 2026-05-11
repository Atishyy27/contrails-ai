# Deepfake Data Source Identification (Task 1)

## 1. Primary Generation Hubs (SOTA 2026)
*   **Civitai (Video Models):** Central hub for Flux.1 and Kling-based LoRAs. High-fidelity face-swaps and character animations are found in the "User Gallery" of specific model pages.
*   **Hugging Face Spaces:** Real-time generation spaces like LivePortrait and Hedra v2. Monitoring these provides raw, uncompressed outputs before they reach social media.
*   **Luma/Kling Explore Feeds:** Direct sources for high-consistency character animations.

## 2. Community & Niche Channels
*   **r/StableDiffusion & r/SoraAI:** High-signal Reddit communities where users benchmark new models.
*   **Telegram Bot Galleries:** Bot specific galleries (e.g., DeepfakeRefinery) host raw outputs that haven't been processed by platform CDNs, preserving forensic noise.

## 3. Categorization Logic
*   **Lip-sync:** Primarily Hedra/HeyGen outputs found on X/Reddit.
*   **Face-swap:** Roop/DeepFaceLab legacy and Ethereal-Face (Gaussian Splatting) current tech.
*   **Animation:** Sora/Kling v2.1/Luma outputs.

Unfiltered:
***praw*** didn't worked bcz of the latest reddit policies. reddit has a legal firewall. Can't use it directly since it states cant use it for training model
***got same hash*** 1 and 11 got same hash due to which i couldnt run the analyze sciptuntil syncing the sqlite db table again
