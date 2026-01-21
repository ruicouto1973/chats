# Criar programa de gestão de condomínios

Este projeto fornece um utilitário em linha de comando para cadastrar condomínios, unidades e moradores.

## Requisitos

- Python 3.10+

## Como usar

Execute o arquivo `main.py` com o comando desejado:

```bash
python main.py criar-condominio "Residencial Aurora" "Rua das Flores, 123"
python main.py criar-unidade "Residencial Aurora" "Bloco A - 101" "Maria Souza"
python main.py criar-morador "Residencial Aurora" "Bloco A - 101" "João Lima" "123.456.789-00"
python main.py listar
```

Por padrão, os dados são salvos em `data/condominios.json`. Você pode alterar o caminho com `--arquivo`.
