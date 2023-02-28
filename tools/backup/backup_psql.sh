#!/bin/bash

echo "run script..."
BASEPATH=/home/vladimir/projects/cigar_project_back/tools/backup;
export PGHOST=localhost;
export PGPORT=5433;
export PGDATABASE=cigar_db;
export PGUSER=cigar;
export PGPASSWORD=cigar;
export SSHHOST=172.17.0.2;
export SSHPATH=/home/vladimir/db_backups;

echo "run dump db $PGDATABASE..."
pg_dump -x > ${BASEPATH%%/}/db.sql || exit 1;
pg_dump -x -Fc > ${BASEPATH%%/}/db.dump;

echo "run ssh copy...";
scp ${BASEPATH%%/}/db.sql ${BASEPATH%%/}/db.dump vladimir@$SSHHOST:$SSHPATH || exit 0;
echo "success operation!";
