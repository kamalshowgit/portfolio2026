from django.urls import path
from . import views

app_name = 'personal'

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/', views.edit, name='edit'),
    path('api/update_profile/', views.update_profile, name='update_profile'),
    path('add_link/', views.add_link, name='add_link'),
    path('delete_link/<int:pk>/', views.delete_link, name='delete_link'),
    path('add_project/', views.add_project, name='add_project'),
    path('delete_project/<int:pk>/', views.delete_project, name='delete_project'),
    path('add_experience/', views.add_experience, name='add_experience'),
    path('delete_experience/<int:pk>/', views.delete_experience, name='delete_experience'),
    path('add_education/', views.add_education, name='add_education'),
    path('delete_education/<int:pk>/', views.delete_education, name='delete_education'),
    path('add_note/', views.add_note, name='add_note'),
    path('toggle_note/<int:pk>/', views.toggle_note, name='toggle_note'),
    path('delete_note/<int:pk>/', views.delete_note, name='delete_note'),
    path('contact/', views.contact_submit, name='contact'),
    path('api/calendar_todos/', views.calendar_todos, name='calendar_todos'),
    path('api/calendar_todos/add/', views.add_calendar_todo, name='add_calendar_todo'),
    path('api/calendar_todos/<int:pk>/toggle/', views.toggle_calendar_todo, name='toggle_calendar_todo'),
    path('api/calendar_todos/<int:pk>/delete/', views.delete_calendar_todo, name='delete_calendar_todo'),
]
