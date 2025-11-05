# 🕐 Configurar Cron Job no Windows - Guia Completo

**Objetivo**: Executar `check_expiring_premium` automaticamente todo dia às 9h da manhã

**Tempo estimado**: 10 minutos

---

## 📋 Passo 1: Testar o Script Batch

Antes de configurar o agendamento, vamos garantir que o script funciona.

### 1.1. Abrir PowerShell ou CMD

- Pressione `Win + R`
- Digite `powershell` ou `cmd`
- Enter

### 1.2. Navegar até a pasta do projeto

```cmd
cd C:\ProjectsDjango\cgbookstore_v3
```

### 1.3. Executar o script manualmente

```cmd
scripts\run_check_expiring_premium.bat
```

### 1.4. Verificar o output

Você deve ver algo como:

```
============================================================
VERIFICACAO DE PREMIUM EXPIRANDO
Data/Hora: 04/11/2025 22:45:00
============================================================

(.venv) C:\ProjectsDjango\cgbookstore_v3>python manage.py check_expiring_premium
======================================================================
VERIFICAÇÃO DE PREMIUM EXPIRANDO
======================================================================

>> Verificando Premium expirando em 3 dias...
   Encontradas: 1 concessao(oes)
   [SKIP] claud: Ja notificado
   Total notificado neste período: 0
...
[SUCCESS] Comando executado com sucesso!

============================================================
EXECUCAO CONCLUIDA: 04/11/2025 22:45:15
============================================================
```

✅ **Se funcionou**, continue para o Passo 2!

❌ **Se deu erro**, verifique:
- Caminho do projeto está correto no script `.bat`
- Ambiente virtual existe em `.venv`
- Python está instalado

---

## 📅 Passo 2: Abrir o Task Scheduler (Agendador de Tarefas)

### Método 1: Busca no Menu Iniciar

1. Pressione a tecla `Win`
2. Digite: **agendador de tarefas** ou **task scheduler**
3. Clique no aplicativo que aparecer

### Método 2: Executar Direto

1. Pressione `Win + R`
2. Digite: `taskschd.msc`
3. Enter

### Resultado Esperado

Você deve ver uma janela como esta:

```
┌────────────────────────────────────────────────────────┐
│ Agendador de Tarefas                        [_][□][X]  │
├────────────────────────────────────────────────────────┤
│ Arquivo  Ação  Exibir  Ajuda                          │
├──────────────┬─────────────────────────────────────────┤
│              │                                         │
│ Biblioteca   │  Nome         Última Execução  Status  │
│ de Tarefas   │  ──────────── ────────────────────────  │
│   ▼ Microsoft│  Task1        01/11/2025       Pronto  │
│     ▼ Windows│  Task2        02/11/2025       Pronto  │
│              │                                         │
└──────────────┴─────────────────────────────────────────┘
```

---

## ➕ Passo 3: Criar Nova Tarefa

### 3.1. No painel direito, clique em:

```
┌─────────────────────────┐
│  Ações                  │
├─────────────────────────┤
│  Criar Tarefa Básica... │  ← CLIQUE AQUI
│  Criar Tarefa...        │
│  Importar Tarefa...     │
└─────────────────────────┘
```

### 3.2. Assistente de Criação

#### Tela 1: Nome e Descrição

```
┌────────────────────────────────────────────┐
│ Criar Tarefa Básica                       │
├────────────────────────────────────────────┤
│                                            │
│ Nome: Check Premium Expiring              │
│                                            │
│ Descrição:                                │
│ ┌────────────────────────────────────────┐│
│ │ Verifica e notifica usuarios com       ││
│ │ Premium expirando em 3 dias, 1 dia     ││
│ │ e hoje. Executa todo dia as 9h.        ││
│ └────────────────────────────────────────┘│
│                                            │
│            [Cancelar]  [Avançar >]        │
└────────────────────────────────────────────┘
```

**Preencha:**
- **Nome**: `Check Premium Expiring`
- **Descrição**: `Verifica e notifica usuarios com Premium expirando`

Clique em **Avançar >**

---

#### Tela 2: Gatilho (Quando Executar)

```
┌────────────────────────────────────────────┐
│ Gatilho                                    │
├────────────────────────────────────────────┤
│ Quando deseja que a tarefa seja iniciada? │
│                                            │
│ ⚫ Diariamente                    ← MARQUE │
│ ○ Semanalmente                            │
│ ○ Mensalmente                             │
│ ○ Uma vez                                 │
│ ○ Quando o computador for iniciado       │
│ ○ Quando eu fizer logon                  │
│                                            │
│          [< Voltar]  [Avançar >]          │
└────────────────────────────────────────────┘
```

**Selecione**: ⚫ **Diariamente**

Clique em **Avançar >**

