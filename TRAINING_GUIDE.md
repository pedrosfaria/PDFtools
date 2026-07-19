# Guia Completo: Como Treinar o Programa para Faturas da Coopérnico

Este guia explica **passo a passo** como ensinar o programa a reconhecer os campos nas faturas da Coopérnico usando o **Modo de Treino**.

## 🎯 O que é o Modo de Treino?

O Modo de Treino é uma **interface interativa** que permite:

1. **Carregar uma fatura PDF** da Coopérnico
2. **Selecionar manualmente** onde está cada dado (número da fatura, consumo, etc.)
3. **Associar o texto selecionado** ao campo correspondente
4. **Guardar os padrões aprendidos** para uso futuro
5. **Testar a extração automática** com os padrões aprendidos

Quanto mais faturas treinar, **melhor o programa fica** a reconhecer os campos automaticamente!

---

## 🚀 Passo a Passo para Treinar o Programa

### Passo 1: Iniciar o Modo de Treino

```bash
# Ativar ambiente virtual
venv\Scripts\activate  # Windows

# Instalar dependências (se ainda não o fez)
pip install flask

# Iniciar a aplicação de treino
python app_train.py
```

Abra o browser em: **http://localhost:5001**

---

### Passo 2: Carregar uma Fatura da Coopérnico

1. Clique em **"Carregar"** no menu
2. Selecione um ficheiro PDF de uma fatura da Coopérnico
3. Clique em **"Carregar e Começar Treino"**

✅ **Pronto!** A fatura foi carregada e o texto está visível.

---

### Passo 3: Selecionar e Anotar os Campos

Agora vai **ensinar o programa** onde estão os dados na fatura.

#### Método 1: Seleção Manual (Recomendado)

1. **No painel da esquerda**, veja o texto da fatura
2. **Selecionar texto** com o rato (arrastar)
3. **No painel da direita**, clique no campo correspondente (ex: "Nº Fatura", "Consumo", etc.)
4. Clique em **"Associar a Campo"**

🎯 **Exemplo prático:**
- Selecione "COOP-2024-001234" no texto
- Clique em "Nº Fatura" na lista de campos
- Clique em "Associar a Campo"

#### Método 2: Usar Sugestões Automáticas

O programa **já pode ter algumas sugestões** com base em faturas anteriores.

1. No painel de **Sugestões Automáticas** (em baixo do texto)
2. Clique numa sugestão para aceitar automaticamente
3. O programa associa o texto ao campo correspondente

---

### Passo 4: Verificar e Corrigir Anotações

À medida que adiciona anotações:

- **Painel "Anotações Atuais"** mostra todas as anotações que fez
- Pode **remover anotações** clicando no ícone do lixo
- Pode **limpar todas** as anotações

✅ **Dica:** Tente anotar pelo menos os **campos obrigatórios** (marcados com *):
- Nº Fatura
- Data Emissão
- Consumo (kWh)
- Total a Pagar (€)
- Nome Cliente
- NIF

---

### Passo 5: Aprender Padrões

Quando terminar de anotar os campos:

1. Clique em **"Aprender Padrões"**
2. O programa **analisa as suas anotações** e cria padrões
3. Os padrões são **guardados automaticamente** no ficheiro `training/patterns.json`

✅ **Pronto!** O programa já aprendeu com esta fatura!

---

### Passo 6: Testar a Extração

Para verificar se o programa aprendeu corretamente:

1. Clique em **"Testar Extração"**
2. Veja os **resultados da extração automática**
3. Verifique se os dados estão corretos

🔍 **Se algum campo estiver errado:**
- Volte ao treino
- Adicione mais anotações para esse campo
- Repita o processo

---

### Passo 7: Treinar com Mais Faturas

Para **melhorar a precisão**, repita o processo com **mais faturas**:

1. Clique em **"Carregar Outra Fatura"**
2. Repita os passos 3-6

✨ **Quanto mais faturas treinar, melhor o programa fica!**

---

## 📊 Estrutura de uma Fatura da Coopérnico

Para ajudar no treino, aqui está a **estrutura típica** de uma fatura da Coopérnico:

