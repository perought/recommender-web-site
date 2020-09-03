from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BookDatabase(models.Model):
    id = models.IntegerField(primary_key=True)
    book_id = models.IntegerField(unique=True)
    best_book_id = models.IntegerField()
    work_id = models.IntegerField()
    books_count = models.IntegerField()
    isbn = models.CharField(max_length=250)
    isbn13 = models.CharField(max_length=250)
    authors = models.TextField()
    original_publication_year = models.CharField(max_length=250)
    original_title = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    language_code = models.CharField(max_length=250)
    average_rating = models.FloatField()
    ratings_count = models.IntegerField()
    work_ratings_count = models.IntegerField()
    work_text_reviews_count = models.IntegerField()
    ratings_1 = models.IntegerField()
    ratings_2 = models.IntegerField()
    ratings_3 = models.IntegerField()
    ratings_4 = models.IntegerField()
    ratings_5 = models.IntegerField()
    image_url = models.CharField(max_length=250)
    small_image_url = models.CharField(max_length=250)
    description = models.TextField()
    categories = models.TextField()
    clean_description = models.TextField(default="")
    soup = models.TextField(default="")


class BookRatings(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(BookDatabase, null=True, default=None, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


class MovieDatabase(models.Model):
    id = models.IntegerField(primary_key=True)
    imdb_id = models.CharField(max_length=250)
    clean_imdb_id = models.IntegerField()
    original_language = models.CharField(max_length=250)
    original_title = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    overview = models.TextField()
    genres = models.CharField(max_length=250)
    casts = models.CharField(max_length=250)
    director = models.CharField(max_length=250)
    keywords = models.CharField(max_length=250)
    spoken_languages = models.CharField(max_length=250)
    production_countries = models.CharField(max_length=250)
    production_companies = models.CharField(max_length=250)
    popularity = models.CharField(max_length=250)
    release_date = models.CharField(max_length=250)
    tagline = models.TextField()
    vote_average = models.CharField(max_length=255)
    vote_count = models.CharField(max_length=255)
    runtime = models.CharField(max_length=250)
    poster = models.URLField()
    movie_index = models.IntegerField(default=-1)


class MovieRatings(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    movie = models.ForeignKey(MovieDatabase, null=True, default=None, on_delete=models.CASCADE)
    rating = models.FloatField(default=0)
    timestamp = models.DateTimeField(verbose_name="rated at", default=None)

    class Meta:
        unique_together = (("user_id", "movie_id"),)


# old books system
class DBBookCategory(models.Model):
    category = models.CharField(max_length=50, default="Novel")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    def __str__(self):
        return self.category


class DBUser(models.Model):
    user_id = models.IntegerField(primary_key=True, default=0, blank=True)
    location = models.CharField(max_length=250, null=True, default=None)
    age = models.IntegerField(null=True, default=None)


class DBBook(models.Model):
    ISBN = models.CharField(max_length=13, primary_key=True, default="123123")
    title = models.CharField(max_length=255, null=True, default=None)
    author = models.CharField(max_length=255, null=True, default=None)
    pub_date = models.IntegerField(null=True, default=None)
    publisher = models.CharField(max_length=255, null=True, default=None)
    book_category = models.ForeignKey(
        DBBookCategory,
        on_delete=models.CASCADE,
        related_name="category_book"
    )
    Rating_CHOICES = (
        (0, 'Not Rated'),
        (1, 'Poor'),
        (2, 'Average'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent')
    )
    book_user_favorite = models.IntegerField(choices=Rating_CHOICES, default=0)
    book_overall_favorite = models.FloatField(default=0)
    book_favorites_count = models.IntegerField(default=0)
    img_url_s = models.URLField(null=True, default=None)
    img_url_m = models.URLField(null=True, default=None)
    img_url_l = models.URLField(null=True, default=None)


class DBBookRating(models.Model):
    user = models.ForeignKey(DBUser, null=True, default=None, on_delete=models.CASCADE)
    ISBN = models.CharField(max_length=13, default="123123")
    rating = models.IntegerField(null=True, default=0, unique=False)

    class Meta:
        unique_together = (("user", "ISBN"),)


class DBUserAddedBook(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="user_added_book")
    user_book = models.ForeignKey(DBBook, on_delete=models.CASCADE)


class DBBookComment(models.Model):
    book = models.ForeignKey(DBBook, default=None, on_delete=models.CASCADE, related_name='comments_book')
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="user_comment_book")
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class DBUserRatedBook(models.Model):
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE, related_name="rated_user")
    book = models.ForeignKey(DBBook, max_length=13, on_delete=models.CASCADE, related_name="rated_book")
    rating_choices = (
        (0, 'Not Rated'),
        (1, 'Poor'),
        (2, 'Average'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent')
    )
    user_rated = models.IntegerField(choices=rating_choices, default=0)

    class Meta:
        unique_together = (("user", "book"),)


