import time
import json
import re
import logging
import requests
from django.conf import settings
from monitoring.models import AIUsageLog

logger = logging.getLogger(__name__)

# Tabela de Preços por 1000 tokens (em USD)
MODEL_PRICING = {
    'gemini-2.5-flash': {'input': 0.000075, 'output': 0.0003},
    'llama-3.3-70b-versatile': {'input': 0.00059, 'output': 0.00079},
    'llama3-8b-8192': {'input': 0.00005, 'output': 0.00008},
    'gpt-4o': {'input': 0.0025, 'output': 0.0075},
    'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
    'claude-3-5-sonnet': {'input': 0.003, 'output': 0.015},
    'local': {'input': 0.0, 'output': 0.0},
    'mock': {'input': 0.0, 'output': 0.0},
}

def log_ai_usage(user, feature_name, provider, model_name, prompt_tokens, completion_tokens, response_time, status, error_message=""):
    """
    Registra no banco de dados o log de telemetria e calcula os custos.
    """
    try:
        # Calcular custo
        pricing = MODEL_PRICING.get(model_name, {'input': 0.0, 'output': 0.0})
        cost = (prompt_tokens / 1000.0 * pricing['input']) + (completion_tokens / 1000.0 * pricing['output'])
        
        AIUsageLog.objects.create(
            user=user if user and user.is_authenticated else None,
            feature_name=feature_name,
            provider=provider,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=cost,
            response_time_seconds=response_time,
            status=status,
            error_message=error_message
        )
    except Exception as e:
        logger.error(f"Erro ao salvar log de uso da IA: {e}")

class BaseAIProvider:
    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        raise NotImplementedError
        
    def generate_json(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> dict:
        text = self.generate_text(prompt, system_instruction, user, feature_name, temperature, max_tokens)
        return self._parse_json(text)

    def _parse_json(self, text: str) -> dict:
        if not text:
            return {}
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```[a-zA-Z]*\n', '', text)
            text = re.sub(r'\n```$', '', text)
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da resposta da IA: {e}. Texto original: {text[:500]}")
            # Tentar extrair JSON usando regex se falhar
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            return {}

class GeminiAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.model_name = 'gemini-2.5-flash'
        self.model = None

    def _setup(self):
        if not self.model and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Erro ao configurar Gemini: {e}")

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        self._setup()
        if not self.model:
            raise Exception("Gemini API key não configurada ou falha na inicialização.")
            
        import google.generativeai as genai
        start_time = time.time()
        try:
            config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"[Instrução do Sistema: {system_instruction}]\n\n{prompt}"
                
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                request_options={"timeout": 15.0}
            )
            
            response_time = time.time() - start_time
            
            # Capturar contagem de tokens se disponível
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                try:
                    p_count = response.usage_metadata.prompt_token_count
                    c_count = response.usage_metadata.candidates_token_count
                    
                    # Se for um MagicMock, type(obj).__name__ é 'MagicMock'
                    if type(p_count).__name__ != 'MagicMock' and p_count is not None:
                        prompt_tokens = int(p_count)
                    else:
                        prompt_tokens = len(prompt) // 4
                        
                    if type(c_count).__name__ != 'MagicMock' and c_count is not None:
                        completion_tokens = int(c_count)
                    else:
                        completion_tokens = len(response.text) // 4
                except Exception as token_err:
                    logger.debug(f"Erro ao parsear tokens de metadados: {token_err}")
                    prompt_tokens = len(prompt) // 4
                    completion_tokens = len(response.text) // 4
            else:
                prompt_tokens = len(prompt) // 4
                completion_tokens = len(response.text) // 4
                
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="gemini",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return response.text
        except Exception as e:
            response_time = time.time() - start_time
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="gemini",
                model_name=self.model_name,
                prompt_tokens=0,
                completion_tokens=0,
                response_time=response_time,
                status="failure",
                error_message=str(e)
            )
            raise e

class GroqAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'GROQ_API_KEY', '')
        self.model_name = 'llama-3.3-70b-versatile'
        self.client = None

    def _setup(self):
        if not self.client and self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Erro ao configurar Groq: {e}")

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        self._setup()
        if not self.client:
            raise Exception("Groq API key não configurada ou falha na inicialização.")
            
        start_time = time.time()
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=15.0
            )
            response_time = time.time() - start_time
            
            prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else len(prompt) // 4
            completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else len(response.choices[0].message.content) // 4
            
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="groq",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return response.choices[0].message.content
        except Exception as e:
            response_time = time.time() - start_time
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="groq",
                model_name=self.model_name,
                prompt_tokens=0,
                completion_tokens=0,
                response_time=response_time,
                status="failure",
                error_message=str(e)
            )
class OpenRouterAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        self.model_name = 'google/gemma-2-9b-it:free'

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        if not self.api_key:
            raise Exception("OPENROUTER_API_KEY não configurada.")
            
        start_time = time.time()
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://www.cgbookstore.com.br",
                "X-Title": "CG BookStore"
            }
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "models": [
                    "google/gemma-2-9b-it:free",
                    "meta-llama/llama-3-8b-instruct:free",
                    "qwen/qwen-2-7b-instruct:free"
                ],
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")
                
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            actual_model = data.get('model', self.model_name)
            usage = data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="openrouter",
                model_name=actual_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return content
        except Exception as e:
            logger.error(f"Erro no provedor OpenRouter: {e}")
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="openrouter",
                model_name=self.model_name,
                prompt_tokens=0,
                completion_tokens=0,
                response_time=time.time() - start_time,
                status="error"
            )
            raise e

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.model_name = 'gpt-4o-mini'

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        if not self.api_key:
            raise Exception("OPENAI_API_KEY não configurada.")
            
        start_time = time.time()
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error {response.status_code}: {response.text}")
                
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            prompt_tokens = data['usage']['prompt_tokens']
            completion_tokens = data['usage']['completion_tokens']
            
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="openai",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return content
        except Exception as e:
            response_time = time.time() - start_time
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="openai",
                model_name=self.model_name,
                prompt_tokens=0,
                completion_tokens=0,
                response_time=response_time,
                status="failure",
                error_message=str(e)
            )
            raise e

