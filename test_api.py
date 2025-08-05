import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
print(f'Chave carregada: {api_key[:20]}...')

try:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model='claude-3-5-sonnet-20241022',
        max_tokens=50,
        messages=[{'role': 'user', 'content': 'Diga apenas: API funcionando!'}]
    )
    print('✅ SUCESSO:', message.content[0].text)
except Exception as e:
    print('❌ ERRO:', str(e))

