from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.utils import timezone
from model_utils import Choices
from django_softdelete.models import SoftDeleteModel


from apps.core.models import CoreModel
from apps.customers.models import Customer
from apps.recipes.models import Ingredient

from .libs import PersonMixin


class CustomerChild(SoftDeleteModel, PersonMixin, CoreModel):
    """
    Contains properties and methods pertaining to a customer's child object.
    """
    SEX_CHOICES = Choices('male', 'female', 'their', 'none')

    first_name = models.TextField()
    last_name = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.TextField(choices=SEX_CHOICES, null=True, blank=True)
    parent = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='children',
    )
    allergies = models.ManyToManyField(to=Ingredient, blank=True)
    allergy_severity = models.TextField(choices=Choices('none', 'allergic'), default='none')

    class Meta(CoreModel.Meta):
        verbose_name_plural = 'Customer Children'

    def __str__(self) -> str:
        return f'{self.first_name} - parent: {self.parent}'

    @property
    def age_in_months(self):
        current_date = timezone.now().today()
        relative_age = relativedelta(current_date, self.birth_date)
        return (relative_age.years * 12) + relative_age.months

    def _create_cart(self):
        from apps.carts.models import Cart
        Cart.objects.create(customer=self.parent, customer_child=self,)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        with transaction.atomic():
            if self.is_new():
                transaction.on_commit(self._create_cart)

            super().save(force_insert, force_update, using, update_fields)
