"""
Script para criar o termo de responsabilidade inicial
Execute com: python create_initial_terms.py
"""
import os
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from new_authors.models import AuthorTermsOfService

# Criar o termo inicial
term_content = """
# TERMO DE RESPONSABILIDADE E USO DA PLATAFORMA
## CG.BookStore - Programa de Autores Emergentes

**Versão 1.0 - Vigente a partir de 10 de dezembro de 2025**

---

## 1. ACEITE E CONCORDÂNCIA

Ao aceitar este Termo de Responsabilidade, você declara:

- Ter lido, compreendido e concordado integralmente com todas as cláusulas aqui estabelecidas
- Possuir capacidade civil plena (idade igual ou superior a 18 anos)
- Fornecer informações verdadeiras, precisas e atualizadas
- Comprometer-se a manter a confidencialidade de suas credenciais de acesso

## 2. ORIGINALIDADE E DIREITOS AUTORAIS

Você se compromete a:

- **Ser o autor original** de todas as obras publicadas na plataforma
- **Não violar direitos autorais** de terceiros, incluindo textos, músicas, imagens ou qualquer outro conteúdo protegido
- **Possuir todos os direitos necessários** para publicar, distribuir e comercializar suas obras
- **Responder integralmente** por qualquer reclamação de violação de direitos autorais relacionada ao seu conteúdo
- **Indenizar a plataforma** em caso de ações judiciais decorrentes de violação de direitos de terceiros

## 3. CONTEÚDO PROIBIDO

É **EXPRESSAMENTE PROIBIDO** publicar conteúdo que:

- Viole leis brasileiras ou internacionais
- Contenha pornografia, exploração sexual ou abuso infantil
- Incentive violência, ódio, discriminação ou preconceito de qualquer natureza
- Promova atividades ilegais, como uso de drogas ilícitas ou crimes
- Seja difamatório, calunioso ou injurioso contra pessoas ou instituições
- Contenha informações falsas, enganosas ou fraudulentas
- Viole a privacidade ou dados pessoais de terceiros sem consentimento

## 4. RESPONSABILIDADE PELO CONTEÚDO

Você é **INTEGRALMENTE RESPONSÁVEL** por:

- Todo o conteúdo publicado em sua conta de autor
- As consequências legais de suas publicações
- Danos causados a terceiros em decorrência de suas obras
- Violações de direitos autorais, marcas registradas ou patentes
- Eventuais processos judiciais relacionados ao seu conteúdo

**A plataforma CG.BookStore não se responsabiliza** pelo conteúdo publicado pelos autores, atuando apenas como intermediadora técnica.

## 5. MODERAÇÃO E REMOÇÃO DE CONTEÚDO

A plataforma reserva-se o direito de:

- **Moderar** todo o conteúdo publicado
- **Remover** imediatamente qualquer obra que viole este termo
- **Suspender ou banir** contas que descumpram as regras estabelecidas
- **Reportar às autoridades** conteúdos que configurem crimes

**Não há direito a indenização** em caso de remoção de conteúdo ou suspensão de conta por violação deste termo.

## 6. POLÍTICA DE MONETIZAÇÃO

Você reconhece e concorda que:

- A plataforma poderá cobrar taxas de serviço sobre vendas e assinaturas
- Os percentuais de repasse serão informados previamente
- A plataforma pode alterar sua política comercial mediante aviso prévio de 30 dias
- Pagamentos estão sujeitos a verificação de identidade e documentação
- A plataforma pode reter pagamentos em caso de suspeita de fraude

## 7. DADOS PESSOAIS E PRIVACIDADE

Ao aceitar este termo, você autoriza:

- A coleta e armazenamento de seus dados pessoais conforme a LGPD (Lei 13.709/2018)
- O uso de seus dados para fins de identificação, pagamento e comunicação
- A divulgação pública de seu nome de autor e biografia
- O armazenamento de seu endereço IP para fins de segurança e auditoria

Seus documentos pessoais (RG, CPF, comprovante de residência) serão armazenados de forma segura e utilizados **APENAS** para verificação de identidade.

## 8. PROPRIEDADE INTELECTUAL

- Você **MANTÉM todos os direitos autorais** sobre suas obras
- A plataforma recebe apenas licença não-exclusiva para hospedar, exibir e distribuir suas obras
- Você pode remover suas obras da plataforma a qualquer momento
- A remoção não afeta exemplares já vendidos ou distribuídos

## 9. ISENÇÃO DE GARANTIAS

A plataforma é fornecida "**NO ESTADO EM QUE SE ENCONTRA**", sem garantias de:

- Disponibilidade ininterrupta
- Ausência de erros ou bugs
- Segurança absoluta contra invasões
- Resultados específicos de vendas ou alcance

## 10. ALTERAÇÕES DO TERMO

Este termo pode ser alterado a qualquer momento. Em caso de alterações substanciais:

- Você será notificado por e-mail
- Terá 30 dias para aceitar ou recusar as novas condições
- A recusa implica no cancelamento de sua conta de autor

## 11. CONTATO E SUPORTE

Para dúvidas, reclamações ou solicitações relacionadas a este termo:

- **E-mail:** suporte@cgbookstore.com.br
- **Tempo de resposta:** até 5 dias úteis

## 12. FORO E LEGISLAÇÃO

Este termo é regido pelas leis brasileiras. Fica eleito o foro da comarca do autor para dirimir quaisquer questões relacionadas a este termo.

---

## DECLARAÇÃO FINAL

**AO MARCAR A OPÇÃO "LI E ACEITO OS TERMOS DE RESPONSABILIDADE", VOCÊ DECLARA:**

1. Ter lido integralmente este documento
2. Compreender todas as cláusulas e condições estabelecidas
3. Concordar livre e espontaneamente com todos os termos
4. Estar ciente das suas responsabilidades como autor na plataforma
5. Comprometer-se a respeitar todas as regras aqui estabelecidas

**Data de aceitação e endereço IP serão registrados para fins legais.**

---

*CG.BookStore - Conectando autores emergentes com leitores apaixonados*
"""