```
┌─────────────────────────────────────────────────────────────┐
│  Coopérnico - Cooperativa de Energia                          │
│  Fatura nº: COOP-2024-001234                                  │
│  Data Emissão: 15-01-2024                                     │
│  Data Vencimento: 30-01-2024                                 │
├─────────────────────────────────────────────────────────────┤
│  Sócio: João Silva                                           │
│  NIF: 123456789                                              │
│  Morada: Rua da Cooperativa, 123                             │
│  Código Postal: 1234-567                                      │
│  Localidade: Lisboa                                          │
├─────────────────────────────────────────────────────────────┤
│  Período de Consumo: 01-12-2023 a 31-12-2023                 │
│  Consumo: 350,50 kWh                                         │
│  Potência Contratada: 6,90 kVA                              │
├─────────────────────────────────────────────────────────────┤
│  Descrição                     | Valor (€)                   │
│  ------------------------------------------------------------│
│  Energia Consumida            | 49,07                       │
│  Acesso à Rede                | 10,50                       │
│  IVA (23%)                    | 13,84                       │
│  ------------------------------------------------------------│
│  Total a Pagar                | 73,41                       │
├─────────────────────────────────────────────────────────────┤
│  Nº Contador: COOP123456                                      │
│  Leitura Atual: 12345                                         │
│  Leitura Anterior: 12000                                     │
│  Data da Leitura: 31-12-2023                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Campos Importantes para Anotar

### 📄 Informações da Fatura
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Nº Fatura | COOP-2024-001234 | Texto | ✅ |
| Data Emissão | 15-01-2024 | Data | ✅ |
| Data Vencimento | 30-01-2024 | Data | ✅ |

### ⚡ Dados de Consumo
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Período de Consumo (Início) | 01-12-2023 | Data | ❌ |
| Período de Consumo (Fim) | 31-12-2023 | Data | ❌ |
| Consumo (kWh) | 350,50 | Número | ✅ |
| Potência Contratada (kVA) | 6,90 | Número | ❌ |
| Preço/kWh (€) | 0,14 | Moeda | ❌ |

### 💰 Valores Monetários
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Custo Energia (€) | 49,07 | Moeda | ❌ |
| Custo Rede (€) | 10,50 | Moeda | ❌ |
| Taxa IVA (%) | 23 | Número | ❌ |
| Valor IVA (€) | 13,84 | Moeda | ❌ |
| Total a Pagar (€) | 73,41 | Moeda | ✅ |

### 👤 Informações do Cliente
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Nome Cliente | João Silva | Texto | ✅ |
| NIF | 123456789 | Texto | ✅ |
| Nº Cliente | CL123456 | Texto | ❌ |
| Morada | Rua da Cooperativa, 123 | Texto | ❌ |
| Código Postal | 1234-567 | Texto | ❌ |
| Localidade | Lisboa | Texto | ❌ |

### 📏 Informações do Contador
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Nº Contador | COOP123456 | Texto | ❌ |
| Leitura Atual | 12345 | Número | ❌ |
| Leitura Anterior | 12000 | Número | ❌ |
| Data da Leitura | 31-12-2023 | Data | ❌ |

### 💳 Informações de Pagamento
| Campo | Exemplo | Tipo | Obrigatório |
|-------|---------|------|-------------|
| Método de Pagamento | Transferência Bancária | Texto | ❌ |
| Referência de Pagamento | 123 456 789 | Texto | ❌ |

---

## 💡 Dicas para um Bom Treino

### ✅ O que Fazer

1. **Comece com faturas claras**
   - Escolha faturas com formato simples e legível
   - Evite faturas com formato muito diferente

2. **Selecione com precisão**
   - Tente selecionar **apenas o texto relevante**
   - Exemplo: Para "Nº Fatura", selecione apenas "COOP-2024-001234", não "Nº Fatura: COOP-2024-001234"

3. **Treine com múltiplos exemplos**
   - Quanto mais faturas treinar, melhor
   - Tente treinar com pelo menos **5-10 faturas**

4. **Verifique os resultados**
   - Depois de treinar, teste a extração
   - Se algum campo estiver errado, adicione mais exemplos

5. **Use sugestões automáticas**
   - O programa sugere automaticamente onde podem estar os campos
   - Clique nas sugestões para aceitar rapidamente

### ❌ O que Evitar

1. **Selecionar texto irrelevante**
   - Não selecione cabeçalhos ou rótulos
   - Selecione apenas os **valores**

2. **Treinar com faturas muito diferentes**
   - Se as faturas tiverem formatos muito diferentes, o programa pode confundir
   - Tente treinar com faturas do **mesmo tipo**

3. **Ignorar campos obrigatórios**
   - Tente sempre anotar os campos obrigatórios (marcados com *)

4. **Esquecer de guardar**
   - Clique sempre em **"Aprender Padrões"** para guardar as anotações

---

## 📈 Como o Programa Aprende

O programa usa **várias técnicas** para aprender com os seus exemplos:

### 1. Padrões de Texto (Regex)
- Se anotar "Nº Fatura: COOP-2024-001234", o programa cria um padrão como:
  ```regex
  Nº Fatura:\\s*([A-Z0-9\\-]+)
  ```
- Este padrão vai procurar por "Nº Fatura:" seguido de um código

### 2. Posição Relativa
- O programa guarda **onde** cada campo aparece no texto
- Se em várias faturas o "Consumo" aparece sempre depois de "Período de Consumo", o programa aprende esta relação

### 3. Contexto
- O programa aprende **que texto aparece antes e depois** de cada campo
- Exemplo: Se "Total a Pagar" aparece sempre entre "IVA" e "Método de Pagamento", o programa usa esta informação

### 4. Formato dos Dados
- O programa reconhece **formatos de dados**:
  - Datas: `dd-mm-yyyy`, `dd/mm/yyyy`
  - Números: `123,45` ou `123.45`
  - Moeda: `123,45 €` ou `€ 123,45`

---

## 🔧 Ferramentas Avançadas

### Exportar e Importar Padrões

Pode **partilhar os padrões aprendidos** com outros utilizadores:

1. **Exportar**:
   - Clique em **"Exportar Padrões Aprendidos"**
   - Guarda o ficheiro `patterns.json`
   - Partilhe este ficheiro com outros

2. **Importar**:
   - Receba um ficheiro `patterns.json` de outro utilizador
   - Clique em **"Importar Padrões"**
   - Selecione o ficheiro
   - O programa carrega os padrões

### Gerir Exemplos de Treino

1. **Ver todos os exemplos**:
   - Clique em **"Exemplos"** no menu
   - Veja a lista de todos os exemplos de treino

2. **Carregar um exemplo**:
   - Clique no ícone de **editar** (✏️) para carregar um exemplo
   - Continua o treino a partir desse exemplo

3. **Apagar um exemplo**:
   - Clique no ícone de **lixo** (🗑️) para apagar um exemplo

4. **Apagar tudo**:
   - Clique em **"Apagar Todos os Exemplos"** para começar do zero

---

## 🎯 Exemplo Prático Completo

Vamos assumir que tem uma fatura da Coopérnico com este texto:

```
Coopérnico - Cooperativa de Energia
Fatura nº: COOP-2024-001234
Data Emissão: 15-01-2024
Data Vencimento: 30-01-2024

