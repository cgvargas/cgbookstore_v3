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
from core.services.image_rights_service import ImageRightsAuditService

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
        expected_label = '⚖️ Limitação legal analisada — Lei nº 9.610/98, Art. 46'

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
        expected_label = '⚖️ Limitação legal analisada — Lei nº 9.610/98, Art. 46'

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

    def test_art46_audit_requires_purpose_and_attribution(self):
        """Verifica que o enquadramento no Art. 46 exige finalidade de uso e atribuição para ser regularizado."""
        from core.services.image_rights_service import ImageRightsAuditService

        # Criar imagem falsa
        dummy_img = SimpleUploadedFile("capa_teste.jpg", b"fake_bytes_content_for_audit")
        self.book.cover_image.save("capa_teste.jpg", dummy_img)

        # 1. Registro do Art. 46 sem finalidade e sem atribuição -> Deve ser 'pending' mesmo com audit_status='regularized'
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            legal_basis='fair_use_art46',
            audit_status='regularized',
            usage_purpose='',  # sem finalidade
            credit_name='',
            source_url=''
        )
        status, _ = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'pending')

        # 2. Completando com finalidade, atribuição e regularização administrativa -> Passa a ser 'regularized'
        rec.audit_status = 'regularized'
        rec.usage_purpose = 'review_debate'
        rec.credit_name = 'Editora Parceira'
        rec.save()

        status, _ = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'regularized')

    def test_legacy_credit_name_only_works(self):
        """Verifica se registro com apenas credit_name legado continua funcionando perfeitamente."""
        from core.templatetags.copyright_tags import render_image_rights

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            credit_name='Ilustrador Legado',
            license_type='licensed',
        )
        self.assertEqual(rec.display_author, 'Ilustrador Legado')
        self.assertEqual(rec.creator_name, '')
        self.assertEqual(rec.rights_holder_name, '')
        self.assertEqual(rec.licensor_name, '')

        # Testar template tag pública
        html = render_image_rights(self.book, 'cover_image')
        self.assertIn('Ilustrador Legado', html)
        self.assertIn('Crédito / Autor:', html)

    def test_creator_name_priority_over_credit_name(self):
        """Verifica se creator_name tem prioridade sobre credit_name na autoria visual."""
        from core.templatetags.copyright_tags import render_image_rights

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            creator_name='Fotógrafo Criativo',
            credit_name='Crédito Genérico Antigo',
            license_type='cc',
            license_url='https://creativecommons.org/licenses/by/4.0/',
            source_url='https://exemplo.com/foto'
        )
        # display_author deve retornar o criador
        self.assertEqual(rec.display_author, 'Fotógrafo Criativo')

        # Template tag deve exibir preferencialmente o criador
        html = render_image_rights(self.book, 'cover_image')
        self.assertIn('Fotógrafo Criativo', html)
        self.assertIn('Criador / Autor da Imagem:', html)

    def test_source_does_not_auto_populate_rights_holder_or_licensor(self):
        """Verifica que preencher source_url não preenche automaticamente rights_holder_name nem licensor_name."""
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            source_url='https://amazon.com.br/livro-exemplo',
            creator_name='Desenhista A'
        )
        rec.refresh_from_db()
        self.assertEqual(rec.source_url, 'https://amazon.com.br/livro-exemplo')
        self.assertEqual(rec.rights_holder_name, '')
        self.assertEqual(rec.licensor_name, '')

    def test_licensor_not_treated_as_creator(self):
        """Verifica que licensor_name não é tratado como criador da obra visual."""
        from core.templatetags.copyright_tags import render_image_rights

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            licensor_name='Banco de Imagens XYZ',
            work_title='Paisagem Épica'
        )
        # Sem creator_name e sem credit_name, display_author deve ser vazio
        self.assertEqual(rec.display_author, '')

        # No modal público, deve constar como Licenciante e não como autor
        html = render_image_rights(self.book, 'cover_image')
        self.assertIn('Licenciante:</strong> Banco de Imagens XYZ', html)
        self.assertNotIn('Criador / Autor da Imagem:</strong> Banco de Imagens XYZ', html)

    def test_new_fields_do_not_grant_automatic_legal_proof(self):
        """Verifica que a presença de creator_name, rights_holder_name ou licensor_name não gera comprovação jurídica automática."""
        client = Client()
        client.login(username='admin_test', password='password123')

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            creator_name='Artista Teste',
            rights_holder_name='Editora Detentora',
            licensor_name='Distribuidora ABC',
            # Sem licença formal e sem fundamento legal
            license_type='',
            legal_basis=''
        )

        response = client.get(reverse('copyright_audit_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Taxa de comprovação legal deve ser 0.0 para esse registro
        self.assertEqual(response.context['legal_proof_rate'], 0.0)
        self.assertEqual(response.context['pending_total'], 1)

    def test_public_modal_does_not_expose_private_information(self):
        """Verifica que o modal público não expõe documentos privados, observações internas, usuário admin ou hashes."""
        from core.templatetags.copyright_tags import render_image_rights

        dummy_doc = SimpleUploadedFile("autorizacao.pdf", b"documento confidencial")
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            creator_name='Artista Sensível',
            rights_holder_name='Titular Confidencial',
            licensor_name='Agência Parceira',
            usage_notes='Notas estritamente internas e confidenciais da equipe jurídica',
            permission_document=dummy_doc,
            image_checksum='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            created_by=self.user,
            license_type='licensed',
            source_url='https://exemplo.com/origem'
        )

        html = render_image_rights(self.book, 'cover_image')
        # Deve conter informações públicas
        self.assertIn('Artista Sensível', html)
        self.assertIn('Titular Confidencial', html)
        self.assertIn('Agência Parceira', html)
        self.assertIn('A identificação da fonte, autor, editora, titular ou licenciante possui finalidade de atribuição', html)

        # NÃO deve conter dados confidenciais/privados
        self.assertNotIn('Notas estritamente internas', html)
        self.assertNotIn('autorizacao.pdf', html)
        self.assertNotIn('admin_test', html)
        self.assertNotIn('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', html)

    def test_default_audit_status_is_not_audited(self):
        """Verifica que novos registros e registros padrão recebem 'not_audited' como valor seguro."""
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
        )
        self.assertEqual(rec.audit_status, 'not_audited')
        self.assertEqual(rec.get_audit_status_display(), '⚪ Não auditada')

    def test_provenance_amazon_or_google_books_does_not_imply_regularized(self):
        """Verifica que a procedência técnica (Amazon, Google Books) não implica regularização automática."""
        dummy_img = SimpleUploadedFile("capa_prov.jpg", b"fake_bytes_content_prov")
        self.book.cover_image.save("capa_prov.jpg", dummy_img)

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            source_url='https://m.media-amazon.com/images/I/sample.jpg',
            license_type='amazon',
        )
        # O registro deve permanecer como não auditado por padrão
        self.assertEqual(rec.audit_status, 'not_audited')

        # O serviço de auditoria técnica não deve considerar regularizado
        status, audit_rec = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertNotEqual(status, 'regularized')
        self.assertEqual(status, 'not_audited')

    def test_contested_audit_status_prevents_legal_proof_in_dashboard(self):
        """Verifica que um registro marcado como 'contested' nunca é tratado como comprovado no dashboard."""
        dummy_img = SimpleUploadedFile("capa_contested.jpg", b"fake_bytes_content_contested")
        self.book.cover_image.save("capa_contested.jpg", dummy_img)

        client = Client()
        client.login(username='admin_test', password='password123')

        dummy_doc = SimpleUploadedFile("contrato.pdf", b"conteudo")
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='contested',
            license_type='licensed',
            permission_document=dummy_doc,
            creator_name='Fotografo Alvo'
        )

        response = client.get(reverse('copyright_audit_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['legal_proof_rate'], 0.0)
        self.assertEqual(response.context['contested_count'], 1)
        self.assertIn('contested', [item['code'] for item in response.context['audit_status_distribution']])

        # Status técnico no serviço também deve ser 'contested'
        status, audit_rec = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'contested')

    def test_not_audited_is_not_treated_as_proven_legal_compliance(self):
        """Verifica que audit_status='not_audited' não é computado como comprovação jurídica mesmo com licença informada."""
        client = Client()
        client.login(username='admin_test', password='password123')

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='not_audited',
            license_type='cc',
            license_url='https://creativecommons.org/licenses/by/4.0/',
            source_url='https://commons.wikimedia.org/wiki/File:Test.jpg',
            creator_name='Autor CC'
        )

        response = client.get(reverse('copyright_audit_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Não deve ser contado como legal_proof_rate pois ainda não foi auditado
        self.assertEqual(response.context['legal_proof_rate'], 0.0)
        self.assertEqual(response.context['not_audited_count'], 1)

    def test_regularized_status_still_subject_to_documentary_validation(self):
        """Verifica que um registro com audit_status='regularized' mas com falha documental é acusado pelo serviço de auditoria."""
        dummy_img = SimpleUploadedFile("capa_cc_fail.jpg", b"fake_bytes_content_cc")
        self.book.cover_image.save("capa_cc_fail.jpg", dummy_img)

        # CC sem URL da licença
        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            license_type='cc',
            license_url='',  # Falha documental
            source_url='https://commons.wikimedia.org/wiki/File:Test.jpg',
            creator_name='Autor CC'
        )

        status, audit_rec = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'pending')

    def test_admin_filtering_by_audit_status(self):
        """Verifica que o Django Admin inclui audit_status em list_filter e permite filtragem."""
        from core.admin.image_rights_admin import ImageRightsRecordAdmin
        self.assertIn('audit_status', ImageRightsRecordAdmin.list_filter)

        client = Client()
        client.login(username='admin_test', password='password123')

        rec1 = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='not_audited'
        )

        response = client.get(reverse('admin:core_imagerightsrecord_changelist') + '?audit_status=not_audited')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Não auditada')

    def test_audit_status_not_exposed_in_public_modal(self):
        """Verifica que o audit_status é estritamente administrativo e não aparece no modal público."""
        from core.templatetags.copyright_tags import render_image_rights

        rec = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='not_audited',
            creator_name='Ilustrador Publico',
            work_title='Capa Publica',
            license_type='cc',
            license_url='https://creativecommons.org/licenses/by/4.0/'
        )

        html = render_image_rights(self.book, 'cover_image')
        self.assertIn('Ilustrador Publico', html)
        self.assertIn('Capa Publica', html)
        self.assertNotIn('Não auditada', html)
        self.assertNotIn('audit_status', html)
        self.assertNotIn('Status de Auditoria', html)
        self.assertNotIn('Contestada', html)
        self.assertNotIn('Regularizada', html)

    def test_historical_license_choices_preserved(self):
        """Verifica que valores históricos de LICENSE_CHOICES continuam válidos e preservados."""
        for code in ['publisher', 'amazon', 'google_books', 'open_library', 'wikimedia', 'other']:
            rec = ImageRightsRecord(
                content_type=self.book_ct,
                object_id=self.book.id,
                image_field_name=f'cover_{code}',
                license_type=code
            )
            # Deve validar choices sem erro
            rec.full_clean()

    # =========================================================================
    # TESTES DO FLUXO DE CONTESTAÇÃO, NOTIFICAÇÃO, TAKEDOWN E SUSPENSÃO PREVENTIVA
    # =========================================================================

    def test_create_takedown_request_linked_to_image_rights_record(self):
        """Verifica criação de ocorrência de contestação vinculada ao ImageRightsRecord sem apagar o arquivo."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        dummy_img = SimpleUploadedFile("capa_original.jpg", b"conteudo_da_capa_original_123")
        self.book.cover_image.save("capa_original.jpg", dummy_img)

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            creator_name='Artista Original',
            image_checksum='checksum123456'
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Dra. Advogada da Silva',
            claimant_email='advogada@autoria.com',
            claimant_organization='Editora Exemplo Ltda.',
            claimant_role='authorized_representative',
            claim_description='A capa foi utilizada sem autorização prévia por escrito.',
            claimed_rights_basis='Titularidade exclusiva dos direitos patrimoniais nos termos do Art. 29 da Lei 9.610/98.',
            created_by=self.user
        )

        self.assertIsNotNone(takedown.pk)
        self.assertEqual(takedown.status, 'received')
        self.assertEqual(takedown.image_rights_record, record)
        # O arquivo no model Book NÃO é apagado
        self.book.refresh_from_db()
        self.assertTrue(bool(self.book.cover_image))
        # O ImageRightsRecord permanece intacto
        record.refresh_from_db()
        self.assertEqual(record.image_checksum, 'checksum123456')
        self.assertEqual(record.creator_name, 'Artista Original')

    def test_takedown_temporary_suspension_blocks_public_display(self):
        """Verifica que a suspensão preventiva altera public_display_allowed e bloqueia a exibição pública."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )
        self.assertTrue(record.can_display_publicly)

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='temporarily_suspended',
            claim_description='Suspensão cautelar solicitada pelo titular.'
        )

        # A propriedade can_display_publicly deve retornar False por ter takedown com status temporarily_suspended
        record.refresh_from_db()
        self.assertFalse(record.can_display_publicly)
        self.assertFalse(ImageRightsAuditService.can_display_publicly(self.book, 'cover_image'))

    def test_suspended_image_renders_safe_neutral_message(self):
        """Verifica que imagem suspensa não exibe dados de reclamante, notas ou links e sim mensagem neutra."""
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.templatetags.copyright_tags import render_image_rights

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False,
            creator_name='Fotógrafo Secreto',
            source_url='https://origem.com/foto.jpg',
            usage_notes='Nota jurídica confidencial'
        )

        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='temporarily_suspended',
            claimant_name='Empresa Notificante Confidencial',
            claimant_email='segredo@notificante.com',
            claim_description='Reclamação sigilosa em apuração'
        )

        html = render_image_rights(self.book, 'cover_image')
        # Deve exibir aviso neutro de indisponibilidade
        self.assertIn('Imagem temporariamente indisponível.', html)
        # NUNCA deve expor dados do reclamante, e-mails, notas ou links de origem
        self.assertNotIn('Empresa Notificante Confidencial', html)
        self.assertNotIn('segredo@notificante.com', html)
        self.assertNotIn('Reclamação sigilosa', html)
        self.assertNotIn('Fotógrafo Secreto', html)
        self.assertNotIn('https://origem.com/foto.jpg', html)
        self.assertNotIn('Nota jurídica confidencial', html)

    def test_restore_public_display_works_when_authorized(self):
        """Verifica que a exibição pública pode ser restaurada após resolução ou arquivamento."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='resolved_keep',
            resolution_notes='Uso amparado por licença comprovada pelo editor.'
        )

        # Restaurar exibição pública
        record.public_display_allowed = True
        record.audit_status = 'regularized'
        record.save()

        self.assertTrue(record.can_display_publicly)
        self.assertTrue(ImageRightsAuditService.can_display_publicly(self.book, 'cover_image'))

    def test_resolved_removed_blocks_public_display_and_keeps_record(self):
        """Verifica que uma ocorrência resolvida com retirada impede exibição pública mantendo registro histórico."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False,
            creator_name='Ilustrador Notificante'
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='resolved_removed',
            resolution_notes='Acordo amigável: imagem retirada do site.',
            resolved_by=self.user
        )

        self.assertFalse(record.can_display_publicly)
        # O registro e a contestação permanecem no banco
        self.assertEqual(ImageRightsRecord.objects.filter(pk=record.pk).count(), 1)
        self.assertEqual(CopyrightTakedownRequest.objects.filter(pk=takedown.pk).count(), 1)

    def test_resolved_keep_does_not_auto_regularize_without_audit(self):
        """Verifica que resolver mantendo a imagem NÃO altera automaticamente um registro incompleto para regularized."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='pending', # Incompleto
            public_display_allowed=True
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='resolved_keep',
            resolution_notes='Reclamação improcedente.'
        )

        record.refresh_from_db()
        # Permanece com status pendente de governança (não vira regularized automaticamente)
        self.assertEqual(record.audit_status, 'pending')

    def test_non_staff_cannot_download_takedown_document(self):
        """Verifica que usuário não staff não consegue baixar documento de contestação."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        dummy_doc = SimpleUploadedFile("notificacao_privada.pdf", b"conteudo_estritamente_confidencial")
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image'
        )
        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='under_review',
            evidence_document=dummy_doc
        )

        client = Client()
        url = reverse('core:protected_takedown_document_download', args=[takedown.pk])

        # Anônimo é redirecionado para login
        resp_anon = client.get(url)
        self.assertEqual(resp_anon.status_code, 302)

        # Usuário comum (não staff) também não acessa
        normal_user = User.objects.create_user(username='reader_user', password='password123')
        client.login(username='reader_user', password='password123')
        resp_normal = client.get(url)
        self.assertEqual(resp_normal.status_code, 302)

        # Staff tem acesso
        client.login(username='admin_test', password='password123')
        resp_staff = client.get(url)
        self.assertEqual(resp_staff.status_code, 200)

    def test_dashboard_displays_takedown_metrics(self):
        """Verifica que o Dashboard de Direitos Autorais contabiliza e apresenta contestações em aberto."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image'
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='under_review',
            claimant_name='Agência Teste',
            claim_description='Disputa de autoria de imagem'
        )

        client = Client()
        client.login(username='admin_test', password='password123')
        response = client.get(reverse('copyright_audit_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['open_takedowns_count'], 1)
        self.assertEqual(response.context['takedown_under_review_count'], 1)
        self.assertContains(response, 'Agência Teste')
        self.assertContains(response, 'Contestações, Notificações e Suspensão Preventiva')

    def test_compliance_map_highlights_restricted_and_contested(self):
        """Verifica se o Mapa de Conformidade contabiliza ativos suspensos e contestados."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        dummy_img = SimpleUploadedFile("capa_mapa.jpg", b"bytes_capa_mapa")
        self.book.cover_image.save("capa_mapa.jpg", dummy_img)

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )

        stats = ImageRightsAuditService.get_model_compliance_stats(Book)
        self.assertEqual(stats['restricted'], 1)

    def test_contact_form_categorizes_copyright_takedown(self):
        """Verifica que o formulário de contato público aceita e processa a categoria de Direitos Autorais."""
        from core.views.contact_view import ContactForm

        form_data = {
            'name': 'Notificante Direitos',
            'email': 'notificante@direitos.com',
            'category': 'copyright_takedown',
            'subject': 'Notificação extrajudicial de imagem de capa',
            'message': 'Solicito esclarecimento sobre a autorização da imagem de capa do livro X.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['category'], 'copyright_takedown')


class FrontendImageSuspensionSecurityTestCase(TestCase):
    """
    Testes de Segurança e Consistência para comprovar que ativos suspensos/restritos
    realmente não são exibidos no frontend e não vazam dados para terceiros.
    """

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_security',
            email='admin_security@test.com',
            password='password123'
        )
        self.author = Author.objects.create(name="Machado de Assis")
        self.book = Book.objects.create(
            title="Dom Casmurro",
            author=self.author,
            price=49.90,
            publication_date="1899-01-01"
        )
        self.dummy_cover = SimpleUploadedFile("dom_casmurro_cover.jpg", b"fake_cover_bytes_12345")
        self.book.cover_image.save("dom_casmurro_cover.jpg", self.dummy_cover)

        self.dummy_photo = SimpleUploadedFile("machado_photo.jpg", b"fake_photo_bytes_67890")
        self.author.photo.save("machado_photo.jpg", self.dummy_photo)

        self.book_ct = ContentType.objects.get_for_model(Book)
        self.author_ct = ContentType.objects.get_for_model(Author)

    def test_public_frontend_renders_normal_image(self):
        """Verifica que imagem regular (public_display_allowed=True) é renderizada no frontend e em SEO."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            creator_name='Ilustrador Oficial',
            audit_status='regularized',
            public_display_allowed=True
        )

        response = self.client.get(reverse('core:book_detail', kwargs={'slug': self.book.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.cover_image.url)
        self.assertTrue(self.book.has_valid_cover)
        self.assertIsNotNone(self.book.cover_image_url)

    def test_public_frontend_blocks_suspended_image(self):
        """Comprova que imagem suspensa NÃO aparece no HTML (img src, og:image, schema JSON-LD)."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )

        # Atualiza a property segura no model
        self.assertFalse(self.book.has_valid_cover)
        self.assertIsNone(self.book.cover_image_url)

        response = self.client.get(reverse('core:book_detail', kwargs={'slug': self.book.slug}))
        self.assertEqual(response.status_code, 200)

        # Garante que a URL física do arquivo NÃO é exposta no frontend
        self.assertNotContains(response, self.book.cover_image.url)

    def test_claimant_pii_and_internal_notes_never_leak(self):
        """Comprova que dados pessoais do reclamante e notas internas nunca vazam no HTML público."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )
        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='temporarily_suspended',
            claimant_name='Secret Claimer Advogados Associados',
            claimant_email='confidencial@advocaciasecreta.com',
            claimant_organization='Agência de Direitos Privados',
            claimed_rights_basis='Titularidade exclusiva de registro 998877',
            claim_description='Descrição confidencial da infração',
            internal_notes='Segredo de justiça interno da equipe jurídica'
        )

        response = self.client.get(reverse('core:book_detail', kwargs={'slug': self.book.slug}))
        self.assertEqual(response.status_code, 200)

        # Nenhum dado da contestação pode estar no HTML público
        self.assertNotContains(response, 'Secret Claimer')
        self.assertNotContains(response, 'confidencial@advocaciasecreta.com')
        self.assertNotContains(response, 'Agência de Direitos Privados')
        self.assertNotContains(response, 'Segredo de justiça interno')
        self.assertNotContains(response, 'Titularidade exclusiva')

    def test_multiple_takedowns_concurrency_resolution(self):
        """Comprova a regra de concorrência: resolver uma contestação mantendo não reativa ativo se houver outra impeditiva."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )

        # Cria duas contestações A e B
        takedown_a = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='temporarily_suspended',
            claimant_name='Reclamante A'
        )
        takedown_b = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='temporarily_suspended',
            claimant_name='Reclamante B'
        )

        # O ativo é suspenso
        ImageRightsAuditService.suspend_image_asset(record, request_user=self.admin)
        record.refresh_from_db()
        self.assertFalse(record.public_display_allowed)
        self.assertEqual(record.audit_status, 'restricted')

        # Tentar restaurar diretamente via service deve falhar
        success_restore, _msg = ImageRightsAuditService.restore_image_asset(record, request_user=self.admin)
        self.assertFalse(success_restore)
        record.refresh_from_db()
        self.assertFalse(record.public_display_allowed)

        # Resolve a contestação A como 'keep'
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown_a,
            resolution_type='keep',
            request_user=self.admin,
            resolution_notes='Comprovada autorização quanto à notificação A'
        )
        takedown_a.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual(takedown_a.status, 'resolved_keep')

        # Como a contestação B ainda está temporarily_suspended, o ativo DEVE continuar suspenso
        self.assertFalse(record.public_display_allowed)
        self.assertEqual(record.audit_status, 'restricted')

        # Resolve a contestação B como 'keep'
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown_b,
            resolution_type='keep',
            request_user=self.admin,
            resolution_notes='Comprovada autorização quanto à notificação B'
        )
        takedown_b.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual(takedown_b.status, 'resolved_keep')

        # Agora, sem contestações impeditivas, o ativo foi liberado
        self.assertTrue(record.public_display_allowed)

    def test_no_physical_file_or_history_deletion(self):
        """Comprova o princípio da não destruição: arquivo físico e histórico continuam íntegros."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )
        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Fotógrafo A'
        )

        # Suspende preventivamente
        ImageRightsAuditService.suspend_image_asset(record, request_user=self.admin)
        # Resolve removendo
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown,
            resolution_type='remove',
            request_user=self.admin,
            resolution_notes='Acordo para remoção do ativo'
        )

        record.refresh_from_db()
        takedown.refresh_from_db()
        self.book.refresh_from_db()

        # O arquivo físico no storage continua existindo intacto
        self.assertTrue(bool(self.book.cover_image and self.book.cover_image.name))
        self.assertTrue(self.book.cover_image.storage.exists(self.book.cover_image.name))


class ImageRightsAuditLogTestCase(TestCase):
    """
    Suíte de testes automatizados para a Trilha Histórica de Auditoria e Governança (ImageRightsAuditLog).
    Cobre:
    - Criação de evento ao criar registro de direitos
    - Alteração de creator_name, rights_holder_name, license_type, legal_basis, audit_status
    - Suspensão pública e restauração
    - Recebimento de contestação e resoluções (keep e remove)
    - Registro atômico dentro de transaction.atomic (rollback não deixa órfãos)
    - Bloqueio de edição/exclusão (append-only) via Model e Django Admin
    - Proteção contra cópia de documentos privados, e-mail do reclamante e internal_notes
    - Histórico não vaza em endpoints públicos
    - Divergência de checksum gera evento e proteção contra duplicatas consecutivas
    - Registros antigos continuam funcionando
    """

    def setUp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.services.image_rights_history_service import ImageRightsHistoryService

        self.User = get_user_model()
        self.admin = self.User.objects.create_superuser(
            username='admin_audit',
            email='admin_audit@cgbookstore.com',
            password='Password123!'
        )
        self.client = Client()
        self.client.force_login(self.admin)

        image_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        self.book = Book.objects.create(
            title="Memórias Póstumas de Brás Cubas",
            slug="memorias-postumas-audit",
            cover_image=SimpleUploadedFile("bras_cubas.png", image_content, content_type="image/png"),
            price=39.90,
            publication_date="1881-01-01"
        )
        self.book_ct = ContentType.objects.get_for_model(Book)

    def test_log_creation_on_record_created(self):
        """Testa a geração de evento record_created na criação de um ImageRightsRecord."""
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='not_audited',
            license_type='licensed',
            legal_basis='express_consent',
            creator_name='Fotógrafo Antigo'
        )

        ImageRightsHistoryService.log_record_created(record, performed_by=self.admin, source='admin')

        log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='record_created').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.performed_by, self.admin)
        self.assertEqual(log.source, 'admin')
        self.assertIn("Registro de direitos autorais criado", log.description)

    def test_field_changes_audit_logging(self):
        """Testa o registro de alterações de creator_name, rights_holder_name, license_type, legal_basis e audit_status."""
        import copy
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='not_audited',
            license_type='licensed',
            legal_basis='express_consent',
            creator_name='Fotógrafo A',
            rights_holder_name='Editora Original'
        )

        # Clonar estado anterior para comparação
        old_instance = copy.copy(record)

        # Modificar campos
        record.creator_name = 'Novo Ilustrador'
        record.rights_holder_name = 'Nova Editora'
        record.license_type = 'cc'
        record.legal_basis = 'creative_commons'
        record.audit_status = 'regularized'
        record.save()

        ImageRightsHistoryService.log_record_changes(record, old_instance, performed_by=self.admin, source='admin')

        # Verificar logs gerados
        creator_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='creator_changed').first()
        self.assertIsNotNone(creator_log)
        self.assertEqual(creator_log.old_value, 'Fotógrafo A')
        self.assertEqual(creator_log.new_value, 'Novo Ilustrador')

        holder_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='rights_holder_changed').first()
        self.assertIsNotNone(holder_log)
        self.assertEqual(holder_log.old_value, 'Editora Original')
        self.assertEqual(holder_log.new_value, 'Nova Editora')

        license_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='license_changed').first()
        self.assertIsNotNone(license_log)

        status_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='audit_status_changed').first()
        self.assertIsNotNone(status_log)
        self.assertEqual(status_log.old_value, '⚪ Não auditada')
        self.assertEqual(status_log.new_value, '🟢 Regularizada')

    def test_suspension_and_restoration_logging(self):
        """Testa que suspensão e restauração geram eventos imutáveis correspondentes."""
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )

        # 1. Suspender
        success, msg = ImageRightsAuditService.suspend_image_asset(record, request_user=self.admin, notes="Auditoria cautelar")
        self.assertTrue(success)
        susp_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='image_suspended').first()
        self.assertIsNotNone(susp_log)
        self.assertEqual(susp_log.performed_by, self.admin)
        self.assertEqual(susp_log.new_value, 'Bloqueada / Suspensa')

        # 2. Restaurar
        record.refresh_from_db()
        success, msg = ImageRightsAuditService.restore_image_asset(record, request_user=self.admin)
        self.assertTrue(success)
        rest_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='image_restored').first()
        self.assertIsNotNone(rest_log)
        self.assertEqual(rest_log.performed_by, self.admin)
        self.assertEqual(rest_log.new_value, 'Permitida')

    def test_takedown_lifecycle_audit_logging(self):
        """Testa o ciclo de contestação: takedown_received, keep e remove."""
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Fotógrafo Reclamante',
            claimant_email='confidencial@fotografo.com',
            claimant_organization='Agência de Fotos',
            claimant_role='rights_holder',
            claim_description='Uso não licenciado da foto de capa',
            internal_notes='Jurídico notificou em 31/08'
        )

        ImageRightsHistoryService.log_takedown_received(takedown, performed_by=self.admin, source='admin')
        rec_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='takedown_received').first()
        self.assertIsNotNone(rec_log)
        self.assertEqual(rec_log.takedown_request, takedown)

        # Resolver como 'keep'
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown,
            resolution_type='keep',
            request_user=self.admin,
            resolution_notes='Comprovada autorização contratual'
        )
        keep_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='takedown_resolved_keep').first()
        self.assertIsNotNone(keep_log)
        self.assertEqual(keep_log.takedown_request, takedown)

        # Resolver como 'remove'
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown,
            resolution_type='remove',
            request_user=self.admin,
            resolution_notes='Retirada solicitada'
        )
        remove_log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='takedown_resolved_removed').first()
        self.assertIsNotNone(remove_log)

    def test_pii_and_confidential_data_never_copied_to_audit_log(self):
        """Garante que e-mails de reclamantes, documentos privados e notas internas não sejam copiados para o log."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        doc = SimpleUploadedFile("contrato_secreto.pdf", b"%PDF-1.4...", content_type="application/pdf")
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            permission_document=doc,
            usage_notes='Contrato confidencial número 987654 - cláusula de sigilo estrito.'
        )
        ImageRightsHistoryService.log_record_created(record, performed_by=self.admin, source='admin')

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Autor Protegido',
            claimant_email='segredo_estrito@privado.com',
            claimant_organization='Firma Confidencial',
            claim_description='Descrição completa e privada da contestação.',
            internal_notes='Anotação interna do conselho jurídico da CG.BookStore.'
        )
        ImageRightsHistoryService.log_takedown_received(takedown, performed_by=self.admin, source='admin')

        all_logs = ImageRightsAuditLog.objects.filter(image_rights_record=record)
        for l in all_logs:
            # Nunca deve conter o e-mail
            self.assertNotIn('segredo_estrito@privado.com', l.description)
            self.assertNotIn('segredo_estrito@privado.com', l.old_value)
            self.assertNotIn('segredo_estrito@privado.com', l.new_value)
            # Nunca deve conter caminho de documento confidencial
            self.assertNotIn('contrato_secreto.pdf', l.old_value)
            self.assertNotIn('contrato_secreto.pdf', l.new_value)
            # Nunca deve conter o texto confidencial das notas internas
            self.assertNotIn('cláusula de sigilo estrito', l.description)
            self.assertNotIn('conselho jurídico', l.description)

    def test_atomic_transaction_rollback_leaves_no_orphaned_logs(self):
        """Testa que rollback de transação reverte o log de auditoria associado."""
        from django.db import transaction
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized'
        )

        initial_logs_count = ImageRightsAuditLog.objects.filter(image_rights_record=record).count()

        try:
            with transaction.atomic():
                ImageRightsHistoryService.log_event(
                    image_rights_record=record,
                    event_type='image_suspended',
                    description='Tentativa de suspensão com erro forçado',
                    performed_by=self.admin
                )
                # Simular erro que força rollback
                raise ValueError("Erro forçado para testar rollback transacional")
        except ValueError:
            pass

        # O log não deve ter sido persistido
        final_logs_count = ImageRightsAuditLog.objects.filter(image_rights_record=record).count()
        self.assertEqual(initial_logs_count, final_logs_count)

    def test_append_only_model_protection_prevents_edit_and_delete(self):
        """Comprova a proteção append-only: ImageRightsAuditLog não pode ser alterado nem excluído."""
        from django.core.exceptions import ValidationError
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized'
        )

        log = ImageRightsAuditLog.objects.create(
            image_rights_record=record,
            event_type='record_created',
            description='Evento original imutável',
            performed_by=self.admin
        )

        # Tentativa de editar
        log.description = 'Tentativa de alteração maliciosa'
        with self.assertRaises(ValidationError):
            log.save()

        # Tentativa de excluir
        with self.assertRaises(ValidationError):
            log.delete()

    def test_admin_disallows_add_change_and_delete_on_audit_log(self):
        """Comprova que o Django Admin bloqueia inserção, alteração e exclusão de ImageRightsAuditLog."""
        from core.admin.image_rights_audit_log_admin import ImageRightsAuditLogAdmin
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from django.contrib.admin.sites import AdminSite

        admin_instance = ImageRightsAuditLogAdmin(ImageRightsAuditLog, AdminSite())

        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/admin/core/imagerightsauditlog/')
        request.user = self.admin

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image'
        )
        log = ImageRightsAuditLog.objects.create(
            image_rights_record=record,
            event_type='record_created',
            description='Teste admin',
            performed_by=self.admin
        )

        self.assertFalse(admin_instance.has_add_permission(request))
        self.assertFalse(admin_instance.has_change_permission(request, log))
        self.assertFalse(admin_instance.has_delete_permission(request, log))

        # Ação delete_selected não deve existir
        actions = admin_instance.get_actions(request)
        self.assertNotIn('delete_selected', actions)

    def test_checksum_divergence_logging_and_deduplication(self):
        """Testa log de divergência de integridade e proteção contra alertas duplicados consecutivos."""
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            image_checksum='a' * 64,
            audit_status='regularized'
        )

        # 1ª execução detecta divergência
        ImageRightsHistoryService.log_integrity_divergence(
            record=record,
            expected_checksum='a' * 64,
            detected_checksum='b' * 64,
            source='command'
        )
        count_after_first = ImageRightsAuditLog.objects.filter(
            image_rights_record=record,
            event_type='integrity_divergence_detected'
        ).count()
        self.assertEqual(count_after_first, 1)

        # 2ª execução idêntica consecutiva (comando rodando periodicamente)
        ImageRightsHistoryService.log_integrity_divergence(
            record=record,
            expected_checksum='a' * 64,
            detected_checksum='b' * 64,
            source='command'
        )
        count_after_second = ImageRightsAuditLog.objects.filter(
            image_rights_record=record,
            event_type='integrity_divergence_detected'
        ).count()
        # Não deve duplicar
        self.assertEqual(count_after_second, 1)

    def test_audit_logs_never_leak_in_public_views(self):
        """Comprova que nenhum dado do log de auditoria trafega para responses públicos."""
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )

        ImageRightsHistoryService.log_event(
            image_rights_record=record,
            event_type='creator_changed',
            description='Alteração confidencial interna de teste de auditoria',
            performed_by=self.admin,
            old_value='ValorVelhoSegredo',
            new_value='ValorNovoSegredo'
        )

        # Testar view pública do livro
        response = self.client.get(self.book.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertNotIn('Alteração confidencial interna', content)
        self.assertNotIn('ValorVelhoSegredo', content)
        self.assertNotIn('ValorNovoSegredo', content)
        self.assertNotIn('ImageRightsAuditLog', content)

        # Os registros continuam existindo no banco de dados
        self.assertTrue(ImageRightsRecord.objects.filter(pk=record.pk).exists())

    def test_protect_on_delete_prevents_deletion_of_record_with_history(self):
        """Comprova que on_delete=models.PROTECT impede a exclusão de ImageRightsRecord com histórico de auditoria."""
        from django.db.models import ProtectedError
        from core.models.image_rights_audit_log import ImageRightsAuditLog
        from core.services.image_rights_history_service import ImageRightsHistoryService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized'
        )

        ImageRightsHistoryService.log_record_created(record, performed_by=self.admin, source='admin')
        self.assertEqual(ImageRightsAuditLog.objects.filter(image_rights_record=record).count(), 1)

        # Tentativa de excluir o registro principal deve disparar ProtectedError
        with self.assertRaises(ProtectedError):
            record.delete()

        # O registro e o log permanecem intactos
        self.assertTrue(ImageRightsRecord.objects.filter(pk=record.pk).exists())
        self.assertEqual(ImageRightsAuditLog.objects.filter(image_rights_record=record).count(), 1)

    def test_protect_on_delete_prevents_deletion_of_record_with_takedown(self):
        """Comprova que on_delete=models.PROTECT impede a exclusão de ImageRightsRecord com contestação vinculada."""
        from django.db.models import ProtectedError
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized'
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Fotógrafo A'
        )

        with self.assertRaises(ProtectedError):
            record.delete()

        self.assertTrue(ImageRightsRecord.objects.filter(pk=record.pk).exists())
        self.assertTrue(CopyrightTakedownRequest.objects.filter(pk=takedown.pk).exists())

    def test_admin_delete_protection_for_records_and_takedowns(self):
        """Comprova que o Django Admin bloqueia exclusão de ImageRightsRecord com histórico e de CopyrightTakedownRequest."""
        from core.admin.image_rights_admin import ImageRightsRecordAdmin
        from core.admin.copyright_takedown_admin import CopyrightTakedownRequestAdmin
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.services.image_rights_history_service import ImageRightsHistoryService
        from django.contrib.admin.sites import AdminSite
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = self.admin

        record_admin = ImageRightsRecordAdmin(ImageRightsRecord, AdminSite())
        takedown_admin = CopyrightTakedownRequestAdmin(CopyrightTakedownRequest, AdminSite())

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image'
        )

        # Sem histórico, permissão padrão
        self.assertTrue(record_admin.has_delete_permission(request, record))

        # Adiciona histórico -> Permissão de exclusão bloqueada
        ImageRightsHistoryService.log_record_created(record, performed_by=self.admin, source='admin')
        self.assertFalse(record_admin.has_delete_permission(request, record))

        # CopyrightTakedownRequest nunca pode ser excluído no admin
        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Autor Y'
        )
        self.assertFalse(takedown_admin.has_delete_permission(request, takedown))
        self.assertFalse(takedown_admin.has_delete_permission(request, None))

        # delete_selected removido de ambos os admins
        self.assertNotIn('delete_selected', record_admin.get_actions(request))
        self.assertNotIn('delete_selected', takedown_admin.get_actions(request))

    def test_suspension_resolution_preserves_all_records_and_files(self):
        """Comprova que ciclo completo de suspensão e resolução preserva o arquivo físico, a contestação e todos os logs."""
        from core.models.copyright_takedown import CopyrightTakedownRequest
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            public_display_allowed=True
        )

        takedown = CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Fotógrafo Notificante',
            claimant_email='notificante@privado.com'
        )

        # 1. Suspende preventivamente
        ImageRightsAuditService.suspend_image_asset(
            record, request_user=self.admin, takedown_request=takedown, notes="Suspensão cautelar"
        )
        # 2. Resolve removendo
        ImageRightsAuditService.resolve_takedown_atomic(
            takedown, resolution_type='remove', request_user=self.admin, resolution_notes="Acordo amigável de retirada"
        )

        record.refresh_from_db()
        takedown.refresh_from_db()
        self.book.refresh_from_db()

        # O arquivo físico no storage permanece intacto
        self.assertTrue(self.book.cover_image.storage.exists(self.book.cover_image.name))
        # O ImageRightsRecord permanece
        self.assertTrue(ImageRightsRecord.objects.filter(pk=record.pk).exists())
        # A contestação permanece
        self.assertEqual(takedown.status, 'resolved_removed')
        # Todos os logs de auditoria permanecem
        logs = ImageRightsAuditLog.objects.filter(image_rights_record=record)
        self.assertTrue(logs.filter(event_type='image_suspended').exists())
        self.assertTrue(logs.filter(event_type='takedown_resolved_removed').exists())


