import re
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.utils import timezone
from core.models import Book
from .models import AffiliatePartner, AffiliatePartnerClick
from .services.affiliate_service import AffiliateService


def get_client_ip(request):
    """
    Recupera de forma robusta o IP do cliente a partir da requisição HTTP.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """
    Realiza o parse da string de User-Agent sem pacotes externos.
    Retorna uma tupla: (navegador, sistema_operacional, dispositivo)
    """
    if not user_agent_string:
        return 'Desconhecido', 'Desconhecido', 'Desconhecido'
        
    ua = user_agent_string.lower()
    
    # 1. Tipo de Dispositivo
    if 'ipad' in ua:
        device = 'Tablet'
    elif 'tablet' in ua or 'playbook' in ua or 'kindle' in ua:
        device = 'Tablet'
    elif 'mobile' in ua or 'android' in ua or 'iphone' in ua or 'ipod' in ua or 'phone' in ua:
        device = 'Mobile'
    else:
        device = 'Desktop'
        
    # 2. Sistema Operacional
    if 'windows' in ua:
        os = 'Windows'
    elif 'android' in ua:
        os = 'Android'
    elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
        os = 'iOS'
    elif 'macintosh' in ua or 'mac os' in ua:
        os = 'macOS'
    elif 'linux' in ua:
        os = 'Linux'
    else:
        os = 'Desconhecido'
        
    # 3. Navegador
    if 'chrome' in ua and 'safari' in ua and 'edge' not in ua and 'edg' not in ua:
        browser = 'Chrome'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'edge' in ua or 'edg' in ua:
        browser = 'Edge'
    elif 'trident' in ua or 'msie' in ua:
        browser = 'Internet Explorer'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    else:
        browser = 'Outro/Desconhecido'
        
    return browser, os, device


def redirect_to_partner(request, book_id, partner_id=None):
    """
    View intermediária que registra o clique e redireciona o usuário para o parceiro comercial.
    """
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        raise Http404("Livro não encontrado")

    partner = None
    if partner_id:
        try:
            partner = AffiliatePartner.objects.get(id=partner_id, ativo=True)
        except AffiliatePartner.DoesNotExist:
            pass

    # Tenta resolver o parceiro pelo nome do parceiro comercial se não fornecido/válido
    if not partner:
        partner = AffiliateService.get_partner_for_book(book)

    # Resolve a URL de compra original
    url_original = book.purchase_partner_url
    if not url_original:
        # Se não há link de compra, redireciona de volta para a página do livro
        return redirect(book.get_absolute_url())

    # Gera o link final de afiliado usando o serviço
    if partner:
        url_final = AffiliateService.generate_link(partner, book, url_original)
    else:
        url_final = url_original

    # Garante chave de sessão para usuários anônimos
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key or ""

    user = request.user if request.user.is_authenticated else None

    # Prevenção de Cliques Duplicados (10 segundos)
    time_window = timezone.now() - timedelta(seconds=10)
    query = AffiliatePartnerClick.objects.filter(
        book=book,
        created_at__gte=time_window
    )
    if partner:
        query = query.filter(partner=partner)
    else:
        query = query.filter(partner__isnull=True)

    if user:
        query = query.filter(user=user)
    else:
        query = query.filter(session_key=session_key)

    if not query.exists():
        # Captura de metadados
        ip_address = get_client_ip(request)
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')[:50]
        
        # Parse do User Agent
        browser, os, device = parse_user_agent(user_agent_str)
        
        # Gravação do log de clique
        AffiliatePartnerClick.objects.create(
            user=user,
            session_key=session_key,
            book=book,
            partner=partner,
            destination_url=url_final,
            ip_address=ip_address,
            user_agent=user_agent_str,
            browser=browser,
            os=os,
            device=device,
            referer=referer or None,
            language=language
        )

    return redirect(url_final)
