import os

# Conteúdo do arquivo .env
env_content = """# Configuracao do Supabase
SUPABASE_URL=https://fbofkwqycnqxoddcgmqk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZib2Zrd3F5Y25xeG9kZGNnbXFrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2ODc1MDQsImV4cCI6MjA1ODI2MzUwNH0.NtCFi6cwuzXkUtGKjnoWMh0OVKXcDrWTaW-XZMtPBRs
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZib2Zrd3F5Y25xeG9kZGNnbXFrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjY4NzUwNCwiZXhwIjoyMDU4MjYzNTA0fQ.0xwTVQKcUsIroyA_apqUa5Y_3aFcw-sxZMTpPlnU6mY
APP_NAME=Brauna Financas
APP_VERSION=1.0.0
"""

# Remover o arquivo .env existente se houver
if os.path.exists('.env'):
    os.remove('.env')

# Criar um novo arquivo .env com a codificação UTF-8
with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("Arquivo .env criado com sucesso usando codificação UTF-8.") 