from django.db import models
from localflavor.us.models import USStateField, USZipCodeField

from apps.core.models import CoreModel
from apps.customers.models import Customer


class Location(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='addresses',
    )
    street_address = models.TextField(default="")
    city = models.TextField(blank=True)
    state = models.TextField(null=True, blank=True)
    zipcode = USZipCodeField()
    is_active = models.BooleanField(default=True)

    STATE_ABBREVIATION_MAP = {
        'Alabama': 'AL',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
    }

    def __str__(self) -> str:
        return f'{self.street_address} {self.city}, {self.state}, {self.zipcode}'

    @property
    def is_complete(self):
        return all([
            self.street_address is not None,
            self.city is not None,
            self.state is not None,
            self.zipcode is not None,
        ])
