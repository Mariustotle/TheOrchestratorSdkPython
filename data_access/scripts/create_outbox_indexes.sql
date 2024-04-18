

-- Index for the de-duplication query
CREATE INDEX "idx_unique_header_handler" ON MessageOutbox(unique_header_hash, handler_name);
CREATE INDEX "idx_created_date" ON MessageOutbox(created_date);

-- Indexes for selecting the next batch query
CREATE INDEX "idx_status_priority_created" ON MessageOutbox(status, priority DESC, created_date);