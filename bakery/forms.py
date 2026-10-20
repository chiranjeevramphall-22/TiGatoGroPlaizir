from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Cake, CustomisationOption


class SignupForm(UserCreationForm):
    # Extra fields not part of the default User model
    full_name = forms.CharField(max_length=200, label="Full Name")
    email = forms.EmailField(label="Email Address")
    phone_number = forms.CharField(max_length=20, label="Phone Number", required=False)
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), label="Delivery Address", required=False)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone_number', 'delivery_address', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create the linked Profile
            Profile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone_number=self.cleaned_data['phone_number'],
                delivery_address=self.cleaned_data['delivery_address'],
            )
        return user

# =====================================================
# CAKE FORM (admin Cake Catalogue page)
# Used for both "New Cake Design" and "Edit".
# @k.d
# =====================================================
class CakeForm(forms.ModelForm):
    is_available = forms.TypedChoiceField(
        label="Availability",
        choices=[(True, 'Available'), (False, 'Unavailable')],
        coerce=lambda value: value == 'True',
        initial=True,
    )
 
    class Meta:
        model = Cake
        fields = ('name', 'base_price', 'photo', 'is_available', 'description')
        labels = {
            'name': 'Cake Name',
            'base_price': 'Base Price (Rs)',
            'photo': 'Design/Reference Image',
        }
        widgets = {
            'base_price': forms.NumberInput(attrs={'min': 0, 'step': '1', 'placeholder': '0'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
 
    def clean_base_price(self):
        price = self.cleaned_data['base_price']
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
 
    def clean(self):
        cleaned = super().clean()
        # A brand-new cake needs a picture, otherwise the cards on the site show a broken image
        has_existing_image = bool(self.instance.pk and (self.instance.photo or self.instance.image))
        if not cleaned.get('photo') and not has_existing_image:
            self.add_error('photo', "Please upload a photo of the cake.")
        return cleaned


# =====================================================
# CUSTOMISATION OPTION FORM
# Validates an option entered on the admin Customisation
# Options page. The selected category is supplied by the
# view, so an administrator only needs to enter its name.
# =====================================================
class CustomisationOptionForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        strip=True,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Add new option...',
            'autocomplete': 'off',
        }),
    )

    class Meta:
        model = CustomisationOption
        fields = ('name',)

    def __init__(self, *args, category, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        # Server-side validation prevents duplicates even when
        # they use different capitalisation, e.g. Vanilla/vanilla.
        duplicate_exists = CustomisationOption.objects.filter(
            category=self.category,
            name__iexact=name,
        ).exists()
        if duplicate_exists:
            raise forms.ValidationError(
                "This option already exists in the selected category."
            )

        return name

    def save(self, commit=True):
        option = super().save(commit=False)
        option.category = self.category
        if commit:
            option.save()
        return option