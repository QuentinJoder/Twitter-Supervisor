import sqlite3
from datetime import datetime


class Database:

    def __init__(self, database_name):
        self.database_name = database_name

    def create_tables(self):
        connection, cursor = self.open_connection()
        cursor.execute("CREATE TABLE `followers` (`id` integer NOT NULL UNIQUE,`username` TEXT, PRIMARY KEY(`id`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS friendship_events"
                       "(user_id integer, event_date text, follows integer)")
        connection.commit()
        connection.close()

    def open_connection(self):
        connection = sqlite3.connect(self.database_name)
        return connection, connection.cursor()

    def get_previous_followers_set(self):
        connection, cursor = self.open_connection()
        cursor.execute("SELECT id FROM followers")
        previous_followers_list = cursor.fetchall()
        connection.close()
        previous_followers = set()
        for follower in previous_followers_list:
            previous_followers.add(int(follower[0]))
        return previous_followers

    def update_followers_list(self, new_followers, traitors):
        connection, cursor = self.open_connection()

        # Update "followers" table
        cursor.executemany("DELETE FROM followers WHERE id=?", self.id_generator(traitors))
        cursor.executemany("INSERT INTO followers(id) VALUES(?)", self.id_generator(new_followers))

        # Update "friendship_events" table
        cursor.executemany("INSERT INTO friendship_events(user_id, event_date, follows) VALUES(?,?,?)",
                           self.event_generator(new_followers, True))
        cursor.executemany("INSERT INTO friendship_events(user_id, event_date, follows) VALUES(?,?,?)",
                           self.event_generator(traitors, False))

        connection.commit()
        connection.close()

    def update_followers_info(self, followers_info):
        connection, cursor = self.open_connection()
        cursor.executemany("UPDATE followers SET username = ? WHERE id = ?", self.follower_generator(followers_info))
        connection.commit()
        connection.close()

    def get_username_by_id(self, user_id):
        connection, cursor = self.open_connection()
        cursor.execute("SELECT username FROM followers WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        connection.close()
        if result is None:
            return None
        else:
            return result[0]

    def get_unknown_followers(self):
        connection, cursor = self.open_connection()
        cursor.execute("SELECT id FROM followers WHERE username is NULL")
        result_tuples = cursor.fetchall()
        connection.close()
        unknown_followers = list()
        for result_tuple in result_tuples:
            unknown_followers.append(result_tuple[0])
        return unknown_followers

    @staticmethod
    def id_generator(users):
        for user_id in users:
            yield user_id,

    @staticmethod
    def event_generator(users_set, true):
        for user_id in users_set:
            if true:
                yield user_id, datetime.today().isoformat(), 1,
            else:
                yield user_id, datetime.today().isoformat(), 0,

    @staticmethod
    def follower_generator(followers):
        for follower in followers:
            yield follower.screen_name, follower.id,

