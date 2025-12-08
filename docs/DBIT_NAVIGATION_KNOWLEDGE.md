# Conhecimentos de Navegação do Dbit

**Data:** 2025-12-05
**Versão:** 1.0

## Resumo

Foram adicionados conhecimentos à base do Dbit para que ele saiba **direcionar usuários para recursos da plataforma** ao invés de tentar realizar ações que devem ser feitas diretamente no site.

## Problema Identificado

O Dbit estava tentando **debater livros diretamente no chat** quando os usuários perguntavam sobre onde poderiam discutir livros com a comunidade. O comportamento correto é **direcionar o usuário para as funcionalidades da plataforma** onde essas interações devem acontecer.

## Solução Implementada

### 1. Correção do Erro no Admin

**Arquivo:** [chatbot_literario/admin.py](../chatbot_literario/admin.py:312)

**Problema:** Erro de formatação no método `confidence_badge` que usava `{:.0%}` (formato Python) ao invés de `{}` (formato Django).

**Correção:**
```python
# Antes (linha 312):
return format_html(
    '<span>...</span>',
    color, label, obj.confidence_score  # Erro: usava {:.0%}
)

# Depois:
percentage = int(obj.confidence_score * 100)
return format_html(
    '<span>...</span>',
    color, label, percentage  # Usa {} com conversão manual
)
```

### 2. Adição de Conhecimentos de Navegação

**Comando Criado:** `python manage.py add_navigation_knowledge`
**Arquivo:** [chatbot_literario/management/commands/add_navigation_knowledge.py](../chatbot_literario/management/commands/add_navigation_knowledge.py)

**5 Conhecimentos Adicionados:**

#### 1. Como debater sobre livros
- **Questão:** "Como posso debater sobre um livro com outros usuários?"
- **Direciona para:**
  - Avaliações públicas de livros
  - Seção Novos Autores
  - Sistema de reviews
- **Tipo:** General
- **Confiança:** 100%

#### 2. Onde encontrar autores independentes
- **Questão:** "Onde posso encontrar livros de autores novos ou independentes?"
- **Direciona para:**
  - /novos-autores/
  - Recursos de busca e filtro
  - Seção "Em Alta"
- **Tipo:** General
- **Confiança:** 100%

#### 3. Como avaliar livros
- **Questão:** "Como faço para avaliar ou dar nota a um livro?"
- **Direciona para:**
  - Passo a passo completo de avaliação
  - Sistema de estrelas e reviews
  - Benefícios (XP e contribuição)
- **Tipo:** General
- **Confiança:** 100%

#### 4. Funcionalidades da plataforma
- **Questão:** "Quais funcionalidades a plataforma oferece além de buscar livros?"
- **Direciona para:**
  - Biblioteca pessoal
  - Avaliações e reviews
  - Novos Autores
  - Sistema de gamificação
  - Dashboard personalizado
  - Busca avançada
- **Tipo:** General
- **Confiança:** 100%

#### 5. Como ver perfil de autores
- **Questão:** "Como posso ver o perfil de um autor ou escritor?"
- **Direciona para:**
  - /novos-autores/autor/[username]/
  - Recursos do perfil
  - Como seguir autores
- **Tipo:** General
- **Confiança:** 100%

## Como Usar

### Adicionar/Atualizar Conhecimentos

```bash
python manage.py add_navigation_knowledge
```

O comando:
- ✅ Cria novos conhecimentos
- 🔄 Atualiza conhecimentos existentes
- 📊 Exibe relatório de execução

### Acessar no Admin

1. Acesse: `http://127.0.0.1:8000/admin/`
2. Vá em: **Chatbot Literário** > **Chatbot knowledges**
3. Visualize, edite ou crie novos conhecimentos

### Filtros Disponíveis

- Por tipo de conhecimento
- Por status (ativo/inativo)
- Por data de criação
- Por nível de confiança

### Ações em Massa

- ✅ Ativar conhecimentos
- ⛔ Desativar conhecimentos
- ⬆️ Aumentar confiança (+0.1)
- ⬇️ Diminuir confiança (-0.1)

## Estrutura dos Conhecimentos

Cada conhecimento contém:

```python
{
    'knowledge_type': 'general',  # Tipo de conhecimento
    'original_question': 'Pergunta do usuário...',
    'incorrect_response': 'Resposta incorreta (para referência)',
    'correct_response': 'Resposta correta com direcionamento',
    'confidence_score': 1.0,  # 0.0 a 1.0
    'admin_notes': 'Observações do administrador',
    'is_active': True,  # Se está ativo
    'created_by': User,  # Usuário que criou
}
```

## Campos Opcionais

