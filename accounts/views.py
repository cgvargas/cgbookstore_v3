"""
Views para gerenciamento de perfil de usuário.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
from PIL import Image
import io
import json
import logging

logger = logging.getLogger(__name__)

# ✅ Imports necessários para a nova funcionalidade
from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile, AccountDeletion
from .models.user_profile import THEME_CHOICES


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Você já pode fazer login.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# ✅ NOVA VIEW: Para a página de edição de perfil
@login_required
def edit_profile(request):
    """
    Exibe e processa o formulário de edição de perfil.
    """
    # Garante que o perfil exista, ou cria um novo se for o primeiro acesso
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('core:library')  # Redireciona de volta para a biblioteca
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
@require_POST
def upload_avatar(request):
    """
    Upload de avatar via AJAX.
    Valida, redimensiona e salva no Supabase Storage.
    """
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado'}, status=400)

        avatar_file = request.FILES['avatar']
        profile = request.user.profile

        max_size = 5 * 1024 * 1024  # 5MB
        if avatar_file.size > max_size:
            return JsonResponse({'success': False, 'error': 'Arquivo muito grande. Tamanho máximo: 5MB'}, status=400)

        if not avatar_file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'Arquivo deve ser uma imagem'}, status=400)

        try:
            img = Image.open(avatar_file)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            max_size_px = (500, 500)
            img.thumbnail(max_size_px, Image.Resampling.LANCZOS)

            width, height = img.size
            if width != height:
                size = min(width, height)
                left, top = (width - size) // 2, (height - size) // 2
                right, bottom = left + size, top + size
                img = img.crop((left, top, right, bottom))

            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)

            if profile.avatar:
                profile.avatar.delete(save=False)

            filename = f'users/avatars/{request.user.id}_{avatar_file.name}'
            profile.avatar.save(filename, output, save=True)

            return JsonResponse({
                'success': True,
                'avatar_url': profile.avatar.url,
                'message': 'Avatar atualizado com sucesso!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao processar imagem: {str(e)}'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro no upload: {str(e)}'}, status=500)


@login_required
@require_POST
def upload_banner(request):
    """
    Upload de banner via AJAX.
    Valida, redimensiona e salva no Supabase Storage.
    """
    try:
        if 'banner' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado'}, status=400)

        banner_file = request.FILES['banner']
        profile = request.user.profile

        max_size = 5 * 1024 * 1024  # 5MB
        if banner_file.size > max_size:
            return JsonResponse({'success': False, 'error': 'Arquivo muito grande. Tamanho máximo: 5MB'}, status=400)

        if not banner_file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'Arquivo deve ser uma imagem'}, status=400)

        try:
            img = Image.open(banner_file)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            target_width, target_height = 1200, 300
            width, height = img.size
            aspect, target_aspect = width / height, target_width / target_height

            if aspect > target_aspect:
                new_height = target_height
                new_width = int(new_height * aspect)
            else:
                new_width = target_width
                new_height = int(new_width / aspect)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            left, top = (new_width - target_width) // 2, (new_height - target_height) // 2
            right, bottom = left + target_width, top + target_height
            img = img.crop((left, top, right, bottom))

            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)

            if profile.banner:
                profile.banner.delete(save=False)

            filename = f'users/banners/{request.user.id}_{banner_file.name}'
            profile.banner.save(filename, output, save=True)

            return JsonResponse({
                'success': True,
                'banner_url': profile.banner.url,
                'message': 'Banner atualizado com sucesso!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao processar imagem: {str(e)}'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro no upload: {str(e)}'}, status=500)


@login_required
@require_POST
def update_theme(request):
    """
    Atualiza o tema visual do usuário via AJAX.
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme')

        if not theme:
            return JsonResponse({'success': False, 'error': 'Tema não especificado'}, status=400)

        valid_themes = [choice[0] for choice in THEME_CHOICES]
        if theme not in valid_themes:
            return JsonResponse({'success': False, 'error': 'Tema inválido'}, status=400)

        premium_themes = [
            'scifi', 'horror', 'mystery', 'biography', 'poetry',
            'adventure', 'thriller', 'historical', 'selfhelp',
            'philosophy', 'dystopian', 'contemporary'
        ]

        if theme in premium_themes and not request.user.profile.is_premium_active():
            return JsonResponse({
                'success': False,
                'error': 'Este tema é exclusivo para membros Premium',
                'requires_premium': True
            }, status=403)

        profile = request.user.profile
        profile.theme_preference = theme
        profile.save(update_fields=['theme_preference'])

        return JsonResponse({
            'success': True,
            'message': 'Tema atualizado com sucesso!',
            'theme': theme
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro ao atualizar tema: {str(e)}'}, status=500)


@login_required
@require_POST
def upload_background(request):
    """
    Upload de background personalizado via AJAX.
    APENAS para usuários PREMIUM.
    Valida, processa e salva no Supabase Storage.
    """
    try:
        # Verificar se é usuário PREMIUM
        if not request.user.profile.is_premium_active():
            return JsonResponse({
                'success': False,
                'error': 'Recurso exclusivo para membros Premium',
                'requires_premium': True
            }, status=403)

        if 'background' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado'}, status=400)

        background_file = request.FILES['background']
        profile = request.user.profile

        # Validar tamanho (10MB para backgrounds)
        max_size = 10 * 1024 * 1024  # 10MB
        if background_file.size > max_size:
            return JsonResponse({'success': False, 'error': 'Arquivo muito grande. Tamanho máximo: 10MB'}, status=400)

        # Validar tipo
        if not background_file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': 'Arquivo deve ser uma imagem'}, status=400)

        try:
            img = Image.open(background_file)

            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Redimensionar mantendo proporção (max 1920x1080)
            max_width, max_height = 1920, 1080
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Salvar com qualidade otimizada
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            # Deletar background anterior se existir
            if profile.custom_background:
                profile.custom_background.delete(save=False)

            # Salvar novo background
            filename = f'users/backgrounds/{request.user.id}_{background_file.name}'
            profile.custom_background.save(filename, output, save=True)

            return JsonResponse({
                'success': True,
                'background_url': profile.custom_background.url,
                'message': 'Background atualizado com sucesso!'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao processar imagem: {str(e)}'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro no upload: {str(e)}'}, status=500)


@login_required
@require_POST
def update_background_settings(request):
    """
    Atualiza as configurações de exibição do background (estilo e opacidade).
    APENAS para usuários PREMIUM.
    """
    try:
        # Verificar se é usuário PREMIUM
        if not request.user.profile.is_premium_active():
            return JsonResponse({
                'success': False,
                'error': 'Recurso exclusivo para membros Premium',
                'requires_premium': True
            }, status=403)

        data = json.loads(request.body)
        profile = request.user.profile

        # Atualizar estilo do background
        if 'background_style' in data:
            style = data['background_style']
            valid_styles = ['cover', 'contain', 'repeat']
            if style in valid_styles:
                profile.background_style = style
            else:
                return JsonResponse({'success': False, 'error': 'Estilo inválido'}, status=400)

        # Atualizar opacidade do overlay
        if 'background_opacity' in data:
            opacity = int(data['background_opacity'])
            if 0 <= opacity <= 100:
                profile.background_opacity = opacity
            else:
                return JsonResponse({'success': False, 'error': 'Opacidade deve estar entre 0 e 100'}, status=400)

        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Configurações atualizadas com sucesso!',
            'background_style': profile.background_style,
            'background_opacity': profile.background_opacity
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro ao atualizar configurações: {str(e)}'}, status=500)


@login_required
@require_POST
def remove_background(request):
    """
    Remove o background personalizado do usuário.
    APENAS para usuários PREMIUM.
    """
    try:
        # Verificar se é usuário PREMIUM
        if not request.user.profile.is_premium_active():
            return JsonResponse({
                'success': False,
                'error': 'Recurso exclusivo para membros Premium',
                'requires_premium': True
            }, status=403)

        profile = request.user.profile

        if profile.custom_background:
            profile.custom_background.delete(save=False)
            profile.custom_background = None
            profile.save(update_fields=['custom_background'])

            return JsonResponse({
                'success': True,
                'message': 'Background removido com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum background para remover'
            }, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro ao remover background: {str(e)}'}, status=500)


@login_required
def delete_account_confirm(request):
    """
    Exibe página de confirmação para exclusão de conta.
    """
    context = {
        'page_title': 'Excluir Conta',
    }
    return render(request, 'accounts/delete_account_confirm.html', context)


@login_required
@require_POST
@transaction.atomic
def delete_account(request):
    """
    Processa a exclusão permanente da conta do usuário.
    Requer confirmação digitando o email e aceitando os termos.
    Envia email de confirmação com mensagem emocional.
    """
    try:
        data = json.loads(request.body)
        email_confirmation = data.get('email_confirmation', '').strip()
        understood = data.get('understood', False)
        deletion_reason = data.get('deletion_reason', '')
        other_reason = data.get('other_reason', '').strip()

        # Validar confirmação
        if not understood:
            return JsonResponse({
                'success': False,
                'error': 'Você precisa confirmar que entende que esta ação é irreversível'
            }, status=400)

        # Validar email
        if email_confirmation != request.user.email:
            return JsonResponse({
                'success': False,
                'error': 'O email digitado não corresponde ao email da sua conta'
            }, status=400)

        # Armazenar informações antes de deletar
        user = request.user
        username = user.username
        email = user.email

        # Mapear motivos para texto legível
        reason_map = {
            'nao_uso_mais': 'Não uso mais o serviço',
            'falta_funcionalidades': 'Falta de funcionalidades necessárias',
            'dificuldade_uso': 'Dificuldade de uso / Interface confusa',
            'problemas_tecnicos': 'Problemas técnicos recorrentes',
            'preco_premium': 'Preço do Premium muito alto',
            'privacidade': 'Preocupações com privacidade',
            'migrando_plataforma': 'Migrando para outra plataforma',
            'conta_duplicada': 'Conta duplicada',
            'outros': other_reason if other_reason else 'Outros motivos'
        }

        deletion_reason_text = reason_map.get(deletion_reason, 'Não informado')

        # Coletar estatísticas para o email
        books_count = 0
        was_premium = False

        try:
            profile = user.profile
            was_premium = profile.is_premium_active()

            # Contar livros na biblioteca
            from core.models import UserBook
            books_count = UserBook.objects.filter(user=user).count()

            # Deletar imagens do perfil
            if profile.avatar:
                profile.avatar.delete(save=False)
            if profile.banner:
                profile.banner.delete(save=False)
            if profile.custom_background:
                profile.custom_background.delete(save=False)
        except Exception as e:
            logger.warning(f"Erro ao coletar estatísticas do perfil: {e}")

        # Calcular dias como membro
        days_as_member = None
        user_created_at = user.date_joined
        if user_created_at:
            delta = timezone.now() - user_created_at
            days_as_member = delta.days

        # Capturar informações adicionais
        ip_address = None
        user_agent = None
        try:
            # Pegar IP do request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Pegar User Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamanho
        except Exception:
            pass

        # Log do motivo de exclusão (para análise interna)
        logger.info(
            f"Conta excluída - User: {username}, Email: {email}, "
            f"Motivo: {deletion_reason_text}, Premium: {was_premium}, "
            f"Livros: {books_count}"
        )

        # Preparar contexto para o email
        context = {
            'username': username,
            'email': email,
            'deletion_date': datetime.now().strftime('%d/%m/%Y às %H:%M'),
            'deletion_reason_text': deletion_reason_text if deletion_reason else None,
            'books_count': books_count,
            'was_premium': was_premium,
            'site_url': request.build_absolute_uri('/'),
            'year': datetime.now().year
        }

        # Variáveis de controle do email
        email_sent_success = False
        email_error_message = None
        email_sent_timestamp = None

        # Renderizar templates de email e enviar
        try:
            subject = '💔 Sua conta na CG.BookStore foi excluída - Sentiremos sua falta'
            text_content = render_to_string('emails/account_deleted.txt', context)
            html_content = render_to_string('emails/account_deleted.html', context)

            # Criar e enviar email
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)  # Capturar erros

            email_sent_success = True
            email_sent_timestamp = timezone.now()
            logger.info(f"Email de confirmação enviado para: {email}")
        except Exception as e:
            # Não bloquear a exclusão se o email falhar
            email_error_message = str(e)[:500]  # Limitar tamanho
            logger.error(f"Erro ao enviar email de confirmação: {e}")

        # Salvar registro da exclusão no banco de dados ANTES de deletar o usuário
        try:
            deletion_record = AccountDeletion.objects.create(
                username=username,
                email=email,
                user_id=user.id,
                user_created_at=user_created_at,
                deletion_reason=deletion_reason if deletion_reason else 'nao_informado',
                other_reason=other_reason if other_reason else None,
                was_premium=was_premium,
                books_count=books_count,
                days_as_member=days_as_member,
                email_sent=email_sent_success,
                email_error=email_error_message,
                email_sent_at=email_sent_timestamp,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            logger.info(f"Registro de exclusão criado: ID {deletion_record.id}")
        except Exception as e:
            # Log do erro mas não bloqueia exclusão
            logger.error(f"Erro ao criar registro de exclusão: {e}")

        # Fazer logout antes de deletar
        logout(request)

        # Deletar usuário (CASCADE vai deletar relacionados automaticamente)
        user.delete()

        return JsonResponse({
            'success': True,
            'message': f'Conta de {username} excluída com sucesso. Sentiremos sua falta! Verifique seu email para confirmação.',
            'redirect_url': '/'
        })

    except Exception as e:
        logger.error(f"Erro ao excluir conta: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao excluir conta: {str(e)}'
        }, status=500)