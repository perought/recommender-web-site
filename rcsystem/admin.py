from django.contrib import admin

from .models import DBBookRating, DBUser, DBBook

admin.site.register(DBBookRating)
admin.site.register(DBUser)
admin.site.register(DBBook)