- `related_book`: Livro relacionado (ForeignKey)
- `related_author`: Autor relacionado (ForeignKey)
- `keywords`: Palavras-chave (gerado automaticamente)
- `times_used`: Contador de uso
- `last_used_at`: Última vez usado

## Comportamento do Dbit

### Antes
- ❌ Tentava debater no chat
- ❌ Não direcionava para recursos
- ❌ Assumia papel que não era dele

### Depois
- ✅ Direciona para avaliações públicas
- ✅ Explica como usar recursos da plataforma
- ✅ Mantém seu papel de assistente
- ✅ Complementa com análises literárias

## Exemplo de Conversa

**Usuário:** "Onde posso debater sobre um livro com outras pessoas?"

**Dbit (Antes):**
> "Eu posso debater o livro com você aqui no chat. Sobre qual livro você quer falar?"

**Dbit (Depois):**
> Para debater sobre livros com outros usuários da comunidade, você tem várias opções na plataforma:
>
> 📚 **Avaliações Públicas de Livros:**
> 1. Acesse a página de detalhes do livro
> 2. Role até a seção de avaliações
> 3. Escreva sua resenha e marque como "Pública"
> 4. Outros leitores poderão ver sua opinião
>
> ✍️ **Seção Novos Autores:**
> - Acesse "Novos Autores" no menu
> - Na página de cada livro, deixe avaliações
> - Interaja com avaliações de outros leitores
>
> 💬 **Dica:** Escreva resenhas detalhadas para ganhar XP extra!
>
> Enquanto isso, posso te ajudar com recomendações e análises literárias. 📖

## Manutenção

### Adicionar Novo Conhecimento

1. Acesse o admin: `/admin/chatbot_literario/chatbotknowledge/add/`
2. Preencha os campos:
   - Tipo de conhecimento
   - Pergunta original
   - Resposta correta
   - Nível de confiança
3. Salve

### Ou via Código

Adicione no arquivo: `chatbot_literario/management/commands/add_navigation_knowledge.py`

```python
{
    'knowledge_type': 'general',
    'original_question': 'Nova pergunta?',
    'incorrect_response': 'Resposta que queremos evitar',
    'correct_response': 'Resposta correta com direcionamento',
    'confidence_score': 1.0,
    'admin_notes': 'Observações'
}
```

Execute: `python manage.py add_navigation_knowledge`

## Monitoramento

### Verificar Uso

No admin, acesse a lista de conhecimentos e veja:
- **Times Used Badge**: Quantas vezes foi usado
- **Last Used At**: Última utilização
- **Confidence Badge**: Nível de confiança

### Otimizar

- Se um conhecimento é muito usado: ✅ Manter ativo, confiança alta
- Se não é usado: ⚠️ Revisar palavras-chave ou desativar
- Se gera confusão: ⬇️ Diminuir confiança ou editar

## Benefícios

### Para os Usuários
- 🎯 Direcionamento correto para recursos
- 📚 Descoberta de funcionalidades
- 💬 Participação na comunidade
- ✨ Melhor experiência

### Para a Plataforma
- 📊 Mais uso de recursos sociais
- 👥 Maior engajamento comunitário
- ⭐ Mais avaliações e reviews
- 🚀 Crescimento orgânico

### Para o Dbit
- 🧠 Mais inteligente e útil
- 🎯 Papel bem definido
- 🤝 Complementa a plataforma
- 📈 Melhor performance

## Próximos Passos

### Conhecimentos Sugeridos para Adicionar

1. **Como adicionar livros à biblioteca**
2. **Como criar estantes personalizadas**
3. **Como seguir autores**
4. **Sistema de gamificação e XP**
5. **Como se tornar autor na plataforma**
6. **Como usar a busca avançada**
7. **Como importar livros do Google Books**
8. **Dashboard e estatísticas**

### Melhorias Futuras

- [ ] Sistema de feedback em conhecimentos
- [ ] Sugestões automáticas de novos conhecimentos
- [ ] Analytics de uso de conhecimentos
- [ ] Versionamento de conhecimentos
- [ ] A/B testing de respostas

## Arquivos Relacionados

- [chatbot_literario/admin.py](../chatbot_literario/admin.py)
- [chatbot_literario/models.py](../chatbot_literario/models.py)
- [chatbot_literario/knowledge_base_service.py](../chatbot_literario/knowledge_base_service.py)
- [chatbot_literario/management/commands/add_navigation_knowledge.py](../chatbot_literario/management/commands/add_navigation_knowledge.py)

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs do Django
2. Acesse o admin e revise os conhecimentos
3. Execute o comando novamente se necessário
4. Consulte a documentação do Knowledge Base System

---

**Última Atualização:** 2025-12-05
**Autor:** Sistema CG.BookStore
**Status:** ✅ Implementado e Funcional
