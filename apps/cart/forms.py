from django import forms
from apps.products.models import Product, ProductVariant


class AddToCartForm(forms.Form):
    """Form for adding products to cart"""
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    variant_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': '1',
            'value': '1'
        })
    )

    # Customization fields
    custom_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter name to be written',
            'maxlength': '50'
        })
    )
    custom_message = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your custom message',
            'rows': '3',
            'maxlength': '200'
        })
    )
    custom_flavor = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}, choices=[
            ('', '-- Select Flavor --'),
            ('Vanilla', 'Vanilla'),
            ('Chocolate', 'Chocolate'),
            ('Strawberry', 'Strawberry'),
            ('Butterscotch', 'Butterscotch'),
            ('Black Forest', 'Black Forest'),
            ('Pineapple', 'Pineapple'),
            ('Red Velvet', 'Red Velvet'),
            ('Other', 'Other'),
        ])
    )
    custom_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean_product_id(self):
        product_id = self.cleaned_data.get('product_id')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            self.cleaned_data['product'] = product
            return product_id
        except Product.DoesNotExist:
            raise forms.ValidationError("Product not found or inactive")

    def clean_variant_id(self):
        variant_id = self.cleaned_data.get('variant_id')
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, is_active=True)
                self.cleaned_data['variant'] = variant
                return variant_id
            except ProductVariant.DoesNotExist:
                raise forms.ValidationError("Variant not found or inactive")
        return None
