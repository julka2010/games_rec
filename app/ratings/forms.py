from django import forms
from django.utils.translation import gettext as _

class PlayerSearchForm(forms.Form):
    search_query = forms.CharField(
        label=_('Enter your boardgamegeek.com username'),
        max_length=255,
    )
