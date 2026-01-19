-- Migration 003: Add AI Designer Context System
-- Run this SQL against your SQLite database

-- Design Context table - stores persistent context for AI Designer
CREATE TABLE IF NOT EXISTS design_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(36) UNIQUE NOT NULL,
    product_analysis TEXT,  -- JSON
    image_inventory TEXT DEFAULT '[]',  -- JSON array
    color_mode VARCHAR(20) DEFAULT 'ai_decides',  -- ai_decides, suggest_primary, locked_palette
    locked_colors TEXT DEFAULT '[]',  -- JSON array of hex colors
    selected_framework_id VARCHAR(50),
    selected_framework_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES generation_sessions(id)
);

-- Prompt History table - tracks all prompts and regenerations
CREATE TABLE IF NOT EXISTS prompt_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context_id INTEGER NOT NULL,
    image_type VARCHAR(20) NOT NULL,  -- main, infographic_1, etc.
    version INTEGER DEFAULT 1,
    prompt_text TEXT NOT NULL,
    user_feedback TEXT,  -- null for version 1
    change_summary TEXT,  -- AI's interpretation of changes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (context_id) REFERENCES design_contexts(id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_design_contexts_session ON design_contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_prompt_history_context ON prompt_history(context_id);
CREATE INDEX IF NOT EXISTS idx_prompt_history_image_type ON prompt_history(context_id, image_type);
