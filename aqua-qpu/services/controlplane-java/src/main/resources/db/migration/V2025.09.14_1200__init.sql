-- Enable TimescaleDB (if available)
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS device_state (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL,
  time TIMESTAMPTZ NOT NULL DEFAULT now(),
  temperature_k DOUBLE PRECISION,
  magnetic_field_t DOUBLE PRECISION,
  vacuum_pa DOUBLE PRECISION,
  analog JSONB,
  status JSONB
);

CREATE TABLE IF NOT EXISTS measurement_record (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL,
  utcs_anchor TEXT NOT NULL,
  iso_time TIMESTAMPTZ NOT NULL,
  payload BYTEA
);

-- Optional hypertable
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname='device_state') THEN
    -- no-op
    NULL;
  END IF;
  -- Try to convert if extension is present
  PERFORM create_hypertable('device_state', 'time', if_not_exists => TRUE);
EXCEPTION WHEN undefined_function THEN
  -- Timescale not present; ignore
  NULL;
END $$;