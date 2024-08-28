import sqlite3
import pandas as pd
import re

class DataBase():
    _instance = None
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'initialized'): 
           
            self.initialized = True
            self.connection = sqlite3.connect(':memory:')
            self.cursor = self.connection.cursor()
        
            self.connection.commit()
        
            self.open_csv()
    
            self.create_users_table()
            self.create_and_fill_authors_table()
            self.create_and_fill_books_table()
            self.update_books_with_author_ids()
            self.create_and_fil_genres_table()
            self.create_and_fill_genres_books_table()
            self.create_users_books_table()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataBase, cls).__new__(cls, *args, **kwargs)
        
        return cls._instance
    
    def open_csv(self):
        self.df = pd.read_csv('Book_Details.csv')
        self.df = self.df[['cover_image_uri', 'book_title', 'book_details', 'author', 'publication_info', 'genres'
                        , 'num_ratings', 'average_rating']].drop_duplicates("book_title")
        self.df = self.df.drop_duplicates(subset="book_title")

        mask = self.df['publication_info'].apply(lambda x: len(x) == 2)
        self.df = self.df[~mask]

        
        self.df['publication_info']=self.df['publication_info'].str.split(',', n=1).str[1]
        self.df['publication_info'] = self.df['publication_info'].str.replace(r'[^0-9\s]', '', regex=True).str.strip()
      
        mask = pd.notna(self.df['genres'])
        filtered_df = self.df[mask]
        self.df = filtered_df

     

        mask = pd.notna(self.df['book_details'])
        filtered_df = self.df[mask]
        self.df = filtered_df

    def create_users_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                            (id  INTEGER PRIMARY KEY  , 
                            first_name TEXT, 
                            second_name TEXT, 
                            email TEXT, 
                            password TEXT)""")
        
    def create_and_fill_authors_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS authors 
                            (id INTEGER PRIMARY KEY,
                             name TEXT)""")
    
 
        author_series = self.df["author"].drop_duplicates()

   

        data = [(author,) for author in author_series]
        self.cursor.executemany("INSERT INTO authors (name) VALUES(?)", data)

    def create_and_fill_books_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY,
                                                   cover_image_uri TEXT,
                                                   book_title TEXT,
                                                   author_id INTEGER,
                                                   book_details TEXT,
                                                   year_of_publication INTEGER,
                                                   num_ratings INTEGER,
                                                   average_rating REAL,
                                                   FOREIGN KEY(author_id) REFERENCES authors(id))""")
        data = [(row.cover_image_uri, row.book_title,row.book_details, row.publication_info, row.num_ratings, row.average_rating) 
                for row in self.df.itertuples()]


        self.cursor.executemany("""INSERT INTO books 
                                (cover_image_uri, book_title,book_details, year_of_publication,num_ratings, average_rating) 
                                VALUES (?, ?, ?, ?, ?, ?)""", data)    
        
    def update_books_with_author_ids(self):

        self.cursor.execute("CREATE TEMPORARY TABLE IF NOT EXISTS temp_books_authors (book_title TEXT, author TEXT)")
    

        data_books_authors = [(row.book_title, row.author) for row in self.df.itertuples(index=False)]

        self.cursor.executemany("INSERT INTO temp_books_authors (book_title, author) VALUES (?, ?)", data_books_authors)
    
 
        self.cursor.execute("""UPDATE books SET author_id = (
                            SELECT authors.id
                            FROM authors
                            JOIN temp_books_authors ON authors.name = temp_books_authors.author
                            WHERE books.book_title = temp_books_authors.book_title)""")
    
    def create_and_fil_genres_table(self):
        genres_series = self.df["genres"]
    
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS genres 
                               (id INTEGER PRIMARY KEY, 
                                name TEXT)""")

        genres = []
        
        for genre in genres_series:

       	    for g in genre.split(","):

                cleaned_genre = re.sub('[^a-zA-Z]', '', g).strip()
                genres.append(cleaned_genre)

        genres_cleaned_series = pd.Series(genres).drop_duplicates()

        data = [(genre,) for genre in genres_cleaned_series] 
        
        self.cursor.executemany("INSERT INTO genres (name) VALUES (?)", data)

    def create_and_fill_genres_books_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS genres_books (genre_id INTEGER,                                                          
                                                                book_id INTEGER,
                                                                FOREIGN KEY(genre_id) REFERENCES genres(id),
                                                                FOREIGN KEY(book_id) REFERENCES book(id),
                                                                PRIMARY KEY(genre_id, book_id))""")
        
        genres_df = pd.read_sql_query("SELECT id, name FROM genres", self.connection)
        books_df = pd.read_sql_query("SELECT id, book_title FROM books", self.connection)


        genre_id_map = dict(zip(genres_df['name'], genres_df['id']))
        book_id_map = dict(zip(books_df['book_title'], books_df['id']))
        


        insert_data = set()

        for row in self.df.itertuples():
            book_id = book_id_map.get(row.book_title)

    
            row_genres = str(row.genres)
            genre_test = row_genres.split(",")
    
            for genre in genre_test:
                cleaned_genre = re.sub(r'[^a-zA-Z\s]+', '', genre).strip()
        
                if cleaned_genre in genre_id_map:
                    genre_id = genre_id_map[cleaned_genre]
                    insert_data.add((genre_id, book_id))


        self.cursor.executemany("INSERT INTO genres_books (genre_id, book_id) VALUES (?, ?)",insert_data)

    def create_users_books_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users_books
                               (user_id INTEGER,
                               book_id INTEGER,
                               rating  INTEGER,
                               FOREIGN KEY(user_id) REFERENCES users(id),
                               FOREIGN KEY(book_id) REFERENCES books(id),
                               PRIMARY KEY(user_id, book_id))
                    """)

    def check_log_in(self, email, password):
        self.cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        email_current = self.cursor.fetchone()
        if not email_current:
            return -1
        else: 
            self.cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))

            if not self.cursor.fetchone():
                return 0
            else: 
                return 1

    def get_logged_user_id(self, email):
        self.cursor.execute("SELECT id FROM users WHERE email=?", (email, ))
        info = self.cursor.fetchone()
        return info[0]
    
    def register(self, first_name, second_name, email, password):
        self.cursor.execute("""INSERT INTO users 
                            (first_name, second_name, email, password) VALUES(?, ?, ?, ?)""", 
                            (first_name, second_name, email, password))
        
        return self.cursor.lastrowid

    def is_user_registered(self, email):
        self.cursor.execute("SELECT email FROM users WHERE email=?", (email,))
        return self.cursor.fetchone() is None

    def get_books_by_user_id(self, user_id):
        self.cursor.execute("SELECT book_id FROM users_books WHERE user_id=?", (int(user_id),))
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_users_books(self, user_id):
        self.cursor.execute("""SELECT books.book_title,authors.name,users_books.rating
                               FROM books
                               INNER JOIN users_books ON books.id = users_books.book_id
                               INNER JOIN authors ON books.author_id = authors.id
                               WHERE users_books.user_id = ?
                """, (user_id,))

        return self.cursor.fetchall()

    def find_book_by_name(self, book_name):
        self.cursor.execute("SELECT id FROM books WHERE book_title=?", (book_name,))
        return self.cursor.fetchone()[0]

    def fill_users_books_table(self, user_id, book_name, rating):
        book_id = self.find_book_by_name(book_name)
        self.cursor.execute("INSERT OR IGNORE INTO users_books VALUES (?,?,?)", (user_id, book_id, rating)) 

    def find_author_and_book(self, search_text):
        search_pattern = f"%{search_text}%"


        self.cursor.execute("""SELECT books.book_title, authors.name, books.year_of_publication, genres.name
                               FROM books
                               INNER JOIN authors ON books.author_id = authors.id
                               INNER JOIN genres_books ON books.id = genres_books.book_id
                               INNER JOIN genres ON genres_books.genre_id= genres.id
                               WHERE books.book_title LIKE ? OR authors.name LIKE ? """,
                               (search_pattern, search_pattern))

        return self.cursor.fetchall()
    
    def get_book_by_id(self, book_id):
        self.cursor.execute("""SELECT books.book_title, authors.name, books.year_of_publication, genres.name
                               FROM books
                               INNER JOIN authors ON books.author_id = authors.id
                               INNER JOIN genres_books ON books.id = genres_books.book_id
                               INNER JOIN genres ON genres_books.genre_id= genres.id
                               WHERE books.id=?""", (str(book_id+1),))
        
        return [row for row in self.cursor.fetchall()]

    def __del__(self):
        self.connection.close()


db = DataBase()
