from anthropic import Anthropic
from config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

models = client.models.list()

for m in models.data:
    print(m.id)