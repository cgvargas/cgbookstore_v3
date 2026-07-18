"""
Product Analytics — CG.BookStore v3

Rastreia comportamento dos usuários dentro da plataforma.
Responsabilidade: medir sessões web, eventos de funil e
gerar snapshots diários de métricas de produto.

Fontes de dados externas (lidas, não duplicadas):
- accounts.BookShelf / ReadingProgress
- finance.Subscription
- partners.AffiliatePartnerClick
- chatbot_literario.ChatSession
- monitoring.AIUsageLog
- recommendations.UserBookInteraction
"""
