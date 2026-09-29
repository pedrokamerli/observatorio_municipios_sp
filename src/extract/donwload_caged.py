from ftplib import FTP, error_perm
from pathlib import Path

import py7zr


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANO = 2023

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/NOVO CAGED"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DESTINO_BASE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
    / str(ANO)
)

DESTINO_BASE.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. CONEXÃO FTP
# ============================================================

print("Conectando ao servidor do Ministério do Trabalho...")

ftp = FTP(
    FTP_HOST,
    timeout=60
)

ftp.login()

print("Conexão realizada com sucesso.")


# ============================================================
# 3. DIRETÓRIO DO ANO
# ============================================================

diretorio_ano = f"{FTP_BASE}/{ANO}"

try:
    ftp.cwd(diretorio_ano)

except error_perm as erro:
    ftp.quit()

    raise RuntimeError(
        f"Não foi possível acessar:\n{diretorio_ano}\n\n"
        f"Erro FTP: {erro}"
    )


print("\nDiretório remoto:")
print(ftp.pwd())


# ============================================================
# 4. FUNÇÃO PARA BAIXAR UM MÊS
# ============================================================

def baixar_mes(competencia: str):

    print("\n" + "=" * 60)
    print(f"Competência: {competencia}")
    print("=" * 60)

    pasta_local = (
        DESTINO_BASE
        / competencia
    )

    pasta_local.mkdir(
        parents=True,
        exist_ok=True
    )

    nome_arquivo = (
        f"CAGEDMOV{competencia}.7z"
    )

    arquivo_7z = (
        pasta_local
        / nome_arquivo
    )

    arquivo_txt = (
        pasta_local
        / f"CAGEDMOV{competencia}.txt"
    )

    # --------------------------------------------------------
    # Se o TXT já existe, não baixa novamente
    # --------------------------------------------------------

    if arquivo_txt.exists():

        print("TXT já existe.")
        print("Pulando download.")

        return

    # --------------------------------------------------------
    # Acessa pasta mensal no FTP
    # --------------------------------------------------------

    ftp.cwd(diretorio_ano)

    try:
        ftp.cwd(competencia)

    except error_perm as erro:

        raise RuntimeError(
            f"Pasta {competencia} não encontrada no FTP.\n"
            f"Erro: {erro}"
        )

    print("Diretório remoto:")
    print(ftp.pwd())

    # --------------------------------------------------------
    # Verifica arquivos disponíveis
    # --------------------------------------------------------

    arquivos_remotos = ftp.nlst()

    arquivo_remoto = None

    for item in arquivos_remotos:

        nome = Path(item).name

        if nome.upper() == nome_arquivo.upper():
            arquivo_remoto = item
            break

    if arquivo_remoto is None:

        raise FileNotFoundError(
            f"{nome_arquivo} não foi encontrado em "
            f"{ftp.pwd()}.\n\n"
            f"Arquivos disponíveis:\n"
            + "\n".join(arquivos_remotos)
        )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    if not arquivo_7z.exists():

        print("\nBaixando:")
        print(nome_arquivo)

        arquivo_temporario = (
            arquivo_7z.with_suffix(
                arquivo_7z.suffix + ".part"
            )
        )

        with open(
            arquivo_temporario,
            "wb"
        ) as arquivo_local:

            ftp.retrbinary(
                f"RETR {arquivo_remoto}",
                arquivo_local.write
            )

        arquivo_temporario.replace(
            arquivo_7z
        )

        print("Download concluído.")

    else:

        print(".7z já existe.")
        print("Pulando download.")

    # --------------------------------------------------------
    # Extração
    # --------------------------------------------------------

    print("\nExtraindo arquivo...")

    with py7zr.SevenZipFile(
        arquivo_7z,
        mode="r"
    ) as arquivo_compactado:

        arquivo_compactado.extractall(
            path=pasta_local
        )

    # --------------------------------------------------------
    # Validação
    # --------------------------------------------------------

    if arquivo_txt.exists():

        print("Extração concluída.")
        print("TXT encontrado:")

        print(arquivo_txt)

    else:

        arquivos_extraidos = [
            item.name
            for item in pasta_local.iterdir()
        ]

        raise FileNotFoundError(
            f"O arquivo esperado "
            f"{arquivo_txt.name} "
            f"não apareceu após a extração.\n\n"
            f"Arquivos encontrados:\n"
            + "\n".join(arquivos_extraidos)
        )


# ============================================================
# 5. COMPETÊNCIAS DO ANO
# ============================================================

competencias = [
    f"{ANO}{mes:02d}"
    for mes in range(1, 13)
]


# ============================================================
# 6. DOWNLOAD DOS 12 MESES
# ============================================================

try:

    for competencia in competencias:

        baixar_mes(
            competencia
        )

finally:

    try:
        ftp.quit()
    except Exception:
        ftp.close()


# ============================================================
# 7. VALIDAÇÃO FINAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO FINAL")
print("=" * 60)

arquivos_ok = 0

for competencia in competencias:

    arquivo = (
        DESTINO_BASE
        / competencia
        / f"CAGEDMOV{competencia}.txt"
    )

    existe = arquivo.exists()

    print(
        competencia,
        "OK" if existe else "FALTANDO"
    )

    if existe:
        arquivos_ok += 1


print("\nArquivos encontrados:")
print(f"{arquivos_ok}/12")


if arquivos_ok != 12:

    raise RuntimeError(
        "Nem todas as competências foram baixadas."
    )


print("\nDownload do Novo CAGED concluído.")