from django.urls import path
from . import views

 
urlpatterns = [
    # Other URL patterns...
    path("logout", views.logout, name="logout"),
    path("book_collection", views.book_collection_view, name="book_collection"),
]
# urls.py

from django.urls import path
from .views import issue_book_view

urlpatterns = [
    # Other URL patterns
    path('issuebook/', issue_book_view, name='issue_book'),
]
