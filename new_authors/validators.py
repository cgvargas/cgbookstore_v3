"""
Validadores customizados para o app New Authors
"""
import re
from django.core.exceptions import ValidationError


def validate_cnpj(value):
    """
    Valida CNPJ brasileiro

    Args:
        value: String com CNPJ (pode conter pontuação ou não)

    Raises:
        ValidationError: Se o CNPJ for inválido
    """
    # Remove pontuação
    cnpj = re.sub(r'[^\d]', '', value)

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        raise ValidationError('CNPJ deve ter 14 dígitos')

    # Verifica se todos os dígitos são iguais (CNPJ inválido)
    if cnpj == cnpj[0] * 14:
        raise ValidationError('CNPJ inválido')

    # Validação do primeiro dígito verificador
    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(12):
        soma += int(cnpj[i]) * peso[i]

    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        raise ValidationError('CNPJ inválido')

    # Validação do segundo dígito verificador
    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(13):
        soma += int(cnpj[i]) * peso[i]

    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != digito2:
        raise ValidationError('CNPJ inválido')

    return value


def format_cnpj(cnpj):
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX

    Args:
        cnpj: String com CNPJ (apenas números)

    Returns:
        str: CNPJ formatado
    """
    # Remove qualquer pontuação existente
    cnpj = re.sub(r'[^\d]', '', cnpj)

    if len(cnpj) != 14:
        return cnpj

    # Formata: XX.XXX.XXX/XXXX-XX
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