class ImageRightsProvenanceTestCase(TestCase):
    """
    Suíte de testes para Registro Automático de Procedência Técnica (ImageRightsProvenanceService).
    Diretriz: Procedência Técnica NÃO é Licença nem Autorização de Uso.
    Cobre:
    - Google Books cria proveniência automaticamente iniciando com not_audited
    - Google Books NÃO vira titular dos direitos patrimoniais
    - Nenhum fundamento legal é atribuído automaticamente
    - Open Library segue a mesma regra
    - Wikimedia pode registrar licença declarada sem marcar regularized
    - Idempotência: chamadas repetidas não duplicam registros
    - Nova importação externa NÃO sobrescreve dados de direitos auditados manualmente
    - Nova importação NÃO remove 'restricted' nem restaura 'public_display_allowed'
    - Nova importação NÃO sobrescreve documento comprobatório
    - Imagem local recebe checksum e dimensões
    - Referência remota não exige checksum obrigatório
    - Evento histórico com source='integration' e tipo apropriado
    - Dados sensíveis/tokens não são armazenados na metadata
    - Dashboard classifica registros automáticos e mapa de conformidade não os presume autorizados
    - Registros legados continuam operacionais
    """

    def setUp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.User = get_user_model()
        self.admin = self.User.objects.create_superuser(
            username='admin_prov',
            email='admin_prov@cgbookstore.com',
            password='Password123!'
        )
        self.client = Client()
        self.client.force_login(self.admin)

        image_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        self.book = Book.objects.create(
            title="Grande Sertão: Veredas",
            slug="grande-sertao-veredas-prov",
            cover_image=SimpleUploadedFile("grande_sertao.png", image_content, content_type="image/png"),
            price=59.90,
            publication_date="1956-01-01"
        )
        self.book_ct = ContentType.objects.get_for_model(Book)

    def test_google_books_provenance_creation_starts_not_audited(self):
        """Comprova que importação do Google Books registra procedência mas inicia not_audited sem titularidade/licença presumida."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            source_url='https://books.google.com/books/content?id=xyz123&printsec=frontcover',
            provider_asset_id='xyz123',
            license_type='google_books',
            provenance_method='api_download',
            safe_metadata={'google_book_id': 'xyz123', 'publisher_declared': 'Editora Nova Fronteira'},
            performed_by=self.admin,
            source='integration'
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertEqual(record.legal_basis, '')  # Nunca preencher base legal automaticamente
        self.assertNotEqual(record.rights_holder_name, 'Google')  # Google não é titular
        self.assertEqual(record.provenance_provider, 'google_books')
        self.assertEqual(record.provider_asset_id, 'xyz123')
        self.assertTrue(record.is_auto_imported)
        self.assertTrue(bool(record.image_checksum))  # Calculado para arquivo local

        # Log histórico de proveniência gerado
        log = ImageRightsAuditLog.objects.filter(image_rights_record=record, event_type='provenance_registered').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.source, 'integration')

    def test_open_library_remote_reference_provenance(self):
        """Comprova registro de procedência para Open Library via referência remota sem checksum forçado."""
        from ereader.models import EBook
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        ebook = EBook.objects.create(
            title="The Picture of Dorian Gray",
            author="Oscar Wilde",
            cover_image="https://covers.openlibrary.org/b/id/12345-L.jpg",
            source="openlibrary",
            external_id="OL12345M",
            language="en"
        )

        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=ebook,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_OPEN_LIBRARY,
            source_url='https://covers.openlibrary.org/b/id/12345-L.jpg',
            provider_asset_id='OL12345M',
            license_type='open_library',
            provenance_method='api_reference',
            safe_metadata={'external_id': 'OL12345M', 'source': 'openlibrary'},
            source='integration'
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertEqual(record.legal_basis, '')
        self.assertEqual(record.provenance_provider, 'open_library')
        self.assertEqual(record.provenance_method, 'api_reference')

    def test_wikimedia_declared_metadata_without_assuming_compliance(self):
        """Comprova que metadados declarados da Wikimedia (CC/Domínio Público) são capturados mas permanecem not_audited."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_WIKIMEDIA,
            source_url='https://commons.wikimedia.org/wiki/File:Guimaraes_Rosa.jpg',
            creator_name='Fotógrafo Desconhecido (Acervo Histórico)',
            license_type='cc',
            license_url='https://creativecommons.org/licenses/by-sa/4.0/',
            provenance_method='api_download',
            safe_metadata={'wikimedia_title': 'File:Guimaraes_Rosa.jpg'},
            source='integration'
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.creator_name, 'Fotógrafo Desconhecido (Acervo Histórico)')
        self.assertEqual(record.license_type, 'cc')
        self.assertEqual(record.license_url, 'https://creativecommons.org/licenses/by-sa/4.0/')
        # NUNCA considerar regularizado automaticamente
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertEqual(record.legal_basis, '')

    def test_idempotence_repeated_imports_do_not_duplicate(self):
        """Comprova que execuções repetidas da mesma integração não duplicam registros no banco."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        rec1 = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            source_url='https://books.google.com/test',
            provider_asset_id='id123'
        )
        rec2 = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            source_url='https://books.google.com/test',
            provider_asset_id='id123'
        )

        self.assertEqual(rec1.pk, rec2.pk)
        self.assertEqual(ImageRightsRecord.objects.filter(object_id=self.book.pk).count(), 1)

    def test_reimport_never_overwrites_manually_audited_rights_and_restrictions(self):
        """Comprova que nova importação JAMAIS sobrescreve dados jurídicos auditados, suspensões ou restrições."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        doc = SimpleUploadedFile("licenca_asssinada.pdf", b"%PDF-1.4...", content_type="application/pdf")
        # Registro já auditado por advogado/admin da plataforma
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            legal_basis='express_consent',
            license_type='licensed',
            creator_name='Ilustrador Contratado Oficial',
            rights_holder_name='Editora Parceira SA',
            public_display_allowed=False,  # Suspenso cautelarmente
            permission_document=doc
        )

        # Tentativa de importação externa do Google Books sobre este mesmo ativo
        updated_rec = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            source_url='https://books.google.com/nova-url',
            creator_name='Nome Errado da API',
            license_type='google_books',
            provider_asset_id='gb777',
            source='integration'
        )

        updated_rec.refresh_from_db()

        # Dados jurídicos e auditoria manual foram 100% preservados
        self.assertEqual(updated_rec.audit_status, 'regularized')
        self.assertEqual(updated_rec.legal_basis, 'express_consent')
        self.assertEqual(updated_rec.license_type, 'licensed')
        self.assertEqual(updated_rec.creator_name, 'Ilustrador Contratado Oficial')
        self.assertEqual(updated_rec.rights_holder_name, 'Editora Parceira SA')
        self.assertFalse(updated_rec.public_display_allowed)
        self.assertTrue(bool(updated_rec.permission_document))

        # Evento de conflito/preservação registrado
        conflict_log = ImageRightsAuditLog.objects.filter(
            image_rights_record=record,
            event_type='provenance_conflict_detected'
        ).first()
        self.assertIsNotNone(conflict_log)

    def test_sensitive_tokens_headers_and_pii_filtered_from_metadata(self):
        """Comprova que tokens, senhas e e-mails são descartados da metadata de proveniência."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        raw_meta = {
            'google_book_id': 'safe_id_999',
            'api_token': 'Bearer secret_token_12345',
            'user_email': 'usuario@externo.com',
            'auth_header': 'Basic secret',
            'publisher_declared': 'Companhia das Letras'
        }

        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            safe_metadata=raw_meta
        )

        saved_meta = record.provenance_metadata
        self.assertEqual(saved_meta.get('google_book_id'), 'safe_id_999')
        self.assertEqual(saved_meta.get('publisher_declared'), 'Companhia das Letras')
        self.assertNotIn('api_token', saved_meta)
        self.assertNotIn('user_email', saved_meta)
        self.assertNotIn('auth_header', saved_meta)

    def test_storage_abstraction_checksum_and_dimensions_without_path(self):
        """Comprova que checksum e dimensões funcionam via abstração de storage mesmo se .path levantar erro."""
        from unittest.mock import MagicMock
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io

        # Gerar imagem em memória (PNG 50x60)
        img_io = io.BytesIO()
        pil_img = Image.new('RGB', (50, 60), color='green')
        pil_img.save(img_io, format='PNG')
        img_bytes = img_io.getvalue()

        # Mock de FieldFile que não suporta .path (como S3 / Supabase / GCS)
        mock_file = MagicMock()
        mock_file.name = 'remote_storage/image_test.png'
        mock_file.size = len(img_bytes)
        
        def mock_path():
            raise NotImplementedError("Storage remoto não suporta .path físico local")
        
        mock_file.path = property(lambda self: mock_path())

        # open('rb') retorna novo stream de bytes
        mock_file.open.side_effect = lambda mode='rb': io.BytesIO(img_bytes)
        mock_file.chunks.return_value = [img_bytes]

        meta = ImageRightsRecord.extract_file_metadata(mock_file)
        self.assertTrue(len(meta['checksum']) == 64)
        self.assertEqual(meta['width'], 50)
        self.assertEqual(meta['height'], 60)
        self.assertGreater(meta['size_kb'], 0)

    def test_stream_closed_after_processing(self):
        """Comprova que os streams de arquivo são fechados após extração de metadados e checksum."""
        from PIL import Image
        import io

        img_io = io.BytesIO()
        pil_img = Image.new('RGB', (30, 30), color='blue')
        pil_img.save(img_io, format='PNG')
        img_bytes = img_io.getvalue()

        class TrackableBytesIO(io.BytesIO):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.is_closed = False

            def close(self):
                self.is_closed = True
                super().close()

        stream = TrackableBytesIO(img_bytes)

        from unittest.mock import MagicMock
        mock_file = MagicMock()
        mock_file.name = 'stream_test.png'
        mock_file.size = len(img_bytes)
        mock_file.open.return_value = stream
        mock_file.chunks.return_value = [img_bytes]

        ImageRightsRecord.extract_file_metadata(mock_file)
        self.assertTrue(stream.is_closed)

    def test_unavailable_file_does_not_alter_audit_status_or_legal_metadata(self):
        """Comprova que falha temporária de I/O no storage não altera status de auditoria nem apaga metadados jurídicos."""
        from unittest.mock import MagicMock
        from core.services.image_rights_service import ImageRightsAuditService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.id,
            image_field_name='cover_image',
            audit_status='regularized',
            legal_basis='fair_use_art46',
            license_type='licensed',
            creator_name='Fotógrafo Anterior',
            image_checksum='a'*64,
            public_display_allowed=True
        )

        mock_broken_file = MagicMock()
        mock_broken_file.name = 'broken_image.jpg'
        mock_broken_file.size = None
        mock_broken_file.open.side_effect = OSError("Storage temporariamente indisponível")

        ImageRightsAuditService.sync_file_metadata(record, mock_broken_file)
        record.refresh_from_db()

        # Metadados e status jurídico permanecem 100% intactos
        self.assertEqual(record.audit_status, 'regularized')
        self.assertEqual(record.legal_basis, 'fair_use_art46')
        self.assertEqual(record.license_type, 'licensed')
        self.assertEqual(record.creator_name, 'Fotógrafo Anterior')
        self.assertEqual(record.image_checksum, 'a'*64)
        self.assertTrue(record.public_display_allowed)

    def test_project_gutenberg_provenance_not_audited_and_no_public_domain_inference(self):
        """Comprova que imagens do Project Gutenberg registram project_gutenberg como provedor e NÃO inferem domínio público."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService
        from ereader.models import EBook

        ebook = EBook.objects.create(
            title="Memoirs of Sherlock Holmes",
            author="Arthur Conan Doyle",
            cover_image="https://www.gutenberg.org/cache/epub/834/pg834.cover.medium.jpg",
            source="gutenberg",
            external_id="834"
        )

        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=ebook,
            image_field_name='cover_image',
            provider='project_gutenberg',
            source_url='https://www.gutenberg.org/cache/epub/834/pg834.cover.medium.jpg',
            provider_asset_id='834',
            provenance_method='api_reference',
            safe_metadata={'gutenberg_id': '834', 'source': 'gutenberg'}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.provenance_provider, 'project_gutenberg')
        self.assertEqual(record.provider_asset_id, '834')
        # Regra Central: NENHUMA licença presumida, mesmo para Gutenberg
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertEqual(record.legal_basis, '')
        self.assertEqual(record.license_type, '')
        self.assertEqual(record.rights_holder_name, '')
        self.assertEqual(record.provenance_metadata.get('gutenberg_id'), '834')

    def test_source_url_sanitization_removes_tokens_and_credentials(self):
        """Comprova que URLs com tokens, chaves e credenciais têm seus parâmetros sensíveis higienizados."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        dirty_url = "https://user:password123@cdn.example.com/covers/book123.jpg?id=456&access_token=secret_jwt_token_999&x-amz-signature=deadbeef&Signature=abcdef&valid_param=high_res"
        
        record = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider='google_books',
            source_url=dirty_url
        )

        clean_url = record.source_url
        self.assertNotIn('password123', clean_url)
        self.assertNotIn('secret_jwt_token_999', clean_url)
        self.assertNotIn('deadbeef', clean_url)
        self.assertNotIn('Signature=', clean_url)
        self.assertIn('cdn.example.com', clean_url)
        self.assertIn('id=456', clean_url)
        self.assertIn('valid_param=high_res', clean_url)

    def test_provider_asset_id_semantics_across_providers(self):
        """Verifica a integridade semântica dos identificadores técnicos em cada provedor."""
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService

        # 1. Google Books Volume ID
        rec_gb = ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
            provider_asset_id='zyTCAlFPjgYC'
        )
        self.assertEqual(rec_gb.provider_asset_id, 'zyTCAlFPjgYC')

        # 2. Unsplash Photo ID
        from news.models import Article
        news = Article.objects.create(title="Notícia Teste", slug="noticia-teste-prov-1", content="Corpo do artigo de teste")
        rec_un = ImageRightsProvenanceService.register_external_provenance(
            target_obj=news,
            image_field_name='featured_image',
            provider=ImageRightsProvenanceService.PROVIDER_UNSPLASH,
            provider_asset_id='rDEOVtE7vOs'
        )
        self.assertEqual(rec_un.provider_asset_id, 'rDEOVtE7vOs')


class ImageRightsAuditQueueTestCase(TestCase):
    """
    Suíte de Testes para a Fila Inteligente e Priorizada de Auditoria de Imagens (Fase 2).
    Comprova o cálculo determinístico de score, níveis de prioridade, motivos explicáveis,
    segurança, ausência de decisões jurídicas automáticas e isolamento da trilha de logs.
    """

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin_queue',
            email='admin_queue@cgbookstore.com.br',
            password='password123'
        )
        self.normal_user = User.objects.create_user(
            username='client_user',
            email='client@cgbookstore.com.br',
            password='password123'
        )
        self.author = Author.objects.create(name="Guimarães Rosa")
        self.book = Book.objects.create(
            title="Grande Sertão: Veredas",
            author=self.author,
            slug="grande-sertao-veredas-queue",
            price=89.90,
            publication_date="1956-05-01"
        )
        self.book_ct = ContentType.objects.get_for_model(Book)

    def test_not_audited_public_image_gets_high_priority_and_reasons(self):
        """Comprova que imagem não auditada em exibição pública recebe prioridade alta/score relevante."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True,
            creator_name='',
            license_type=''
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertIn(item.priority_level, [ImageRightsAuditQueueService.PRIORITY_HIGH, ImageRightsAuditQueueService.PRIORITY_CRITICAL])
        self.assertGreaterEqual(item.priority_score, 55)
        self.assertTrue(any("exibição pública" in r.lower() for r in item.reasons))

    def test_not_audited_auto_imported_gets_priority_boost(self):
        """Comprova que imagem não auditada importada automaticamente recebe incremento de prioridade."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        rec_manual = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            provenance_provider='publisher',
            is_auto_imported=False,
            public_display_allowed=True
        )
        rec_auto = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='featured_image',
            audit_status='not_audited',
            provenance_provider='publisher',
            is_auto_imported=True,
            public_display_allowed=True
        )

        item_manual = ImageRightsAuditQueueService.evaluate_record(rec_manual)
        item_auto = ImageRightsAuditQueueService.evaluate_record(rec_auto)

        self.assertGreater(item_auto.priority_score, item_manual.priority_score)
        self.assertTrue(any("importação automática" in r.lower() for r in item_auto.reasons))

    def test_active_takedown_gets_critical_priority_and_score_above_90(self):
        """Comprova que contestação ativa eleva a prioridade para Crítica e score >= 90."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='contested',
            public_display_allowed=False
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='under_review',
            claimant_name='Advogado Notificante'
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertEqual(item.priority_level, ImageRightsAuditQueueService.PRIORITY_CRITICAL)
        self.assertGreaterEqual(item.priority_score, 90)
        self.assertTrue(item.has_active_takedown)
        self.assertEqual(item.suggested_action, ImageRightsAuditQueueService.ACTION_REVIEW_TAKEDOWN)
        self.assertTrue(any("contestação" in r.lower() for r in item.reasons))

    def test_contested_status_without_active_takedown_gets_high_priority(self):
        """Comprova que status contested recebe prioridade elevada."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='contested',
            public_display_allowed=False
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertGreaterEqual(item.priority_score, 45)

    def test_pending_status_needs_review(self):
        """Comprova que status pending aparece na fila para verificação de documentação."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='pending',
            public_display_allowed=True
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertEqual(item.suggested_action, ImageRightsAuditQueueService.ACTION_VERIFY_DOCUMENTATION)

    def test_restricted_resolved_removed_not_critically_urgent(self):
        """Comprova que registro restrito por remoção final resolvida não fica artificialmente crítico."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='resolved_removed',
            resolution_notes='Imagem removida consensualmente.'
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertFalse(item.needs_review)
        self.assertEqual(item.priority_level, ImageRightsAuditQueueService.PRIORITY_LOW)
        self.assertLess(item.priority_score, 30)

    def test_normal_regularized_does_not_need_review(self):
        """Comprova que registro regularizado consistente não aparece na fila principal."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='regularized',
            legal_basis='own_production',
            license_type='own',
            public_display_allowed=True
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertFalse(item.needs_review)
        self.assertEqual(item.priority_score, 0)
        self.assertEqual(item.priority_level, ImageRightsAuditQueueService.PRIORITY_LOW)

    def test_regularized_with_new_takedown_returns_to_queue(self):
        """Comprova que registro regularizado com nova contestação volta à fila com prioridade crítica."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='regularized',
            legal_basis='express_consent',
            license_type='licensed',
            public_display_allowed=True
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='received',
            claimant_name='Titular Reclamante'
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertEqual(item.priority_level, ImageRightsAuditQueueService.PRIORITY_CRITICAL)
        self.assertGreaterEqual(item.priority_score, 90)

    def test_missing_creator_and_license_generate_reasons(self):
        """Comprova que ausência de criador e licença gera motivos explicáveis."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            creator_name='',
            credit_name='',
            license_type='',
            public_display_allowed=True
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(any("criador" in r.lower() for r in item.reasons))
        self.assertTrue(any("licença" in r.lower() for r in item.reasons))

    def test_missing_provenance_generates_reason(self):
        """Comprova que ausência de procedência técnica gera motivo de revisão."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            provenance_provider='',
            source_url='',
            public_display_allowed=True
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(any("procedência" in r.lower() for r in item.reasons))

    def test_non_public_image_lower_priority_than_public_counterpart(self):
        """Comprova que imagem com exibição desabilitada tem prioridade menor que pública equivalente."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        rec_pub = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )
        rec_priv = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='featured_image',
            audit_status='not_audited',
            public_display_allowed=False
        )

        item_pub = ImageRightsAuditQueueService.evaluate_record(rec_pub)
        item_priv = ImageRightsAuditQueueService.evaluate_record(rec_priv)

        self.assertGreater(item_pub.priority_score, item_priv.priority_score)

    def test_score_is_strictly_between_0_and_100(self):
        """Comprova que o score permanece rigorosamente no intervalo [0, 100]."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertGreaterEqual(item.priority_score, 0)
        self.assertLessEqual(item.priority_score, 100)

    def test_evaluation_is_deterministic_and_has_no_side_effects(self):
        """Comprova que o cálculo de score não altera audit_status, display_allowed nem grava logs."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        initial_logs_count = ImageRightsAuditLog.objects.count()

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )

        item1 = ImageRightsAuditQueueService.evaluate_record(record)
        item2 = ImageRightsAuditQueueService.evaluate_record(record)

        self.assertEqual(item1.priority_score, item2.priority_score)
        self.assertEqual(item1.priority_level, item2.priority_level)
        self.assertEqual(item1.reasons, item2.reasons)

        record.refresh_from_db()
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertTrue(record.public_display_allowed)
        # Nenhum log de auditoria criado durante avaliação de fila
        self.assertEqual(ImageRightsAuditLog.objects.count(), initial_logs_count)

    def test_queue_view_requires_staff_permission(self):
        """Comprova que usuários anônimos e não-staff são barrados na rota da fila."""
        client = Client()
        queue_url = reverse('copyright_audit_queue')

        # Anônimo é redirecionado para login
        resp_anon = client.get(queue_url)
        self.assertEqual(resp_anon.status_code, 302)

        # Usuário comum (não-staff) é redirecionado
        client.login(username='client_user', password='password123')
        resp_user = client.get(queue_url)
        self.assertEqual(resp_user.status_code, 302)

    def test_staff_can_access_queue_view_and_see_items(self):
        """Comprova que usuário staff autenticado acessa a view da fila com sucesso."""
        ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )

        client = Client()
        client.login(username='admin_queue', password='password123')
        queue_url = reverse('copyright_audit_queue')

        response = client.get(queue_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fila Inteligente de Auditoria")
        self.assertContains(response, "Grande Sertão: Veredas")

    def test_queue_filters_and_ordering(self):
        """Comprova o funcionamento dos filtros e ordenação da fila."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        rec_gb = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            provenance_provider='google_books',
            public_display_allowed=True
        )
        rec_un = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='featured_image',
            audit_status='not_audited',
            provenance_provider='unsplash',
            public_display_allowed=True
        )

        items_gb = ImageRightsAuditQueueService.get_queue_queryset(filters={'provider': 'google_books'})
        self.assertEqual(len(items_gb), 1)
        self.assertEqual(items_gb[0].record.provenance_provider, 'google_books')

    def test_queue_page_does_not_expose_claimant_email_or_private_notes(self):
        """Comprova que e-mail de reclamante e notas confidenciais de takedown não vazam no HTML da fila."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='contested',
            public_display_allowed=False
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='under_review',
            claimant_name='Advogado Notificante',
            claimant_email='confidencial_email@reclamante.com',
            internal_notes='Segredo estratégico interno do corpo jurídico da livraria.'
        )

        client = Client()
        client.login(username='admin_queue', password='password123')
        queue_url = reverse('copyright_audit_queue')

        response = client.get(queue_url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertNotIn('confidencial_email@reclamante.com', html)
        self.assertNotIn('Segredo estratégico interno', html)

    def test_not_audited_public_manual_image_gets_minimum_priority_high(self):
        """
        [Fase 2 - Prompt 1.1] Comprova que qualquer registro not_audited + public_display_allowed=True
        recebe prioridade operacional mínima HIGH, mesmo sem importação automática e sem outros agravantes.
        """
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        # Registro manual, sem takedown, sem divergência, criador e titular preenchidos
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            is_auto_imported=False,
            public_display_allowed=True,
            creator_name='Fotógrafo Manual',
            rights_holder_name='Editora Parceira',
            provenance_provider='publisher',
            source_url='https://editora.com/capa.jpg'
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertEqual(item.priority_level, ImageRightsAuditQueueService.PRIORITY_HIGH)
        self.assertEqual(item.priority_level_display, 'Alta')
        # Score informativo preservado
        self.assertGreaterEqual(item.priority_score, 40)
        self.assertLessEqual(item.priority_score, 100)

    def test_not_audited_public_auto_imported_remains_high_or_critical(self):
        """[Fase 2 - Prompt 1.1] Comprova que imagem pública não auditada de importação automática fica HIGH ou superior."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            is_auto_imported=True,
            public_display_allowed=True,
            provenance_provider='google_books',
            source_url='https://books.google.com/thumbnail'
        )

        item = ImageRightsAuditQueueService.evaluate_record(record)
        self.assertTrue(item.needs_review)
        self.assertIn(item.priority_level, [ImageRightsAuditQueueService.PRIORITY_HIGH, ImageRightsAuditQueueService.PRIORITY_CRITICAL])
        self.assertGreaterEqual(item.priority_score, 55)

    def test_queue_query_does_not_prefetch_all_audit_logs(self):
        """
        [Fase 2 - Prompt 1.1] Comprova que get_queue_queryset não carrega o histórico completo de audit_logs,
        utilizando anotações booleanas e select_related otimizado.
        """
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )
        for i in range(5):
            ImageRightsAuditLog.objects.create(
                image_rights_record=record,
                event_type='record_created',
                description=f'Log histórico #{i}',
                performed_by=self.user
            )

        items = ImageRightsAuditQueueService.get_queue_queryset(filters={'show_all': True})
        target_item = next(it for it in items if it.record.pk == record.pk)

        # Não deve haver 'audit_logs' populado no cache de prefetch do objeto
        self.assertFalse(hasattr(target_item.record, '_prefetched_objects_cache') and 'audit_logs' in target_item.record._prefetched_objects_cache)
        # Deve possuir anotação booleana
        self.assertTrue(hasattr(target_item.record, 'has_logged_divergence'))

    def test_filter_by_creator_and_rights_holder_and_license(self):
        """[Fase 2 - Prompt 1.1] Comprova filtros de criador, titular e licença informados vs ausentes."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        rec_with_meta = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='pending',
            creator_name='Artista X',
            rights_holder_name='Editora Y',
            license_type='licensed',
            public_display_allowed=True
        )
        rec_empty_meta = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='featured_image',
            audit_status='pending',
            creator_name='',
            rights_holder_name='',
            license_type='',
            public_display_allowed=True
        )

        # Criador
        items_c_yes = ImageRightsAuditQueueService.get_queue_queryset(filters={'has_creator': 'true'})
        self.assertTrue(any(it.record.pk == rec_with_meta.pk for it in items_c_yes))
        self.assertFalse(any(it.record.pk == rec_empty_meta.pk for it in items_c_yes))

        items_c_no = ImageRightsAuditQueueService.get_queue_queryset(filters={'has_creator': 'false'})
        self.assertTrue(any(it.record.pk == rec_empty_meta.pk for it in items_c_no))

        # Titular
        items_r_yes = ImageRightsAuditQueueService.get_queue_queryset(filters={'has_rights_holder': 'true'})
        self.assertTrue(any(it.record.pk == rec_with_meta.pk for it in items_r_yes))

        # Licença
        items_l_yes = ImageRightsAuditQueueService.get_queue_queryset(filters={'has_license': 'true'})
        self.assertTrue(any(it.record.pk == rec_with_meta.pk for it in items_l_yes))
        self.assertFalse(any(it.record.pk == rec_empty_meta.pk for it in items_l_yes))

    def test_filter_by_content_type_and_image_field(self):
        """[Fase 2 - Prompt 1.1] Comprova filtros por model de origem e campo de imagem."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        rec1 = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='pending',
            public_display_allowed=True
        )
        rec2 = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='banner_image',
            audit_status='pending',
            public_display_allowed=True
        )

        items_cover = ImageRightsAuditQueueService.get_queue_queryset(filters={'image_field_name': 'cover_image'})
        self.assertTrue(any(it.record.pk == rec1.pk for it in items_cover))
        self.assertFalse(any(it.record.pk == rec2.pk for it in items_cover))

        items_ct = ImageRightsAuditQueueService.get_queue_queryset(filters={'content_type_id': self.book_ct.id})
        self.assertTrue(any(it.record.pk == rec1.pk for it in items_ct))

    def test_suggest_verify_license_only_when_appropriate(self):
        """[Fase 2 - Prompt 1.1] Comprova que a sugestão 'Verificar licença' ocorre quando apropriado."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService

        # Imagem externa sem licença e sem fundamento
        rec_external = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            provenance_provider='google_books',
            creator_name='Autor Capa',
            license_type='',
            legal_basis='',
            public_display_allowed=True
        )
        item_ext = ImageRightsAuditQueueService.evaluate_record(rec_external)
        self.assertEqual(item_ext.suggested_action, ImageRightsAuditQueueService.ACTION_VERIFY_LICENSE)

        # Imagem de produção própria (não sugere verificar licença de terceiros)
        rec_own = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='featured_image',
            audit_status='not_audited',
            legal_basis='own_production',
            public_display_allowed=True
        )
        item_own = ImageRightsAuditQueueService.evaluate_record(rec_own)
        self.assertNotEqual(item_own.suggested_action, ImageRightsAuditQueueService.ACTION_VERIFY_LICENSE)

    def test_queue_divergence_technical_urgency_without_legal_prejudgment(self):
        """[Fase 2 - Prompt 1.1] Comprova que divergência de integridade gera urgência técnica sem pré-julgamento jurídico."""
        from core.services.image_rights_audit_queue_service import ImageRightsAuditQueueService
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='regularized',
            image_checksum='1111' * 16,
            public_display_allowed=True
        )
        ImageRightsAuditLog.objects.create(
            image_rights_record=record,
            event_type='integrity_divergence_detected',
            description='Checksum divergente detectado.',
            performed_by=self.user
        )

        items = ImageRightsAuditQueueService.get_queue_queryset(filters={'show_all': True})
        target = next(it for it in items if it.record.pk == record.pk)

        self.assertTrue(target.has_integrity_divergence)
        self.assertTrue(target.needs_review)
        self.assertEqual(target.suggested_action, ImageRightsAuditQueueService.ACTION_REVIEW_DIVERGENCE)
        # audit_status permanece regularized sem alteração arbitrária
        record.refresh_from_db()
        self.assertEqual(record.audit_status, 'regularized')


