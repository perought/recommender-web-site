import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise import dump
from fastai.collab import CollabDataLoaders, collab_learner

# 1A) Books items
books_dataset = pd.read_csv("rcsystem/static/books_dataset.csv")
books_count_vec = CountVectorizer(stop_words='english')
books_count_matrix = books_count_vec.fit_transform(books_dataset['soup'])
books_cosine_sim = cosine_similarity(books_count_matrix, books_count_matrix)

# 1B) Books users
books_ratings = pd.read_csv("rcsystem/static/books_ratings.csv")

# surprise model
_, user_based_book_algo = dump.load("rcsystem/static/user_based_book.dump")

# fastai model
# Important: Used seed=1 to match size of the vocabulary. It may cause problems after training different day
books_dls = CollabDataLoaders.from_df(books_ratings, item_name='title', seed=1)
books_collab_filtering = collab_learner(books_dls, y_range=(0.5, 5.5))
books_collab_filtering.model_dir = "."
books_collab_filtering = books_collab_filtering.load("rcsystem/static/books_collab_filtering")

# 2A) Movies items
movies_dataset = pd.read_csv("rcsystem/static/movies_dataset.csv")
movies_count_vec = CountVectorizer(stop_words='english')
movies_count_matrix = movies_count_vec.fit_transform(movies_dataset['soup'][:10000])
movies_cosine_sim = cosine_similarity(movies_count_matrix, movies_count_matrix)

# 2B) Movies users
movies_ratings = pd.read_csv("rcsystem/static/movies_ratings.csv")

# surprise model
_, user_based_movie_algo = dump.load("rcsystem/static/user_based_movie.dump")

# fastai model
movies_dls = CollabDataLoaders.from_df(movies_ratings, item_name='title', seed=1)
movies_collab_filtering = collab_learner(movies_dls, y_range=(0.5, 5.5))
movies_collab_filtering.model_dir = "."
movies_collab_filtering = movies_collab_filtering.load("rcsystem/static/movies_collab_filtering")
