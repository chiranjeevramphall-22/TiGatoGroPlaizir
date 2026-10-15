from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


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