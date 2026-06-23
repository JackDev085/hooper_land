import yt_dlp
from pathlib import Path
from yt_dlp.utils import DownloadError, ExtractorError

def baixa_videos_treino(lista, cookies_path: str | None = None):
    if not lista:
        print("Lista vazia.")
        return

    downloads = Path("downloads")
    downloads.mkdir(parents=True, exist_ok=True)

    arquivos_existentes = {p.name for p in downloads.iterdir() if p.is_file()}
    data = [exercicio.link_video for exercicio in lista]

    for link_video in data:
        print("=" * 60)
        filename = f"{link_video}.mp4"

        if filename in arquivos_existentes:
            print(f"✅ Vídeo {link_video} já baixado, pulando.")
            continue

        url = f"https://www.youtube.com/watch?v={link_video}"
        print(f"🎬 Baixando vídeo {link_video}...")

        # opções base
        ydl_opts = {
            "outtmpl": str(downloads / f"{link_video}.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        # cookies (manual ou automático)
        if cookies_path:
            ydl_opts["cookiefile"] = cookies_path
        else:
            ydl_opts["cookiesfrombrowser"] = ("chrome",)

        # tenta primeiro com o melhor formato possível
        formatos_tentados = ["best"]
        sucesso = False

        for formato in formatos_tentados:
            ydl_opts["format"] = formato
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print(f"✅ Download concluído ({formato})!")
                sucesso = True
                break
            except DownloadError as e:
                msg = str(e)
                print(f"❌ Erro ao baixar {link_video} ({formato}): {msg}")

                if "Requested format is not available" in msg:
                    print("🔄 Tentando outro formato...")
                    continue
                elif "Sign in to confirm" in msg or "use --cookies" in msg.lower():
                    print("⚠️ YouTube exige autenticação. Passe cookies_path.")
                    break
                else:
                    print("⚠️ Erro desconhecido, continuando para o próximo vídeo.")
                    break
            except ExtractorError as e:
                print(f"⚠️ Erro no extrator ({link_video}): {e}")
                break
            except Exception as e:
                print(f"⚠️ Erro inesperado: {e}")
                break

        if not sucesso:
            print(f"🚫 Não foi possível baixar {link_video}. Pulando...\n")
