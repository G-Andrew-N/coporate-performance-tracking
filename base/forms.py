from django import forms
from .models import PropertyListing

class PropertyListingForm(forms.ModelForm):
    class Meta:
        model = PropertyListing
        fields = [
            'propertyType', 'location', 'address', 'floors', 'coveredArea',
            'electricityStatus', 'bathroomCount', 'bedroomCount', 'bookingAmount',
            'price', 'status', 'image'
        ]