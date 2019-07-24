__author__ = ["Amir Hossein Sorouri", "Anthony Sigogne"]
__copyright__ = "Copyright 2019, DSL-SE"
__email__ = ["amirsorouri26@gmail.com", "anthony@byprog.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

from django.urls import include, path
from .views import ui_one, ui_two, search, another_search

app_name = 'client_side'

urlpatterns = [
    path('form/', include(([
        path('1', ui_one, name='template_test_one'),
        path('2', ui_two, name='template_test_two'),
        # path('', search, name='page'),
        path('', another_search, name='page'),
        
    ], 'client_side'), namespace='form')),

    path('rest/', include(([
        
    ], 'client_side'), namespace='rest')),
]