from django.db.transaction import atomic
from django.test import TransactionTestCase
from tests.django_dummy_app.models import Article, Source
from tests.django_dummy_app.documents import ArticleDocument


class ArticleTestCase(TransactionTestCase):

    def setUp(self) -> None:
        try:
            ArticleDocument._index.delete()
        except Exception:
            pass
        ArticleDocument.init()

    def test_article_creation(self):
        # ArticleDocument.init()
        with atomic():
            source = Source.objects.create(domain="nu.nl", name="Nu.nl")
            article = Article.objects.create(url="https://nu.nl", source=source)

            article.title = "test"
            article.save(update_fields=["title"])

        with atomic():
            article.title = "test1"
            article.save(update_fields=["title"])

        with atomic():
            for i in range(0, 100):
                Article.objects.create(url=f"https://nu.nl/{i}", source=source)

        with atomic():
            source.name = "nu.nl - 1"
            source.save(update_fields=['name'])

        with atomic():
            source.delete()

        # with atomic():
        #     Article.objects.all().delete()

    def tearDown(self) -> None:
        try:
            ArticleDocument._index.delete()
        except Exception:
            pass