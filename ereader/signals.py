import os
import tempfile
import shutil
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files import File
from .models import EBook
from .utils.kindle_converter import convert_kindle_to_epub

@receiver(pre_save, sender=EBook)
def convert_kindle_upload(sender, instance, **kwargs):
    """
    Intercepta uploads de arquivos .mobi / .azw3 e converte para .epub.
    """
    if not instance.epub_file:
        return
        
    try:
        # Verificar se o arquivo mudou (apenas em update, para evitar reprocessar)
        if instance.pk:
            try:
                old_instance = EBook.objects.get(pk=instance.pk)
                if old_instance.epub_file == instance.epub_file:
                    return # Arquivo não mudou
            except EBook.DoesNotExist:
                pass 
    except Exception:
        pass # Novo objeto ou erro, processar
        
    filename = instance.epub_file.name
    # Handle cases where name is full path
    base_name = os.path.basename(filename)
    base, ext = os.path.splitext(base_name)
    ext = ext.lower()
    
    if ext in ['.mobi', '.azw3', '.prc']:
        print(f"[KindleConverter] Detectado arquivo Kindle: {filename}. Iniciando conversão...")
        
        # Criar arquivo temporário para o input
        # Precisamos escrever o conteúdo do upload no disco para o mobi ler
        # Delete=False porque o Windows nao permite abrir o arquivo se ele estiver aberto por outro processo (NamedTemporaryFile quirks)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_input:
            try:
                # Se o arquivo for muito grande, chunks.
                if instance.epub_file.multiple_chunks():
                    for chunk in instance.epub_file.chunks():
                        tmp_input.write(chunk)
                else:
                    tmp_input.write(instance.epub_file.read())
            except Exception as e:
                # As vezes o arquivo já está fechado ou lido
                instance.epub_file.open()
                tmp_input.write(instance.epub_file.read())
                
            tmp_input_path = tmp_input.name
            
        try:
            # Chamar conversor
            epub_path = convert_kindle_to_epub(tmp_input_path)
            
            if epub_path and os.path.exists(epub_path):
                # Ler o epub gerado e substituir no campo
                with open(epub_path, 'rb') as f_epub:
                    new_filename = base + '.epub'
                    # save=False evita loop infinito recursivo de save()
                    instance.epub_file.save(new_filename, File(f_epub), save=False)
                    print(f"[KindleConverter] Sucesso! Salvo como {new_filename}")
                    
                # Atualizar source se for upload manual para indicar conversão
                if instance.source == 'upload':
                    instance.description += f"\n\n(Convertido automaticamente de {ext})"
                    
                # Limpar epub gerado
                try:
                    os.remove(epub_path)
                except: pass
            else:
                print("[KindleConverter] Falha na conversão. Mantendo arquivo original.")
                
        except Exception as e:
            print(f"[KindleConverter] Erro no signal de conversão: {e}")
        finally:
            # Limpar input temp
            if os.path.exists(tmp_input_path):
                try:
                    os.remove(tmp_input_path)
                except: pass