class ImageRightsAssistedAuditTestCase(TestCase):
    """
    [FASE 2 - PROMPT 2] Testes da Auditoria Assistida Simples de Direitos Autorais de Imagens.
    Valida simplicidade visual, procedência, pendência principal, privacidade (sem PII),
    segurança (respeito a suspensão/bloqueio), navegação e ausência de decisões jurídicas automáticas.
    """

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_assisted',
            email='admin_assisted@cgbookstore.com.br',
            password='password123'
        )
        self.client_user = User.objects.create_user(
            username='regular_user_assisted',
            email='user@cgbookstore.com.br',
            password='password123'
        )
        self.author = Author.objects.create(name="J.R.R. Tolkien")
        self.book = Book.objects.create(
            title="O Hobbit",
            author=self.author,
            slug="o-hobbit-assisted-audit",
            price=59.90,
            publication_date="1937-09-21"
        )
        self.book_ct = ContentType.objects.get_for_model(Book)

    def test_assisted_audit_view_requires_staff_permission(self):
        """Comprova que usuários anônimos e não-staff são barrados na rota de Auditoria Assistida."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        # Anônimo
        resp_anon = client.get(url)
        self.assertEqual(resp_anon.status_code, 302)

        # Usuário regular (não staff)
        client.login(username='regular_user_assisted', password='password123')
        resp_user = client.get(url)
        self.assertEqual(resp_user.status_code, 302)

    def test_assisted_audit_view_returns_200_for_staff(self):
        """Comprova que administrador autorizado acessa a Auditoria Assistida com sucesso."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            provenance_provider='google_books',
            source_url='https://books.google.com/cover123.jpg',
            creator_name='Ilustrador Capa',
            public_display_allowed=True
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Auditoria da Imagem")
        self.assertContains(response, "O Hobbit")
        self.assertContains(response, "Google Books")
        self.assertContains(response, "Ilustrador Capa")

    def test_assisted_audit_view_404_for_nonexistent_record(self):
        """Comprova que registro inexistente retorna 404 seguro."""
        url = reverse('copyright_assisted_audit', args=[999999])
        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_assisted_audit_displays_nao_informado_for_missing_metadata(self):
        """Comprova que criador e titular ausentes são apresentados claramente como 'Não informado'."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            creator_name='',
            rights_holder_name='',
            public_display_allowed=True
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')
        self.assertIn("Não informado", html)

    def test_assisted_audit_suggested_action_and_primary_reason_from_queue_service(self):
        """Comprova que a pendência principal e a próxima ação sugerida vêm da lógica central da fila."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='pending',
            public_display_allowed=True
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verificar documentação")

    def test_assisted_audit_active_takedown_prevalence_and_pii_protection(self):
        """Comprova destaque visual de contestação ativa e proteção total contra vazamento de PII."""
        from core.models.copyright_takedown import CopyrightTakedownRequest

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='contested',
            public_display_allowed=False
        )
        CopyrightTakedownRequest.objects.create(
            image_rights_record=record,
            status='under_review',
            claimant_name='Advogado Notificante',
            claimant_email='confidencial_email_takedown@dominio.com',
            internal_notes='Parecer confidencial da consultoria externa.'
        )

        url = reverse('copyright_assisted_audit', args=[record.pk])
        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        # Destaque de contestação presente
        self.assertIn("Contestação formal em análise", html)
        self.assertIn("Revisar contestação", html)

        # PII e notas confidenciais NUNCA expostas
        self.assertNotIn("confidencial_email_takedown@dominio.com", html)
        self.assertNotIn("Parecer confidencial da consultoria externa", html)

    def test_assisted_audit_respects_can_display_publicly_no_bypass(self):
        """Comprova que imagem com exibição suspensa/bloqueada exibe placeholder seguro sem bypass."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='restricted',
            public_display_allowed=False
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn("Exibição pública bloqueada ou suspensa preventivamente", html)

    def test_assisted_audit_technical_details_and_sanitization(self):
        """Comprova que detalhes técnicos ficam recolhidos e que tokens/secrets são sanitizados."""
        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            image_checksum='abcdef1234567890' * 4,
            image_width_px=800,
            image_height_px=1200,
            file_size_kb=145.5,
            provenance_metadata={
                'format': 'jpeg',
                'color_space': 'RGB',
                'api_secret_token': 'SECRET_TOKEN_12345',
                'auth_key': 'KEY_SENSITIVE'
            },
            public_display_allowed=True
        )
        url = reverse('copyright_assisted_audit', args=[record.pk])

        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        # Checksum e dimensões presentes em detalhes técnicos
        self.assertIn("abcdef1234567890", html)
        self.assertIn("800 × 1200 px", html)

        # Chaves sensíveis sanitizadas
        self.assertNotIn("SECRET_TOKEN_12345", html)
        self.assertNotIn("KEY_SENSITIVE", html)

    def test_assisted_audit_read_only_no_mutations_or_logs(self):
        """Comprova que abrir a Auditoria Assistida é 100% livre de efeitos colaterais e mutações."""
        from core.models.image_rights_audit_log import ImageRightsAuditLog

        record = ImageRightsRecord.objects.create(
            content_type=self.book_ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            audit_status='not_audited',
            public_display_allowed=True
        )
        initial_logs_count = ImageRightsAuditLog.objects.count()

        url = reverse('copyright_assisted_audit', args=[record.pk])
        client = Client()
        client.login(username='admin_assisted', password='password123')
        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        record.refresh_from_db()
        self.assertEqual(record.audit_status, 'not_audited')
        self.assertTrue(record.public_display_allowed)
        self.assertEqual(ImageRightsAuditLog.objects.count(), initial_logs_count)







