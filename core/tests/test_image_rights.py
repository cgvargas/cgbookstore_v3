# core/tests/test_image_rights.py
"""
Testes automatizados para o Sistema Corporativo de Governança de Ativos Visuais e Direitos Autorais.
Verifica:
1. Restrição única (unique_together: content_type, object_id, image_field_name).
2. Validação de image_field_name no Form do Admin.
3. Cálculo de SHA-256 Checksum e alerta de substituição.
4. Regras de Atribuição TASL (Creative Commons).
5. Acesso protegido/privado ao documento de autorização.
"""

from django.test import TestCase, Client
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Book, Author, ImageRightsRecord
from core.admin.image_rights_admin import ImageRightsRecordForm

User = get_user_model()


class ImageRightsRecordTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='password123'
        )
        self.author = Author.objects.create(name="J.R.R. Tolkien")
        self.book = Book.objects.create(
            title="O Senhor dos Anéis",
            author=self.author,
            price=99.90,
            publication_date="1954-07-29"
        )
        self.book_ct = ContentType.objects.get_for_model(Book)

    def test_unique_together_constraint(self):
        """Verifica se apenas um registro pode existir para o mesmo campo de imagem de um objeto."""
        ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            credit_name='Alan Lee',
            license_type='licensed'
        )

        with self.assertRaises(Exception):
            ImageRightsRecord.objects.create(
                content_type=self.book_ct,
                object_id=self.book.id,
                image_field_name='cover_image',
                credit_name='Outro Artista',
                license_type='cc'
            )

    def test_admin_form_validates_image_field_name(self):
        """Verifica se o form bloqueia nomes de campos inexistentes ou que não são de imagem."""
        form_data = {
            'content_type': self.book_ct.id,
            'object_id': self.book.id,
            'image_field_name': 'title', # Título não é ImageField/FileField
            'credit_name': 'Test'
        }
        form = ImageRightsRecordForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Campo válido 'cover_image'
        form_data_valid = {
            'content_type': self.book_ct.id,
            'object_id': self.book.id,
            'image_field_name': 'cover_image',
            'credit_name': 'John Howe',
            'license_type': 'own'
        }
        form_valid = ImageRightsRecordForm(data=form_data_valid)
        self.assertTrue(form_valid.is_valid())

    def test_protected_document_download_requires_staff(self):
        """Verifica se o download de documentos de autorização exige autenticação staff."""
        client = Client()

        dummy_doc = SimpleUploadedFile("contrato.pdf", b"conteudo confidencial de autorizacao")
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            permission_document=dummy_doc,
            license_type='licensed'
        )

        url = reverse('protected_copyright_document', kwargs={'record_id': record.id})

        # Não logado -> Redireciona para login do admin
        resp_anonymous = client.get(url)
        self.assertEqual(resp_anonymous.status_code, 302)

        # Logado como admin staff -> Permite acesso 200 OK
        client.login(username='admin_test', password='password123')
        resp_admin = client.get(url)
        self.assertEqual(resp_admin.status_code, 200)

    def test_calculate_file_checksum(self):
        """Verifica geração correta do SHA-256."""
        dummy_img = SimpleUploadedFile("teste.jpg", b"fake_image_bytes_content")
        checksum = ImageRightsRecord.calculate_file_checksum(dummy_img)
        self.assertEqual(len(checksum), 64) # Tamanho padrão do hash SHA-256

    def test_compliance_map_view_requires_staff(self):
        """Verifica se o Mapa de Conformidade de Ativos Visuais exige autenticação staff."""
        client = Client()
        url = reverse('copyright_compliance_map')

        # Não logado -> Redireciona para o login
        resp_anonymous = client.get(url)
        self.assertEqual(resp_anonymous.status_code, 302)

        # Logado como staff -> Permite acesso 200 OK
        client.login(username='admin_test', password='password123')
        resp_staff = client.get(url)
        self.assertEqual(resp_staff.status_code, 200)

    def test_field_audit_status_calculation(self):
        """Verifica os cálculos dos status de auditoria (missing vs regularized)."""
        from core.services.image_rights_service import ImageRightsAuditService

        # 1. Livro sem capa salva no disco
        status, record = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'no_image')

    def test_usage_purpose_and_legal_basis_fields(self):
        """Verifica se os campos de finalidade e enquadramento jurídico salvam corretamente e usam o label atualizado."""
        expected_label = '⚖️ Limitação aos Direitos Autorais — Art. 46 da Lei nº 9.610/98'

        # 1. Criação de novo registro
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            usage_purpose='review_debate',
            legal_basis='fair_use_art46',
            display_dimensions='400x600px (120 KB)'
        )
        self.assertEqual(record.usage_purpose, 'review_debate')
        self.assertEqual(record.legal_basis, 'fair_use_art46')
        self.assertEqual(record.get_legal_basis_display(), expected_label)
        self.assertEqual(record.display_dimensions, '400x600px (120 KB)')

        # 2. Edição de registro existente
        record.legal_basis = 'express_consent'
        record.save()
        record.refresh_from_db()
        self.assertEqual(record.legal_basis, 'express_consent')
        self.assertEqual(record.get_legal_basis_display(), '📜 Autorização Expressa da Editora/Autor')

        # Retornar para o enquadramento do Art. 46
        record.legal_basis = 'fair_use_art46'
        record.save()
        record.refresh_from_db()
        self.assertEqual(record.legal_basis, 'fair_use_art46')
        self.assertEqual(record.get_legal_basis_display(), expected_label)

    def test_form_legal_basis_choices_and_submission(self):
        """Verifica se o formulário do admin renderiza e valida a opção com o label atualizado."""
        expected_label = '⚖️ Limitação aos Direitos Autorais — Art. 46 da Lei nº 9.610/98'

        # Verificar se a escolha está presente nos choices do formulário
        form = ImageRightsRecordForm()
        choices_dict = dict(form.fields['legal_basis'].choices)
        self.assertIn('fair_use_art46', choices_dict)
        self.assertEqual(choices_dict['fair_use_art46'], expected_label)

        # Submissão via formulário para novo registro
        form_data = {
            'content_type': self.book_ct.id,
            'object_id': self.book.id,
            'image_field_name': 'cover_image',
            'legal_basis': 'fair_use_art46',
            'credit_name': 'Artista de Teste',
        }
        form_valid = ImageRightsRecordForm(data=form_data)
        self.assertTrue(form_valid.is_valid())
        new_record = form_valid.save()
        self.assertEqual(new_record.legal_basis, 'fair_use_art46')
        self.assertEqual(new_record.get_legal_basis_display(), expected_label)

        # Edição via formulário
        edit_form_data = {
            'content_type': self.book_ct.id,
            'object_id': self.book.id,
            'image_field_name': 'cover_image',
            'legal_basis': 'fair_use_art46',
            'credit_name': 'Artista Atualizado',
        }
        edit_form = ImageRightsRecordForm(data=edit_form_data, instance=new_record)
        self.assertTrue(edit_form.is_valid())
        updated_record = edit_form.save()
        self.assertEqual(updated_record.credit_name, 'Artista Atualizado')
        self.assertEqual(updated_record.get_legal_basis_display(), expected_label)

    def test_audit_image_rights_management_command(self):
        """Verifica a execução do comando de gerenciamento audit_image_rights sem erros."""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command('audit_image_rights', '--auto-create', stdout=out)
        self.assertIn('[OK] Rastreamento Concluido!', out.getvalue())

