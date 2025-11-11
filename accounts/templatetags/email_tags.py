# -*- coding: utf-8 -*-
"""
Template tags para verificação de email
"""
from django import template
from allauth.account.models import EmailAddress

register = template.Library()


@register.simple_tag
def is_email_verified(user):
    """
    Retorna True se usuário tem email verificado

    Uso no template:
        {% load email_tags %}
        {% is_email_verified user as verified %}
        {% if verified %}
            Email verificado!
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return EmailAddress.objects.filter(
        user=user,
        verified=True
    ).exists()


@register.inclusion_tag('accounts/includes/email_verification_badge.html')
def show_email_badge(user):
    """
    Renderiza badge de verificação de email

    Uso no template:
        {% load email_tags %}
        {% show_email_badge user %}
    """
    if not user or not user.is_authenticated:
        return {'verified': False, 'show': False}

    verified = EmailAddress.objects.filter(
        user=user,
        verified=True
    ).exists()

    return {
        'user': user,
        'verified': verified,
        'show': True
    }


@register.filter
def email_verified(user):
    """
    Filter que retorna True/False para email verificado

    Uso no template:
        {% load email_tags %}
        {% if user|email_verified %}
            Verificado!
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return EmailAddress.objects.filter(
        user=user,
        verified=True
    ).exists()
