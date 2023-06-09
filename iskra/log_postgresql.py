#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import datetime
import pathlib
import psycopg
import serial
import smllib
import tzlocal

BUFFER_SIZE = 320
SQL = 'INSERT INTO iskra (time, id, current_consumption, total_consumption, total_supply) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (time, id) DO NOTHING;'


def get_database_connection(config, database: str):
    parameters = {}
    if config.has_section(database):
        for item in config.items(database):
            parameters[item[0]] = item[1]
    else:
        raise Exception(f'Section {database} not found in the {config} file')
    return psycopg.connect(**parameters)


def main() -> None:
    parser = argparse.ArgumentParser(description='export data from ISKRA to PostgreSQL', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--device', default='/dev/tty0', type=str, help='Serial to read from')
    parser.add_argument('--database', default='postgresql', help='database config to use')
    parser.add_argument('--db-settings', default='database.ini', type=str, help='file containing postgresql connection configuration')
    parser.add_argument('--sql-file', default='iskra-cache.sql', type=str, help='folder for caching sql requests')

    arguments = parser.parse_args()

    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    now = now.astimezone(tzlocal.get_localzone()).isoformat()
    values = {}
    with serial.Serial(arguments.device, timeout=2) as device:
        reader = smllib.SmlStreamReader()
        count = 0
        while device.readable() and count <= 0:
            data = device.read(BUFFER_SIZE)
            reader.add(data)
            frame = reader.get_frame()
            if frame is None:
                # need to gather more bytes
                continue

            for message in frame.parse_frame():
                count = count + 1
                for entry in getattr(message.message_body, 'val_list', []):
                    code = entry.obis.obis_code
                    value = entry.get_value()
                    if code == '1-0:96.1.0*255':
                        values['id'] = value
                        continue
                    if code == '1-0:1.8.0*255':
                        values['total_consumption'] = value
                        continue
                    if code == '1-0:16.7.0*255':
                        values['current_consumption'] = value
                        continue
                    if code == '1-0:2.8.0*255':
                        values['total_supply'] = value
                        continue

    cache_file = pathlib.Path(arguments.sql_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'a', encoding='utf-8') as file:
        statement = SQL.replace('%s', "'%s'")
        statement = statement % (now, values['id'], values['current_consumption'], values['total_consumption'], values['total_supply'])
        file.write(statement)
        file.write('\n')

    db_config = configparser.ConfigParser()
    db_config.read(arguments.db_settings)
    with get_database_connection(db_config, arguments.database) as database:
        cursor = database.cursor()
        cursor.execute(SQL, [now, values['id'], values['current_consumption'], values['total_consumption'], values['total_supply']])
        cursor.close()
        database.commit()


if __name__ == '__main__':
    main()
