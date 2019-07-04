from django.apps import AppConfig


class ElasticAppConfig(AppConfig):
    name = 'elastic_app'
    def ready(self):
        import elastic_app.signals