CREATE TABLE IF NOT EXISTS "User"(
  id BIGINT PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "Article"(
  id BIGINT PRIMARY KEY,
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  text_uri TEXT,
  image_uri TEXT,
  video_uri TEXT
);

CREATE TABLE IF NOT EXISTS "Read"(
  id BIGINT PRIMARY KEY,
  ts TIMESTAMP NOT NULL,
  uid BIGINT NOT NULL REFERENCES "User"(id),
  aid BIGINT NOT NULL REFERENCES "Article"(id),
  agreeNum INT DEFAULT 0,
  commentNum INT DEFAULT 0,
  shareNum INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS "BeRead"(
  id BIGINT PRIMARY KEY,
  aid BIGINT NOT NULL REFERENCES "Article"(id),
  readNum INT DEFAULT 0,
  agreeNum INT DEFAULT 0,
  commentNum INT DEFAULT 0,
  shareNum INT DEFAULT 0,
  shareUidList TEXT
);

CREATE TABLE IF NOT EXISTS "PopularRank"(
  id BIGINT PRIMARY KEY,
  ts TIMESTAMP NOT NULL,
  temporalGranularity TEXT NOT NULL,  -- daily/weekly/monthly
  articleAidList TEXT NOT NULL
);
