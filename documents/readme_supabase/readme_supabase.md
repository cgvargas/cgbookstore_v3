# 🚀 CG.BookStore v3 - Configuração com Supabase

## 📋 Pré-requisitos

- Python 3.10+
- Conta no [Supabase](https://supabase.com)
- Git

## 🔧 Configuração do Supabase

### 1. Criar Projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com)
2. Faça login ou crie uma conta
3. Clique em **"New Project"**
4. Configure:
   - **Project Name**: `cgbookstore` (ou nome de sua preferência)
   - **Database Password**: Crie uma senha forte (guarde-a!)
   - **Region**: Escolha a mais próxima (São Paulo recomendado)
   - **Pricing Plan**: Free tier funciona perfeitamente

### 2. Obter Credenciais

Após criar o projeto, vá em **Settings > API** e copie:

- **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
- **Anon/Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (opcional)

Para o banco de dados, vá em **Settings > Database** e copie:

- **Connection String > URI**: A string completa de conexão

### 3. Configurar Variáveis de