Sócio: João Silva
NIF: 123456789
Morada: Rua da Cooperativa, 123
Código Postal: 1234-567
Localidade: Lisboa

Período de Consumo: 01-12-2023 a 31-12-2023
Consumo: 350,50 kWh
Potência Contratada: 6,90 kVA

Preço da Energia: 0,14 €/kWh
Custo da Energia: 49,07 €
Acesso à Rede: 10,50 €
IVA (23%): 13,84 €

Total a Pagar: 73,41 €

Nº Contador: COOP123456
Leitura Atual: 12345
Leitura Anterior: 12000
Data da Leitura: 31-12-2023
```

### Passos para treinar:

1. **Carregar a fatura** (já feito)

2. **Anotar campos:**
   - Selecionar "COOP-2024-001234" → Clicar em "Nº Fatura" → "Associar a Campo"
   - Selecionar "15-01-2024" → Clicar em "Data Emissão" → "Associar a Campo"
   - Selecionar "30-01-2024" → Clicar em "Data Vencimento" → "Associar a Campo"
   - Selecionar "João Silva" → Clicar em "Nome Cliente" → "Associar a Campo"
   - Selecionar "123456789" → Clicar em "NIF" → "Associar a Campo"
   - Selecionar "350,50" → Clicar em "Consumo (kWh)" → "Associar a Campo"
   - Selecionar "73,41" → Clicar em "Total a Pagar (€)" → "Associar a Campo"

3. **Aprender padrões** → Clique em "Aprender Padrões"

4. **Testar extração** → Clique em "Testar Extração"

5. **Verificar resultados** → Deve ver todos os campos preenchidos corretamente

---

## ❓ Perguntas Frequentes

### Q: Quantas faturas preciso de treinar?
**R:** Quanto mais melhor! Mas com **5-10 faturas** já deve ter bons resultados para a maioria dos campos.

### Q: O programa esquece o que aprendeu?
**R:** Não! Os padrões são guardados no ficheiro `training/patterns.json`. Ficam guardados até apagar manualmente.

### Q: Posso treinar com faturas de outros fornecedores?
**R:** Sim! O programa guarda os padrões por fornecedor. Pode treinar com faturas da EDP, Galp, etc.

### Q: Como sei se o programa está a aprender corretamente?
**R:** Depois de treinar, clique em **"Testar Extração"**. Se os dados estiverem corretos, o programa está a aprender bem.

### Q: O que fazer se o programa extrair dados errados?
**R:**
1. Volte ao treino
2. Adicione mais anotações para os campos que estão errados
3. Clique em "Aprender Padrões" novamente
4. Teste a extração

### Q: Posso editar os padrões manualmente?
**R:** Sim! Pode editar o ficheiro `training/patterns.json` manualmente. Mas tenha cuidado com a sintaxe JSON.

### Q: O que acontece se apagar o ficheiro patterns.json?
**R:** O programa volta aos padrões iniciais. Não perde os exemplos de treino, apenas os padrões aprendidos.

---

## 📊 Monitorizar o Progresso

Pode ver o progresso do treino em:

1. **Número de exemplos**: Quantas faturas já treinou
2. **Número de anotações**: Quantos campos já anotou
3. **Campos únicos**: Quantos campos diferentes já anotou
4. **Taxa de sucesso**: Percentagem de campos extraídos corretamente

---

## 🎉 Dicas Finais

1. **Comece simples**: Treine primeiro com os campos obrigatórios
2. **Seja consistente**: Tente anotar os mesmos campos em todas as faturas
3. **Verifique sempre**: Teste a extração depois de treinar
4. **Partilhe padrões**: Se treinar com muitas faturas, exporte os padrões para partilhar com a equipa
5. **Atualize regularmente**: À medida que recebe novas faturas, adicione-as ao treino

---

## 🚀 Próximos Passos

Agora que sabe como treinar o programa:

1. ✅ **Carregue uma fatura** da Coopérnico
2. ✅ **Anote os campos** importantes
3. ✅ **Aprenda os padrões**
4. ✅ **Teste a extração**
5. 🔄 **Repita com mais faturas**

**Quanto mais treinar, melhor o programa fica!** 🎯

---

## 📚 Documentação Relacionada

- **[WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)** - Como criar a aplicação web
- **[COOPERNICO_GUIDE.md](COOPERNICO_GUIDE.md)** - Guia específico para Coopérnico
- **[INSTALL.md](INSTALL.md)** - Guia de instalação

---

## 💬 Suporte

Se tiver problemas ou dúvidas:

1. Verifique este guia novamente
2. Teste com o exemplo prático acima
3. Contacte-me com:
   - O erro que está a receber
   - Uma amostra da fatura que está a treinar
   - Os passos que seguiu

Estou aqui para ajudar! 🚀
