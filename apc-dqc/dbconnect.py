# -*- coding: utf-8 -*-
"""A module-level docstring

Notice the comment above the docstring specifying the encoding.
Docstrings do appear in the bytecode, so you can access this through
the ``__doc__`` attribute. This is also what you'll see if you call
help() on a module or any other Python object.
"""


import pyodbc  # support for sql server connection
from config import ODBCDRIVER  # specified odbc driver for sql server
import redshift_connector  # support for redshift connection
from utils import get_logger  # logging


class SQLServerDB:
    """ Creating a SQL Server DB instance"""

    def __init__(self, host: str = None, database: str = None,
                 user: str = None, password: str = None, odbc_driver: str = ODBCDRIVER):

        get_logger(False).info(
            f'host: {host}, database: {database}, user: {user}, password: *****, odbc_driver: {odbc_driver}')

        try:
            self.connection = pyodbc.connect(
                f"DRIVER={{{odbc_driver}}};SERVER={host};DATABASE={database};UID={user};PWD={password}")
            get_logger().info(f'[CONNECTION ESTABLISHED]\n')
        except Exception as e:
            self.connection = None
            get_logger().error(f'[FAILED CONNECTING] {e}\n')


class RedshiftDB:
    """ Creating a Redshift DB instance with connection attribute """

    def __init__(self, host: str = None, port: int = None, database: str = None,
                 user: str = None, password: str = None, ssl: bool = False):

        get_logger(False).info(
            f'host: {host}, port: {port}, database: {database}, user: {user}, password: *****, ssl: {ssl}')

        try:
            self.connection = redshift_connector.connect(
                host=host, database=database, user=user, password=password,
                port=int(port), ssl=False)
            get_logger().info(f'[CONNECTION ESTABLISHED]\n')
        except Exception as e:
            self.connection = None
            get_logger().error(f'[FAILED CONNECTING] {e}\n')


def connect(dict_conn, dbs):
    for db_id in dict_conn:
        dict_db = dict_conn[db_id]
        get_logger().info('[CONNECTING TO DATABASE...]')
        if dict_db['database_type'] == 'REDSHIFT':
            dbs[db_id] = RedshiftDB(host=dict_db['server_name'], port=dict_db['port_number'],
                                    database=dict_db['database_name'],
                                    user=dict_db['user_name'], password=dict_db['password'])
        elif dict_db['database_type'] == 'MSSQL':
            dbs[db_id] = SQLServerDB(host=dict_db['server_name'], database=dict_db['database_name'],
                                     user=dict_db['user_name'], password=dict_db['password'])
    return dbs

# TODO add support for other database engines
# class BigQueryDB(DB):
#     def __init__(self, location: str = None, project: str = None, dataset: str = None,
#                  gcloud_gcs_bucket_name=None, service_account_private_key_file: str = None,
#                  use_legacy_sql: bool = False):
#         """
#         Connection information for a BigQueryDB database

#         Enabling the BigQuery API and Service account json credentials are required. For more:
#         https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries#before-you-begin

#         Args:
#             location: Default geographic location to use when creating datasets or determining where jobs should run
#             project: Default project to use for requests.
#             dataset: Default dataset to use for requests.
#             service_account_private_key_file: The private key file provided by Google when creating a service account. (it's a JSON file).
#             gcloud_gcs_bucket_name: The Google Cloud Storage bucked used as cache for loading data
#             use_legacy_sql: (default: false) If true, use the old BigQuery SQL dialect is used.
#         """
#         self.service_account_private_key_file = service_account_private_key_file
#         self.location = location
#         self.project = project
#         self.dataset = dataset
#         self.gcloud_gcs_bucket_name = gcloud_gcs_bucket_name
#         self.use_legacy_sql = use_legacy_sql


# class MysqlDB(DB):
#     def __init__(self, host: str = None, port: int = None, database: str = None,
#                  user: str = None, password: str = None, ssl: bool = None, charset: str = None):
#         self.host = host
#         self.database = database
#         self.port = port
#         self.user = user
#         self.password = password
#         self.ssl = ssl
#         self.charset = charset


# class OracleDB(DB):
#     def __init__(self, host: str = None, port: int = 0, endpoint: str = None, user: str = None, password: str = None):
#         self.host = host
#         self.port = port
#         self.endpoint = endpoint
#         self.user = user
#         self.password = password


# class SQLiteDB(DB):
#     def __init__(self, file_name: pathlib.Path) -> None:
#         self.file_name = file_name
