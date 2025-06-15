# Autores
Autores

- PG55944 Gonçalo Costa
Costa
- PG56006 Rodrigo Novo
- PG56967 José Correia

# Sistema de Recuperação de Informação - TP2 SPLN

Este documento descreve, em detalhe, a implementação de um sistema de Recuperação de Informação baseado em embeddings de sentenças, desenvolvido para o **Trabalho Prático II da unidade curricular de Sistemas de Processamento de Linguagem Natural (SPLN)**, usando dados do RepositoriUM.

---

## 🔍 Objetivo Geral

Desenvolver um sistema capaz de:

* Indexar documentos académicos a partir do RepositoriUM
* Calcular similaridade semântica entre documentos
* Recuperar documentos relevantes com base numa query textual
* Avaliar o desempenho do sistema de retrieval

---

## 📂 Estrutura Geral do Projeto

```
.
├── data/
│   ├── result.json   # Documentos processados em JSON
│   ├── similarities.json  # Pares de treino (doc1, doc2, similarity)
├── models/                         # Modelos treinados ou checkpoints
├── parameters.py                  # Configurações globais
├── scripts.py (diveros)           # Código principal do sistema
└── report.md                      # Este ficheiro
```

O projeto é dividido em 5 scripts, cada um com uma função específica e modularizados de forma a conseguirem correr de forma independente.

---

## 📚 Retrievel dos dados - Script `retrievel.py`

A extração de documentos é feita a partir da API **OAI-PMH** do RepositoriUM:

* URL base: `https://repositorium.sdum.uminho.pt/oai/oai`
* Coleções usadas: `msc`, `msc_di`
* Formato: `dim` (esquema de metadados)

Este script desempenha o papel de iterar sobre as coleções e extrair os registos XML e armazená-los num único ficheiro XML.

---
## 📊 Limpeza dos dados - Script `xml_to_json.py`

Os documentos são convertidos de XML para JSON com os seguintes filtros:

* Abstracts com tamanho entre 50 e 2000 caracteres
* Eliminação de registos incompletos
* Campos extraidos:

  * `id, title, abstract, authors/Autores (pode haver vários), keywords, date, type, language, subjects_udc, subjects_fos, collections`
  
Este script lê o ficheiro XML encontra todos os registos `<record>` e para cada registo extrai os campos relevantes e verifica se o mesmo é válido segundo as regras definidas em cima e "limpa" e normaliza os campos necessários.

---

## 🚀 Similaridade e Treino do modelo - Scripts `get_similarity.` e `model.py`

### ⚖️ Similaridade

Este script carrega documentos (a partir do JSON criado no script anterior, calcula similaridade entre todos os pares possíveis, guarda os pares mais semelhantes (acima de um certo limiar) num ficheiro de treino e mostrar estatísticas sobre essas similaridades.

Como é calculada a similaridade:

- Keywords (peso 45%), calculada por comparação keywords + palavras do abstract, removendo stopwords e aquelas que são mais raras e comuns

- UDC subjects (peso 25%), calculada por Jaccard entre subjects_udc

- FOS subjects (peso 20%), calculada por Jaccard entre subjects_fos

- Coleções (peso 10%), calculada por Jaccard entre coleções

Cada uma é normalizada e ponderada. A soma dá a pontuação final de 0.0 a 1.0.

### 🎓 Embeddings

Modelos usados:

```python
"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
"all-MiniLM-L6-v2"
"distiluse-base-multilingual-cased-v2"
```

Este script carrega os dados de treino gerados no script anterior, treina um modelo SentenceTransformer, usando CosineSimilarityLoss, avalia o modelo com métricas reais (MSE, MAE) e guarda o modelo treinado para uso posterior

### 🎓 Treino do Modelo

O modelo pode ser afinado com exemplos supervisionados:

* `similarities.json` contém pares:

```json
{
  "text1": "Resumo do doc A",
  "text2": "Resumo do doc B",
  "similarity": 0.9
}
```

* O treino é feito com o `SentenceTransformer` e `InputExample`

Parâmetros usados:

```python
EPOCHS = 5
BATCH = 16
THRESHOLD_SIMILARITY = 0.3
```

É importante destacar que, durante os testes preliminares, os modelos `all-MiniLM-L6-v2` e `distiluse-base-multilingual-cased-v2` demonstraram desempenho superior em termos de qualidade das similaridades geradas, especialmente quando combinados com batch sizes maiores e valores elevados para o número de documentos recuperados por consulta. No entanto, tendo em conta as limitações computacionais dos equipamentos utilizados pelos membros do grupo, n optou-se por adotar o modelo `paraphrase-multilingual-MiniLM-L12-v2`. Este modelo oferece um bom compromisso entre desempenho e eficiência computacional, permitindo treinos com batch size 16 e 5 épocas, alcançando resultados satisfatórios dentro dos recursos disponíveis.


---

## 🤝 Testes e User Engine - Script `search_engine.py`

O que este script faz é carrega o modelo treinado (ou o modelo base se necessário, em caso de falha num script anterior, carrega os documentos com metadados e resumos, calcula os embeddings de todos os documentos (para serem usados em pesquisa) e permite fazer consultas de texto livre e recuperar os documentos mais semelhantes


### Funções principais:

* `load_model()` - Carrega modelo base ou treinado
* `load_docss()` - Carrega os documentos JSON
* `get_embendiings()` - Gera embeddings dos resumos
* `get_docss(query, ...)` - Recupera documentos com base na query
* `fetch_results()` - Apresenta resultados formatados ao utilizador
* `search_query_by_user()` - Modo interativo com input do utilizador

### Exemplo de Output:

```
Query: "classificação de texto"
1. SCORE -  0.784
   TITLE - Classificação de documentos com SVM
   AUTHORS - JJ
   DATE - 2019
   ABSTRACT - Este trabalho aborda...
   KEYWORDS - machine learning, text classification
```

---

## ⚖️ Avaliação (Comentado no Código)


* Precision
* Recall
* F1 Score


---

## ⚙️ Melhorias Futuras

* Usar modelo `e5` com prompt:

  * `"query: texto"` e `"passage: documento"`
* Re-ranker com `CrossEncoder` para melhorar top 10
* Indexação com faiss ou elasticsearch para rapidez
* Normalização lexical, lematização, filtros de linguagem
* Geração semi-automática de dados de treino com heurísticas

---

## 🛌 Conclusão

Este sistema constitui um pipeline completo de Information Retrieval sobre o RepositoriUM, baseado em embeddings semânticos. Está preparado para ser expandido, re-treinado e melhorado com rerankers, modelos mais avançados ou avaliação formal.


