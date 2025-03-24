from PIL import Image, ImageDraw, ImageFont
import os

# Verificar se o diretório existe
if not os.path.exists('app/static'):
    os.makedirs('app/static')

# Criar uma imagem simples para o logotipo
img = Image.new('RGBA', (300, 100), color=(255, 255, 255, 0))
d = ImageDraw.Draw(img)

# Desenhar um retângulo verde como fundo
d.rectangle([(0, 0), (300, 100)], fill=(0, 100, 0, 255))

# Adicionar texto
try:
    # Tentar carregar uma fonte
    font = ImageFont.truetype("arial.ttf", 36)
except IOError:
    # Usar fonte padrão se não encontrar arial
    font = ImageFont.load_default()

# Escrever o texto do logo
d.text((20, 30), "Brauna Finanças", fill=(255, 255, 255), font=font)

# Salvar a imagem
img.save('app/static/brauna_logo.png')

print("Logo criado com sucesso em app/static/brauna_logo.png") 