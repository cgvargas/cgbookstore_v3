import os
import uuid
import logging
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
from django.conf import settings

from core.services.ai_book_assistant import AIBookAssistantService
from core.models import Author, Category

logger = logging.getLogger(__name__)


@staff_member_required
@require_http_methods(["POST"])
def analyze_metadata(request):
    """
    Endpoint para analisar textos e arquivos usando a IA do Gemini
    e extrair metadados estruturados de livros.
    """
    text_content = request.POST.get('text', '').strip()
    uploaded_file = request.FILES.get('file')

    if not text_content and not uploaded_file:
        return JsonResponse({
            'success': False,
            'message': 'Forneça um texto ou envie um arquivo para análise.'
        }, status=400)

    service = AIBookAssistantService()
    if not service.is_available():
        return JsonResponse({
            'success': False,
            'message': 'Serviço de IA do Gemini não está configurado. Configure a chave GEMINI_API_KEY no arquivo .env.'
        }, status=503)

    temp_file_path = None
    try:
        if uploaded_file:
            # Validar extensões permitidas
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'message': f'Extensão de arquivo não suportada: {ext}. Envie imagens (.png, .jpg, .webp) ou PDFs.'
                }, status=400)

            # Criar diretório temporário se não existir
            temp_dir = os.path.join(settings.BASE_DIR, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Salvar arquivo temporariamente
            temp_file_name = f"ai_upload_{uuid.uuid4().hex}{ext}"
            temp_file_path = os.path.join(temp_dir, temp_file_name)

            with open(temp_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            mime_type = uploaded_file.content_type
        else:
            mime_type = None

        # Chamar serviço de IA
        data = service.analyze_book_data(
            text_content=text_content if text_content else None,
            file_path=temp_file_path,
            mime_type=mime_type
        )

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        logger.error("Erro ao processar metadados com IA: %s", e, exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Erro ao processar dados com IA: {str(e)}'
        }, status=500)

    finally:
        # Garantir remoção do arquivo temporário do servidor local
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning("Falha ao remover arquivo temporário local %s: %s", temp_file_path, e)


@staff_member_required
@require_http_methods(["POST"])
def create_author_quick(request):
    """
    Cria um autor rapidamente a partir do assistente de IA.
    """
    name = request.POST.get('name', '').strip()
    bio = request.POST.get('bio', '').strip()
    if not name:
        return JsonResponse({
            'success': False,
            'message': 'Nome do autor é obrigatório.'
        }, status=400)

    try:
        # Verificar se já existe (case-insensitive)
        author = Author.objects.filter(name__iexact=name).first()
        created = False
        
        if not author:
            # Gerar slug único
            base_slug = slugify(name)
            if not base_slug:
                base_slug = "autor"
            slug = base_slug
            counter = 1
            while Author.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            author = Author.objects.create(
                name=name,
                slug=slug,
                bio=bio if bio else 'Biografia gerada automaticamente ou a ser preenchida.'
            )
            created = True
            message = f'Autor "{author.name}" criado com sucesso!'
        else:
            message = f'Autor "{author.name}" já cadastrado.'
            if bio:
                is_placeholder = not author.bio or 'Biografia gerada' in author.bio or author.bio == 'A ser preenchida.' or 'Autor cadastrado via' in author.bio
                if is_placeholder:
                    author.bio = bio
                    author.save()
                    message = f'Autor "{author.name}" já existia, biografia atualizada com sucesso!'

        return JsonResponse({
            'success': True,
            'id': author.id,
            'name': author.name,
            'created': created,
            'message': message
        })
    except Exception as e:
        logger.error("Erro ao criar autor rápido: %s", e)
        return JsonResponse({'success': False, 'message': f'Erro ao criar autor: {str(e)}'}, status=500)


@staff_member_required
@require_http_methods(["POST"])
def create_category_quick(request):
    """
    Cria uma categoria rapidamente a partir do assistente de IA.
    """
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'message': 'Nome da categoria é obrigatório.'}, status=400)

    # A Categoria tem unique=True no model, tratamos a verificação
    existing = Category.objects.filter(name__iexact=name).first()
    if existing:
        return JsonResponse({
            'success': True,
            'id': existing.id,
            'name': existing.name,
            'message': 'Categoria já existente selecionada automaticamente.'
        })

    try:
        category = Category.objects.create(
            name=name
            # Slug é gerado automaticamente no save() do model Category
        )
        return JsonResponse({
            'success': True,
            'id': category.id,
            'name': category.name,
            'message': f'Categoria "{category.name}" criada com sucesso!'
        })
    except Exception as e:
        logger.error("Erro ao criar categoria rápida: %s", e)
        return JsonResponse({'success': False, 'message': f'Erro ao criar categoria: {str(e)}'}, status=500)
