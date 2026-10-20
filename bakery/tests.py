from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CustomisationOption


# =====================================================
# ADMIN CUSTOMISATION OPTIONS TESTS
# Verifies staff permissions, create/read/delete behavior,
# duplicate validation and customer-page integration.
# =====================================================
class AdminCustomisationOptionsTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.customer = User.objects.create_user(
            username='customer',
            password='test-password',
        )
        self.page_url = reverse('admin_customisation_options')

    def test_staff_can_open_options_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Customisation Options')

    def test_customer_is_redirected_from_options_page(self):
        self.client.force_login(self.customer)
        response = self.client.get(self.page_url)

        self.assertRedirects(
            response,
            f"{reverse('admin_login')}?next={self.page_url}",
        )

    def test_staff_can_add_an_option(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.page_url, {
            'category': 'flavour',
            'name': 'Pistachio',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomisationOption.objects.filter(
            category='flavour',
            name='Pistachio',
        ).exists())

    def test_duplicate_option_is_rejected_case_insensitively(self):
        CustomisationOption.objects.create(category='flavour', name='Pistachio')
        self.client.force_login(self.staff_user)

        response = self.client.post(self.page_url, {
            'category': 'flavour',
            'name': 'pistachio',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        self.assertEqual(
            CustomisationOption.objects.filter(
                category='flavour',
                name__iexact='pistachio',
            ).count(),
            1,
        )

    def test_staff_can_delete_an_option(self):
        option = CustomisationOption.objects.create(
            category='decoration',
            name='Sugar Pearls',
        )
        self.client.force_login(self.staff_user)

        response = self.client.post(reverse(
            'admin_customisation_option_delete',
            args=[option.id],
        ))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CustomisationOption.objects.filter(pk=option.id).exists())

    def test_customer_page_displays_database_option(self):
        CustomisationOption.objects.create(category='filling', name='Lotus Cream')

        response = self.client.get(reverse('customise'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lotus Cream')