---

#### Tela 3: Diariamente (Configurar Horário)

```
┌────────────────────────────────────────────┐
│ Diariamente                                │
├────────────────────────────────────────────┤
│                                            │
│ Iniciar: [04/11/2025]  [09:00:00]        │
│                                            │
│ Recorrer a cada: [1] dia(s)               │
│                                            │
│          [< Voltar]  [Avançar >]          │
└────────────────────────────────────────────┘
```

**Preencha:**
- **Data de início**: Data de hoje
- **Hora**: `09:00:00` (9h da manhã)
- **Recorrer a cada**: `1` dia(s)

Clique em **Avançar >**

---

#### Tela 4: Ação (O que Executar)

```
┌────────────────────────────────────────────┐
│ Ação                                       │
├────────────────────────────────────────────┤
│ Que ação você deseja realizar?            │
│                                            │
│ ⚫ Iniciar um programa        ← MARQUE     │
│ ○ Enviar um email                         │
│ ○ Exibir uma mensagem                     │
│                                            │
│          [< Voltar]  [Avançar >]          │
└────────────────────────────────────────────┘
```

**Selecione**: ⚫ **Iniciar um programa**

Clique em **Avançar >**

---

#### Tela 5: Iniciar um Programa (Configurar Script)

```
┌────────────────────────────────────────────────────────────┐
│ Iniciar um Programa                                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Programa/script:                                          │
│ ┌────────────────────────────────────────────────────┐   │
│ │ C:\ProjectsDjango\cgbookstore_v3\scripts\          │   │
│ │ run_check_expiring_premium.bat                     │   │
│ └────────────────────────────────────────────────────┘   │
│                                        [Procurar...]      │
│                                                            │
│ Adicionar argumentos (opcional):                          │
│ ┌────────────────────────────────────────────────────┐   │
│ │ (deixe em branco)                                  │   │
│ └────────────────────────────────────────────────────┘   │
│                                                            │
│ Iniciar em (opcional):                                    │
│ ┌────────────────────────────────────────────────────┐   │
│ │ C:\ProjectsDjango\cgbookstore_v3                   │   │
│ └────────────────────────────────────────────────────┘   │
│                                                            │
│                  [< Voltar]  [Avançar >]                  │
└────────────────────────────────────────────────────────────┘
```

**Preencha:**

**Programa/script:**
```
C:\ProjectsDjango\cgbookstore_v3\scripts\run_check_expiring_premium.bat
```

**Iniciar em:**
```
C:\ProjectsDjango\cgbookstore_v3
```

💡 **Dica**: Use o botão **[Procurar...]** para selecionar o arquivo `.bat`

Clique em **Avançar >**

---

#### Tela 6: Resumo

```
┌────────────────────────────────────────────┐
│ Resumo                                     │
├────────────────────────────────────────────┤
│                                            │
│ Nome: Check Premium Expiring              │
│ Descrição: Verifica e notifica...        │
│ Gatilho: Diariamente às 09:00:00         │
│ Ação: Iniciar programa                    │
│   run_check_expiring_premium.bat          │
│                                            │
│ ☑ Abrir a caixa de diálogo Propriedades  │
│   para esta tarefa ao clicar em Concluir  │
│                                            │
│          [< Voltar]  [Concluir]           │
└────────────────────────────────────────────┘
```

✅ **IMPORTANTE**: Marque a caixa:
```
☑ Abrir a caixa de diálogo Propriedades para esta tarefa ao clicar em Concluir
```

Clique em **Concluir**

---

## ⚙️ Passo 4: Configurações Avançadas (Propriedades)

A janela de **Propriedades** deve abrir automaticamente. Se não abriu:
1. Encontre a tarefa na lista
2. Clique com botão direito
3. Selecione **Propriedades**

### 4.1. Aba "Geral"

```
┌────────────────────────────────────────────┐
│ [Geral] [Gatilhos] [Ações] [Condições]   │
├────────────────────────────────────────────┤
│                                            │
│ Nome: Check Premium Expiring              │
│                                            │
│ Conta de segurança:                       │
│ ○ Executar somente quando o usuário      │
│   estiver conectado                       │
│ ⚫ Executar independentemente de o        │
│   usuário estar conectado ou não          │
│                                            │
│ ☑ Executar com privilégios mais altos    │
│                                            │
│ Configurar para: [Windows 10 ▼]          │
│                                            │
│          [OK]  [Cancelar]  [Aplicar]      │
└────────────────────────────────────────────┘
```

**Configure:**
- ⚫ **Executar independentemente de o usuário estar conectado ou não**
- ☑ **Executar com privilégios mais altos** (se necessário)

### 4.2. Aba "Gatilhos"

Verifique se está correto:
```
Diariamente às 09:00 todos os dias
Status: Habilitado
```

