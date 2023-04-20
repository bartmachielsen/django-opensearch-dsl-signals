import logging
from time import sleep

from django.db.transaction import atomic
from django.test import TransactionTestCase
from tests.django_dummy_app.models import Article, Source, ArticleKeyword, Author
from tests.django_dummy_app.documents import ArticleDocument

logger = logging.getLogger(__name__)


class ArticleTestCase(TransactionTestCase):

    def setUp(self) -> None:
        # Check if index exists
        if ArticleDocument._index.exists():
            try:
                ArticleDocument._index.delete()
            except Exception:
                pass
        ArticleDocument.init()

    def test_simple_article_creation(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)

        article_document = ArticleDocument.get(id=article.id)
        self.assertIsNotNone(article_document)

        self.assertEqual(
            article_document.doc.url,
            "https://example.com"
        )
        self.assertEqual(
            article_document.doc.source.name,
            "example.com"
        )

    def test_source_update(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)

        with atomic():
            source.name = "example.com"
            source.save(update_fields=["name"])

        self.assertEqual(
            ArticleDocument.get(id=article.id).doc.source.name,
            "example.com"
        )

    def test_merged_updates(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)

            article.url = "https://example.com/1"
            article.save(update_fields=["url"])

        self.assertEqual(
            ArticleDocument.get(id=article.id).doc.url,
            "https://example.com/1"
        )

    def test_delete(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article1 = Article.objects.create(url="https://example.com/1", source=source)
            article2 = Article.objects.create(url="https://example.com/2", source=source)

        self.assertEqual(
            ArticleDocument.search().execute().hits.total.value,
            2
        )
        with atomic():
            article1.delete()

        self.assertEqual(
            ArticleDocument.search().execute().hits.total.value,
            1
        )

        article2.delete()
        self.assertEqual(
            ArticleDocument.search().execute().hits.total.value,
            0
        )

    def test_batch_create_delete(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            for i in range(0, 100):
                Article.objects.create(
                    url=f"https://example.com/{i}",
                    source=source
                )

            self.assertEqual(
                ArticleDocument.search().execute().hits.total.value,
                0
            )

        self.assertEqual(
            ArticleDocument.search().execute().hits.total.value,
            100
        )

        source.delete()

        self.assertEqual(
            ArticleDocument.search().execute().hits.total.value,
            0
        )

    def test_article_keyword_addition(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)
            keyword1 = ArticleKeyword.objects.create(article=article, keyword="test")

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.keywords), 1)
        self.assertEqual(article_document.doc.keywords[0]["keyword"], "test")

    def test_article_keyword_update(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)
            keyword1 = ArticleKeyword.objects.create(article=article, keyword="test")

        with atomic():
            keyword1.keyword = "updated_test"
            keyword1.save(update_fields=["keyword"])

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.keywords), 1)
        self.assertEqual(article_document.doc.keywords[0]["keyword"], "updated_test")

    def test_article_keyword_deletion(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)
            keyword1 = ArticleKeyword.objects.create(article=article, keyword="test")

        with atomic():
            keyword1.delete()

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.keywords), 0)

    def test_batch_keyword_creation(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)
            for i in range(10):
                ArticleKeyword.objects.create(article=article, keyword=f"test-{i}")

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.keywords), 10)
        keywords = [k["keyword"] for k in article_document.doc.keywords]
        for i in range(10):
            self.assertIn(f"test-{i}", keywords)

    def test_article_author_addition(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            author = Author.objects.create(first_name="John", last_name="Doe")
            article = Article.objects.create(url="https://example.com", source=source)
            article.authors.add(author)

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.authors), 1)
        self.assertEqual(article_document.doc.authors[0].first_name, "John")
        self.assertEqual(article_document.doc.authors[0].last_name, "Doe")

    def test_article_author_update(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            author = Author.objects.create(first_name="John", last_name="Doe")
            article = Article.objects.create(url="https://example.com", source=source)
            article.authors.add(author)

        with atomic():
            author.first_name = "Jane"
            author.last_name = "Smith"
            author.save(update_fields=["first_name", "last_name"])

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.authors), 1)
        self.assertEqual(article_document.doc.authors[0].first_name, "Jane")
        self.assertEqual(article_document.doc.authors[0].last_name, "Smith")

    def test_article_author_deletion(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            author = Author.objects.create(first_name="John", last_name="Doe")
            article = Article.objects.create(url="https://example.com", source=source)
            article.authors.add(author)

        with atomic():
            article.authors.remove(author)

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.authors), 0)

    def test_article_author_deletion_other(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            author = Author.objects.create(first_name="John", last_name="Doe")
            article = Article.objects.create(url="https://example.com", source=source)
            article.authors.add(author)

        with atomic():
            author.delete()

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.authors), 0)

    def test_batch_author_creation(self):
        with atomic():
            source = Source.objects.create(domain="example.com", name="example.com")
            article = Article.objects.create(url="https://example.com", source=source)
            for i in range(5):
                author = Author.objects.create(first_name=f"John-{i}", last_name=f"Doe-{i}")
                article.authors.add(author)

        article_document = ArticleDocument.get(id=article.id)
        self.assertEqual(len(article_document.doc.authors), 5)
        for i in range(5):
            author_data = {
                "first_name": f"John-{i}",
                "last_name": f"Doe-{i}",
            }
            self.assertIn(author_data, [author.to_dict() for author in article_document.doc.authors])

    def tearDown(self) -> None:
        if ArticleDocument._index.exists():
            try:
                ArticleDocument._index.delete()
            except Exception:
                pass