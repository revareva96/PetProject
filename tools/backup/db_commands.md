# PSQL COMMANDS
Cоздание схемы, если не существует, ... с типом авторизации для роли/пользователя ... <br>
```create schema if not exists data authorization cigar;```<br>
создание пользователя ... с паролем ... с отсутсвием возможности создавать БД
```create user cigar_user with password 'password123' NOCREATEDB;```<br>
посмотреть права у пользователя ...<br>
```
SELECT *\
FROM information_schema.role_table_grants```
where grantee = 'cigar_user'<br>
```
накидывает права на чтение всех таблиц в схеме ... для пользователя ...<br>
```GRANT SELECT ON ALL TABLES IN SCHEMA DATA to cigar_user;```
накидывает  права на возможность пользоваться схемой ... для пользователя ...<br>
```GRANT USAGE ON SCHEMA DATA to cigar_user;```
отбирает все права на все таблицы в схеме ... для пользователя ...<br>
накидывает права на чтение таблицы ... в схеме ... для пользователя ...<br>
```
GRANT SELECT ON DATA.USERS to cigar_user;
REVOKE ALL ON ALL TABLES IN SCHEMA DATA from cigar_user;
```
отбирает права на чтение в таблице ... схемы ... для пользователя ...<br>
```
REVOKE SELECT ON TABLE DATA.USERS_PASSWORDS from cigar_user;
```
# DB DUMP
экспортируем переменные в окружение, теперь может подключиться к БД через cli, просто вызвав psql<br>
```
export PGHOST=localhost;
export PGPORT=5433;
export PGDATABASE=cigar_db;
export PGUSER=cigar;
export PGPASSWORD=cigar;
```
сам dump в виде файла sql и в виде архива, с помощью которого можно восстановить с утилитой pg_restore<br>
-x нужно для того, чтобы не воспроизводились команды по users<br>
```pg_dump -x > db.sql;```<br>
-Fc определенный формат выходного файла<br>
```pg_dump -x -Fc > db.dump;```<br>
восстановление можно сделать простой утилитой psql<br>
```psql -f $PATH_TO_FILE```<br>
или с помощью утилиты pg_restore<br>
```pg_restore -d $DB_NAME $PATH_TO_FILE```
