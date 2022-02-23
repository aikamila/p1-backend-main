from django.apps import AppConfig


class PostsCommentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts_comments'

    def ready(self):
        import posts_comments.signals
