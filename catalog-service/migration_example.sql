BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001

CREATE TABLE product (
    id BIGSERIAL NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    vehicle_type VARCHAR(64) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('0001') RETURNING alembic_version.version_num;

COMMIT;

