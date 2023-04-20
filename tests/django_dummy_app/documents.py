from typing import Union

from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry
from tests.django_dummy_app.models import Article, Source, ArticleKeyword, Author


@registry.register_document
class ArticleDocument(Document):
    """Article document."""

    source = fields.ObjectField(properties={
        "domain": fields.TextField(),
        "name": fields.TextField()
    })

    keywords = fields.NestedField(properties={
        "keyword": fields.TextField()
    })
    authors = fields.NestedField(properties={
        "first_name": fields.KeywordField(),
        "last_name": fields.KeywordField()
    })

    class Django:
        model = Article
        fields = [
            "url",
            "title",
            "snippet"
        ]
        related_models = [
            Source,
            ArticleKeyword,
            Author
        ]

    class Index:
        """Elasticsearch Index Data."""

        name = "articles"
        settings = {"number_of_shards": 2, "number_of_replicas": 1}

    def get_instances_from_related(self, related_instance: Union[Source]):
        """Get related instances from related instance."""
        if isinstance(related_instance, Source):
            return related_instance.articles.all(), "source"
