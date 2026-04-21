# Multimodal Document Understanding, PDF Image Processing, and Visual Document Retrieval

## Research Survey -- April 2026

This document surveys the academic landscape around multimodal document understanding, with a focus on OCR-free visual document retrieval, multimodal RAG architectures, document layout analysis, and embedding models for visually rich documents.

---

## 1. OCR-Free Visual Document Retrieval (ColPali / ColQwen Paradigm)

This paradigm represents the most significant recent shift in document retrieval: treating document pages as images and embedding them directly via vision-language models, entirely bypassing OCR pipelines.

### 1.1 ColPali: Efficient Document Retrieval with Vision Language Models

- **Authors:** Manuel Faysse, Hugues Sibille, Tony Wu, Bilel Omrani, Gautier Viaud, Celine Hudelot, Pierre Colombo
- **Published:** ICLR 2025 (arXiv:2407.01449, June 2024)
- **Link:** [arxiv.org/abs/2407.01449](https://arxiv.org/abs/2407.01449)

**Key Contribution:** Introduced the concept of doing document retrieval by directly embedding images of document pages using a Vision Language Model, bypassing all OCR, text extraction, and chunking pipelines.

**Approach:** ColPali is built on PaliGemma and uses a late interaction matching mechanism (inherited from ColBERT). The model produces multi-vector embeddings from page images, where each image patch generates an embedding vector. Query-document matching is done via MaxSim -- summing the maximum similarity between each query token embedding and all document patch embeddings.

**Results/Benchmarks:**
- Introduced the **ViDoRe** (Visual Document Retrieval Benchmark), spanning multiple domains, languages, and settings
- ColPali significantly outperforms all text-centric retrieval baselines across ViDoRe, particularly on visually complex tasks (InfographicVQA, ArxivQA, TabFQuAD)
- Drastically simpler pipeline than OCR + chunking + embedding approaches
- End-to-end trainable with strong latency characteristics

**Practical Implications:** Eliminates the need for brittle OCR pipelines, layout detection, and text chunking for document indexing. A single model replaces what previously required multiple specialized tools. Open-source at [hf.co/vidore](https://hf.co/vidore).

### 1.2 ColQwen / ColQwen2

- **Model family page:** [HuggingFace vidore collection](https://huggingface.co/vidore)
- **Context:** [Weaviate overview](https://weaviate.io/blog/late-interaction-overview)

**Key Contribution:** Extends the ColPali concept from PaliGemma to the Qwen2-VL backbone, achieving improved performance on ViDoRe benchmarks while maintaining the same late-interaction architecture.

**Approach:** Same conceptual architecture as ColPali (Contextualized Late Interaction over Qwen2), treating entire PDF pages as images. ColQwen2 benefits from Qwen2-VL's stronger vision-language understanding, particularly its native dynamic resolution handling.

**Practical Implications:** ColQwen2.5-v0.2 is widely used in multimodal RAG pipelines as a drop-in visual retriever. The latest ColQwen3-4B and ColQwen3-8B variants continue to push performance on ViDoRe.

### 1.3 Reproducibility Study: Visual Document Retrieval with Late Interaction

- **Authors:** Jingfen Qiao, Jia-Huei Ju, Xinyu Ma, Evangelos Kanoulas, Andrew Yates
- **Published:** arXiv:2505.07730, May 2025
- **Link:** [arxiv.org/abs/2505.07730](https://arxiv.org/abs/2505.07730)

**Key Contribution:** Systematic reproducibility and replicability study of ColPali across multiple VLM backbones.

**Key Findings:**
- Late interaction yields considerable improvements in retrieval effectiveness -- confirmed reproducibly
- However, late interaction introduces **computational inefficiencies during inference** (storage and compute costs for multi-vector representations)
- VDR models trained on visual documents can **generalize to text document retrieval under zero-shot settings**
- ColPali is more robust to increased corpus size compared to OCR-based retrieval, especially for documents with higher non-textual content
- Query tokens in late interaction tend to match patches containing visually similar tokens or their surrounding patches, rather than explicit text matching

### 1.4 Spatially-Grounded Document Retrieval (Snappy)

- **Author:** Athos Georgiou
- **Published:** arXiv:2512.02660, December 2025
- **Link:** [arxiv.org/abs/2512.02660](https://arxiv.org/abs/2512.02660)

**Key Contribution:** Proposes a hybrid architecture that bridges ColPali's visual retrieval with OCR-based spatial precision, using patch-level similarity scores as spatial relevance filters over OCR-extracted regions.

**Approach:** Maps ColPali patch grids to OCR bounding boxes, enabling sub-page localization of relevant content. ColQwen3-4B with percentile-50 thresholding achieves 59.7% hit rate at IoU@0.5 for within-page localization.

**Results:**
- Reduces context tokens by 28.8% vs. returning all OCR regions
- Reduces context tokens by 52.3% vs. full-page image tokens
- No additional training required -- operates at inference time
- Open-source: [github.com/athrael-soju/Snappy](https://github.com/athrael-soju/Snappy)

**Practical Implications:** Addresses the main limitation of ColPali (page-level granularity) for RAG applications where precise context extraction is needed.

---

## 2. Document Screenshot Embedding (Single-Vector Approaches)

### 2.1 DSE: Unifying Multimodal Retrieval via Document Screenshot Embedding

- **Authors:** Xueguang Ma et al.
- **Published:** arXiv:2406.11251, June 2024 (EMNLP 2024)
- **Link:** [arxiv.org/abs/2406.11251](https://arxiv.org/abs/2406.11251)

**Key Contribution:** Proposes representing documents as screenshots and using a CLIP-based vision encoder + LVLM (Phi-3) to generate a single compressed embedding per document page.

**Approach:** Uses a vision encoder to produce patch embeddings from screenshots, then feeds them into an LVLM (e.g., Phi-3) to generate contextualized embeddings that are compressed into a single vector. This single-vector approach integrates seamlessly with standard dense retrieval infrastructure.

**Key Difference from ColPali:** DSE produces a single vector per page (dense retrieval compatible), while ColPali produces multi-vectors (late interaction). This means DSE is simpler to deploy with existing vector databases but generally less expressive than ColPali's multi-vector approach.

**Practical Implications:** More practical for existing retrieval infrastructure that uses single-vector similarity (e.g., FAISS, Pinecone), but ColPali's late interaction tends to outperform on complex visual retrieval tasks.

### 2.2 VisRAG: Vision-based Retrieval-Augmented Generation on Multi-modality Documents

- **Authors:** Shi Yu et al.
- **Published:** arXiv:2410.10594, October 2024
- **Link:** [arxiv.org/abs/2410.10594](https://arxiv.org/abs/2410.10594)

**Key Contribution:** A complete vision-based RAG pipeline that replaces the traditional text-based RAG with visual retrieval and visual generation, keeping documents in their original image format throughout.

**Approach:** VisRAG embeds document pages as images for retrieval (using MiniCPM-V) and passes retrieved page images directly to a multimodal LLM for generation, avoiding all information loss from text extraction.

**Results:**
- Outperforms traditional text-based RAG pipelines across multiple document QA benchmarks
- Demonstrates strong generalization with limited training data
- The "vision-in, vision-out" paradigm preserves layout, formatting, and visual context

**Practical Implications:** Demonstrates that the entire RAG pipeline can operate in the visual domain without text extraction, though it depends on the visual understanding capabilities of the generation model.

---

## 3. Layout-Aware Document Understanding Models

### 3.1 LayoutLM Series (LayoutLM / LayoutLMv2 / LayoutLMv3)

- **LayoutLM:** arXiv:1912.13318, December 2019 ([link](https://arxiv.org/abs/1912.13318))
- **LayoutLMv3:** arXiv:2204.08387, April 2022 ([link](https://arxiv.org/abs/2204.08387))
- **Authors (v3):** Yupan Huang, Tengchao Lv, Lei Cui, Yutong Lu, Furu Wei (Microsoft)

**Key Contribution:** The LayoutLM family pioneered jointly learning text, layout (spatial position), and image representations for Document AI.

**LayoutLMv3 Approach:**
- Unified pre-training with Masked Language Modeling (MLM), Masked Image Modeling (MIM), and Word-Patch Alignment (WPA)
- First multimodal pre-trained Document AI model without CNNs for image embeddings
- General-purpose model for both text-centric tasks (form understanding, receipt extraction) and image-centric tasks (document classification, layout analysis)

**Evolution:**
- **LayoutLM** (2019): First to jointly model text + layout in a single framework
- **LayoutLMv2** (2020): Added visual features and spatial-aware self-attention
- **LayoutLMv3** (2022): Unified text and image masking, removed CNN dependency, achieved SOTA on multiple Document AI benchmarks

**Practical Implications:** LayoutLMv3 remains a widely-used backbone for document understanding tasks. It is particularly strong for structured document extraction (forms, invoices, receipts) where spatial relationships between text regions matter.

### 3.2 Document Parsing Survey

- **Title:** Document Parsing Unveiled: Techniques, Challenges, and Prospects for Structured Data Extraction
- **Published:** arXiv:2410.21169, October 2024
- **Link:** [arxiv.org/abs/2410.21169](https://arxiv.org/abs/2410.21169)

**Key Contribution:** Comprehensive survey of document parsing techniques including layout analysis, table extraction, figure extraction, and how these integrate with large-scale language models for downstream tasks like document QA and information extraction.

**Notable finding:** Recent work (ColParse) demonstrates that document parsing models can generate compact layout-informed representations useful for retrieval, bridging the gap between structured parsing and visual retrieval paradigms.

---

## 4. OCR-Free Document Conversion Models

### 4.1 Nougat: Neural Optical Understanding for Academic Documents

- **Authors:** Lukas Blecher, Guillem Cucurull, Thomas Scialom, Robert Stojnic (Meta AI)
- **Published:** arXiv:2308.13418, August 2023
- **Link:** [arxiv.org/abs/2308.13418](https://arxiv.org/abs/2308.13418)

**Key Contribution:** A Visual Transformer model that converts images of scientific document pages directly into structured markup (Mathpix Markdown), without traditional OCR.

**Approach:** End-to-end encoder-decoder architecture. The encoder is a Swin Transformer that processes the page image; the decoder is a Transformer that autoregressively generates the markup language output. Trained on a large corpus of scientific papers paired with their LaTeX source.

**Results:**
- Successfully handles mathematical equations, tables, and complex formatting that traditional OCR struggles with
- Produces structured, machine-readable output directly from page images
- Particularly strong on academic/scientific documents

**Practical Implications:** Nougat is useful as a preprocessing step for RAG systems that need structured text from academic PDFs, especially those with heavy mathematical content. However, it can produce hallucinated or repetitive text for pages it has difficulty with.

### 4.2 Marker (PDF to Markdown)

- **Tool:** [github.com/VikParuchuri/marker](https://github.com/VikParuchuri/marker)
- **Related:** Surya OCR engine (same author)

**Key Contribution:** Open-source tool for high-quality PDF to Markdown conversion, using a pipeline of deep learning models (Surya for OCR + layout detection, plus heuristics for structure).

**Approach:** Combines OCR, layout analysis, reading order detection, and table recognition into a unified pipeline optimized for quality Markdown output. Unlike Nougat, Marker uses explicit OCR but with deep learning models for layout understanding.

**Practical Implications:** Widely used in RAG pipelines as a preprocessing step. Produces cleaner, more reliable output than Nougat for general-purpose documents, while Nougat excels specifically on academic papers with equations.

---

## 5. Multimodal Embedding Models

### 5.1 VLM2Vec: Training Vision-Language Models for Massive Multimodal Embedding Tasks

- **Authors:** Ziyan Jiang, Rui Meng, Xinyi Yang, Semih Yavuz, Yingbo Zhou, Wenhu Chen
- **Published:** arXiv:2410.05160, October 2024
- **Link:** [arxiv.org/abs/2410.05160](https://arxiv.org/abs/2410.05160)

**Key Contribution:** Demonstrates that VLMs can be converted into strong universal multimodal embedding models through instruction-tuned contrastive learning. Introduces the Massive Multimodal Embedding Benchmark (MMEB) with 36 datasets across 4 meta-task categories.

**Approach:** Uses Phi-3.5-V as a backbone, applies contrastive training with instruction-following across classification, VQA, retrieval, and grounding tasks. Deeply fuses visual and textual spaces rather than late-fusing separate encoders.

**Results:**
- 10-20% absolute improvement over CLIP, BLIP2, SigLIP, and other multimodal embedding models
- Strong generalization to unseen tasks through instruction following
- Demonstrates VLMs are "secretly strong embedding models"

### 5.2 VLM2Vec-V2: Advancing Multimodal Embedding for Videos, Images, and Visual Documents

- **Authors:** Rui Meng et al.
- **Published:** arXiv:2507.04590, July 2025
- **Link:** [arxiv.org/abs/2507.04590](https://arxiv.org/abs/2507.04590)

**Key Contribution:** Extends VLM2Vec to handle videos and visual documents (not just natural images), using Qwen2-VL as the backbone with native dynamic resolution support.

**Practical Implications:** Addresses a key gap -- most multimodal embedding models were trained on natural images and perform poorly on document images. VLM2Vec-V2 specifically targets this modality gap.

---

## 6. Multimodal RAG Architectures and Benchmarks

### 6.1 Survey: A Survey of Multimodal Retrieval-Augmented Generation

- **Authors:** Lang Mei, Siyu Mo, Zhihan Yang, Chong Chen
- **Published:** arXiv:2504.08748, March 2025
- **Link:** [arxiv.org/abs/2504.08748](https://arxiv.org/abs/2504.08748)

**Key Contribution:** Comprehensive survey of Multimodal RAG (MRAG), covering components, datasets, evaluation methods, and limitations.

**Key Findings:**
- There is a persistent **performance gap between multimodal and text-only retrieval**
- A new paradigm is emerging: **parallel textual + visual RAG** using OCR for text indexing and document screenshots for multimodal indexing, with results fused
- Multimodal RAG outperforms traditional text-only RAG especially in scenarios requiring both visual and textual understanding
- Planning strategies (fixed vs. adaptive) for handling multimodal queries are an active research area

### 6.2 Survey: Scaling Beyond Context -- Multimodal RAG for Document Understanding

- **Published:** arXiv:2510.15253, October 2025
- **Link:** [arxiv.org/abs/2510.15253](https://arxiv.org/abs/2510.15253)

**Key Contribution:** Survey focused specifically on document understanding through multimodal RAG, covering the shift from text-centric to visual approaches.

**Key Findings:**
- Multi-page documents are increasingly represented as image sequences for retrieval
- Finer-grained modeling within individual pages (tables, charts, structured elements) improves retrieval accuracy
- Text-based approaches have fundamental limitations in handling visually rich documents -- they fail to capture cross-modal cues and structural semantics

### 6.3 UniDoc-Bench: A Unified Benchmark for Document-Centric Multimodal RAG

- **Authors:** Xiangyu Peng, Can Qin, Zeyuan Chen, Ran Xu, Caiming Xiong, Chien-Sheng Wu (Salesforce)
- **Published:** arXiv:2510.03663, October 2025
- **Link:** [arxiv.org/abs/2510.03663](https://arxiv.org/abs/2510.03663)

**Key Contribution:** First large-scale realistic benchmark for multimodal RAG built from real-world PDF pages, supporting apples-to-apples comparison across four retrieval paradigms.

**Four paradigms compared:**
1. Text-only retrieval
2. Image-only retrieval
3. Multimodal text-image fusion retrieval
4. Multimodal joint retrieval (unified embedding)

**Key Finding:** **Multimodal text-image fusion RAG consistently outperforms both unimodal approaches and jointly multimodal embedding-based retrieval.** Neither text nor images alone are sufficient, and current multimodal embeddings remain inadequate for capturing both modalities effectively.

**Practical Implications:** The best current approach is to run text and visual retrieval in parallel and fuse results, rather than relying on a single unified multimodal embedding.

### 6.4 MMDocRAG: Benchmarking Retrieval-Augmented Multimodal Generation for Document QA

- **Authors:** Kuicai Dong, Yujing Chang, Shijie Huang, Yasheng Wang, Ruiming Tang, Yong Liu
- **Published:** NeurIPS 2025 (arXiv:2505.16470, May 2025)
- **Link:** [arxiv.org/abs/2505.16470](https://arxiv.org/abs/2505.16470)

**Key Contribution:** Comprehensive benchmark with 4,055 expert-annotated QA pairs featuring multi-page, cross-modal evidence chains, evaluated with 60 VLM/LLM models and 14 retrieval systems.

**Key Findings:**
- Advanced proprietary LVMs (GPT-4o, Claude) show superior performance over open-source alternatives
- Proprietary models show **moderate advantages** using multimodal inputs over text-only
- Open-source alternatives show **significant performance degradation** with multimodal inputs
- Fine-tuned LLMs achieve substantial improvements when using **detailed image descriptions** as a proxy for visual content

**Practical Implications:** For open-source deployments, converting images to detailed text descriptions (via captioning) may outperform directly passing images to the generator. This "describe then reason" pattern is a practical workaround for weaker visual understanding.

### 6.5 Augmentation Strategies in Multi-modal RAG

- **Published:** arXiv:2512.16802, December 2025
- **Link:** [arxiv.org/abs/2512.16802](https://arxiv.org/abs/2512.16802)

**Key Finding on ColPali in RAG:** ColFlor (a smaller/faster variant) matched ColPali while being far smaller and faster. With stronger generator models (GPT-4o), ColPali-based visual retrieval becomes competitive with text-based approaches. However, **with weaker generators, conversion to text lowers the burden on the generator** -- OCR-free pipelines require the LLM to effectively "read" the image, which many models do poorly.

---

## 7. Key Benchmarks

| Benchmark | Focus | Key Property |
|-----------|-------|-------------|
| **ViDoRe** | Visual document retrieval | Page-level retrieval across domains, languages; introduced with ColPali |
| **MMEB** | Multimodal embedding | 36 datasets across classification, VQA, retrieval, grounding; introduced with VLM2Vec |
| **UniDoc-Bench** | Document-centric multimodal RAG | Real-world PDFs, 4 retrieval paradigms, human-validated QA pairs |
| **MMDocRAG** | Document QA with multimodal RAG | 4,055 expert-annotated QA pairs, cross-modal evidence chains |
| **MIRACL-VISION** | Multilingual visual document retrieval | Extends ViDoRe to multilingual settings |
| **BBox-DocVQA** | Spatially-grounded document QA | Ground-truth bounding boxes for sub-page localization evaluation |

---

## 8. Synthesis: Current State and Practical Guidance

### What works best today (ranked by approach)

1. **Parallel text + visual retrieval with fusion** is the strongest overall approach for document RAG. Extract text via OCR/parsing AND embed pages as images, retrieve from both, fuse results.

2. **ColPali/ColQwen late-interaction retrieval** is the strongest standalone visual retriever. Best for document collections with heavy visual content (infographics, charts, complex layouts). Requires multi-vector storage.

3. **Traditional text extraction + dense retrieval** remains competitive for text-heavy documents with simple layouts. Cheaper and simpler to deploy.

4. **VisRAG-style end-to-end visual pipelines** are conceptually elegant but depend heavily on the generator model's visual understanding capabilities.

### Key trade-offs

| Dimension | Visual Retrieval (ColPali) | Text Retrieval (OCR-based) | Hybrid Fusion |
|-----------|---------------------------|---------------------------|---------------|
| Setup complexity | Simple (no OCR needed) | Complex (OCR + parsing + chunking) | Most complex |
| Storage | High (multi-vector per page) | Lower (single vector per chunk) | Highest |
| Visual content handling | Excellent | Poor | Excellent |
| Text-heavy documents | Good | Excellent | Excellent |
| Generator requirements | Needs strong VLM | Any LLM works | Depends on fusion |
| Latency | Fast retrieval, heavier indexing | Standard | Higher |

### Open problems

- **Sub-page granularity:** ColPali operates at page level; Snappy and ColParse are early attempts at finer-grained visual retrieval
- **Multimodal embedding quality:** Current unified embeddings (single vector for text + image) underperform fusion approaches ([UniDoc-Bench](https://arxiv.org/abs/2510.03663))
- **Open-source generation gap:** Open-source VLMs significantly underperform proprietary ones when reasoning over visual document content ([MMDocRAG](https://arxiv.org/abs/2505.16470))
- **Computational cost of late interaction:** Multi-vector storage and matching is expensive at scale; compression and approximation methods needed
- **Multilingual visual retrieval:** MIRACL-VISION highlights that visual retrieval models still underperform on non-English documents
