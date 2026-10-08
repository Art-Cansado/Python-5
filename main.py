
import csv
import re
from datetime import datetime


# Exceção personalizada para erros nas regras de validação
class FormatoInvalidoError(Exception):
    pass


# Expressões regulares para validar os campos
PADRAO_EMAIL = r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$"
PADRAO_CPF = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
PADRAO_TELEFONE = r"^\(\d{2}\) \d{4,5}-\d{4}$"
PADRAO_DATA = r"^\d{2}/\d{2}/\d{4}$"


def validar_registro(registro):
    # Lê os campos do registro e remove espaços desnecessários
    nome = str(registro["nome"] or "").strip()
    email = str(registro["email"] or "").strip()
    cpf = str(registro["cpf"] or "").strip()
    telefone = str(registro["telefone"] or "").strip()
    data = str(registro["data"] or "").strip()

    erros = []

    # Valida o nome
    if not nome:
        erros.append("Nome não informado")

    # Valida o e-mail
    if not re.match(PADRAO_EMAIL, email):
        erros.append("E-mail inválido")

    # Valida o formato do CPF
    if not re.match(PADRAO_CPF, cpf):
        erros.append("CPF fora do formato 000.000.000-00")

    # Valida o telefone
    if not re.match(PADRAO_TELEFONE, telefone):
        erros.append("Telefone fora do formato (00) 00000-0000")

    # Valida o formato e a existência da data
    if not re.match(PADRAO_DATA, data):
        erros.append("Data fora do formato DD/MM/AAAA")
    else:
        # Verifica se a data existe no calendário
        datetime.strptime(data, "%d/%m/%Y")

    # Se houver erros, lança a exceção personalizada
    if erros:
        raise FormatoInvalidoError("; ".join(erros))

    return {
        "nome": nome,
        "email": email,
        "cpf": cpf,
        "telefone": telefone,
        "data": data
    }


def gerar_relatorio(validos, invalidos):
    total = len(validos) + len(invalidos)

    print("\n" + "=" * 50)
    print("       RELATÓRIO DE VALIDAÇÃO DE DADOS")
    print("=" * 50)

    print(f"Total de registros: {total}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")

    if total > 0:
        percentual = (len(validos) / total) * 100
        print(f"Percentual aprovado: {percentual:.2f}%")
    else:
        print("Percentual aprovado: 0.00%")

    print("\n--- REGISTROS VÁLIDOS ---")

    if validos:
        for registro in validos:
            print(
                f"Nome: {registro['nome']} | "
                f"E-mail: {registro['email']} | "
                f"CPF: {registro['cpf']} | "
                f"Telefone: {registro['telefone']} | "
                f"Data: {registro['data']}"
            )
    else:
        print("Nenhum registro válido.")

    print("\n--- REGISTROS INVÁLIDOS ---")

    if invalidos:
        for registro in invalidos:
            print(
                f"Linha {registro['linha']} | "
                f"Nome: {registro['nome']} | "
                f"Motivo: {registro['motivo']}"
            )
    else:
        print("Nenhum registro inválido.")

    print("=" * 50)


def main():
    registros_validos = []
    registros_invalidos = []

    # Define as colunas obrigatórias do arquivo CSV
    colunas_obrigatorias = {
        "nome",
        "email",
        "cpf",
        "telefone",
        "data"
    }

    try:
        # Abre o arquivo com segurança e codificação UTF-8
        with open(
            "dados.csv",
            mode="r",
            newline="",
            encoding="utf-8"
        ) as arquivo:

            leitor = csv.DictReader(arquivo)

            # Verifica se o arquivo possui cabeçalho
            if leitor.fieldnames is None:
                raise ValueError("O arquivo CSV está vazio ou sem cabeçalho.")

            # Verifica se todas as colunas obrigatórias existem
            colunas_encontradas = set(leitor.fieldnames)
            colunas_faltantes = (
                colunas_obrigatorias - colunas_encontradas
            )

            if colunas_faltantes:
                raise KeyError(
                    "Colunas ausentes: "
                    + ", ".join(sorted(colunas_faltantes))
                )

            # Percorre os registros; a primeira linha é o cabeçalho
            for numero_linha, registro in enumerate(leitor, start=2):
                nome = registro.get("nome") or ""

                try:
                    registro_validado = validar_registro(registro)

                except FormatoInvalidoError as erro:
                    # Trata erros encontrados pelas validações
                    registros_invalidos.append({
                        "linha": numero_linha,
                        "nome": nome or "Não informado",
                        "motivo": str(erro)
                    })

                except ValueError:
                    # Trata datas impossíveis, como 32/15/2001
                    registros_invalidos.append({
                        "linha": numero_linha,
                        "nome": nome or "Não informado",
                        "motivo": "Data inexistente no calendário"
                    })

                except KeyError as erro:
                    # Trata campos ausentes no registro
                    registros_invalidos.append({
                        "linha": numero_linha,
                        "nome": nome or "Não informado",
                        "motivo": f"Campo ausente: {erro}"
                    })

                else:
                    # Executa somente se o registro for válido
                    registros_validos.append(registro_validado)

    except FileNotFoundError:
        print("Erro: o arquivo 'dados.csv' não foi encontrado.")
        print("Verifique se ele está na mesma pasta do main.py.")

    except KeyError as erro:
        print(f"Erro na estrutura do CSV: {erro}")

    except ValueError as erro:
        print(f"Erro ao ler os dados: {erro}")

    else:
        # Executa quando o arquivo é processado sem erro estrutural
        gerar_relatorio(registros_validos, registros_invalidos)

    finally:
        # Executa independentemente de ocorrer um erro ou não
        print("\nProcessamento encerrado.")


# Inicia o programa
if __name__ == "__main__":
    main()
