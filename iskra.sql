CREATE TABLE IF NOT EXISTS iskra (
    time                TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    id                  VARCHAR   NOT NULL,
    current_consumption REAL,
    total_consumption   REAL,
    total_supply        REAL,
    UNIQUE              (time, id)
);

