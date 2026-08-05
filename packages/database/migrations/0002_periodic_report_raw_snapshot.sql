ALTER TABLE periodic_monitoring_reports
ADD COLUMN IF NOT EXISTS raw_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb;
