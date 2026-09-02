# DOC_EDITOR_3000 - Editor Profissional de Documentos

> ⚠️ **AVISO LEGAL / FINS EDUCATIVOS**
> Este software é **destinado exclusivamente a fins educativos e de estudo**. Você é o único responsável por qualquer uso.
> Só use este programa com documentos de sua **propriedade legítima** ou com **autorização expressa**. A alteração de documentos oficiais pode configurar crime de falsificação documental (Art. 298-299, Código Penal Brasileiro), fraude acadêmica, trabalhista ou bancária, entre outros delitos puníveis com prisão e multa.
> Ao usar este programa, você declara que vai usá-lo apenas com fins legítimos e educativos, assumindo toda a responsabilidade por qualquer uso indevido. Os autores/colaboradores **não se responsabilizam por uso ilícito**.

## O que o programa faz

Ferramenta gráfica avançada que permite **substituir texto em imagens, PDFs e DOCX** de forma intuitiva: abrir → detectar texto com OCR → clicar (ou buscar) o que quer mudar → digitar a substituição em tempo real com controle total de tipografia e filtros forenses → salvar. Além disso, permite sobrepor fotos 3x4 com alças interativas, ajustar atributos NTFS e controlar metadados (EXIF).

## Principais funcionalidades

- **Edição de Texto com OCR Avançado:** clique na palavra (ou use o campo "Buscar") e digite o novo texto. Controles em tempo real: fonte (Arial, Times, Courier, Century, etc.), negrito, itálico, tamanho, espessura de traço decimal, espaçamento entre letras (tracking), rotação, cor customizada / pipeta, nitidez, escuridão, blur, ruído de grão, aberração cromática subpixel (arco-íris laranja/azul) e compressão JPEG de scanners/WhatsApp.
- **Detecção OCR por Região:** clique e arraste no documento para rodar OCR localizado rapidamente.
- **Foto 3x4 / Imagem Sobreposta:** carregue uma foto, arraste e redimensione diretamente pelas alças no canvas com controle de foco, ruído, saturação, brilho, contraste e rotação.
- **Comparador Lado a Lado Permanente (Live Split Dock):** visualização ampliada e instantânea [ORIGINAL vs MODIFICADO] do trecho selecionado com réguas milimétricas e zoom ajustável.
- **Análise Forense e Veracidade:** comparador visual Antes vs Depois (Overlay 0-100%, Lado a Lado, Mapa de Ruído / ELA - Error Level Analysis) com cálculo de score de camuflagem, coerência luminosa e recomendações inteligentes.
- **Propriedades Reais & Metadados:** tabela EXIF completa com edição por clique duplo, gravação de atributos reais de datas NTFS no Windows (`kernel32`) e injeção de padding binário para tamanho em KB.
- **Formatos Suportados:** abre PDF, DOCX, DOC, JPG, PNG, BMP, TIFF. Salva como PNG, JPEG (com EXIF) ou PDF.

## Arquitetura do Projeto (Padrão Modular Senior)

O projeto é desacoplado em camadas com separação clara de responsabilidades:

```
PROJETO CAMELÔ/
│
├── core/                                # Camada de Processamento (Engine pura)
│   ├── __init__.py                      # Exportações públicas da engine
│   ├── constants.py                     # Constantes de fontes e famílias tipográficas
│   ├── fonts.py                         # Resolução inteligente de variantes TTF
│   ├── image_processing.py              # OCR, substituição de texto, foto 3x4 e réguas
│   └── metadata.py                      # Atributos reais NTFS, padding em KB, PDF e EXIF
│
├── ui/                                  # Camada de Apresentação (Tkinter / TTK)
│   ├── __init__.py                      # Exportações da UI
│   ├── themes.py                        # Gerenciamento de temas (Claro e VS Code Dark)
│   ├── canvas_handler.py                # Mixin de eventos do Canvas (Pan, Zoom, Lupa HUD, Handles)
│   ├── dialogs/                         # Janelas Modais e Diálogos
│   │   ├── __init__.py
│   │   ├── forensics.py                 # Análise Forense & ELA
│   │   ├── viewer.py                    # Visualizador da imagem limpa com zoom/lupa
│   │   ├── options.py                   # Tema e tamanho da tela
│   │   └── metadata_dialog.py           # Tabela EXIF e propriedades de arquivo
│   └── main_window.py                   # Janela Principal (App tk.Tk), Menus e Toolbar
│
├── doc_editor.py                        # Ponto de entrada oficial (preserva compatibilidade)
├── compilar.py                          # Compilador autônomo PyInstaller (.exe)
├── requirements.txt                     # Dependências do projeto
├── app_icon.ico                         # Ícone do aplicativo
├── iniciar.bat                          # Inicializador padrão
├── DOC_EDITOR_3000.bat                  # Atalho de inicialização
└── DOC_EDITOR_3000.vbs                  # Atalho de inicialização silenciosa
```

## Requisitos

- **Windows 10/11**
- **Python 3.11+** (no ambiente de desenvolvimento)
- **LibreOffice** (opcional, para abrir arquivos .docx/.doc sem o Microsoft Office)

## Instalação e Execução

### Rodando diretamente:
Basta dar dois cliques em `iniciar.bat` ou rodar via terminal:
```bash
iniciar.bat
```

### Ambiente virtual (desenvolvimento):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python doc_editor.py
```

## Compilando o Executável (.exe)

O script `compilar.py` empacota a aplicação automaticamente usando o PyInstaller com todas as dependências e submódulos:

```bash
.venv\Scripts\activate
python compilar.py
```
O executável autônomo será gerado em:
`dist\DOC_EDITOR_3000\DOC_EDITOR_3000.exe`

---

**Versão:** 3.1.0 (Arquitetura Modular)  
**Licença:** Uso educativo e de pesquisa
