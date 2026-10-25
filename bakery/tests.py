from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cake, CustomisationOption, Order, Profile


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


# =====================================================
# CUSTOMER ORDER HISTORY TESTS
# Verifies authentication, customer privacy, history
# status filtering and the sidebar order counts.
# =====================================================
class CustomerOrderHistoryTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='history-customer',
            password='test-password',
        )
        Profile.objects.create(
            user=self.customer,
            full_name='History Customer',
        )

        self.other_customer = User.objects.create_user(
            username='other-customer',
            password='test-password',
        )
        Profile.objects.create(
            user=self.other_customer,
            full_name='Other Customer',
        )

        self.cake = Cake.objects.create(
            name='Celebration Cake',
            description='A test cake',
            base_price=1200,
        )
        self.page_url = reverse('order_history')

    def create_order(self, customer, status):
        return Order.objects.create(
            customer=customer,
            cake=self.cake,
            size='Medium (8")',
            total_price=1200,
            status=status,
        )

    def test_login_is_required(self):
        response = self.client.get(self.page_url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.page_url}",
        )

    def test_history_shows_only_logged_in_customers_past_orders(self):
        delivered = self.create_order(self.customer, 'delivered')
        cancelled = self.create_order(self.customer, 'cancelled')
        current = self.create_order(self.customer, 'baking')
        other = self.create_order(self.other_customer, 'delivered')
        self.client.force_login(self.customer)

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'ORDER #TG-{delivered.id}')
        self.assertContains(response, f'ORDER #TG-{cancelled.id}')
        self.assertNotContains(response, f'ORDER #TG-{current.id}')
        self.assertNotContains(response, f'ORDER #TG-{other.id}')

    def test_delivered_filter_excludes_cancelled_orders(self):
        delivered = self.create_order(self.customer, 'delivered')
        cancelled = self.create_order(self.customer, 'cancelled')
        self.client.force_login(self.customer)

        response = self.client.get(self.page_url, {'status': 'delivered'})

        self.assertContains(response, f'ORDER #TG-{delivered.id}')
        self.assertNotContains(response, f'ORDER #TG-{cancelled.id}')
        self.assertEqual(response.context['active_filter'], 'delivered')

    def test_sidebar_counts_current_and_past_orders(self):
        self.create_order(self.customer, 'ready')
        self.create_order(self.customer, 'delivered')
        self.create_order(self.customer, 'cancelled')
        self.client.force_login(self.customer)

        response = self.client.get(self.page_url)

        self.assertEqual(response.context['current_orders_count'], 1)
        self.assertEqual(response.context['history_count'], 2)
