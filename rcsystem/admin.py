from django.contrib import admin

from .models import BookDatabase, BookRatings, MovieDatabase, MovieRatings, \
    DBBookRating, DBUser, DBBook

# admin_name: rsroot, admin_pass: SQL
admin.site.register(BookDatabase)
admin.site.register(BookRatings)
admin.site.register(MovieDatabase)
admin.site.register(MovieRatings)

# old system
admin.site.register(DBBookRating)
admin.site.register(DBUser)
admin.site.register(DBBook)