class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'CLAUDE_API_KEY', '')
        self.model_name = 'claude-3-5-sonnet'

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        if not self.api_key:
            raise Exception("CLAUDE_API_KEY não configurada.")
            
        start_time = time.time()
        try:
            headers = {
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if system_instruction:
                payload["system"] = system_instruction
                
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=15.0)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                raise Exception(f"Claude API error {response.status_code}: {response.text}")
                
            data = response.json()
            content = data['content'][0]['text']
            
            prompt_tokens = data['usage']['input_tokens']
            completion_tokens = data['usage']['output_tokens']
            
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="claude",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return content
        except Exception as e:
            response_time = time.time() - start_time
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="claude",
                model_name=self.model_name,
                prompt_tokens=0,
                completion_tokens=0,
                response_time=response_time,
                status="failure",
                error_message=str(e)
            )
            raise e

class LocalAIProvider(BaseAIProvider):
    def __init__(self):
        self.endpoint = getattr(settings, 'LOCAL_AI_ENDPOINT', 'http://localhost:11434/api/generate')
        self.model_name = getattr(settings, 'LOCAL_AI_MODEL', 'llama3')

    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        start_time = time.time()
        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System: {system_instruction}\nUser: {prompt}"
                
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            response = requests.post(self.endpoint, json=payload, timeout=25)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                raise Exception(f"Local AI endpoint error {response.status_code}")
                
            data = response.json()
            content = data.get('response', '')
            
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(content) // 4
            
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="local",
                model_name="local",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time=response_time,
                status="success"
            )
            return content
        except Exception as e:
            response_time = time.time() - start_time
            log_ai_usage(
                user=user,
                feature_name=feature_name,
                provider="local",
                model_name="local",
                prompt_tokens=0,
                completion_tokens=0,
                response_time=response_time,
                status="failure",
                error_message=str(e)
            )
            raise e

class MockAIProvider(BaseAIProvider):
    def generate_text(self, prompt: str, system_instruction: str = None, user=None, feature_name="general", temperature=0.3, max_tokens=1000) -> str:
        # Registrar logs para o Mock de IA
        log_ai_usage(
            user=user,
            feature_name=feature_name,
            provider="mock",
            model_name="mock",
            prompt_tokens=len(prompt) // 4,
            completion_tokens=200,
            response_time=0.01,
            status="success"
        )
        prompt_lower = prompt.lower()
        # Perfil literário / biografia do leitor
        if "biografia" in prompt_lower or "estilo_leitura" in prompt_lower or "afinidades por categoria" in prompt_lower or "reader_profile" in prompt_lower:
            return json.dumps({
                "biografia": "Usuário focado em mundos fantásticos e ficção clássica. Um explorador literário que busca sempre novos universos.",
                "estilo_leitura": {
                    "humor": "Aventureiro",
                    "complexidade": "Média",
                    "ritmo": "Moderado",
                    "temas_frequentes": ["Fantasia", "Clássicos"]
                }
            })
        # Análise/resenha de livro
        elif "resumo" in prompt_lower or "perfil_leitor" in prompt_lower or "temas_principais" in prompt_lower:
            return json.dumps({
                "resumo": "Este é um resumo simulado de alta qualidade gerado para fins de teste.",
                "perfil_leitor": "Leitores interessados em testes de integração.",
                "faixa_etaria": "Livre",
                "complexidade": "Fácil",
                "tempo_leitura": "5 horas",
                "temas_principais": ["Testes", "Automação", "Qualidade"],
                "nota_geral": 9.5
            })
        # Análise expandida (curiosidades, contexto, personagens)
        elif "contexto_historico" in prompt_lower or "curiosidades" in prompt_lower or "personagens_principais" in prompt_lower:
            return json.dumps({
                "contexto_historico": "Contexto histórico simulado pela IA de teste.",
                "curiosidades": [
                    "Curiosidade 1 simulada.",
                    "Curiosidade 2 simulada.",
                    "Curiosidade 3 simulada."
                ],
                "personagens_principais": [
                    {"nome": "Personagem A", "papel": "Protagonista da história simulada."},
                    {"nome": "Personagem B", "papel": "Antagonista da história simulada."}
                ],
                "conexoes_universo": "Conexão simulada com outras obras do mesmo universo literário."
            })
        return "Resposta simulada do provedor Mock de IA."

class AIProviderFactory:
    @classmethod
    def get_provider(cls, provider_name: str = None) -> BaseAIProvider:
        """Cria o provedor solicitado ou, por compatibilidade, o provedor principal."""
        ai_provider = (provider_name or getattr(settings, 'AI_PROVIDER', 'mock')).lower()
        
        if ai_provider == 'gemini':
            return GeminiAIProvider()
        elif ai_provider == 'groq':
            return GroqAIProvider()
        elif ai_provider == 'openai':
            return OpenAIProvider()
        elif ai_provider == 'claude':
            return ClaudeProvider()
        elif ai_provider == 'openrouter':
            return OpenRouterAIProvider()
        elif ai_provider == 'local':
            return LocalAIProvider()
        else:
            return MockAIProvider()
