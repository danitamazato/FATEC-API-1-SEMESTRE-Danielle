import json

from regra_de_negocio.gerenciador_ciclos import (
    obter_ciclo,
    obter_datas_ciclos,
)
from regra_de_negocio.gerenciador_turmas import obter_turma
from regra_de_negocio.service import gerenciador_turmas_alunos

from datetime import datetime, timedelta


def calcular_fee_turma_aluno(id_turma, id_aluno):
    id_turma_str = str(id_turma)
    id_aluno_str = str(id_aluno)
    notas_por_turma_aluno = listar_notas_por_turma_aluno(id_turma_str, id_aluno_str)
    soma_das_notas = 0.0
    soma_dos_pesos = 0.0
    for id_nota in notas_por_turma_aluno:
        ciclo = obter_ciclo(notas_por_turma_aluno[id_nota]["id_ciclo"])
        peso_nota = ciclo["peso_nota"]
        valor = notas_por_turma_aluno[id_nota]["valor"]
        soma_das_notas += peso_nota * valor
        soma_dos_pesos += peso_nota
    if len(notas_por_turma_aluno) > 0:
        media_fee = soma_das_notas / float(soma_dos_pesos)
        valor_fee = round(media_fee, 2)
        gerenciador_turmas_alunos.adicionar_fee_na_turma_aluno(
            id_aluno, id_turma, valor_fee
        )


def atualiza_todos_fee_da_turma(id_turma):
    alunos = gerenciador_turmas_alunos.listar_turmas_alunos()
    for id_aluno in alunos.keys():
        if alunos[id_aluno]["id_turma"] == id_turma:
            calcular_fee_turma_aluno(id_turma, id_aluno)


def listar_notas():
    with open("dados/notas.json", "r", encoding="utf-8") as f:
        notas = json.load(f)
        return notas


def filtrar_notas_por_id_turma_svc(notas, id_turma):
    if not id_turma:
        return {}
    id_turma_str = str(id_turma)
    notas_encontradas = {}
    for id_nota in notas.keys():
        if id_turma_str == notas[id_nota]["id_turma"]:
            notas_encontradas[id_nota] = notas[id_nota]
    return notas_encontradas


def listar_notas_por_id_aluno(notas, id_aluno):
    if not id_aluno:
        return {}
    id_aluno_str = str(id_aluno)
    notas_encontradas = {}
    for id_nota in notas.keys():
        if id_aluno_str == notas[id_nota]["id_aluno"]:
            notas_encontradas[id_nota] = notas[id_nota]

    return notas_encontradas


def listar_notas_por_id_ciclo(notas, id_ciclo):
    if not id_ciclo:
        return {}
    id_ciclo_str = str(id_ciclo)
    notas_encontradas = {}
    for id_nota in notas.keys():
        if id_ciclo_str == notas[id_nota]["id_ciclo"]:
            notas_encontradas[id_nota] = notas[id_nota]
    return notas_encontradas


def listar_notas_por_turma_aluno(id_turma, id_aluno):
    if not id_turma or not id_aluno:
        return {}
    notas = listar_notas()
    notas_por_turma = filtrar_notas_por_id_turma_svc(notas, id_turma)
    notas_por_turma_aluno = listar_notas_por_id_aluno(notas_por_turma, id_aluno)
    return notas_por_turma_aluno


def adicionar_nota(nova_nota):
    notas = listar_notas()
    novo_id_nota = _obter_novo_id_nota()
    notas[novo_id_nota] = nova_nota
    _salvar_notas(notas)
    calcular_fee_turma_aluno(
        notas[novo_id_nota]["id_turma"], notas[novo_id_nota]["id_aluno"]
    )


