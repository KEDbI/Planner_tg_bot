import psycopg2
import psycopg2.extras
from config_data.config import DatabaseConfig, load_database_config

db_config: DatabaseConfig = load_database_config()


class Database:
    table_name: str
    user_id_column_name: str

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def select_columns_as_dict(self, *column_names: str) -> dict | None:
        # Выводит результат в виде словаря {column_name: value, column_name: value}; получить несколько значений
        # из одного столбца не получится, т.к. этот метод возвращает только последнюю строку из полученной выборки
        columns = ', '.join(column_names)
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(f'SELECT {columns} FROM {self.table_name} '
                           f'WHERE {self.user_id_column_name}={self.user_id}')
            try:
                result: dict
                for row in cursor:
                    result = dict(row)
                return result
            except:
                return None

    def update_row(self, **column_names_with_new_values: str | int) -> None:
        # на всякий случай здесь прописал защиту от инъекций
        columns = ''
        values = []
        for key, value in column_names_with_new_values.items():
            columns += f"{key} = %s,\n"
            values.append(f'{value}')
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE {self.table_name} '
                           f'SET ' + f'{columns.rstrip(',\n')} ' +
                           f'WHERE {self.user_id_column_name} = {self.user_id}', tuple(values))

    def check_user(self) -> bool:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE {self.user_id_column_name} = {self.user_id}')
            if cursor.fetchone():
                return True
            else:
                return False

    def delete_all_user_data(self) -> None:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {self.table_name} WHERE {self.user_id_column_name} = {self.user_id}')

    def get_several_values_from_column(self, column_name) -> str:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT {column_name} FROM {self.table_name} '
                           f'WHERE {self.user_id_column_name}={self.user_id}')
            temp_str = ''
            for row in cursor.fetchall():
                temp_str += f'{row[0]}\n'
            res = (f'Список задач:\n'
                   f'{temp_str}')
            return res


class Users(Database):
    table_name: str = 'users'
    user_id_column_name: str = 'id'

    def __init__(self, user_id: int, user_name: str = 'NULL', full_name: str = 'NULL') -> None:
        super().__init__(user_id)
        self.user_name = user_name
        self.full_name = full_name

    def insert_new_user(self) -> None:
        # на всякий случай здесь прописал защиту от инъекций
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} (id, user_name, full_name) "
                           f"VALUES (%s, %s, %s)", (self.user_id, self.user_name, self.full_name))


class GlobalTasks(Database):
    table_name: str = 'global_tasks'
    user_id_column_name: str = 'user_id'

    def __init__(self, user_id: int) -> None:
        super().__init__(user_id)

    def insert_task(self, task_name: str, description: str = 'NULL', deadline: str = 'NULL',
                    is_done: str = 'false') -> None:
        if deadline != 'NULL':
            deadline = f"'{deadline}'"
        subquery = '(SELECT MAX(task_id) FROM global_tasks)+1)'
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} (user_id, task_name, description, deadline, "
                           f"is_done, task_id) "
                           f"VALUES (%s, %s, %s, {deadline}, %s, {subquery}",
                           (self.user_id, task_name, description, is_done))

    def get_last_task(self) -> int | None:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT MAX(task_id) FROM {self.table_name} '
                           f'WHERE user_id={self.user_id}')
            try:
                return cursor.fetchone()[0]
            except:
                return None

    def get_all_active_tasks(self) -> str | None | int:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT task_name, TO_CHAR(deadline, 'DD.MM.YYYY'), task_id FROM {self.table_name} "
                           f"WHERE {self.user_id_column_name}={self.user_id} AND is_done = false "
                           f"ORDER BY deadline")
            res = ''
            try:
                for row in cursor.fetchall():
                    if row[1] is None:
                        res += f'No deadline — {row[0]} — ({row[2]})\n'
                    else:
                        res += f'{row[1]} — ' + f'{row[0]} — ({row[2]})\n'
                return res
            except:
                return None

    def set_is_done(self, task_id: int) -> None:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE TABLE {self.table_name} SET is_done = true '
                           f'WHERE {self.user_id_column_name} = {self.user_id} '
                           f'AND task_id = {task_id}')

    def get_ids_of_active_tasks(self) -> list:
        with psycopg2.connect(database=db_config.db.database_name, user=db_config.db.user,
                              password=db_config.db.password, host=db_config.db.host, port=db_config.db.port) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT task_id FROM {self.table_name} '
                           f'WHERE {self.user_id_column_name} = {self.user_id} '
                           f'AND is_done = false')
            lst: list = []
            for row in cursor:
                lst.append(row[0])
            return lst


db = GlobalTasks(1274018099)
