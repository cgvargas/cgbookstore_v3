import shutil
import tempfile
import traceback
import zipfile
from ebooklib import epub

try:
    import mobi
except ImportError:
    mobi = None

def convert_kindle_to_epub(kindle_file_path):
    """
    Converte arquivo Kindle (.mobi, .azw3) para EPUB.
    Retorna o caminho do arquivo EPUB gerado se sucesso, ou None.
    Cria o arquivo .epub no mesmo diretório do arquivo original.
    """
    if not mobi:
        print("Biblioteca 'mobi' não instalada.")
        return None
        
    temp_dir = tempfile.mkdtemp()
    try:
        # Extrair conteúdo do MOBI
        print(f"Extraindo MOBI: {kindle_file_path}")
        # mobi.extract retorna (temp_dir_path, html_file_path)
        extracted_dir, html_path = mobi.extract(kindle_file_path)
        
        if not html_path or not os.path.exists(html_path):
             print("Falha na extração do MOBI: HTML não encontrado.")
             return None

        # Criar EPUB
        book = epub.EpubBook()
        
        # Metadados básicos
        filename = os.path.basename(kindle_file_path)
        title = os.path.splitext(filename)[0]
        book.set_title(title)
        book.set_language('pt')
        book.add_author('Unknown') # Tentar extrair do MOBI seria ideal, mas complexo aqui
        
        # Ler conteúdo HTML extraído
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Limpar HTML básico se necessário (mobi extract as vezes deixa lixo)
        # Por enquanto, confiar no raw
            
        c1 = epub.EpubHtml(title='Conteúdo', file_name='content.xhtml', lang='pt')
        c1.content = content
        book.add_item(c1)
        
        # Adicionar imagens extraídas
        parent_dir = os.path.dirname(html_path)
        # O mobi extai imagens na mesma pasta ou subpastas
        added_images = []
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                    # Adicionar imagem ao EPUB
                    img_path = os.path.join(root, file)
                    try:
                        with open(img_path, 'rb') as f_img:
                            img_content = f_img.read()
                        
                        img_item = epub.EpubImage(
                            uid=file,
                            file_name=file,
                            media_type=f'image/{file.split(".")[-1].replace("jpg", "jpeg")}',
                            content=img_content
                        )
                        book.add_item(img_item)
                        added_images.append(file)
                    except Exception as e:
                        print(f"Erro ao adicionar imagem {file}: {e}")

        # Definir estrutura
        book.toc = (epub.Link('content.xhtml', 'Início', 'intro'),)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Adicionar CSS básico
        style = 'body { font-family: serif; } img { max-width: 100%; }'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        
        book.spine = ['nav', c1]
        
        # Gerar caminho de saída
        dir_name = os.path.dirname(kindle_file_path)
        base_name = os.path.splitext(os.path.basename(kindle_file_path))[0]
        epub_path = os.path.join(dir_name, f"{base_name}.epub")
        
        print(f"Escrevendo EPUB em: {epub_path}")
        epub.write_epub(epub_path, book, {})
        
        # Validar se o arquivo gerado é um ZIP válido (EPUB é um ZIP)
        if not zipfile.is_zipfile(epub_path):
            print(f"Erro CRÍTICO: O arquivo gerado em {epub_path} não é um ZIP válido e será descartado.")
            return None
            
        try:
             with zipfile.ZipFile(epub_path, 'r') as z:
                 if z.testzip() is not None:
                     print(f"Erro CRÍTICO: O arquivo ZIP gerado em {epub_path} está corrompido.")
                     return None
        except Exception as e:
            print(f"Erro ao validar ZIP: {e}")
            return None
        
        return epub_path

    except Exception as e:
        print(f"Erro na conversão Kindle->EPUB: {e}")
        traceback.print_exc()
        return None
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            # Tentar limpar o diretório temporário criado pelo mobi (ele cria um em /temp também)
            if 'extracted_dir' in locals() and os.path.exists(extracted_dir):
                shutil.rmtree(extracted_dir, ignore_errors=True)
        except:
            pass
