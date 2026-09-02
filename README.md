# DOC_EDITOR_3000 - Editor Profissional de Documentos

> ⚠️ **AVISO LEGAL / FINO EDUCATIVO**
> Este software é **destinado exclusivamente a fins educativos e de estudo**. Você é o único responsável por qualquer uso.
> Só use este programa com documentos de sua **propriedade legítima** ou com **autorização expressa**. A alteração de documentos oficiais pode configurar crime de falsificação documental (Art. 298-299, Código Penal Brasileiro), fraude acadêmica, trabalhista ou bancária, entre outros delitos puníveis com prisão e multa.
> Ao usar este programa, você declara que vai usá-lo apenas com fins legítimos e educativos, assumindo toda a responsabilidade por qualquer uso indevido. Os autores/colaboradores **não se responsabilizam por uso ilícito**.

## O que o programa faz

Ferramenta gráfica que permite **substituir texto em imagens, PDFs e DOCX** de forma intuitiva: abrir → detectar texto com OCR → clicar (ou buscar) o que quer mudar → digitar a substituição → salvar. Além disso, permite sobrepor fotos 3x4 e controlar metadados (EXIF).

## Principais funcionalidades

- **Edição de Texto (OCR):** clique na palavra (ou use o campo "Buscar") e digite o novo texto. Controles: fonte (Arial, Times, Courier…), negrito, itálico, tamanho, traço, espaçamento, rotação, cor, nitidez, escuridão, blur, ruído, arco-íris subpixel e compressão JPG — tudo em tempo real.
- **Detecção por região:** clique e arraste na imagem para rodar OCR só naquela área (mais rápido).
- **Foto 3x4 sobreposta:** carregue uma foto, mova/redimensione pelas alças no canvas, ajuste foco/nitidez/brilho/contraste.
- **Comparador ao vivo (Live Dock):** preview lado a lado [ORIGINAL vs MODIFICADO] do trecho selecionado com zoom ajustável e grade milimétrica opcional.
- **Análise Forense:** mede a "compatibilidade" entre a edição e o documento original (score, ruído, bordas, luminância) com sugestões de ajuste (ruído, blur).
- **Metadados (EXIF):** visualiza todos os metadados da imagem e permite removê-los ao salvar (limpeza para imagens sensíveis).
- **Formatos:** abre PDF, DOCX, JPG, PNG, BMP, TIFF. Salva como PNG, JPEG ou PDF.

## Requisitos

- **Windows 10/11**
- **Python 3.11+** (já empacotado no executável; não é necessário para o usuário final)
- **LibreOffice** instalado (para abrir .docx/.doc) — https://www.libreoffice.org/download/download/
- **Microsoft Word** (opcional, alternativa ao LibreOffice para converter .docx)

## Instalação para desenvolvedores

```bash
# cria ambiente virtual e instala dependências
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install docx2pdf  # opcional, para Word
```

## Como usar (exemplos educativos)

### Exemplo 1: Corrigir erro tipográfico no seu próprio documento
1. Clique em **Abrir Documento** e escolha um PNG/PDF/DOCX
2. Clique em **Detectar texto** — ou clique e arraste na imagem para rodar OCR só naquela região
3. Clique na palavra que tem o erro (ex.: "Fulana" → deve ser "Fulano")
4. No campo **Novo**, digite "Fulano"
5. Ajuste tamanho/cor/fonte se necessário (comparador em tempo real ajuda)
6. Salve em PNG ou PDF

### Exemplo 2: Trocar a foto 3x4 de um documento seu
1. Abra o documento
2. Vá para a aba **🖼️ 2. Foto 3x4 / Imagem Sobreposta**
3. Clique em **📂 Carregar Foto**
4. Arraste a foto no canvas (aparece com borda laranja) para posicionar; puxe as alças para redimensionar
5. Ajuste nitidez/blur para o documento parecer natural
6. Salve

### Exemplo 3: Remover metadados (EXIF) de uma imagem
1. Abra a imagem
2. Vá para a aba **📊 3. Metadados (EXIF)**
3. Clique em **🔄 Atualizar** para ver todos os metadados (camera, data, GPS etc.)
4. Clique em **🗑️ Remover Todos** para limpar
5. Salve a imagem

### Exemplo 4: Verificar se a edição parece natural
1. Edite o texto (ex.: troque "2024" por "2025")
2. Clique em **🔬 Análise Forense**
3. Veja o **Score de Veracidade** e ajuste: se estiver baixo, aumente o "Ruído" ou o "Blur" na aba Texto até ficar verde

## Botões principais

| Botão | Ação |
|-------|------|
| **Abrir Documento** | Abre PDF, DOCX ou imagem |
| **Detectar texto (OCR)** | Roda OCR no documento inteiro |
| **Arrastar no canvas** | Roda OCR só na região arrastada (rápido) |
| **Salvar Imagem** | Exporta em PNG/JPG/PDF |
| **Limpar Tudo** | Remove todas as edições |
| **🔎 Lupa HUD** | Ativa lente de aumento 10x com cor RGB/HEX |
| **🔬 Análise Forense** | Compara original vs modificado e gera score |
| **Zoom - / 100% / +** | Controla o zoom do documento |

## Estrutura de pastas

```
.
├── doc_editor.py                  # Código-fonte principal
├── compilar.py                    # Script PyInstaller para gerar .exe
├── requirements.txt               # Dependências
├── app_icon.ico                   # Ícone do aplicativo
├── DOC_EDITOR_3000.bat            # Iniciador
├── DOC_EDITOR_3000.vbs            # Iniciador silencioso
├── iniciar.bat                    # Iniciador desenvolvimento
├── DOC_EDITOR_3000_Pronto_Para_Enviar.zip  # Executável zipado
├── dist/DOC_EDITOR_3000/          # Pasta gerada pelo PyInstaller
└── .venv/                         # Ambiente virtual Python
```

## Compilando o executável

```bash
.venv\Scripts\activate
python compilar.py
# resultado em: dist\DOC_EDITOR_3000\DOC_EDITOR_3000.exe
```

---

**Versão:** 3.0.0
**Autor:** Projeto de estudo
**Licença:** Uso educativo