### 4.3. Aba "Ações"

Verifique se o caminho está correto:
```
Iniciar programa
Programa: C:\...\run_check_expiring_premium.bat
Iniciar em: C:\ProjectsDjango\cgbookstore_v3
```

### 4.4. Aba "Condições"

```
┌────────────────────────────────────────────┐
│ Condições                                  │
├────────────────────────────────────────────┤
│                                            │
│ Energia:                                   │
│ ☐ Iniciar a tarefa somente se o          │
│   computador estiver conectado            │
│   à energia CA                            │
│                                            │
│ ☐ Interromper se o computador alternar   │
│   para energia da bateria                 │
│                                            │
│ Ativar o computador para executar        │
│ esta tarefa: ☐                            │
│                                            │
└────────────────────────────────────────────┘
```

**Recomendação**: **Desmarque** todas as opções de energia para garantir execução.

### 4.5. Aba "Configurações"

```
┌────────────────────────────────────────────┐
│ Configurações                              │
├────────────────────────────────────────────┤
│                                            │
│ ☑ Permitir que a tarefa seja executada   │
│   sob demanda                             │
│                                            │
│ ☑ Executar a tarefa assim que possível   │
│   após a hora agendada ter sido perdida  │
│                                            │
│ ☐ Se a tarefa falhar, reiniciar a cada:  │
│   [1 minuto ▼]                            │
│   Tentativa de reinicialização por até:  │
│   [3 vezes ▼]                             │
│                                            │
└────────────────────────────────────────────┘
```

**Recomendação**:
- ☑ **Permitir que a tarefa seja executada sob demanda** (para testes)
- ☑ **Executar a tarefa assim que possível após a hora agendada ter sido perdida**
- Pode marcar reinicialização se quiser (opcional)

Clique em **OK** para salvar.

---

## ✅ Passo 5: Testar a Tarefa Agendada

Não precisa esperar até as 9h! Vamos testar agora.

### 5.1. Encontrar sua tarefa

Na lista de tarefas, procure por: **Check Premium Expiring**

### 5.2. Executar manualmente

1. **Clique com botão direito** na tarefa
2. Selecione **Executar**

```
┌─────────────────────────┐
│ Check Premium Expiring  │  ← Sua tarefa
├─────────────────────────┤
│ Executar            ←── CLIQUE
│ Finalizar               │
│ Desabilitar             │
│ Exportar...             │
│ Propriedades            │
│ Excluir                 │
└─────────────────────────┘
```

### 5.3. Verificar execução

**Coluna "Última Execução"** deve mostrar a data/hora atual.

**Coluna "Último Resultado"** deve mostrar:
- `0x0` ou `Êxito` = Funcionou ✅
- Outro código = Erro ❌

### 5.4. Verificar notificações criadas

Abra PowerShell e execute:

```powershell
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
python scripts\list_notifications.py
```

Deve mostrar notificações recentes (se houver Premium expirando).

---

## 📊 Passo 6: Monitorar Logs (Opcional mas Recomendado)

### 6.1. Criar arquivo de log

Modificar o script `.bat` para salvar logs:

Editar `scripts\run_check_expiring_premium.bat`:

```batch
@echo off
REM Script para executar verificacao de Premium expirando

REM Definir arquivo de log com data
set LOG_DIR=C:\ProjectsDjango\cgbookstore_v3\logs
set LOG_FILE=%LOG_DIR%\premium_check_%date:~6,4%%date:~3,2%%date:~0,2%.log

REM Criar pasta de logs se não existir
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Redirecionar output para arquivo de log
(
    echo ============================================================
    echo VERIFICACAO DE PREMIUM EXPIRANDO
    echo Data/Hora: %date% %time%
    echo ============================================================
    echo.

    cd /d "C:\ProjectsDjango\cgbookstore_v3"
    call .venv\Scripts\activate.bat
    python manage.py check_expiring_premium
    deactivate

    echo.
    echo ============================================================
    echo EXECUCAO CONCLUIDA: %date% %time%
    echo ============================================================
) >> "%LOG_FILE%" 2>&1
```

### 6.2. Ver logs

```powershell
# Ver log de hoje
type C:\ProjectsDjango\cgbookstore_v3\logs\premium_check_20251104.log

# Ver últimas linhas
Get-Content C:\ProjectsDjango\cgbookstore_v3\logs\premium_check_20251104.log -Tail 20
```

---

## 🔍 Passo 7: Verificar Histórico de Execução

### No Task Scheduler:

1. Selecione sua tarefa: **Check Premium Expiring**
2. Embaixo, clique na aba **Histórico**

