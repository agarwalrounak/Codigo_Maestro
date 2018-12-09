from django.urls import path

from . import views


app_name = 'home'

urlpatterns = [
    path('', views.index, name = "index"),
    path('auth/', views.auth, name="auth"),
    path('details/', views.details, name="details"),
    path('details/comparator/', views.comparator, name="comparator"),
    path('details/common_rankings/', views.rankings, name="rankings"),
    path('details/rating/', views.rating, name="rating"),
    path('details/rating/problems', views.problems, name="problems"),
    path('details/logout/', views.logout, name='logout'),
]

