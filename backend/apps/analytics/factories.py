from factory import lazy_attribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class PixelFactory(DjangoModelFactory):
    name = FuzzyText(prefix='pixel-')

    @lazy_attribute
    def tag_script(self):
        return '<script>console.log("hello world")</script>'

    class Meta:
        model = 'analytics.Pixel'
