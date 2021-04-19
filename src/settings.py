import os
import psycopg2


def get_configs():
    configs = {'host': os.getenv('HOST'), 'port': os.getenv('PORT'), 'debug': os.getenv('DEBUG'),
               'db_host': os.getenv('DB_HOST'), 'db_name': os.getenv('DB_NAME'), 'db_port': os.getenv('DB_PORT'),
               'db_user': os.getenv('DB_USER'), 'db_password': os.getenv('DB_PASSWORD')}

    return configs


def load_config():
    configs = get_configs()

    conn_string = 'host={} dbname={} user={} password={}'.format(
        configs['db_host'], configs['db_name'], configs['db_user'], configs['db_password']
    )
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    return conn, cur
