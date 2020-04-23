import sqlite3
from datetime import datetime


class Database:

    def __init__(self, database_name):
        self.database_name = database_name

    def open_connection(self):
        connection = sqlite3.connect(self.database_name)
        return connection, connection.cursor()

    def get_previous_followers_set(self):
        connection, cursor = self.open_connection()
        cursor.execute("CREATE TABLE IF NOT EXISTS followers (id integer)")
        connection.commit()
        cursor.execute("SELECT * FROM followers")
        previous_followers_list = cursor.fetchall()
        connection.close()
        previous_followers = set()
        for follower in previous_followers_list:
            previous_followers.add(int(follower[0]))
        return previous_followers

    def update_followers_table(self, new_followers, traitors):
        connection, cursor = self.open_connection()

        # Populate "followers" table
        cursor.executemany("DELETE FROM followers WHERE id=?", self.id_generator(traitors))
        cursor.executemany("INSERT INTO followers(id) VALUES(?)", self.id_generator(new_followers))

        # Create & populate "friendship_events" table
        cursor.execute("CREATE TABLE IF NOT EXISTS friendship_events"
                       "(user_id integer, event_date text, follows integer)")
        cursor.executemany("INSERT INTO friendship_events(user_id, event_date, follows) VALUES(?,?,?)",
                           self.event_generator(new_followers, True))
        cursor.executemany("INSERT INTO friendship_events(user_id, event_date, follows) VALUES(?,?,?)",
                           self.event_generator(traitors, False))

        connection.commit()
        connection.close()

    @staticmethod
    def id_generator(followers_set):
        for user_id in followers_set:
            yield user_id,

    @staticmethod
    def event_generator(users_set, true):
        for user_id in users_set:
            if true:
                yield user_id, datetime.today().isoformat(), 1,
            else:
                yield user_id, datetime.today().isoformat(), 0,
