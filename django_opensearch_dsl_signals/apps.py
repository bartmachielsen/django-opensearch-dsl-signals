from django.apps import AppConfig
from django.conf import settings


class DjangoOpensearchDSLSignalsApp(AppConfig):
    """Django Opensearch DSL Appconfig."""

    name = "django_opensearch_dsl_signals"
    verbose_name = "django-opensearch-dsl-signals"
    signal_processor = None

    def ready(self):
        """Autodiscover documents and register signals."""

        # Set up the signal processor.
        if not self.signal_processor:
            from django_opensearch_dsl_signals.signals import DocumentSignalProcessor
            self.signal_processor = DocumentSignalProcessor()
            # Disable auto sync as we will handle it manually.
            setattr(settings, "OPENSEARCH_DSL_AUTOSYNC", False)
