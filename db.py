import sqlite3


class DB:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS client(
                    client_user_id INT,
                    sex INT,
                    age INT,
                    city INT,
                    relation INT)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS match(
                    match_user_id INT,
                    id_client INT
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS photos(
                    id INT,
                    photo_url TEXT
        )""")
        self.connection.commit()

    def close(self):
        self.connection.close()


def insert_user_to_db(db, client_info, match_user_id):
    db.cursor.execute("INSERT INTO match VALUES (?, ?)",
                      (match_user_id,
                       client_info['client_user_id']))
    db.connection.commit()


def insert_data(db, match_user_id, photo_urls):
    db.cursor.execute("INSERT INTO client VALUES (?, ?, ?, ?, ?)",
                      (match_user_id['user_id'],
                       match_user_id['sex'],
                       match_user_id['age'],
                       match_user_id['city'],
                       match_user_id['relation']))

    for url in photo_urls:
        db.cursor.execute("INSERT INTO photos VALUES (?, ?)",
                          (match_user_id['user_id'], url))
    db.connection.commit()


# def is_user_in_db(db, match_user_id, client_user_id):
#     db.cursor.execute(f'SELECT match_user_id, id_client FROM match WHERE match_user_id = {match_user_id} AND id_client != {client_user_id}')
#     # todo переписать запрос с испозьзованием ?
#     # todo JOIN
#     if db.cursor.fetchone() is None:
#         return False
#     else:
#         return True

def is_user_in_db(db, match_user_id, client_user_id):
    db.cursor.execute(f'SELECT id_client FROM match WHERE id_client = {client_user_id}')
    if db.cursor.fetchone() is not None:
        db.cursor.execute(f'SELECT match_user_id FROM match WHERE match_user_id = {match_user_id}')
        if db.cursor.fetchone() is None:
            return False
        else:
            return True
    else:
        return True