from lxml import etree
import difflib
from transformers import pipeline

# Carrega o modelo de resumo
resumidor = pipeline("summarization")

def carregar_arquivo_xml(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return f.read()

def comparar_xml(texto1, texto2):
    linhas1 = texto1.splitlines()
    linhas2 = texto2.splitlines()
    diff = difflib.unified_diff(linhas1, linhas2, fromfile='pagerduty-v8.1.0-dev.xml', tofile='custom.xml', lineterm='')
    return '\n'.join(diff)

def resumir_diferencas(diferencas):
    if not diferencas.strip():
        return "Nenhuma diferença encontrada."
    
    # O modelo tem limite de tokens. Reduzimos se for muito grande.
    if len(diferencas) > 1000:
        diferencas = diferencas[:1000]
    
    resumo = resumidor(diferencas, max_length=80, min_length=25, do_sample=False)
    return resumo[0]['summary_text']

if __name__ == "__main__":
    xml_base = carregar_arquivo_xml('pagerduty-v8.1.0-dev.xml')
    xml_custom = carregar_arquivo_xml('custom.xml')

    print("🔍 Comparando os arquivos...")
    diferencas = comparar_xml(xml_base, xml_custom)
    print("\n🧾 Diferenças encontradas:")
    print(diferencas)

    print("\n🧠 Resumo das mudanças:")
    resumo = resumir_diferencas(diferencas)
    print(resumo)