def editar_nota(notas_atualizada):
    if not notas_atualizada:
        return False
    notas = listar_notas()
    for id_nota in notas_atualizada:
        id_nota_atualizada_str = str(id_nota)
        if id_nota_atualizada_str in notas.keys():
            notas[id_nota_atualizada_str]["valor"] = float(
                notas_atualizada[id_nota_atualizada_str]["valor"]
            )
            calcular_fee_turma_aluno(
                notas[id_nota_atualizada_str]["id_turma"],
                notas[id_nota_atualizada_str]["id_aluno"],
            )
        else:
            return False
    return _salvar_notas(notas)


def remover_nota(id_nota, delecao_cascata=False):
    id_nota_str = str(id_nota)
    notas = listar_notas()
    id_turma = notas[id_nota_str]["id_turma"]
    id_aluno = notas[id_nota_str]["id_aluno"]
    if id_nota_str in notas.keys():
        notas.pop(id_nota_str)
        _salvar_notas(notas)
        if delecao_cascata:
            return
        calcular_fee_turma_aluno(id_turma, id_aluno)
    else:
        return False


# Essa função verifica se já existe nota dentro de um ciclo
def verificar_existencia_nota_por_ciclo(nota):
    notas = listar_notas_por_turma_aluno(nota["id_turma"], nota["id_aluno"])
    notas_por_ciclo = listar_notas_por_id_ciclo(notas, nota["id_ciclo"])
    return len(notas_por_ciclo) != 0


def _obter_novo_id_nota():
    ids_numericos = []
    ids_numericos.append(0)
    notas = listar_notas()
    for id_str in notas.keys():
        id_int = int(id_str)
        ids_numericos.append(id_int)
    ids_numericos.sort()
    id_max_int = ids_numericos.pop()
    novo_id = str(id_max_int + 1)
    return novo_id


def _salvar_notas(notas):
    dados = json.dumps(notas, indent=4)
    with open("dados/notas.json", "w", encoding="utf-8") as f:
        f.write(dados)
        return True


def verificar_edicao_habilitada(notas, id_nota):
    """
    {'1': -> id_ciclo
       {'data_de_inicio_ciclo': '02/11/2023',
       'data_de_fim_ciclo': '12/11/2023'}
    """
    id_nota_str = str(id_nota)
    nota = notas[id_nota_str]
    ciclo = obter_ciclo(nota["id_ciclo"])
    ciclo_nota = nota["id_ciclo"]
    turma = obter_turma(nota["id_turma"])
    data_ciclos = obter_datas_ciclos(turma, nota["id_turma"])
    formato_data = "%d/%m/%Y"
    prazo_insercao_nota = int(ciclo["prazo_insercao_nota"])
    if ciclo_nota in data_ciclos.keys():
        data_atual = datetime.now()
        data_fim_ciclo = data_ciclos[ciclo_nota]["data_de_fim_ciclo"]
        data_inicial_insercao_nota = datetime.strptime(
            data_fim_ciclo, formato_data
        ) + timedelta(
            days=1
        )  # O dia apos o fim do ciclo
        data_final_insercao_nota = data_inicial_insercao_nota + timedelta(
            days=prazo_insercao_nota
        )
        if data_inicial_insercao_nota <= data_atual <= data_final_insercao_nota:
            return True
        else:
            return False
    else:
        return False


def excluir_notas_relacionadas_turma(id_turma):
    print("\n> Excluindo notas relacionados a turma...\n")
    todos_notas = listar_notas()
    for id in todos_notas.keys():
        if todos_notas[id]["id_turma"] == id_turma:
            remover_nota(id, delecao_cascata=True)


def adicionar_notas_aluno_turma(ciclos, alunos, id_nova_turma_str):
    for id_aluno in alunos:
        for id_ciclo in ciclos:
            nova_nota = {}
            nova_nota["id_turma"] = id_nova_turma_str
            nova_nota["id_aluno"] = str(id_aluno)
            nova_nota["id_ciclo"] = str(id_ciclo)
            nova_nota["valor"] = 0.0
            nova_nota["fee"] = False
            adicionar_nota(nova_nota)
            calcular_fee_turma_aluno(id_nova_turma_str, id_aluno)
