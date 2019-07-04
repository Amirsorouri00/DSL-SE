from django.urls import include, path
from .views import ui_one, ui_two, search

app_name = 'client_side'

urlpatterns = [
    path('form/', include(([
        path('1', ui_one, name='template_test_one'),
        path('2', ui_two, name='template_test_two'),
        path('', search, name='page'),
        
    ], 'client_side'), namespace='form')),

    path('rest/', include(([

        # path('', SingleEvent.as_view(), name='single_event_view'),
        
    ], 'client_side'), namespace='rest')),
]