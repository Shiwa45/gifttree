from django import forms
from django.contrib.auth import get_user_model
from .models import Order
from apps.users.models import Address

User = get_user_model()


class CheckoutAddressForm(forms.Form):
    """Form for entering shipping address during checkout"""
    
    # Choose existing address or add new
    use_existing = forms.BooleanField(required=False, initial=False)
    existing_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        empty_label="Select an existing address"
    )
    
    # New address fields
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    address_line_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address Line 1'
        })
    )
    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address Line 2 (Optional)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        })
    )
    pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pincode'
        })
    )
    
    save_address = forms.BooleanField(
        required=False,
        initial=False,
        label="Save this address for future orders"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['existing_address'].queryset = Address.objects.filter(
                user=user, 
                is_active=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        use_existing = cleaned_data.get('use_existing')
        existing_address = cleaned_data.get('existing_address')
        
        if use_existing and not existing_address:
            raise forms.ValidationError("Please select an existing address or enter a new one.")
        
        if not use_existing:
            required_fields = ['full_name', 'phone', 'address_line_1', 'city', 'state', 'pincode']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required.')
        
        return cleaned_data


class CheckoutDeliveryForm(forms.Form):
    """Form for selecting delivery options"""
    
    DELIVERY_CHOICES = [
        ('same_day', 'Same Day Delivery - FREE'),
        ('midnight', 'Midnight Delivery - ₹99'),
        ('fixed_time', 'Fixed Time Delivery - ₹49'),
    ]
    
    delivery_option = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect,
        initial='same_day'
    )
    
    delivery_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    delivery_time_slot = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Time Slot'),
            ('09:00-12:00', '9:00 AM - 12:00 PM'),
            ('12:00-15:00', '12:00 PM - 3:00 PM'),
            ('15:00-18:00', '3:00 PM - 6:00 PM'),
            ('18:00-21:00', '6:00 PM - 9:00 PM'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special instructions for delivery?',
            'rows': 3
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_option = cleaned_data.get('delivery_option')
        
        if delivery_option == 'fixed_time':
            if not cleaned_data.get('delivery_date'):
                self.add_error('delivery_date', 'Please select a delivery date.')
            if not cleaned_data.get('delivery_time_slot'):
                self.add_error('delivery_time_slot', 'Please select a time slot.')
        
        return cleaned_data


class CheckoutPaymentForm(forms.Form):
    """Form for payment method selection"""
    
    PAYMENT_CHOICES = [
        ('online', 'Pay Online (Cards, UPI, Wallets)'),
        ('cod', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='online'
    )
    
    billing_same_as_shipping = forms.BooleanField(
        required=False,
        initial=True,
        label="Billing address same as shipping address"
    )
    
    # Billing address fields (only if different from shipping)
    billing_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    billing_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    billing_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    billing_address_line_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address Line 1'
        })
    )
    billing_address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address Line 2 (Optional)'
        })
    )
    billing_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    billing_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        })
    )
    billing_pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pincode'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        billing_same = cleaned_data.get('billing_same_as_shipping')
        
        if not billing_same:
            required_fields = [
                'billing_name', 'billing_email', 'billing_phone',
                'billing_address_line_1', 'billing_city', 'billing_state', 'billing_pincode'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required.')
        
        return cleaned_data


class CouponForm(forms.Form):
    """Form for applying coupon codes"""
    coupon_code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )