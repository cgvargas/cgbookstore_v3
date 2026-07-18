"""
Testes para as views do módulo Product Analytics.

Cobre:
- Acesso restrito a usuários do staff
- Carregamento do template do dashboard
- Filtros de períodos de data e fallback seguro
"""
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone


class DashboardViewTest(TestCase):
    """Testa a view de dashboard analítico do produto."""

    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.url = reverse("product_analytics:dashboard")

        # Usuários com níveis de permissão distintos
        self.staff_user = self.User.objects.create_user(
            username="admin_analytics",
            password="adminpassword",
            email="admin@test.com",
            is_staff=True
        )
        self.normal_user = self.User.objects.create_user(
            username="leitor_comum",
            password="userpassword",
            email="user@test.com",
            is_staff=False
        )

    def test_anonymous_user_redirected_to_login(self):
        """Usuário anônimo não deve ter acesso e deve ser redirecionado para o login."""
        response = self.client.get(self.url)
        # Deve redirecionar para a página de login do admin
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_normal_user_redirected_to_login(self):
        """Usuário autenticado comum (sem is_staff) deve ser bloqueado."""
        self.client.login(username="leitor_comum", password="userpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_staff_user_access_allowed(self):
        """Usuário do staff deve conseguir acessar com sucesso."""
        self.client.login(username="admin_analytics", password="adminpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product_analytics/dashboard.html")
        self.assertIn("metrics", response.context)
        self.assertIn("charts", response.context)

    def test_date_range_filtering_success(self):
        """Verifica se os parâmetros de data são passados e interpretados corretamente."""
        self.client.login(username="admin_analytics", password="adminpassword")
        response = self.client.get(self.url, {
            "start_date": "2026-07-01",
            "end_date": "2026-07-15"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["start_date"], "2026-07-01")
        self.assertEqual(response.context["end_date"], "2026-07-15")

    def test_invalid_dates_fallback(self):
        """Verifica se datas inválidas acionam o fallback padrão seguro."""
        self.client.login(username="admin_analytics", password="adminpassword")
        response = self.client.get(self.url, {
            "start_date": "data-invalida",
            "end_date": "2026-99-99"
        })
        self.assertEqual(response.status_code, 200)
        # Deve cair no fallback padrão de 30 dias atrás
        today = timezone.localdate()
        expected_start = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(response.context["start_date"], expected_start)
