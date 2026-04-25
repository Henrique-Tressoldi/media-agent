# Documentação de Contexto: Agente Analista de Mídia Júnior

## 1. Objetivo do Sistema
Construir um **Agente de IA Autônomo (MVP)** capaz de atuar como um Analista de Mídia. O foco principal não é apenas a extração de dados, mas a conversão de métricas brutas do Google BigQuery em **insights acionáveis** para os times de Mídia e Growth, otimizando a análise de ROI por canal.

## 2. Stack Tecnológica Obrigatória
* **Linguagem:** Python 3.10+.
* **Web Framework:** FastAPI(Uso obrigatório).
* **Orquestração de IA:** LangGraph (Uso obrigatório).
* **Arquitetura:** Agente baseado em **Tool Calling (Function Calling)**. Proibido o uso de prompts monolíticos com dados estáticos.
* **Banco de Dados:** Google BigQuery (Biblioteca cliente oficial `google-cloud-bigquery`).

## 3. Estrutura do Dataset (`thelook_ecommerce`)
O agente deve consultar o dataset público `bigquery-public-data.thelook_ecommerce`.

| Tabela | Colunas Chave | Propósito |
| :--- | :--- | :--- |
| `users` | `id`, `traffic_source`, `created_at` | Identificar origem do tráfego (Search, Organic, Facebook, etc). |
| `orders` | `order_id`, `user_id`, `status`, `created_at` | Monitorar volume de pedidos e conversão. |
| `order_items` | `order_id`, `sale_price` | Cálculo de receita e ROI. |

## 4. Requisitos de Comportamento do Agente
O fluxo de raciocínio da IA deve seguir rigorosamente:
1.  **Identificação de Intenção:** Reconhecer se o usuário busca volume, performance ou comparação.
2.  **Seleção de Ferramenta (Tool Calling):** O agente deve decidir qual função Python chamar para executar a query SQL no BigQuery.
3.  **Execução de Dados:** As queries devem ser parametrizadas (segurança contra SQL Injection) e eficientes (uso de JOINs e agregações).
4.  **Processamento de Insight:** A LLM recebe o JSON/Dataframe e deve traduzi-lo em uma análise estratégica (ex: "O canal Search cresceu X%, mas o ROI caiu Y% devido a...").

## 5. Critérios Críticos de Sucesso (KPIs de Desenvolvimento)
* **Separação de Preocupações:** A lógica de prompt deve estar isolada da lógica de execução de código (Tools).
* **Tipagem Estrita:** Uso obrigatório de `Pydantic` e `Type Hints` em todo o backend.
* **Tratamento de Erros:** Implementar capturas específicas para falhas de conexão com BigQuery e timeouts de LLM.
* **Visão de Produto:** Evitar respostas que sejam apenas "dumps" de dados. A resposta deve ser útil para um Gerente de Mídia.

## 6. Prompt de Sistema Sugerido para o Agente
> "Você é um Analista de Mídia Júnior de alto nível. Seu tom é profissional, analítico e direto. Você tem acesso ao BigQuery para responder perguntas sobre tráfego e vendas. Sempre que receber uma pergunta, verifique se precisa de dados reais antes de responder. Se os dados não estiverem disponíveis ou a pergunta estiver fora do escopo de e-commerce, informe ao usuário de forma clara. Priorize encontrar tendências e não apenas listar números."

## 7. Instruções de Setup para a IA Desenvolvedora
Ao iniciar o projeto:
1.  Configure as variáveis de ambiente para `OPENAI_API_KEY` (ou Anthropic) e `GOOGLE_APPLICATION_CREDENTIALS`.
2.  Utilize `poetry` ou `pip` com `requirements.txt` detalhado.
3.  Crie uma estrutura de pastas seguindo Clean Architecture ou MVC.
4.  Documente o fluxo do agente em um diagrama `mermaid.js` no README.

---

### Análise Estratégica do Conselheiro
O maior risco deste projeto é a **alucinação de SQL**. Para mitigar isso, certifique-se de que a IA que desenvolverá o código forneça o esquema exato das tabelas no prompt das ferramentas de consulta. Se o agente tentar adivinhar nomes de colunas que não existem no `thelook_ecommerce`, o projeto falhará no critério de "Engenharia de Dados". 

Você vai seguir com a implementação agora ou quer que eu revise a estrutura de pastas proposta pela IA antes de você começar?