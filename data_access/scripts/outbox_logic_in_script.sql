-- Creating a subquery to find the maximum created_date for each unique_header_hash and handler_name combination
WITH LatestEntries AS (
    SELECT 
        "unique_header_hash",
        "handler_name",
        MAX("created_date") AS "latest_date"
    FROM 
        "MessageOutbox"
    GROUP BY 
        "unique_header_hash", 
        "handler_name"
)

-- Updating the older duplicate records to mark them as duplicates
UPDATE "MessageOutbox"
SET 
    "status" = "Duplicate",
    "is_completed" = "True"
WHERE EXISTS (
    SELECT 1
    FROM LatestEntries
    WHERE 
        MessageOutbox.unique_header_hash = LatestEntries.unique_header_hash AND
        MessageOutbox.handler_name = LatestEntries.handler_name AND
        MessageOutbox.created_date < LatestEntries.latest_date
);

-- Selecting the next batch of messages based on status, priority, and created_date
SELECT *
FROM "MessageOutbox"
WHERE "status" = 'Ready'
ORDER BY "priority" DESC, "created_date"
LIMIT 50; 

