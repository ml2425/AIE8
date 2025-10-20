# Multi-Agent RAG System for Educational MCQs

A comprehensive multiagentic hierarchical RAG system designed for generating high-quality educational multiple-choice questions (MCQs) from medical literature and web resources.

## Notebook Sections Overview

The `multiagent.ipynb` notebook contains 16 comprehensive sections:

**Section 0: Config - Environment Setup**
- Load API keys from .env file
- Configure Tavily and stub mode settings
- Display configuration status

**Section 1: State Models - Typed Containers for Docs and MCQs**
- Define TypedDict structures (Doc, DocWithScore, MCQ)
- Set up data models for the pipeline

**Section 2: PubMedAgent - PubMed E-utilities Integration**
- Search PubMed using NCBI E-utilities API
- Retrieve medical literature abstracts

**Section 3: TavilyAgent - Web Search Integration**
- Web search using Tavily API
- Retrieve guidelines and resources

**Section 4: Merge + Re-rank - Combine and Rank Results**
- Merge PubMed and Tavily results
- Re-rank using Cohere API (model: rerank-english-v3.0)
- Fallback to cosine similarity

**Section 5: MCQ Generation - Create Questions from Ranked Results**
- Generate MCQs using OpenAI GPT-4o-mini
- Create stems, options, answers, and rationales

**Section 6: End-to-End Run - Complete Pipeline Execution**
- Run complete pipeline from search to MCQ generation
- Display results summary

**Section 7: Chunk and Store - Vector Database Integration**
- Chunk documents and store in Qdrant vector database
- Create embeddings using OpenAI

**Section 8: Mini Knowledge Graph - Regex-based Concept Extraction**
- Extract medical concepts using regex patterns
- Build SQLite knowledge graph
- Link papers to concepts/objectives

**Section 9: Retrieval Integration - Semantic + Knowledge Graph**
- Combine Qdrant semantic retrieval with KG lookup
- Merge contexts with token budgeting

**Section 10: Hierarchical Orchestration with LangGraph**
- Multi-agent system with Supervisor and Researchers
- LangGraph workflow orchestration
- State management across agents

**Section 11: MCQ Rubric & Checks (Agent Node)**
- Rule-based MCQ quality assessment
- Score clarity, relevance, distractor quality
- Validate single correct answer

**Section 12: RAGAS Evaluation (Qdrant-Grounded, Clean Rewrite)**
- Evaluate pipeline using RAGAS framework
- Generate synthetic QA from Qdrant chunks
- Compute faithfulness, answer relevancy, context precision, context recall

**Section 13: Advanced Retrieval (Hybrid: Qdrant Dense + SQLite FTS5 Sparse with RRF)**
- Hybrid retriever combining dense (Qdrant) and sparse (SQLite FTS5) search
- Reciprocal Rank Fusion (RRF) for result fusion
- Swappable retriever modes (dense vs hybrid_rrf)

**Section 14: Orchestration with Swappable Retriever (LangGraph)**
- End-to-end pipeline using swappable retriever from Section 13
- Complete workflow with retriever mode selection
- Console summary and MCQ display

**Section 15: RAGAS Evaluation (Retriever Comparison Mode)**
- Evaluate different retriever modes using RAGAS
- Compare dense vs hybrid retrieval performance
- Store metrics for comparison analysis

## Agentic Components

The system employs a sophisticated multi-agent architecture built on **LangGraph** for hierarchical orchestration. The **Supervisor Agent** acts as the central coordinator, managing workflow state and making high-level decisions about task distribution and result aggregation. **Researcher Agents** operate in parallel, with specialized PubMedAgent and TavilyAgent handling medical literature and web search respectively. The system uses **node types** including start nodes, agent nodes, and decision nodes to create a robust workflow graph. **Decision making** occurs at multiple levels: the Supervisor determines which agents to activate based on query complexity, while individual agents make retrieval and processing decisions. This hierarchical approach ensures efficient resource utilization and maintains context across the entire pipeline, enabling sophisticated reasoning about when to search, how to merge results, and when to generate final outputs.

## Knowledge Graph Retrieval Role

The **Mini Knowledge Graph** serves as a critical component for enhancing retrieval precision and contextual understanding. Built using regex-based concept extraction from medical literature, it creates a lightweight SQLite database that maps papers to key medical concepts and learning objectives. This knowledge graph enables **concept-driven retrieval** that complements semantic search by identifying papers related to specific medical topics, procedures, or conditions. The KG retrieval works in tandem with Qdrant's vector search, providing **hybrid context** that combines semantic similarity with explicit concept relationships. This dual approach ensures that retrieved documents are not only semantically relevant but also topically aligned with specific medical domains, significantly improving the quality and accuracy of generated MCQs by providing more targeted and educationally relevant content.

## Retrieval Technique Comparison

The system implements a comprehensive comparison between **dense retrieval** (Qdrant vector search only) and **hybrid retrieval** (Qdrant + SQLite FTS5 with Reciprocal Rank Fusion). **Dense retrieval** relies purely on semantic embeddings to find contextually similar documents, excelling at capturing conceptual relationships and handling paraphrased queries. **Hybrid retrieval** combines dense semantic search with sparse keyword matching using SQLite's FTS5 full-text search, then employs Reciprocal Rank Fusion (RRF) to merge and rank results. This hybrid approach provides superior **recall** for exact medical terms and specific terminology while maintaining semantic understanding. The comparison evaluates four key metrics: **faithfulness** (how well answers are grounded in retrieved context), **answer relevancy** (quality of generated responses), **context precision** (relevance of retrieved documents), and **context recall** (completeness of retrieved information). Typically, hybrid retrieval shows improved performance in medical domains where precise terminology and concept matching are crucial.

## Using Retriever Comparison (Sections 13-15)

To leverage the retriever comparison functionality for new use cases, follow this systematic approach: **First**, in Section 13, set `RETRIEVER_MODE = "dense"` to evaluate pure semantic retrieval, then run Sections 14-15 to generate MCQs and compute RAGAS metrics. **Second**, change `RETRIEVER_MODE = "hybrid_rrf"` in Section 13 and re-run Sections 14-15 to evaluate the hybrid approach. **Third**, compare the stored metrics in the `ragas_comparison` dictionary to analyze performance differences across faithfulness, relevancy, precision, and recall dimensions. This comparison framework is particularly valuable for **domain-specific applications** where you need to determine the optimal retrieval strategy. For medical education, hybrid retrieval typically outperforms dense-only approaches due to the importance of exact terminology. For other domains, you can adapt the concept extraction patterns in Section 8 and adjust the retrieval parameters to optimize performance for your specific use case, ensuring the system delivers the most accurate and relevant content for your educational objectives.
