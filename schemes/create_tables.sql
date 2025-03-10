CREATE TABLE IF NOT EXISTS "guilds" (
    "id" UNSIGNED BIGINT NOT NULL UNIQUE,
    "logging_chnl" UNSIGNED BIGINT DEFAULT NULL,
    "fill_dialog" BOOLEAN DEFAULT 0,
    PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "proxies" (
    "id" UNSIGNED BIGINT NOT NULL UNIQUE,
    PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "dataset_dialog" (
    "idx" INTEGER NOT NULL UNIQUE,
    "speaker_id" UNSIGNED BIGINT NOT NULL,
    "listener_id" UNSIGNED BIGINT NOT NULL,
    "x" VARCHAR(2000) NOT NULL UNIQUE,
    "y" VARCHAR(2000) NOT NULL,
    PRIMARY KEY("idx" AUTOINCREMENT)
);