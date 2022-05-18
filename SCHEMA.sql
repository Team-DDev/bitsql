CREATE TABLE blk (
  id INT NOT NULL,
  blkhash CHAR(64) NOT NULL,
  miningtime TIMESTAMP NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (blkhash)
);
CREATE INDEX idx_miningtime ON blk (miningtime);
