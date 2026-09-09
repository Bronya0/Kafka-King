<p align="center">
  <img src="../../app/build/appicon.png" width="200" alt="Image">
</p>
<h1 align="center">Kafka King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">Um cliente GUI de Kafka moderno e prático</h3>

</div>
<h4 align="center">
<a href="../../readme.md">English</a> | <a href="../../README-CN.md">简体中文</a> | <a href="readme-ja.md">日本語</a> | <a href="readme-ru.md">рускі</a> | <a href="readme-ko.md">한국인</a> | <a href="readme-es.md">Español</a> | <a href="readme-fr.md">Français</a> | <a href="readme-de.md">Deutsch</a> | <a href="readme-pt.md">Português</a> | <a href="readme-it.md">Italiano</a> | <a href="readme-vi.md">Tiếng Việt</a> | <a href="readme-id.md">Bahasa Indonesia</a>  
</h4>

Torne o Kafka mais fácil de usar, make kafka great again!

Este projeto é um cliente GUI de Kafka compatível com vários sistemas desktop (exceto Win7), suportando Kafka 0.8.0 a 3.8+, construído com Wails e franz-go. Dê uma estrela para apoiar o autor! ❤❤

> Confira também o cliente Elasticsearch `ES-King`, igualmente prático: https://github.com/Bronya0/ES-King

**Doc（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Funcionalidades do Kafka-King
- [x] Visualizar lista de nós do cluster, suporte a configuração dinâmica de brokers e topics.
- [x] Suporte a cliente consumidor, consumir mensagens de topics com grupo, tamanho e timeout, exibindo detalhes em tabela.
- [x] Suporte a PLAIN, SSL, SASL, Kerberos, sasl_plaintext, etc.
- [x] Suporte a compressão e descompressão gzip, lz4, snappy, zstd.
- [x] Criar (suporta lotes) e excluir topics, especificar réplicas e partições.
- [x] Estatísticas de total de mensagens, offset confirmado e acumulação por grupo consumidor.
- [x] Informações detalhadas de partições (offsets), suporte para adicionar partições extras.
- [x] Simular produtor, enviar mensagens em lote com cabeçalhos e partição específica.
- [x] Verificação de saúde de topics e partições (concluído).
- [x] Visualização de grupos de consumidores e consumidores individuais.
- [x] Relatório de inspeção de offsets.
- [x] Suporte ao Schema Registry: gerenciamento de subjects/versões, compatibilidade e decodificação Avro, JSON e Protobuf.
- [x] Consumo em streaming múltiplo: streaming em tempo real, ordenação reversa, abas e commit de offsets.
- [x] Redefinição de offsets de grupos: redefinir para Start (mais antigo), End (mais recente), timestamp ou offset específico.
- [x] Limpeza de mensagens (DeleteRecords): exclusão de mensagens por partição ou em todo o tópico até o offset indicado.
- [x] Reatribuição de réplicas de partição: inspeção visual e ajuste de réplicas, com suporte para cancelamento.
- [x] Inspeção aprimorada de nós: indicador de Controller, análise de espaço em disco LogDirs e gestão de cotas de clientes.
- [x] Importação e exportação de conexões: exportação para YAML e importação de YAML/JSON com desduplicação inteligente.
- [x] Autenticação estendida: suporte a OAUTHBEARER (token estático), AWS MSK IAM e túnel SSH para múltiplos brokers.
- [x] Reprodução e exportação de mensagens: reenviar mensagens selecionadas para outros tópicos e exportação em JSON/CSV.

# Download
Baixe pelo lado direito ou visite a [página de releases](https://github.com/Bronya0/Kafka-King/releases). Expanda 【Assets】 e escolha a versão adequada para sua plataforma: Windows, macOS, Linux.

**Usuários macOS: se o aplicativo aparecer como "danificado" ao abrir, execute `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` no terminal (o app não está assinado e está bloqueado pelo Gatekeeper).**

`Notas importantes:`
1. **Antes de usar, verifique se a configuração `advertised.listeners` do seu cluster Kafka está correta. Se não configurada ou usando domínios, adicione a resolução correspondente no arquivo hosts da sua máquina.**
2. **Se sua conexão exigir SSL, habilite TLS e desative a verificação, a menos que você tenha um certificado — nesse caso, habilite a verificação TLS e forneça o caminho do certificado.**
3. **Usuários SASL devem habilitar SASL, selecionar o protocolo SASL adequado (geralmente plain) e inserir usuário e senha.**
4. **Em caso de erros de tempo de execução do webview2, baixe e reinstale o runtime do site oficial da Microsoft: https://developer.microsoft.com/pt-br/microsoft-edge/webview2**


# Compilação
A compilação manual é necessária apenas para estudar o código-fonte.

cd app

wails dev

# Licença
Licença Apache-2.0

# Agradecimentos
- wails: https://wails.io/docs/gettingstarted/installation
- naive ui: https://www.naiveui.com/
- franz-go: https://github.com/twmb/franz-go/
- xicons: https://xicons.org/#/

# Tradução
Suporta chinês, japonês, inglês, coreano, russo e outros idiomas.

Corrigir ou adicionar novo idioma: https://github.com/Bronya0/Kafka-King/issues/51
