#!/usr/bin/env python
"""
Script de diagnóstico para monitorar recursos do sistema
"""
import os
import psutil
import time
import sys
import platform
import streamlit as st

def formatar_bytes(bytes, sufixo="B"):
    """
    Escala os bytes para seu formato apropriado
    ex: 1253656 => '1.20MB'
    """
    fator = 1024
    for unidade in ["", "K", "M", "G", "T", "P"]:
        if bytes < fator:
            return f"{bytes:.2f}{unidade}{sufixo}"
        bytes /= fator

def monitorar_recursos(segundos=10, intervalo=1):
    """
    Monitora recursos do sistema por um período específico
    """
    print(f"Iniciando monitoramento de recursos por {segundos} segundos...")
    print(f"Sistema: {platform.system()} {platform.version()}")
    print(f"Processador: {platform.processor()}")
    print("-" * 50)
    
    # Informações de memória
    mem = psutil.virtual_memory()
    print(f"Memória total: {formatar_bytes(mem.total)}")
    print(f"Memória disponível: {formatar_bytes(mem.available)}")
    print(f"Porcentagem usada: {mem.percent}%")
    print("-" * 50)
    
    # Monitoramento contínuo
    cpu_max = 0
    mem_max = 0
    
    for i in range(segundos):
        cpu_percent = psutil.cpu_percent(interval=intervalo)
        mem_percent = psutil.virtual_memory().percent
        
        cpu_max = max(cpu_max, cpu_percent)
        mem_max = max(mem_max, mem_percent)
        
        print(f"[{i+1}/{segundos}] CPU: {cpu_percent}% | Memória: {mem_percent}%")
    
    print("-" * 50)
    print(f"Máximos detectados: CPU: {cpu_max}% | Memória: {mem_max}%")
    
    # Verificar processos que consomem mais recursos
    print("\nProcessos com maior consumo de memória:")
    processos = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processos.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Ordenar processos por uso de memória
    processos = sorted(processos, key=lambda x: x['memory_percent'], reverse=True)
    
    # Mostrar os 5 principais processos
    for i, proc in enumerate(processos[:5]):
        print(f"{i+1}. {proc['name']} (PID: {proc['pid']}): {proc['memory_percent']:.2f}%")
    
    return {
        'cpu_max': cpu_max,
        'mem_max': mem_max,
        'mem_total': mem.total,
        'mem_available': mem.available,
        'processos': processos[:5]
    }

def verificar_streamlit():
    """
    Verifica potenciais problemas com a configuração do Streamlit
    """
    print("\nVerificação da configuração do Streamlit:")
    try:
        # Verificar se o streamlit está instalado
        import streamlit
        print(f"Versão do Streamlit: {streamlit.__version__}")
        
        # Verificar arquivos do projeto
        arquivos_py = [f for f in os.listdir() if f.endswith('.py')]
        print(f"Arquivos Python encontrados: {len(arquivos_py)}")
        
        # Verificar uso de cache
        cache_issues = False
        for arquivo in arquivos_py:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    if '@st.cache' in conteudo and 'Streamlit' in arquivo:
                        print(f"AVISO: Uso de cache obsoleto em {arquivo}")
                        cache_issues = True
            except:
                pass
        
        if not cache_issues:
            print("Nenhum problema de cache obsoleto encontrado")
            
    except ImportError:
        print("Streamlit não está instalado")
    except Exception as e:
        print(f"Erro ao verificar Streamlit: {str(e)}")

def main():
    print("Diagnóstico de recursos do sistema")
    print("=" * 50)
    
    recursos = monitorar_recursos(segundos=5)
    verificar_streamlit()
    
    print("\nDiagnóstico concluído!")
    
    # Verificar se há algum problema crítico
    if recursos['mem_max'] > 90:
        print("\nALERTA CRÍTICO: Uso de memória muito alto detectado!")
        print("Isto pode causar travamentos ou desligamentos do sistema.")
    
    if recursos['cpu_max'] > 90:
        print("\nALERTA: Uso de CPU muito alto detectado!")
        print("Isto pode causar lentidão no sistema.")

if __name__ == "__main__":
    main() 