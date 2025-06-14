# SPLN-TP2
SPLN-TP2

# Enunciado

---
title: Trabalho Prático II
author: 

- Filipe Cunha
- José João
date: Maio 2025
---

# Enunciado geral

Fazer um módulo de Information Retrival

- com base no RepsitoriUM
  - numa subcoleção a extrair / usar
- Calculador de similaridades de texto

## Extrair uma coleção a partir do RepositoriUM

- script python com `request.get(urlbase, params)` ...→ XML

### repositorium → XML

```py
url = "https://repositorium.sdum.uminho.pt/oai/oai"
col = "col_1822_21316"   #(msctesis do DI; 1822_2 msc; 1822_3 phd
n = #( 0, 100, 200, ...)

params = {"verb": "ListRecords",
          "resumptionToken": f"dim///{col}/{n}" }
r = requests.get(url, params=params).text
if "noRecordsMatch" not in r:  
  #( XML += r    Juntar r ao XML )
```

No RepositoriUM, o valor do "resumptionToken" tem a seguinte leitura

-  "dim"   é o "metadataPrefix"  ("dim" é o mais completo)
-  "col" é a coleção (correspondente ao parametro "Set" do OAI-PMH) ver:

  `https://repositorium.sdum.uminho.pt/oai/oai?verb=ListSets`

-  n  é o offset do próximo grupo de docs (0, 100, 200, ...)

## Calcular Coleção documental (XML → Json)

ColDoc.json = XML→Json(OAI.xml) 

Arrumar a informação: Limpando, filtrando, normalizando

## Calcular Coleção-treino-similaridades

### ColTrain

```py

ColTrain :: (txt,txt,sim)*

for d1,d2 in ColDoc.json²:
   ColTrain.append(d1.abst, d2.abst, guess_sim(d1,d1))
filtrar os pares relevantes
```
### Guess_sim

Estudar heurísticas para guess_sim(d1,d2) usando:

- keywords em comum; mas ter em conta:
  - nº de key de cada doc
  - raridade/trivialidades das keys
- subject UDC
- subject fos
- Coleções (diferentes das usadas na query)

## Treinar sentence-transformer 

- com base numa coleção (doc1, doc2, similarity)*

```py
modelo = train(BERT, ColTrain)
```

## Usar modelo

```py
retrive( quest, Col ) =
  mostrelevant ( 
    [ (doc, model.similarity(quest,Col) ) for doc in Col ]
  )
```