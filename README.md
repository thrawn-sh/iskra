# ISKRA
python module to interact and read statistics from [ISKRA](https://www.iskra.eu/) smartmeter.

## Install depencies
```sh
$> poetry install
```

## Check source code
```sh
$> poetry run flake8
```

## Build package
```sh
$> poetry build
```

### Log available statistics from ISKRA to PostgreSQL
```sh
# create database and user
$> sudo --user=postgres createuser --no-createdb --no-createrole --no-superuser --pwprompt <USER>
$> sudo --user=postgres createdb --encoding=UTF-8 --owner=<USER> <DATABASE>

# create schema for database
$> cat iskra.sql | psql --host=<HOST> --dbname=<DATABASE> <USER>

# create database connection configuration
$> cat > database.ini <<EOF
[postgresql]
host=<HOST>
port=5432
dbname=<DATABASE>
user=<USER>
password=<PASSWORD>
sslmode=require
EOF

$> ./bin/log_postgresql --device <DEVICE>
```