```
┌──────────────────────────────────────────────────────┐
│ [Geral] [Gatilhos] [Ações] [Histórico]              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Data/Hora         Nível  Origem    ID Evento       │
│ ──────────────────────────────────────────────────  │
│ 04/11 09:00:00   Info   TaskSched  100  Iniciado   │
│ 04/11 09:00:15   Info   TaskSched  102  Concluído  │
│ 03/11 09:00:00   Info   TaskSched  100  Iniciado   │
│ 03/11 09:00:12   Info   TaskSched  102  Concluído  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**IDs de Evento úteis:**
- **100**: Tarefa iniciada
- **102**: Tarefa concluída com sucesso
- **103**: Tarefa falhou
- **201**: Ação "Iniciar programa" foi executada

---

## 🚨 Troubleshooting

### Problema 1: Tarefa não executa

**Sintoma**: Passa das 9h e nada acontece

**Soluções**:

1. **Verificar se a tarefa está habilitada**:
   - Clique direito na tarefa
   - Certifique-se que "Desabilitar" está disponível (se estiver "Habilitar", ela está desabilitada)

2. **Verificar condições de energia**:
   - Propriedades → Aba "Condições"
   - Desmarcar todas as opções relacionadas a energia

3. **Verificar conta de usuário**:
   - Propriedades → Aba "Geral"
   - Usar "Executar independentemente de o usuário estar conectado"

### Problema 2: Tarefa executa mas falha

**Sintoma**: Último Resultado mostra código de erro (não é 0x0)

**Soluções**:

1. **Verificar caminho do script**:
   ```
   C:\ProjectsDjango\cgbookstore_v3\scripts\run_check_expiring_premium.bat
   ```
   Certifique-se que o arquivo existe e o caminho está correto.

2. **Testar o script manualmente**:
   ```cmd
   cd C:\ProjectsDjango\cgbookstore_v3
   scripts\run_check_expiring_premium.bat
   ```

3. **Verificar ambiente virtual**:
   - `.venv` existe?
   - Django está instalado?

4. **Executar com privilégios de administrador**:
   - Propriedades → Aba "Geral"
   - Marcar "Executar com privilégios mais altos"

### Problema 3: Script não encontra Python ou Django

**Sintoma**: Erro "python não é reconhecido" ou "ModuleNotFoundError"

**Solução**: Usar caminho absoluto para o Python no script `.bat`:

```batch
REM Em vez de:
python manage.py check_expiring_premium

REM Use:
C:\ProjectsDjango\cgbookstore_v3\.venv\Scripts\python.exe manage.py check_expiring_premium
```

### Problema 4: Notificações não são enviadas

**Sintoma**: Tarefa executa com sucesso mas nenhuma notificação

**Causas**:
1. Não há Premium expirando nos próximos 3 dias
2. Usuários já foram notificados hoje

**Verificar**:
```powershell
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
python manage.py check_expiring_premium --dry-run
```

---

## 📝 Checklist Final

Antes de considerar concluído, verifique:

- [ ] Script `.bat` criado e testado manualmente
- [ ] Tarefa criada no Task Scheduler
- [ ] Nome: "Check Premium Expiring"
- [ ] Gatilho: Diariamente às 09:00
- [ ] Ação: Executar o script `.bat`
- [ ] Propriedades configuradas corretamente
- [ ] Teste manual executado com sucesso
- [ ] Última Execução mostra data/hora recente
- [ ] Último Resultado é 0x0 (sucesso)
- [ ] Logs sendo gerados (opcional)
- [ ] Notificações aparecendo no banco de dados

---

## 🎯 Próximos Passos

Depois de configurado:

1. **Aguardar primeira execução automática** (amanhã às 9h)
2. **Verificar logs** no dia seguinte
3. **Monitorar notificações** criadas
4. **Ajustar horário** se necessário

---

## 📞 Comandos Úteis

### Ver status da tarefa:
```powershell
schtasks /query /tn "Check Premium Expiring" /fo list /v
```

### Executar manualmente via CMD:
```cmd
schtasks /run /tn "Check Premium Expiring"
```

### Desabilitar temporariamente:
```cmd
schtasks /change /tn "Check Premium Expiring" /disable
```

### Habilitar novamente:
```cmd
schtasks /change /tn "Check Premium Expiring" /enable
```

### Deletar tarefa:
```cmd
schtasks /delete /tn "Check Premium Expiring" /f
```

---

## ✅ Conclusão

Parabéns! 🎉 Seu sistema de notificações automáticas está configurado e rodando.

**Lembre-se**:
- ✅ Executa todo dia às 9h automaticamente
- ✅ Não precisa deixar terminal aberto
- ✅ Funciona mesmo se você não estiver logado
- ✅ Envia no máximo 1 notificação por dia por usuário
- ✅ Logs salvos para auditoria

**Boa sorte!** 🚀
