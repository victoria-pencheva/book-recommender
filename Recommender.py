import pandas as pd
from Database import DataBase
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


db = DataBase()

class Recommender():

    def find_books_and_genres_len(self):
        query = "SELECT id FROM books"
        df_books = pd.read_sql_query(query, db.connection)
        query = "SELECT id FROM genres"
        df_genres = pd.read_sql(query, db.connection)
        return len(df_books), len(df_genres)
    
    def cosine_similarity(self, vec1, vec2):
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0  

        return np.dot(vec1, vec2) / (norm1 * norm2)


    def fill_genre_vector(self):
        genre_vector = np.zeros(shape=(self.find_books_and_genres_len()[0], self.find_books_and_genres_len()[1]))
        query = "SELECT genre_id, book_id FROM genres_books"
        df = pd.read_sql_query(query, db.connection)

        for index, row in df.iterrows():
            genre_id = row['genre_id']
            book_id = row['book_id']
            genre_vector[book_id-1][genre_id-1] = 1

        return genre_vector

    def calculate_genre_similarity(self,book_id):
        genre_vector = self.fill_genre_vector()
        similarity_scores = np.zeros(shape=(1, self.find_books_and_genres_len()[0]))

        for i in range(0, self.find_books_and_genres_len()[0]):
            similarity_scores[:,i] = self.cosine_similarity(genre_vector[book_id], genre_vector[i]) 

        return similarity_scores

    def calculate_year_similarity(self,book_id):
        query = "SELECT year_of_publication FROM books"
        df = pd.read_sql_query(query, db.connection)
        df_normalized = df.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) if np.max(x) != np.min(x) else x)

        normalized_array = df_normalized.to_numpy()

        similarity_scores = np.zeros(shape=(1, self.find_books_and_genres_len()[0]))

        for i in range(normalized_array.shape[0]):
            similarity_scores[:, i] = np.abs(normalized_array[book_id] - normalized_array[i])

        return similarity_scores

    def author_similarity(self,book_id):
        query = "SELECT id, author_id FROM BOOKS"
        df = pd.read_sql_query(query, db.connection)
        array = df.to_numpy()

        similarity_score = np.zeros(shape=(1, self.find_books_and_genres_len()[0]))

        for i in range (0, self.find_books_and_genres_len()[0]):
            if array[book_id][1] == array[i][1]:
                similarity_score[:,i] = 1

        return similarity_score

    def description_similarity(self):
        query = "SELECT book_details FROM books"
        df = pd.read_sql_query(query, db.connection)    
        documents = df['book_details'].tolist()

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        return similarity_matrix

    def similarities_sum(self,book_id):
        sum = self.calculate_genre_similarity(book_id)-self.calculate_year_similarity(book_id)  + self.author_similarity(book_id) + self.description_similarity()[book_id]
        return sum

    def give_recommendations(self, book_ids, recommendation_len=10):

        sum_vector = np.zeros((self.find_books_and_genres_len()[0],))

   
        for book_id in book_ids:
            similarity_vector = self.similarities_sum(book_id)

            if similarity_vector.ndim > 1:
                similarity_vector = similarity_vector.flatten()
            sum_vector += similarity_vector
    
        for book_id in book_ids:
            sum_vector[book_id] = 0


        recommendations_indices = np.argsort(sum_vector)[::-1][:recommendation_len]

        return recommendations_indices
    

