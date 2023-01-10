import os.path
import sqlite3
import logging
import re
from config import basedir


class Database(object):

    # Build up a connection to database --> data.sqlite
    def __init__(self, connection=None):
        if connection is None:
            try:
                connection = sqlite3.connect(os.path.normpath(basedir + "/app/database/data.sqlite"))
            except Exception as error:
                logging.basicConfig(filename='../exceptions.log', level=logging.DEBUG,
                                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
                print('Error: connection not established {}'.format(error))
            else:
                print('Connection established')
            self.connection = connection
            return

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def query_insert_into_database(self, author, title, file):
        query = 'INSERT INTO user_data (Author, Title, File) VALUES (?, ?, ?);'
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (author, title, file))
        except Exception as error:
            print(error)
        # calling self.cursor variable include execute statement
        self.connection.commit()
        return

    def query_to_mirror_database(self):
        query = '''
        SELECT * FROM user_data
        '''
        cursor = self.connection.cursor()
        file_records = cursor.execute(query).fetchall()
        # fetchall returns a list with the selected entries
        self.connection.commit()
        return file_records

    # get all text from every user selection -->
    def get_user_selection(self, entry_id):
        query = f'''
            SELECT File
            FROM user_data
            WHERE ID = {entry_id} 
            '''
        cursor = self.connection.cursor()
        file_records = cursor.execute(query).fetchall()
        # fetchall returns a list with the selected entries
        self.connection.commit()
        return str(file_records)

    # query to export only the geographic names
    def query_to_export_local_entity(self):
        query = '''
        SELECT name, id FROM geographic_data 
         '''
        cursor = self.connection.cursor()
        entity_records = cursor.execute(query).fetchall()
        self.connection.commit()
        return entity_records


    def query_to_export_all_local_data(self):
        query = '''
        SELECT * FROM geographic_data ORDER BY id
        '''
        cursor = self.connection.cursor()
        geographic_tupel = cursor.execute(query).fetchall()
        self.connection.commit()
        return geographic_tupel

    # fit in the geographic names in a nested dictionary
    @staticmethod
    def get_records(entity_records):
        record_map = {}
        for element in entity_records:
            it = record_map
            keys = element[0].split(" ")
            for key in keys:
                # keys = geographic name [0] / value = id [1]
                if key not in it:
                    it[key] = {}
                it = it[key]
                # print(key)
            it["id"] = element[1]
        # print(record_map)
        # print(record_map["Schwarzach"]["b."])
        return record_map

    def get_names(self, record_map, name, full_names):
        for first_key in record_map.keys():
            if name is None:
                full_name = first_key
            else:
                full_name = name + " " + first_key
            if type(record_map[first_key]) != type({}):
                full_names.append(name)
            else:
                self.get_names(record_map[first_key], full_name, full_names)
        return full_names

    # process single user selection
    def divide_user_selection(self, data: str):
        # eliminate leading whitespaces
        data.strip()
        # deploy delimiters
        delimiters = ' ', '.', ':', ',', '-', '(', ')', '\'', '\r', '\n', '\\r\\n', '[', ']'
        # split the text_file
        pattern = '|'.join(map(re.escape, delimiters))
        # remove empty strings from the text
        words = list(filter(None, re.split(pattern, data)))
        # print(words)
        return words

    # compare the words of the text with the geographic names
    def lookup(self, words, full_names):
        # list for the dropdown
        matches = []
        for word in words:
            for full_name in full_names:
                # split the geographic names and take the first part of the name
                first_word = full_name.split(" ")[0]
                # compare the word from the user text with the first part of the geographic name
                if len(first_word) >= len(word):
                    # if they match?
                    if first_word[:len(word)] == word:
                        matches.append(full_name)
        return matches

database = Database()
ergebnis = database.query_to_export_local_entity()
user = database.get_user_selection(153)
sel = database.divide_user_selection(user)
# database.lookido(ergebnis, sel)
result = database.get_records(ergebnis)
names = database.get_names(result, None, [])
look = database.lookup(sel, names)
print(look)


# varchar anstatt blob verwenden
# nicht über die komplette Datenbank iterieren in jedem Schritt --> nicht realisierbar
# full_names aus dem Tokenfenster erstellen
# nach match --> window auf token nach longest match setzen
# auf Github hochladen!!!