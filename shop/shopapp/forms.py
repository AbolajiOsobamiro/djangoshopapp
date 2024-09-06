from django import forms
from . import models


class productUploadForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'description', 'image', 'price', 'stock', 'category']
        labels = {
            'item_name': 'Item name',
            'item_description': 'Description',
            'image': 'Item image',
            'price': 'Item Price',
            'stock': 'Amount Available',
            'category': 'Category'
        }
       
