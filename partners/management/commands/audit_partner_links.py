"""Auditoria somente leitura dos parceiros e links comerciais legados."""

from collections import Counter

from django.core.management.base import BaseCommand, CommandError

from core.models import Book
from partners.models import AffiliatePartner
from partners.services.affiliate_service import AffiliateService
from partners.services.url_validation_service import URLValidationService


class Command(BaseCommand):
    help = (
        'Audita parceiros e URLs comerciais sem modificar registros. '
        'Use --fail-on-findings em automações para retornar código 1 quando houver achados.'
    )

    ISSUE_METADATA = {
        'partner_not_registered': ('Relacionamento', 'Alto', 'Livro com parceiro não cadastrado'),
        'partner_inactive': ('Disponibilidade', 'Alto', 'Parceiro inativo'),
        'https_required': ('Transporte', 'Crítico', 'URL usando HTTP ou esquema inseguro'),
        'domain_not_allowed': ('Domínio', 'Crítico', 'Domínio fora da allowlist'),
        'malformed_url': ('Integridade', 'Alto', 'URL malformada'),
        'malformed_hostname': ('Integridade', 'Alto', 'Hostname malformado'),
        'control_characters': ('Segurança', 'Crítico', 'URL com caracteres de controle'),
        'encoded_control_characters': ('Segurança', 'Crítico', 'URL com controles codificados'),
        'ambiguous_url': ('Segurança', 'Crítico', 'URL ambígua'),
        'shortened_url': ('Segurança', 'Crítico', 'Link encurtado'),
        'embedded_credentials': ('Segurança', 'Crítico', 'URL contendo credenciais'),
        'ip_host_not_allowed': ('Segurança', 'Crítico', 'URL usando endereço IP'),
        'port_not_allowed': ('Segurança', 'Crítico', 'URL usando porta não permitida'),
        'invalid_port': ('Integridade', 'Alto', 'URL usando porta inválida'),
        'tracking_id_mismatch': ('Tracking', 'Alto', 'Tracking ID diferente do parceiro'),
        'tracking_without_partner_id': ('Tracking', 'Médio', 'Tracking presente sem ID administrativo'),
        'partner_without_url': ('Completude', 'Alto', 'Livro com parceiro, mas sem URL'),
        'url_without_partner': ('Completude', 'Alto', 'Livro com URL, mas sem parceiro'),
        'partner_without_allowlist': ('Configuração', 'Alto', 'Parceiro sem allowlist efetiva'),
    }

    SUGGESTIONS = {
        'partner_not_registered': 'Cadastrar o parceiro no Django Admin com nome/slug compatíveis com o livro.',
        'partner_inactive': 'Revisar o cadastro e ativar somente parceiros aptos a receber tráfego.',
        'https_required': 'Substituir o destino por uma URL HTTPS oficial do parceiro.',
        'domain_not_allowed': 'Corrigir a URL ou declarar explicitamente o host legítimo na allowlist.',
        'malformed_url': 'Substituir por uma URL absoluta e estruturalmente válida.',
        'malformed_hostname': 'Corrigir o hostname; não usar espaços, curingas ou labels inválidos.',
        'control_characters': 'Remover caracteres de controle e recadastrar a URL a partir da fonte oficial.',
        'encoded_control_characters': 'Remover sequências de controle codificadas e recadastrar a URL oficial.',
        'ambiguous_url': 'Remover barras invertidas e usar a representação canônica HTTPS.',
        'shortened_url': 'Resolver manualmente o destino final e cadastrar a URL oficial não encurtada.',
        'embedded_credentials': 'Remover usuário/senha da URL e revisar a origem do dado.',
        'ip_host_not_allowed': 'Usar o domínio oficial declarado na allowlist, nunca um IP literal.',
        'port_not_allowed': 'Usar a porta HTTPS padrão, sem porta explícita não autorizada.',
        'invalid_port': 'Corrigir ou remover a porta inválida da URL.',
        'tracking_id_mismatch': 'Remover o tracking legado divergente; o AffiliateService inserirá o ID administrativo.',
        'tracking_without_partner_id': 'Cadastrar o Tracking ID no parceiro ou remover o parâmetro legado da URL.',
        'partner_without_url': 'Cadastrar a URL oficial do livro ou remover o parceiro até o dado estar completo.',
        'url_without_partner': 'Associar o nome do parceiro correspondente ao domínio da URL.',
        'partner_without_allowlist': 'Cadastrar url_base e/ou PARTNER_COMMERCIAL_CONFIG com hosts explícitos.',
    }

    SEVERITY_ORDER = ('Crítico', 'Alto', 'Médio', 'Baixo')

    def add_arguments(self, parser):
        parser.add_argument(
            '--fail-on-findings',
            action='store_true',
            help='Retorna código 1 quando a auditoria encontrar incompatibilidades.',
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Omite os detalhes por registro e exibe somente o resumo e as sugestões.',
        )

    def handle(self, *args, **options):
        counts = Counter()
        details = []

        partners = list(AffiliatePartner.objects.all().order_by('nome'))
        books = Book.objects.only(
            'id', 'title', 'purchase_partner_name', 'purchase_partner_url'
        ).order_by('id')

        self.stdout.write(self.style.MIGRATE_HEADING('AUDITORIA DE LINKS DE PARCEIROS'))
        self.stdout.write('Modo: SOMENTE LEITURA (nenhum registro será alterado)')

        for partner in partners:
            self._audit_partner(partner, counts, details)

        total_books = 0
        books_with_commercial_data = 0
        for book in books.iterator():
            total_books += 1
            partner_name = (book.purchase_partner_name or '').strip()
            url = (book.purchase_partner_url or '').strip()

            if not partner_name and not url:
                continue

            books_with_commercial_data += 1
            if partner_name and not url:
                self._add_finding(
                    'partner_without_url',
                    f'Livro #{book.id} "{book.title}": parceiro="{partner_name}", URL ausente.',
                    counts,
                    details,
                )
                continue

            if url and not partner_name:
                self._add_finding(
                    'url_without_partner',
                    f'Livro #{book.id} "{book.title}": URL informada sem parceiro.',
                    counts,
                    details,
                )
                self._collect_validation_issues(book, URLValidationService.validate(url), counts, details)
                continue

            partner = AffiliateService.find_partner_by_name(partner_name, active_only=False)
            if not partner:
                self._add_finding(
                    'partner_not_registered',
                    f'Livro #{book.id} "{book.title}": parceiro "{partner_name}" não cadastrado.',
                    counts,
                    details,
                )
                self._collect_validation_issues(book, URLValidationService.validate(url), counts, details)
                continue

            if not partner.ativo:
                self._add_finding(
                    'partner_inactive',
                    f'Livro #{book.id} "{book.title}": parceiro "{partner.nome}" está inativo.',
                    counts,
                    details,
                )

            validation = URLValidationService.validate(url, partner=partner)
            self._collect_validation_issues(book, validation, counts, details)
            self._audit_tracking(book, partner, url, counts, details)

        self._print_report(
            partners=len(partners),
            total_books=total_books,
            books_with_commercial_data=books_with_commercial_data,
            counts=counts,
            details=details,
            summary_only=options['summary_only'],
        )

        if details and options['fail_on_findings']:
            raise CommandError('Auditoria concluída com incompatibilidades (código de saída 1).')

    def _audit_partner(self, partner, counts, details):
        allowed_domains = URLValidationService.get_allowed_domains(partner)
        if not allowed_domains:
            self._add_finding(
                'partner_without_allowlist',
                f'Parceiro #{partner.id} "{partner.nome}" não possui domínios permitidos.',
                counts,
                details,
            )

        if partner.url_base:
            validation = URLValidationService.validate(partner.url_base, partner=partner)
            for issue in validation.issues:
                if issue.code == 'missing_url':
                    continue
                self._add_finding(
                    issue.code,
                    f'Parceiro #{partner.id} "{partner.nome}": URL base: {issue.message}',
                    counts,
                    details,
                )

    def _audit_tracking(self, book, partner, url, counts, details):
        tracking_values = URLValidationService.get_tracking_values(url, partner)
        expected_tracking = (partner.tracking_id or '').strip()
        if expected_tracking and any(value != expected_tracking for value in tracking_values):
            self._add_finding(
                'tracking_id_mismatch',
                f'Livro #{book.id} "{book.title}": tracking presente não corresponde ao parceiro "{partner.nome}".',
                counts,
                details,
            )
        elif tracking_values and not expected_tracking:
            self._add_finding(
                'tracking_without_partner_id',
                f'Livro #{book.id} "{book.title}": tracking presente, mas o parceiro "{partner.nome}" não possui ID administrativo.',
                counts,
                details,
            )

    def _collect_validation_issues(self, book, validation, counts, details):
        for issue in validation.issues:
            if issue.code == 'missing_url':
                continue
            self._add_finding(
                issue.code,
                f'Livro #{book.id} "{book.title}": {issue.message} Host="{validation.hostname or "N/A"}".',
                counts,
                details,
            )

    @staticmethod
    def _add_finding(code, message, counts, details):
        counts[code] += 1
        details.append((code, message))

    def _print_report(
        self,
        *,
        partners,
        total_books,
        books_with_commercial_data,
        counts,
        details,
        summary_only,
    ):
        category_counts = Counter()
        severity_counts = Counter()
        for code, count in counts.items():
            category, severity, _label = self.ISSUE_METADATA.get(code, ('Outros', 'Médio', code))
            category_counts[category] += count
            severity_counts[severity] += count

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('RESUMO EXECUTIVO'))
        self.stdout.write(f'Parceiros cadastrados: {partners}')
        self.stdout.write(f'Livros examinados: {total_books}')
        self.stdout.write(f'Livros com dados comerciais: {books_with_commercial_data}')
        self.stdout.write(f'Total de ocorrências: {sum(counts.values())}')
        for severity in self.SEVERITY_ORDER:
            if severity_counts[severity]:
                self.stdout.write(f'- Severidade {severity}: {severity_counts[severity]}')

        if details and not summary_only:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('INCOMPATIBILIDADES ENCONTRADAS'))
            for code, message in details:
                category, severity, label = self.ISSUE_METADATA.get(code, ('Outros', 'Médio', code))
                self.stdout.write(f'- [{severity} | {category} | {label}] {message}')
        elif not details:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Nenhuma incompatibilidade encontrada.'))

        if counts:
            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING('CONTAGEM POR CATEGORIA'))
            for category in sorted(category_counts):
                self.stdout.write(f'- {category}: {category_counts[category]}')

            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING('CONTAGEM POR TIPO'))
            for code in self.ISSUE_METADATA:
                if counts[code]:
                    self.stdout.write(f'- {self.ISSUE_METADATA[code][2]}: {counts[code]}')

            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING('SUGESTÕES DE CORREÇÃO'))
            for code in self.ISSUE_METADATA:
                if counts[code]:
                    self.stdout.write(f'- {self.ISSUE_METADATA[code][2]}: {self.SUGGESTIONS[code]}')

        self.stdout.write('')
        self.stdout.write(
            'Código de saída: 0 (auditoria executada). '
            'Com --fail-on-findings: 0 sem achados, 1 com achados.'
        )
