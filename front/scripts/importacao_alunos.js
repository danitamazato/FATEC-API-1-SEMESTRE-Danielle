// Função para listar turmas no elemento select
async function listarTurmas() {
  try {
    const response = await fetch(
      "http://127.0.0.1:8080/api/v1/turmas/nao_iniciadas"
    );
    const turmaData = await response.json();

    const opcoesTurma = document.getElementById("selecionaTurma");

    for (const turmaId in turmaData) {
      if (turmaData.hasOwnProperty(turmaId)) {
        const turma = turmaData[turmaId];
        const option = document.createElement("option");
        option.value = turmaId;
        option.dataset.Nome = turma.nome;
        option.textContent = turma.nome;

        opcoesTurma.appendChild(option);
      }
    }
  } catch (error) {
    console.error("Erro ao buscar dados da API -> ", error);
  }
}

function validaEntrada() {
  const arquivo = document.getElementById("arquivo");
  const arquivoImportado = arquivo.files[0];
  const turmaSelecionada = document.getElementById("selecionaTurma");
  const nomeTurmaSelecionada =
    turmaSelecionada.options[turmaSelecionada.selectedIndex].dataset.Nome;
  const idTurmaSelecionada = turmaSelecionada.value;

  if (idTurmaSelecionada && arquivoImportado) {
    const nomeArquivo = arquivo.files[0].name;
    if (nomeArquivo.toLowerCase().endsWith(".csv")) {
      criaRequisicao(
        arquivoImportado,
        idTurmaSelecionada,
        nomeTurmaSelecionada
      );
    } else {
      const mensagem = "Selecione um arquivo no formato CSV.";
      exibirAlertaNoModal(mensagem);
    }
  } else {
    const mensagem = "Selecione uma turma e um arquivo.";
    exibirAlertaNoModal(mensagem);
  }
}

function exibirAlertaNoModal(mensagem) {
  const modal = document.getElementById("custom-modal");
  const modalMessage = document.getElementById("modal-message");
  const confirmButton = document.getElementById("confirmButton");
  const cancelButton = document.getElementById("cancelButton");

  modalMessage.innerHTML = `<strong>Alerta: ${mensagem}</strong>`;
  modal.style.display = "flex";
  confirmButton.innerText = "OK";
  confirmButton.addEventListener("click", function () {
    modal.style.display = "none";
  });
  cancelButton.style.display = "none";
}

async function criaRequisicao(
  arquivoImportado,
  idTurmaSelecionada,
  nomeTurmaSelecionada
) {
  const arquivoImportadoJson = await converteCsvToJson(arquivoImportado);
  const respostaValidacao = await validarjson(arquivoImportadoJson);

  if (respostaValidacao.sucesso) {
    const corpoRequisicao = {
      turma_id: idTurmaSelecionada,
      nome_Turma: nomeTurmaSelecionada,
      alunos_importados: arquivoImportadoJson,
    };
    const decisao_usuario = await criar_modal_confirmar(
      nomeTurmaSelecionada,
      arquivoImportadoJson
    );
    if (decisao_usuario) {
      resposta = await importaAluno(corpoRequisicao);
      window.location.href = "informacoes_turma.html?id=" + idTurmaSelecionada;
    }
  } else {
    const erros = respostaValidacao.erros;
    exibirErrosNoModal(erros);
  }
}

function criar_modal_confirmar(nome_Turma, arquivoImportadoJson) {
  return new Promise((resolve) => {
    arquivoImportadoJson = JSON.parse(arquivoImportadoJson);

    let mensagem = `Atenção! Os alunos serão adicionados à turma ${nome_Turma}:\n\n`;

    for (const aluno of arquivoImportadoJson) {
      const alunoNome = aluno["Nome Completo do Aluno"];
      const alunoGenero = aluno["Gênero"];
      const alunoNascimento = aluno["Data de Nascimento"];

      mensagem += `Nome do aluno: ${alunoNome}, `;
      mensagem += `Gênero: ${alunoGenero}, `;
      mensagem += `Data de Nascimento: ${alunoNascimento}\n\n`;
    }

    mensagem += "\nDeseja prosseguir com a importação?";

    document.getElementById("modal-message").innerText = mensagem;

    document.getElementById("custom-modal").style.display = "flex";

    document
      .getElementById("confirmButton")
      .addEventListener("click", function () {
        document.getElementById("custom-modal").style.display = "none";
        resolve(true);
      });
    document
      .getElementById("cancelButton")
      .addEventListener("click", function () {
        document.getElementById("custom-modal").style.display = "none";
        resolve(false);
      });
  });
}

function exibirErrosNoModal(erros) {
  const modal = document.getElementById("custom-modal");
  const modalMessage = document.getElementById("modal-message");
  const confirmButton = document.getElementById("confirmButton");
  const cancelButton = document.getElementById("cancelButton");

  // erros
  modalMessage.innerHTML =
    "<strong>Erros encontrados:</strong><br><br>" +
    erros.join("<br>") +
    "<br><br>Por favor corrigir arquivo para importação<br>";

  // Exibe o modal
  modal.style.display = "flex";

  // Adiciona ouvintes de evento ao botão OK
  confirmButton.innerText = "OK";
  confirmButton.addEventListener("click", function () {
    modal.style.display = "none";
  });
  cancelButton.style.display = "none";
}

async function converteCsvToJson(arquivoImportado) {
  try {
    const arquivoImportadoTexto = await csvToText(arquivoImportado);
    const arquivoImportadoJson = textToJson(arquivoImportadoTexto);
    return arquivoImportadoJson;
  } catch (error) {
    console.error("Erro ao processar o arquivo -> ", error);
  }
}

function csvToText(arquivoImportado) {
  return new Promise((resolve, reject) => {
    const leitor = new FileReader();
    leitor.onload = (evt) => {
      const arquivoImportadoTexto = evt.target.result;
      resolve(arquivoImportadoTexto);
    };
    leitor.onerror = (error) => {
      reject(error);
    };

    leitor.readAsText(arquivoImportado);
  });
}

function textToJson(arquivoImportadoTexto) {
  var linhas = arquivoImportadoTexto.split("\n");

  var resultado = [];
  var headers = linhas[0].split(";");

  for (var i = 1; i < linhas.length; i++) {
    var linhaAtual = linhas[i].split(";");

    linhaAtual = linhaAtual.map((element) => element.replace(/\r$/, ""));

    // Ignora linhas completamente vazias
    if (linhaAtual.some((element) => element.trim() !== "")) {
      if (linhaAtual.length === headers.length) {
        var obj = {};
        for (var j = 0; j < headers.length; j++) {
          obj[headers[j]] = linhaAtual[j];
        }
        resultado.push(obj);
      }
    }
  }
  return JSON.stringify(resultado).replace(/\\r/g, "").replace(/\\n/g, "");
}

async function validarjson(arquivoImportadoJson) {
  try {
    const response = await fetch(
      "http://127.0.0.1:8080/api/v1/importacao/validar",
      { method: "POST", body: JSON.stringify(arquivoImportadoJson) }
    );
    const reposta = await response.json();
    console.log(reposta);
    return reposta;
  } catch (error) {
    console.error("Erro ao buscar dados da API -> ", error);
    return null;
  }
}

async function importaAluno(corpoRequisicao) {
  try {
    const response = await fetch(
      "http://127.0.0.1:8080/api/v1/importacao/importaAluno",
      { method: "POST", body: JSON.stringify(corpoRequisicao) }
    );
  } catch (error) {
    console.error("Erro ao buscar dados da API -> ", error);
    return null;
  }
}
