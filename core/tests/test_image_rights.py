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



