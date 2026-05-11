-- data/schema.sql
CREATE TABLE IF NOT EXISTS media_vault (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Provenance & Metadata
    source_url TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL,          -- 'reddit', 'civitai', 'discord', 'youtube'
    synthetic_label TEXT,            -- 'synthetic', 'real', 'mixed'
    generation_method TEXT,          -- 'diffusion', 'gan', 'manual'
    manipulation_type TEXT,          -- 'face_swap', 'lip_sync', 'animation', 'none'
    
    -- File Data
    file_path TEXT,
    sha256_hash TEXT UNIQUE,
    
    -- Forensic Signals (Technical Metadata)
    bitrate INTEGER,
    width INTEGER,
    height INTEGER,
    fps REAL,
    duration REAL,
    codec TEXT,
    
    -- Heuristic Triage Metrics
    pmr_mean REAL,
    pmr_variance REAL,
    
    -- Pipeline States
    ingestion_status TEXT DEFAULT 'pending', -- 'pending', 'downloading', 'completed', 'failed', 'corrupt'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hash ON media_vault(sha256_hash);
CREATE INDEX IF NOT EXISTS idx_status ON media_vault(ingestion_status);
CREATE INDEX IF NOT EXISTS idx_synthetic ON media_vault(synthetic_label);