from ftplib import FTP, error_perm
from pathlib import Path

import py7zr


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANOS = [
    2020,
    2021,
    2022,
    2023,
]

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/NOVO CAGED"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DESTINO_BASE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
)

DESTINO_BASE.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. CONEXÃO FTP
# ============================================================

print("\nConectando ao servidor do Ministério do Trabalho...")

ftp = FTP(
    FTP_HOST,
    timeout=120
)

ftp.login()

print("Conexão realizada com sucesso.")


# ============================================================
# 3. FUNÇÃO PARA BAIXAR UMA COMPETÊNCIA
# ============================================================

def baixar_competencia(ano, mes):

    competencia = f"{ano}{mes:02d}"

    print("\n" + "=" * 60)
    print(f"Competência: {competencia}")
    print("=" * 60)

    pasta_local = (
        DESTINO_BASE
        / str(ano)
        / competencia
    )

    pasta_local.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_txt = (
        pasta_local
        / f"CAGEDMOV{competencia}.txt"
    )

    arquivo_7z = (
        pasta_local
        / f"CAGEDMOV{competencia}.7z"
    )

    # --------------------------------------------------------
    # Se o TXT já existe, não baixa novamente
    # --------------------------------------------------------

    if arquivo_txt.exists():

        print("TXT já existe.")
        print("Pulando competência.")

        return

    # --------------------------------------------------------
    # DIRETÓRIO REMOTO
    # --------------------------------------------------------

    diretorio_remoto = (
        f"{FTP_BASE}/{ano}/{competencia}"
    )

    try:

        ftp.cwd("/")

        ftp.cwd(
            diretorio_remoto
        )

    except error_perm as erro:

        raise RuntimeError(
            f"Não foi possível acessar "
            f"{diretorio_remoto}\n"
            f"Erro FTP: {erro}"
        )

    print("\nDiretório remoto:")
    print(
        ftp.pwd()
    )

    # --------------------------------------------------------
    # LISTAGEM DOS ARQUIVOS
    # --------------------------------------------------------

    arquivos_remotos = ftp.nlst()

    nome_esperado = (
        f"CAGEDMOV{competencia}.7z"
    )

    arquivo_remoto = None

    for item in arquivos_remotos:

        nome = Path(item).name

        if (
            nome.upper()
            == nome_esperado.upper()
        ):
            arquivo_remoto = item
            break

    if arquivo_remoto is None:

        raise FileNotFoundError(
            f"{nome_esperado} não encontrado.\n"
            f"Arquivos disponíveis:\n"
            + "\n".join(
                arquivos_remotos
            )
        )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    if not arquivo_7z.exists():

        print("\nBaixando:")
        print(
            nome_esperado
        )

        arquivo_temporario = (
            arquivo_7z.with_suffix(
                ".7z.part"
            )
        )

        with open(
            arquivo_temporario,
            "wb"
        ) as destino:

            ftp.retrbinary(
                f"RETR {arquivo_remoto}",
                destino.write
            )

        arquivo_temporario.replace(
            arquivo_7z
        )

        print("Download concluído.")

    else:

        print(
            ".7z já existe. "
            "Pulando download."
        )

    # --------------------------------------------------------
    # EXTRAÇÃO
    # --------------------------------------------------------

    print("Extraindo...")

    with py7zr.SevenZipFile(
        arquivo_7z,
        mode="r"
    ) as compactado:

        compactado.extractall(
            path=pasta_local
        )

    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    if not arquivo_txt.exists():

        raise FileNotFoundError(
            f"O TXT esperado não apareceu: "
            f"{arquivo_txt}"
        )

    print("TXT pronto:")
    print(
        arquivo_txt
    )


# ============================================================
# 4. DOWNLOAD DOS ANOS
# ============================================================

try:

    for ano in ANOS:

        print("\n" + "#" * 60)
        print(f"ANO {ano}")
        print("#" * 60)

        for mes in range(1, 13):

            baixar_competencia(
                ano,
                mes
            )

finally:

    try:
        ftp.quit()
    except Exception:
        ftp.close()


# ============================================================
# 5. VALIDAÇÃO FINAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DOS ARQUIVOS")
print("=" * 60)

total_esperado = (
    len(ANOS) * 12
)

total_encontrado = 0

for ano in ANOS:

    for mes in range(1, 13):

        competencia = (
            f"{ano}{mes:02d}"
        )

        arquivo = (
            DESTINO_BASE
            / str(ano)
            / competencia
            / f"CAGEDMOV{competencia}.txt"
        )

        if arquivo.exists():
            total_encontrado += 1
        else:
            print(
                "FALTANDO:",
                competencia
            )


print("\nArquivos esperados:")
print(
    total_esperado
)

print("\nArquivos encontrados:")
print(
    total_encontrado
)

if total_encontrado != total_esperado:

    raise RuntimeError(
        "Nem todos os arquivos foram baixados."
    )


print(
    "\nDownload multianual concluído com sucesso."
)