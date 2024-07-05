import psycopg2
import psycopg2.extras
from config_data.config import DatabaseConfig, load_database_config

db_config: DatabaseConfig = load_database_config()

class Database:
    def __init__(self, user_id: int, name: str = 'NULL', surname: str = 'NULL'):
        self.user_id = user_id
        self.name = name
        self.surname = surname

    def insert_new_user(self, table_name: str, **column_names_with_values: str | int) -> None:
        #на всякий случай здесь прописал защиту от инъекций
        columns = []
        values = []
        for column, value in column_names_with_values.items():
            columns.append(f'{column}')
            values.append(f'{value}')
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} (id, {', '.join(columns)}) "
              f"VALUES ({self.user_id}, %s, %s)", values)


    def select_columns(self, *column_names: str, table_name: str) -> dict | None:
        columns = ', '.join(column_names)
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(f'SELECT {columns} FROM {table_name} '
                           f'WHERE id={self.user_id}')
            try:
                result: dict
                for row in cursor:
                    result = dict(row)
                return result
            except:
                return None

    def update_row(self, table_name: str, **column_names_with_new_values: str | int) -> None:
        #на всякий случай здесь прописал защиту от инъекций
        set_query = ''
        values = []
        for key, value in column_names_with_new_values.items():
            set_query += f"{key} = %s,\n"
            values.append(f'{value}')
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE {table_name} '
                           f'SET ' + f'{set_query.rstrip(',\n')} ' + f'WHERE id = {self.user_id}', tuple(values))

    def check_user(self, table_name: str) -> bool:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name} WHERE id = {self.user_id}')
            if cursor.fetchone():
                return True
            else:
                return False
