import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("     COMPILADOR OFICIAL DOC_EDITOR_3000 (.EXE)")
    print("=" * 60)
    
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    os.chdir(diretorio_atual)
    
    # 1. Instalar PyInstaller se não estiver presente
    try:
        import PyInstaller
        print("\n[OK] PyInstaller já está instalado.")
    except ImportError:
        print("\nInstalando PyInstaller no ambiente virtual...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Comando de compilação autônomo
    print("\nCompilando aplicativo para pasta 'dist/DOC_EDITOR_3000'...")
    
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--name=DOC_EDITOR_3000",
        "--noconsole",
        "--onedir",
        "--icon=app_icon.ico",
        "--add-data=app_icon.ico;.",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=PIL.ImageFilter",
        "--hidden-import=PIL.ImageEnhance",
        "--hidden-import=PIL.ImageDraw",
        "--hidden-import=PIL.ImageFont",
        "--hidden-import=fitz",
        "--hidden-import=pymupdf",
        "--hidden-import=easyocr",
        "--hidden-import=docx",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--clean",
        "--noconfirm",
        "doc_editor.py"
    ]
    
    res = subprocess.run(comando)
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print(" [CONCLUÍDO COM SUCESSO!]")
        print(" O executável autônomo foi gerado em: dist\\DOC_EDITOR_3000\\")
        print(" O arquivo principal é: dist\\DOC_EDITOR_3000\\DOC_EDITOR_3000.exe")
        print(" Você pode compactar essa pasta em .ZIP e enviar para qualquer PC!")
        print("=" * 60)
    else:
        print("\n[ERRO] Ocorreu um problema durante a compilação.")

if __name__ == "__main__":
    main()
