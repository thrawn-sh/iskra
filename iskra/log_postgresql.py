#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import psycopg
import serial
import sml


def get_database_connection(config, database: str):
    parameters = {}
    if config.has_section(database):
        for item in config.items(database):
            parameters[item[0]] = item[1]
    else:
        raise Exception(f'Section {database} not found in the {config} file')
    return psycopg.connect(**parameters)


def main() -> None:
    parser = argparse.ArgumentParser(description='export data from SIKRA to PostgreSQL', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--device', default='/dev/tty0', type=str, help='Serial to read from')
    parser.add_argument('--database', default='postgresql', help='database config to use')
    parser.add_argument('--db-settings', default='database.ini', type=str, help='file containing postgresql connection configuration')

    arguments = parser.parse_args()

    db_config = configparser.ConfigParser()
    db_config.read(arguments.db_settings)
    with get_database_connection(db_config, arguments.database) as database:
        with serial.Serial(arguments.device) as device:
            reader = sml.SmlStreamReader()
            while True and device.readable():
                data = device.read(512)
                reader.add(data)
                frame = reader.get_frame()
                if frame is None:
                    # geather more bytes
                    continue

                cursor = database.cursor()
                for message in frame.parse_frame():
                    # prints a nice overview over the received values
                    print(message.format_msg())
                    # cursor.executemany(sql, inserts)
                cursor.close()
                database.commit()


if __name__ == '__main__':
    main()
