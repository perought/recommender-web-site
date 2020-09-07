import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise import dump

books_dataset = pd.read_csv("rcsystem/static/books_dataset.csv")
books_count_vec = CountVectorizer(stop_words='english')
books_count_matrix = books_count_vec.fit_transform(books_dataset['soup'])
books_cosine_sim = cosine_similarity(books_count_matrix, books_count_matrix)

books_ratings = pd.read_csv("rcsystem/static/books_ratings.csv")
_, user_based_book_algo = dump.load("rcsystem/static/user_based_book.dump")

movies_dataset = pd.read_csv("rcsystem/static/movies_dataset.csv")
movies_count_vec = CountVectorizer(stop_words='english')
movies_count_matrix = movies_count_vec.fit_transform(movies_dataset['soup'][:10000])
movies_cosine_sim = cosine_similarity(movies_count_matrix, movies_count_matrix)

movies_ratings = pd.read_csv("rcsystem/static/movies_ratings.csv")
_, user_based_movie_algo = dump.load("rcsystem/static/user_based_movie.dump")
