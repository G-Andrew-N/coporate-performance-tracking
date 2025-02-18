from django import forms
from .models import PropertyListing, Salez

class PropertyListingForm(forms.ModelForm):
    class Meta:
        model = PropertyListing
        fields = [
            'propertyType', 'location', 'address', 'floors', 'coveredArea',
            'electricityStatus', 'bathroomCount', 'bedroomCount', 'bookingAmount',
            'price', 'status', 'image'
        ]

class SaleForm(forms.ModelForm):
    class Meta:
        model = Salez
        fields = ['buyer_name', 'buyer_id', 'buyer_email', 'buyer_tel', 'buyer_address',
                  'payment_method', 'seller_name', 'seller_tel', 'seller_email', 'seller_address',
                  'ownership_verification', 'sale_date', 'sale_price', 'title_insurance',
                  'legal_fees', 'deposit', 'closing_date']