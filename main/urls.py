from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('activate/<token>/', views.ActivateAccount.as_view(),
         name='activateaccount'),
    path('profile/<int:pk>/', views.Profile.as_view(), name='profile'),
    path('change_password/', views.PasswordChange.as_view(), name='change_password'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('top', views.Top.as_view(), name="top"),
    path('newrequest', views.CreateScrapeRequest.as_view(), name="newrequest"),
    path('history', views.ListScrapeRequest.as_view(), name="history"),
    path('setting/<int:pk>/', views.Setting.as_view(), name="setting"),
    path('download', views.download, name="download"),
    path('deleterequest/<int:pk>/', views.delete_request, name='deleterequest'),
    path('results', views.ListScrapeRequestResult.as_view(), name='results'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:id>/', views.unsubscribe, name='unsubscribe'),

]