summary_points = [
    "📝 Você é o autor original e possui todos os direitos sobre suas obras",
    "⚖️ É proibido publicar conteúdo ilegal, ofensivo, difamatório ou que viole direitos autorais",
    "🛡️ Você é integralmente responsável pelo conteúdo publicado e suas consequências legais",
    "🔍 A plataforma pode moderar, remover conteúdo e suspender contas que violem as regras",
    "💰 Taxas de serviço serão cobradas sobre vendas, com percentuais informados previamente",
    "🔒 Seus dados pessoais serão protegidos conforme a LGPD",
    "✅ Você mantém todos os direitos autorais sobre suas obras",
    "📧 Alterações no termo serão notificadas com 30 dias de antecedência"
]

# Verificar se já existe
existing = AuthorTermsOfService.objects.filter(version='1.0').first()

if existing:
    print(f"⚠️  Termo versão 1.0 já existe (ID: {existing.id})")
    print(f"   is_current: {existing.is_current}")
    print(f"   is_active: {existing.is_active}")
else:
    # Criar novo termo
    term = AuthorTermsOfService.objects.create(
        title='Termo de Responsabilidade - Autores Emergentes',
        version='1.0',
        content=term_content.strip(),
        summary_points=summary_points,
        is_active=True,
        is_current=True,
        effective_date=datetime.now()
    )

    print("✅ Termo de Responsabilidade versão 1.0 criado com sucesso!")
    print(f"   ID: {term.id}")
    print(f"   Versão: {term.version}")
    print(f"   Status: Ativo e Atual")
    print(f"   Data de vigência: {term.effective_date}")
    print(f"\n📋 Pontos principais incluídos:")
    for point in summary_points:
        print(f"   • {point}")

    print(f"\n🌐 O termo estará disponível em: /novos-autores/termos/")
    print(f"💡 Novos autores deverão aceitar este termo ao se cadastrar")
