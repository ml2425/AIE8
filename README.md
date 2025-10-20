Multiagent Notebook Section Summary
Sections 0 - 12
          ┌──────────────┐
          │ PubMed / Tavily │
          └──────┬─────────┘
                 │
        [Summarise & Chunk]
                 │
          ▼ Vectorize Text
        ┌──────────────┐
        │ Qdrant Store │
        └──────────────┘
                 │
         ┌───────┴────────┐
         │ Mini-KG (SQLite)│
         └───────┬────────┘
                 │
     ┌───────────┼───────────┐
     │ Retrieve & Rerank     │
     │ (Qdrant + Cohere)     │
     └───────────┼───────────┘
                 │
        ▼ Context to LLM
   [MCQ / Answer Generation]
                 │
           ▼ Evaluation
        ┌──────────────────────┐
        │ RAGAS (Faith., Rel., │
        │ Ctx Prec., Recall)  │
        └──────────────────────┘


Section 0: Config - Environment Setup
Load API keys from .env file
Configure Tavily and stub mode settings
Display configuration status

Section 1: State Models - Typed Containers for Docs and MCQs
Define TypedDict structures (Doc, DocWithScore, MCQ)
Set up data models for the pipeline

Section 2: PubMedAgent - PubMed E-utilities Integration
Search PubMed using NCBI E-utilities API
Retrieve medical literature abstracts

Section 3: TavilyAgent - Web Search Integration
Web search using Tavily API
Retrieve guidelines and resources

Section 4: Merge + Re-rank - Combine and Rank Results
Merge PubMed and Tavily results
Re-rank using Cohere API (model: rerank-english-v3.0)
Fallback to cosine similarity

Section 5: MCQ Generation - Create Questions from Ranked Results
Generate MCQs using OpenAI GPT-4o-mini
Create stems, options, answers, and rationales

Section 6: End-to-End Run - Complete Pipeline Execution
Run complete pipeline from search to MCQ generation
Display results summary

Section 7: Chunk and Store - Vector Database Integration
Chunk documents and store in Qdrant vector database
Create embeddings using OpenAI
Section 8: Mini Knowledge Graph - Regex-based Concept Extraction
Extract medical concepts using regex patterns
Build SQLite knowledge graph
Link papers to concepts/objectives

Section 9: Retrieval Integration - Semantic + Knowledge Graph
Combine Qdrant semantic retrieval with KG lookup
Merge contexts with token budgeting

Section 10: Hierarchical Orchestration with LangGraph
Multi-agent system with Supervisor and Researchers
LangGraph workflow orchestration
State management across agents

Section 11: MCQ Rubric & Checks (Agent Node)
Rule-based MCQ quality assessment
Score clarity, relevance, distractor quality
Validate single correct answer

Section 12: RAGAS Evaluation (Qdrant-Grounded, Clean Rewrite)
Evaluate pipeline using RAGAS framework
Generate synthetic QA from Qdrant chunks
Compute faithfulness, answer relevancy, context precision, context recall

Section 13: Advanced Retrieval (Hybrid: Qdrant Dense + SQLite FTS5 Sparse with RRF)
Hybrid retriever combining dense (Qdrant) and sparse (SQLite FTS5) search
Reciprocal Rank Fusion (RRF) for result fusion
Swappable retriever modes (dense vs hybrid_rrf)

Section 14: Orchestration with Swappable Retriever (LangGraph)
End-to-end pipeline using swappable retriever from Section 13
Complete workflow with retriever mode selection
Console summary and MCQ display

Section 15: RAGAS Evaluation (Retriever Comparison Mode)
Evaluate different retriever modes using RAGAS
Compare dense vs hybrid retrieval performance
Store metrics for comparison analysis

## Comparing Retriever Performance (Dense vs Hybrid)

To compare the performance of dense retrieval (Qdrant only) versus hybrid retrieval (Qdrant + SQLite FTS5 with RRF), follow these steps:

1. **First Run - Dense Mode**: In Section 13, set `RETRIEVER_MODE = "dense"`, then run Sections 14-15. This will evaluate pure semantic retrieval using only Qdrant embeddings.

2. **Second Run - Hybrid Mode**: In Section 13, change `RETRIEVER_MODE = "hybrid_rrf"`, then run Sections 14-15 again. This will evaluate the hybrid approach combining dense semantic search with sparse keyword matching.

3. **Compare Results**: Section 15 automatically stores metrics in the `ragas_comparison` dictionary, allowing you to compare faithfulness, answer relevancy, context precision, and context recall between the two modes. The hybrid approach typically shows improved recall for exact medical terms while maintaining semantic understanding.

Sections 13 - 15

User Query
   │
   ▼
┌─────────────────────────────┐
│ Hybrid Retrieval            │
│ (Qdrant dense + SQLite FTS5 │
│  fused via RRF + Cohere)    │
└─────────────────────────────┘
   │
   ▼
[Same MCQ + RAGAS pipeline]
