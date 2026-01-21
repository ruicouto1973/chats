#!/usr/bin/env python3
"""Programa simples de gestão de condomínios (Portugal).

Funcionalidades:
- Gestão de condomínios
- Gestão de frações
- Gestão de proprietários
- Registo de despesas e receitas
- Cálculo de saldo por condomínio
- Persistência em ficheiro JSON
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "dados_condominios.json"
DATE_FORMAT = "%d-%m-%Y"


@dataclass
class Fracao:
    identificador: str
    area_m2: float
    permilagem: int
    proprietario_id: Optional[str]


@dataclass
class Proprietario:
    id: str
    nome: str
    contacto: str


@dataclass
class Movimento:
    tipo: str  # "despesa" ou "receita"
    descricao: str
    valor: float
    data: str


@dataclass
class Condominio:
    id: str
    nome: str
    morada: str
    fracoes: List[Fracao]
    proprietarios: List[Proprietario]
    movimentos: List[Movimento]


class GestorCondominios:
    def __init__(self, ficheiro: str = DATA_FILE) -> None:
        self.ficheiro = ficheiro
        self.condominios: Dict[str, Condominio] = {}
        self._carregar()

    def _carregar(self) -> None:
        if not os.path.exists(self.ficheiro):
            return
        with open(self.ficheiro, "r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
        for condominio in dados.get("condominios", []):
            fracoes = [Fracao(**f) for f in condominio.get("fracoes", [])]
            proprietarios = [
                Proprietario(**p) for p in condominio.get("proprietarios", [])
            ]
            movimentos = [Movimento(**m) for m in condominio.get("movimentos", [])]
            self.condominios[condominio["id"]] = Condominio(
                id=condominio["id"],
                nome=condominio["nome"],
                morada=condominio["morada"],
                fracoes=fracoes,
                proprietarios=proprietarios,
                movimentos=movimentos,
            )

    def _guardar(self) -> None:
        dados = {
            "condominios": [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "morada": c.morada,
                    "fracoes": [asdict(f) for f in c.fracoes],
                    "proprietarios": [asdict(p) for p in c.proprietarios],
                    "movimentos": [asdict(m) for m in c.movimentos],
                }
                for c in self.condominios.values()
            ]
        }
        with open(self.ficheiro, "w", encoding="utf-8") as ficheiro:
            json.dump(dados, ficheiro, ensure_ascii=False, indent=2)

    def adicionar_condominio(self, condominio: Condominio) -> None:
        self.condominios[condominio.id] = condominio
        self._guardar()

    def listar_condominios(self) -> List[Condominio]:
        return list(self.condominios.values())

    def obter_condominio(self, condominio_id: str) -> Optional[Condominio]:
        return self.condominios.get(condominio_id)

    def guardar_condominio(self, condominio: Condominio) -> None:
        self.condominios[condominio.id] = condominio
        self._guardar()


class InterfaceCLI:
    def __init__(self, gestor: GestorCondominios) -> None:
        self.gestor = gestor

    def executar(self) -> None:
        while True:
            print("\n=== Gestão de Condomínios ===")
            print("1. Listar condomínios")
            print("2. Adicionar condomínio")
            print("3. Gerir condomínio")
            print("0. Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._listar_condominios()
            elif opcao == "2":
                self._adicionar_condominio()
            elif opcao == "3":
                self._gerir_condominio()
            elif opcao == "0":
                print("Até breve!")
                break
            else:
                print("Opção inválida.")

    def _listar_condominios(self) -> None:
        condominios = self.gestor.listar_condominios()
        if not condominios:
            print("Não existem condomínios registados.")
            return
        print("\nCondomínios registados:")
        for condominio in condominios:
            print(f"- [{condominio.id}] {condominio.nome} | {condominio.morada}")

    def _adicionar_condominio(self) -> None:
        condominio_id = input("ID do condomínio: ").strip()
        if self.gestor.obter_condominio(condominio_id):
            print("Já existe um condomínio com esse ID.")
            return
        nome = input("Nome: ").strip()
        morada = input("Morada: ").strip()
        condominio = Condominio(
            id=condominio_id,
            nome=nome,
            morada=morada,
            fracoes=[],
            proprietarios=[],
            movimentos=[],
        )
        self.gestor.adicionar_condominio(condominio)
        print("Condomínio adicionado com sucesso.")

    def _gerir_condominio(self) -> None:
        condominio_id = input("ID do condomínio a gerir: ").strip()
        condominio = self.gestor.obter_condominio(condominio_id)
        if not condominio:
            print("Condomínio não encontrado.")
            return
        while True:
            print(f"\n--- {condominio.nome} ---")
            print("1. Listar frações")
            print("2. Adicionar fração")
            print("3. Listar proprietários")
            print("4. Adicionar proprietário")
            print("5. Registar movimento")
            print("6. Ver saldo")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._listar_fracoes(condominio)
            elif opcao == "2":
                self._adicionar_fracao(condominio)
            elif opcao == "3":
                self._listar_proprietarios(condominio)
            elif opcao == "4":
                self._adicionar_proprietario(condominio)
            elif opcao == "5":
                self._registar_movimento(condominio)
            elif opcao == "6":
                self._mostrar_saldo(condominio)
            elif opcao == "0":
                self.gestor.guardar_condominio(condominio)
                break
            else:
                print("Opção inválida.")

    def _listar_fracoes(self, condominio: Condominio) -> None:
        if not condominio.fracoes:
            print("Não existem frações registadas.")
            return
        print("\nFrações:")
        for fracao in condominio.fracoes:
            proprietario = self._obter_nome_proprietario(condominio, fracao.proprietario_id)
            print(
                f"- {fracao.identificador} | {fracao.area_m2:.2f} m² | "
                f"Permilagem: {fracao.permilagem} | Proprietário: {proprietario}"
            )

    def _adicionar_fracao(self, condominio: Condominio) -> None:
        identificador = input("Identificador da fração (ex: A-1): ").strip()
        if any(f.identificador == identificador for f in condominio.fracoes):
            print("Já existe uma fração com esse identificador.")
            return
        area_m2 = self._ler_float("Área (m²): ")
        permilagem = self._ler_int("Permilagem: ")
        proprietario_id = input(
            "ID do proprietário (ou deixe em branco): "
        ).strip() or None
        if proprietario_id and not self._proprietario_existe(condominio, proprietario_id):
            print("Proprietário não encontrado. Será registado sem proprietário.")
            proprietario_id = None
        condominio.fracoes.append(
            Fracao(
                identificador=identificador,
                area_m2=area_m2,
                permilagem=permilagem,
                proprietario_id=proprietario_id,
            )
        )
        self.gestor.guardar_condominio(condominio)
        print("Fração adicionada com sucesso.")

    def _listar_proprietarios(self, condominio: Condominio) -> None:
        if not condominio.proprietarios:
            print("Não existem proprietários registados.")
            return
        print("\nProprietários:")
        for proprietario in condominio.proprietarios:
            print(
                f"- [{proprietario.id}] {proprietario.nome} | {proprietario.contacto}"
            )

    def _adicionar_proprietario(self, condominio: Condominio) -> None:
        proprietario_id = input("ID do proprietário: ").strip()
        if self._proprietario_existe(condominio, proprietario_id):
            print("Já existe um proprietário com esse ID.")
            return
        nome = input("Nome: ").strip()
        contacto = input("Contacto (telemóvel/email): ").strip()
        condominio.proprietarios.append(
            Proprietario(id=proprietario_id, nome=nome, contacto=contacto)
        )
        self.gestor.guardar_condominio(condominio)
        print("Proprietário adicionado com sucesso.")

    def _registar_movimento(self, condominio: Condominio) -> None:
        tipo = input("Tipo (despesa/receita): ").strip().lower()
        if tipo not in {"despesa", "receita"}:
            print("Tipo inválido.")
            return
        descricao = input("Descrição: ").strip()
        valor = self._ler_float("Valor (€): ")
        data = input(f"Data ({DATE_FORMAT}): ").strip() or datetime.now().strftime(
            DATE_FORMAT
        )
        if not self._validar_data(data):
            print("Data inválida.")
            return
        condominio.movimentos.append(
            Movimento(tipo=tipo, descricao=descricao, valor=valor, data=data)
        )
        self.gestor.guardar_condominio(condominio)
        print("Movimento registado com sucesso.")

    def _mostrar_saldo(self, condominio: Condominio) -> None:
        total_receitas = sum(
            movimento.valor
            for movimento in condominio.movimentos
            if movimento.tipo == "receita"
        )
        total_despesas = sum(
            movimento.valor
            for movimento in condominio.movimentos
            if movimento.tipo == "despesa"
        )
        saldo = total_receitas - total_despesas
        print("\nResumo financeiro:")
        print(f"Total de receitas: {total_receitas:.2f} €")
        print(f"Total de despesas: {total_despesas:.2f} €")
        print(f"Saldo atual: {saldo:.2f} €")

    def _ler_float(self, prompt: str) -> float:
        while True:
            valor = input(prompt).replace(",", ".").strip()
            try:
                return float(valor)
            except ValueError:
                print("Valor inválido. Tente novamente.")

    def _ler_int(self, prompt: str) -> int:
        while True:
            valor = input(prompt).strip()
            try:
                return int(valor)
            except ValueError:
                print("Valor inválido. Tente novamente.")

    def _proprietario_existe(self, condominio: Condominio, proprietario_id: str) -> bool:
        return any(p.id == proprietario_id for p in condominio.proprietarios)

    def _obter_nome_proprietario(
        self, condominio: Condominio, proprietario_id: Optional[str]
    ) -> str:
        if not proprietario_id:
            return "(sem proprietário)"
        for proprietario in condominio.proprietarios:
            if proprietario.id == proprietario_id:
                return proprietario.nome
        return "(não encontrado)"

    def _validar_data(self, data: str) -> bool:
        try:
            datetime.strptime(data, DATE_FORMAT)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    gestor = GestorCondominios()
    InterfaceCLI(gestor).executar()
