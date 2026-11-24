CREATE TABLE IF NOT EXISTS topologies (
    district TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    payload TEXT NOT NULL,
    digest TEXT NOT NULL,
    PRIMARY KEY (district, revision)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS feeds (
    district TEXT NOT NULL,
    revision INTEGER NOT NULL,
    source TEXT NOT NULL,
    batch TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('survey', 'notice')),
    reported_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    digest TEXT NOT NULL,
    PRIMARY KEY (district, revision, source, batch),
    FOREIGN KEY (district, revision) REFERENCES topologies(district, revision)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS feeds_cutoff ON feeds(district, revision, reported_at);

CREATE TABLE IF NOT EXISTS releases (
    id TEXT PRIMARY KEY,
    district TEXT NOT NULL,
    revision INTEGER NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    cutoff TEXT NOT NULL,
    envelope TEXT NOT NULL,
    CHECK (start < end),
    UNIQUE (district, id),
    FOREIGN KEY (district, revision) REFERENCES topologies(district, revision)
);

CREATE INDEX IF NOT EXISTS releases_district ON releases(district, cutoff DESC, id);

CREATE TABLE IF NOT EXISTS channel_events (
    district TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('field', 'public')),
    generation INTEGER NOT NULL CHECK (generation > 0),
    release_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('publish', 'restore')),
    note TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    PRIMARY KEY (district, channel, generation),
    FOREIGN KEY (district, release_id) REFERENCES releases(district, id)
) WITHOUT ROWID;
