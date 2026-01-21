from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Morador:
    nome: str
    documento: str


@dataclass
class Unidade:
    identificador: str
    proprietario: str
    moradores: list[Morador] = field(default_factory=list)


@dataclass
class Condominio:
    nome: str
    endereco: str
    unidades: list[Unidade] = field(default_factory=list)


class CondominioStorage:
    def __init__(self, arquivo: Path) -> None:
        self.arquivo = arquivo

    def carregar(self) -> list[Condominio]:
        if not self.arquivo.exists():
            return []
        data = json.loads(self.arquivo.read_text(encoding="utf-8"))
        return [self._condominio_from_dict(item) for item in data]

    def salvar(self, condominios: list[Condominio]) -> None:
        data = [self._condominio_to_dict(item) for item in condominios]
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.arquivo.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _condominio_from_dict(self, data: dict[str, Any]) -> Condominio:
        unidades = [self._unidade_from_dict(item) for item in data.get("unidades", [])]
        return Condominio(
            nome=data["nome"],
            endereco=data["endereco"],
            unidades=unidades,
        )

    def _unidade_from_dict(self, data: dict[str, Any]) -> Unidade:
        moradores = [self._morador_from_dict(item) for item in data.get("moradores", [])]
        return Unidade(
            identificador=data["identificador"],
            proprietario=data["proprietario"],
            moradores=moradores,
        )

    def _morador_from_dict(self, data: dict[str, Any]) -> Morador:
        return Morador(nome=data["nome"], documento=data["documento"])

    def _condominio_to_dict(self, condominio: Condominio) -> dict[str, Any]:
        return {
            "nome": condominio.nome,
            "endereco": condominio.endereco,
            "unidades": [self._unidade_to_dict(unidade) for unidade in condominio.unidades],
        }

    def _unidade_to_dict(self, unidade: Unidade) -> dict[str, Any]:
        return {
            "identificador": unidade.identificador,
            "proprietario": unidade.proprietario,
            "moradores": [self._morador_to_dict(m) for m in unidade.moradores],
        }

    def _morador_to_dict(self, morador: Morador) -> dict[str, Any]:
        return {"nome": morador.nome, "documento": morador.documento}


class CondominioService:
    def __init__(self, storage: CondominioStorage) -> None:
        self.storage = storage

    def adicionar_condominio(self, nome: str, endereco: str) -> Condominio:
        condominios = self.storage.carregar()
        if any(c.nome.lower() == nome.lower() for c in condominios):
            raise ValueError("Condomínio já cadastrado.")
        novo = Condominio(nome=nome, endereco=endereco)
        condominios.append(novo)
        self.storage.salvar(condominios)
        return novo

    def adicionar_unidade(self, condominio_nome: str, identificador: str, proprietario: str) -> Unidade:
        condominios = self.storage.carregar()
        condominio = self._buscar_condominio(condominios, condominio_nome)
        if any(u.identificador == identificador for u in condominio.unidades):
            raise ValueError("Unidade já cadastrada.")
        unidade = Unidade(identificador=identificador, proprietario=proprietario)
        condominio.unidades.append(unidade)
        self.storage.salvar(condominios)
        return unidade

    def adicionar_morador(
        self, condominio_nome: str, unidade_id: str, nome: str, documento: str
    ) -> Morador:
        condominios = self.storage.carregar()
        condominio = self._buscar_condominio(condominios, condominio_nome)
        unidade = self._buscar_unidade(condominio, unidade_id)
        if any(m.documento == documento for m in unidade.moradores):
            raise ValueError("Documento já cadastrado para esta unidade.")
        morador = Morador(nome=nome, documento=documento)
        unidade.moradores.append(morador)
        self.storage.salvar(condominios)
        return morador

    def listar_condominios(self) -> list[Condominio]:
        return self.storage.carregar()

    def _buscar_condominio(self, condominios: list[Condominio], nome: str) -> Condominio:
        for condominio in condominios:
            if condominio.nome.lower() == nome.lower():
                return condominio
        raise ValueError("Condomínio não encontrado.")

    def _buscar_unidade(self, condominio: Condominio, unidade_id: str) -> Unidade:
        for unidade in condominio.unidades:
            if unidade.identificador == unidade_id:
                return unidade
        raise ValueError("Unidade não encontrada.")
