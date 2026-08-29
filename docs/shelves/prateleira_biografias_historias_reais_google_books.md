# Prateleira – Biografias & Histórias Reais
Projeto: CG.BookStore
Objetivo: Criar uma nova prateleira inexistente no catálogo atual e popular com livros reais,
bem avaliados e amplamente conhecidos, utilizando busca via Google Books API.

---

## 📚 Biografias & Histórias Reais (Sucessos Mundiais)

- Steve Jobs — Walter Isaacson
- Minha História (Becoming) — Michelle Obama
- O Diário de Anne Frank — Anne Frank
- Long Walk to Freedom — Nelson Mandela
- Eu Sou Malala — Malala Yousafzai
- Quando o Ar Rarefeito — Jon Krakauer
- A Educação de um Genial — Tara Westover
- Churchill: Uma Vida — Martin Gilbert
- Leonardo da Vinci — Walter Isaacson
- Malcolm X: Uma Vida de Reinvenções — Manning Marable

---

## 🔎 Observações Técnicas
- Priorizar buscas pelo padrão: "Título + Autor"
- Aceitar resultados nos idiomas:
  - PT-BR
  - EN
- Validar retorno mínimo:
  - Título
  - Autor(es)
  - Capa (thumbnail)
  - Descrição
- Evitar duplicação de livros já existentes no banco de dados
- Associar os livros à prateleira:
  - "Biografias & Histórias Reais"
