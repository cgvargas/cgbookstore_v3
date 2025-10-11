"""
Views para gerenciamento de perfil de usuário.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from PIL import Image
import io
import json

# ✅ Imports necessários para a nova funcionalidade
from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile
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

        max_size = 2 * 1024 * 1024  # 2MB
        if avatar_file.size > max_size:
            return JsonResponse({'success': False, 'error': 'Arquivo muito grande. Tamanho máximo: 2MB'}, status=400)

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