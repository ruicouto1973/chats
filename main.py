from __future__ import annotations

import argparse
from pathlib import Path

from src.condominio import CondominioService, CondominioStorage


def configurar_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Programa de gestão de condomínios",
    )
    parser.add_argument(
        "--arquivo",
        default="data/condominios.json",
        help="Caminho para o arquivo de dados JSON.",
    )

    subparsers = parser.add_subparsers(dest="comando", required=True)

    cmd_condominio = subparsers.add_parser("criar-condominio", help="Cadastrar um condomínio.")
    cmd_condominio.add_argument("nome", help="Nome do condomínio.")
    cmd_condominio.add_argument("endereco", help="Endereço do condomínio.")

    cmd_unidade = subparsers.add_parser("criar-unidade", help="Cadastrar uma unidade.")
    cmd_unidade.add_argument("condominio", help="Nome do condomínio.")
    cmd_unidade.add_argument("identificador", help="Identificador da unidade.")
    cmd_unidade.add_argument("proprietario", help="Nome do proprietário.")

    cmd_morador = subparsers.add_parser("criar-morador", help="Cadastrar um morador.")
    cmd_morador.add_argument("condominio", help="Nome do condomínio.")
    cmd_morador.add_argument("unidade", help="Identificador da unidade.")
    cmd_morador.add_argument("nome", help="Nome do morador.")
    cmd_morador.add_argument("documento", help="Documento do morador.")

    subparsers.add_parser("listar", help="Listar condomínios cadastrados.")

    return parser


def imprimir_listagem(service: CondominioService) -> None:
    condominios = service.listar_condominios()
    if not condominios:
        print("Nenhum condomínio cadastrado.")
        return

    for condominio in condominios:
        print(f"Condomínio: {condominio.nome}")
        print(f"  Endereço: {condominio.endereco}")
        if not condominio.unidades:
            print("  Unidades: nenhuma cadastrada")
            continue
        print("  Unidades:")
        for unidade in condominio.unidades:
            print(f"    - {unidade.identificador} | Proprietário: {unidade.proprietario}")
            if not unidade.moradores:
                print("      Moradores: nenhum cadastrado")
                continue
            print("      Moradores:")
            for morador in unidade.moradores:
                print(f"        * {morador.nome} (Doc: {morador.documento})")


def main() -> None:
    parser = configurar_cli()
    args = parser.parse_args()

    arquivo = Path(args.arquivo)
    service = CondominioService(CondominioStorage(arquivo))

    if args.comando == "criar-condominio":
        condominio = service.adicionar_condominio(args.nome, args.endereco)
        print(f"Condomínio '{condominio.nome}' cadastrado com sucesso.")
        return

    if args.comando == "criar-unidade":
        unidade = service.adicionar_unidade(args.condominio, args.identificador, args.proprietario)
        print(f"Unidade '{unidade.identificador}' cadastrada com sucesso.")
        return

    if args.comando == "criar-morador":
        morador = service.adicionar_morador(
            args.condominio, args.unidade, args.nome, args.documento
        )
        print(f"Morador '{morador.nome}' cadastrado com sucesso.")
        return

    if args.comando == "listar":
        imprimir_listagem(service)
        return

    parser.error("Comando inválido.")


if __name__ == "__main__":
    main()
