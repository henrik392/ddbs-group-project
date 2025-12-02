-- User table
-- Fragmented by region: Beijing -> DBMS1, Hong Kong -> DBMS2
DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
  timestamp VARCHAR(14) NOT NULL,
  id VARCHAR(10) PRIMARY KEY,
  uid VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10),
  email VARCHAR(100),
  phone VARCHAR(20),
  dept VARCHAR(50),
  grade VARCHAR(20),
  language VARCHAR(10),
  region VARCHAR(20) NOT NULL,
  role VARCHAR(20),
  preferTags VARCHAR(100),
  obtainedCredits VARCHAR(10)
);
CREATE INDEX idx_user_region ON "user"(region);
CREATE INDEX idx_user_uid ON "user"(uid);

-- Article table
-- Fragmented by category: science -> DBMS1 & DBMS2 (replicated), technology -> DBMS2
DROP TABLE IF EXISTS "article" CASCADE;
CREATE TABLE "article" (
  timestamp VARCHAR(14) NOT NULL,
  id VARCHAR(10) PRIMARY KEY,
  aid VARCHAR(10) UNIQUE NOT NULL,
  title VARCHAR(200) NOT NULL,
  category VARCHAR(20) NOT NULL,
  abstract TEXT,
  articleTags VARCHAR(200),
  authors VARCHAR(200),
  language VARCHAR(10),
  text VARCHAR(500),
  image VARCHAR(500),
  video VARCHAR(500)
);
CREATE INDEX idx_article_category ON "article"(category);
CREATE INDEX idx_article_aid ON "article"(aid);

-- Read table (user_read)
-- Co-located with User table: same fragmentation as User
DROP TABLE IF EXISTS "user_read" CASCADE;
CREATE TABLE "user_read" (
  timestamp VARCHAR(14) NOT NULL,
  id VARCHAR(10) PRIMARY KEY,
  uid VARCHAR(10) NOT NULL,
  aid VARCHAR(10) NOT NULL,
  readTimeLength VARCHAR(10),
  agreeOrNot VARCHAR(5),
  commentOrNot VARCHAR(5),
  shareOrNot VARCHAR(5),
  commentDetail TEXT
);
CREATE INDEX idx_read_uid ON "user_read"(uid);
CREATE INDEX idx_read_aid ON "user_read"(aid);

-- Be-Read table
-- Replicated: science -> DBMS1 & DBMS2, technology -> DBMS2
DROP TABLE IF EXISTS "be_read" CASCADE;
CREATE TABLE "be_read" (
  id VARCHAR(10) PRIMARY KEY,
  timestamp BIGINT NOT NULL,
  aid VARCHAR(10) NOT NULL,
  readNum INTEGER DEFAULT 0,
  readUidList TEXT,
  commentNum INTEGER DEFAULT 0,
  commentUidList TEXT,
  agreeNum INTEGER DEFAULT 0,
  agreeUidList TEXT,
  shareNum INTEGER DEFAULT 0,
  shareUidList TEXT
);
CREATE INDEX idx_beread_aid ON "be_read"(aid);

-- Popular-Rank table
-- Fragmented by temporalGranularity: daily -> DBMS1, weekly/monthly -> DBMS2
DROP TABLE IF EXISTS "popular_rank" CASCADE;
CREATE TABLE "popular_rank" (
  id VARCHAR(10) PRIMARY KEY,
  timestamp BIGINT NOT NULL,
  temporalGranularity VARCHAR(20) NOT NULL,
  articleAidList TEXT NOT NULL
);
CREATE INDEX idx_popularrank_granularity ON "popular_rank"(temporalGranularity);
