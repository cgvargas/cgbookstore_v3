from django.views.generic import TemplateView

# A classe 'ChatbotView' precisa ser definida aqui para que possa ser importada.
class ChatbotView(TemplateView):
    """
    View para a interface do chatbot.
    Renderiza o template 'chatbot_literario/chat.html'.
    """
    template_name = 'chatbot_literario/chat.html'
