-- ====================================================================
-- EMS ASSISTANT - SUPABASE / POSTGRESQL PGVECTOR SCHEMA
-- ====================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Bots table (for multi-tenant or multi-agent support)
CREATE TABLE IF NOT EXISTS bots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    system_prompt TEXT,
    model_name TEXT DEFAULT 'gemini-2.5-flash',
    embedding_model TEXT DEFAULT 'text-embedding-004',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default EMS bot
INSERT INTO bots (id, name, description, model_name, embedding_model)
VALUES (
    'ems',
    'EMS Assistant',
    'User-facing AI Event Assistant for MLRIT CIE Event Management System (EMS)',
    'gemini-2.5-flash',
    'text-embedding-004'
) ON CONFLICT (id) DO NOTHING;

-- 3. Knowledge Sources (Events, URLs, PDFs, Raw Text)
CREATE TABLE IF NOT EXISTS knowledge_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_id TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL, -- 'event', 'url', 'pdf', 'text', 'markdown'
    external_id TEXT, -- e.g. EMS event ID
    title TEXT NOT NULL,
    source_url TEXT,
    content_hash TEXT NOT NULL, -- SHA256 to avoid redundant re-embedding
    status TEXT DEFAULT 'ready', -- 'pending', 'indexing', 'ready', 'failed'
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_sources_bot_id ON knowledge_sources(bot_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_external_id ON knowledge_sources(external_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_content_hash ON knowledge_sources(content_hash);

-- 4. Knowledge Chunks with Vector Embeddings (768 dimensions for Google text-embedding-004)
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_id TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL DEFAULT 0,
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_bot_id ON knowledge_chunks(bot_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source_id ON knowledge_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_metadata ON knowledge_chunks USING gin (metadata);

-- HNSW Vector Index for Fast Approximate Nearest Neighbor search
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding ON knowledge_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 5. Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    bot_id TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    session_id TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 7. Sync Runs (Tracking EMS event synchronization)
CREATE TABLE IF NOT EXISTS sync_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_id TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL DEFAULT 'ems',
    status TEXT NOT NULL, -- 'running', 'completed', 'failed'
    total_events INT DEFAULT 0,
    added_count INT DEFAULT 0,
    updated_count INT DEFAULT 0,
    deleted_count INT DEFAULT 0,
    unchanged_count INT DEFAULT 0,
    error_log TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 8. Usage & Analytics Events (Privacy-safe metrics)
CREATE TABLE IF NOT EXISTS usage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_id TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    conversation_id TEXT,
    event_type TEXT NOT NULL, -- 'chat_success', 'out_of_scope', 'error'
    latency_ms INT,
    retrieval_count INT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. PostgreSQL RPC Function for Hybrid / Vector Matching
CREATE OR REPLACE FUNCTION match_knowledge_chunks(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.4,
    match_count int DEFAULT 6,
    filter_bot_id text DEFAULT 'ems',
    filter_event_id text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    source_id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kc.id,
        kc.source_id,
        kc.content,
        kc.metadata,
        1 - (kc.embedding <=> query_embedding) AS similarity
    FROM knowledge_chunks kc
    WHERE kc.bot_id = filter_bot_id
      AND (filter_event_id IS NULL OR kc.metadata->>'event_id' = filter_event_id)
      AND (1 - (kc.embedding <=> query_embedding)) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
