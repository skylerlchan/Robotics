# PDF to Markdown Conversion & Multimodal RAG Pipeline Research

*Created: April 21, 2026*

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [PDF to Markdown Conversion Tools](#pdf-to-markdown-conversion-tools)
3. [Multimodal RAG Architectures](#multimodal-rag-architectures)
4. [Visual Document Retrieval (ColPali/ColQwen)](#visual-document-retrieval-colpalicolqwen)
5. [Multimodal Embedding Models](#multimodal-embedding-models)
6. [Image Handling Strategies for RAG](#image-handling-strategies-for-rag)
7. [End-to-End Pipeline Recommendations](#end-to-end-pipeline-recommendations)
8. [Code Examples](#code-examples)
9. [Decision Framework](#decision-framework)

---

## Executive Summary

The PDF-to-Markdown-to-RAG pipeline has matured significantly through 2025-2026. The field has bifurcated into two fundamentally different paradigms:

**Paradigm 1 -- Parse-then-Embed (Traditional):** Extract text and images from PDFs into markdown, chunk them, embed separately, store in vector DB. Tools: Marker, Docling, MinerU, PyMuPDF4LLM.

**Paradigm 2 -- Vision-First (Emerging):** Treat entire PDF pages as images, embed them directly using vision-language models, skip OCR entirely. Tools: ColPali/ColQwen, Byaldi, Nomic Embed Multimodal, Gemini Embedding 2.

The best current approach for most use cases is a **hybrid pipeline**: use a strong parser (Marker or Docling) for text extraction, extract images as separate assets, generate image descriptions via VLM, and use either multimodal embeddings or dual-index retrieval for search. For document types heavy on charts/figures/tables where layout matters, the vision-first approach via ColPali/ColQwen is increasingly competitive and dramatically simpler.

---

## PDF to Markdown Conversion Tools

### Head-to-Head Comparison

| Feature | Marker | Docling | MinerU | pdf-craft | PyMuPDF4LLM |
|---|---|---|---|---|---|
| **GitHub Stars** | 19K+ | 20K+ | 30K+ | 4.6K | 2K+ |
| **OCR Engine** | Surya | Custom | PaddleOCR | DeepSeek | None |
| **GPU Required** | No (optional) | No (optional) | Recommended | Yes | No |
| **Scanned PDFs** | Yes | Yes | Yes | Yes (specialized) | No |
| **Multi-format** | PDF, DOCX, PPTX, EPUB, images | PDF, DOCX, PPTX, HTML, audio | PDF | PDF | PDF |
| **Tables** | Good | Good | Excellent | Basic | Basic |
| **Formulas** | Good | Basic | Good | Good | No |
| **LLM Boost** | Optional `--use_llm` | No | No | No | No |
| **Image Extraction** | Extracts + preserves | Extracts + preserves | Extracts as PNGs | Screenshots | References only |
| **RAG Integration** | JSON/chunks output | LlamaIndex, LangChain native | JSON output | None | Basic |
| **Speed (native PDF)** | Fast | Moderate | Moderate | N/A | Fastest |
| **CJK Support** | Good | Good | Excellent | Good | Basic |

Source: [themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)

### 1. Marker (datalab-to/marker)

**The all-rounder and safest default choice.**

Marker converts PDFs, images, DOCX, PPTX, XLSX, HTML, and EPUB to Markdown, JSON, or chunks. Uses Surya OCR for text recognition. Supports GPU, CPU, and Apple MPS ([PyPI](https://pypi.org/project/marker-pdf/)).

Key differentiator: the optional `--use_llm` flag layers an LLM on top for accuracy-critical documents. On the FinTabNet benchmark, `--use_llm` provides a 9.1-point accuracy lift over base Marker for table extraction ([IDP-Software](https://idp-software.com/vendors/datalab/)).

**Image handling:** Marker extracts images and preserves them as separate files referenced in the markdown output. However, community reports note that Marker can sometimes skip images, particularly when images are embedded in complex layouts ([Reddit r/Rag](https://www.reddit.com/r/Rag/comments/1m7gsvp/struggling_with_image_extraction_while_pdf_parsing/)). The JSON output mode preserves image bounding box coordinates and page metadata, which is useful for maintaining image-text context linkage.

**Throughput:** ~25 pages/sec on H100 in batch mode ([themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)).

**Best for:** General-purpose conversion, multi-format pipelines, teams wanting one tool for everything.

### 2. Docling (docling-project/docling)

**The enterprise RAG pick.**

Built by IBM Research, under the Linux Foundation AI umbrella. Outputs a structured `DoclingDocument` format that preserves semantic hierarchy -- not just text, but the meaning of document structure ([Docling docs](https://docling-project.github.io/docling/examples/)).

Uses DocLayNet for layout analysis and TableFormer for table recognition ([Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/03/enhancing-multimodal-rag-capabilities-using-docling/)). First-class integrations with LlamaIndex, LangChain, and Haystack. Examples include RAG pipelines with Milvus, Weaviate, and Qdrant as vector stores.

**Image handling:** Docling extracts figures and tables as separate assets and maintains their document position metadata. The structured `DoclingDocument` format preserves which images belong to which sections, enabling context-aware chunking. However, community feedback notes that "images rarely end up in the right context window let alone the right structured location" ([Reddit r/LangChain](https://www.reddit.com/r/LangChain/comments/1iu0ru4/whats_the_best_pdf_extractor_for_rag_llamaparse/)).

**Best for:** Enterprise document processing, teams in the LlamaIndex/LangChain ecosystem, structured extraction.

### 3. MinerU (opendatalab/MinerU)

**The heavy hitter for complex layouts.**

Highest GitHub stars (30K+). Built by OpenDataLab (Shanghai AI Lab). Uses PaddleOCR and custom layout detection models. Exceptional at CJK content and complex academic papers ([themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)).

**Image handling:** MinerU treats non-text elements (charts, graphs, diagrams) as visual components and extracts them as cropped PNG screenshots. This separation -- text bucket + image bucket -- is the foundation of the RAG-Anything pipeline, which uses MinerU as its default parser ([mejba.me](https://www.mejba.me/blog/rag-anything-multimodal-rag-guide)).

**Best for:** CJK documents, complex academic papers, the RAG-Anything framework.

### 4. PyMuPDF4LLM

**The lightweight, zero-ML option.**

No ML models, no GPU, no heavy dependencies. Fastest option for native (non-scanned) PDFs with embedded text. Just `pip install pymupdf4llm`. Detects headers, paragraphs, tables, and images using PyMuPDF's layout engine ([themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)).

**Image handling:** References images in markdown but does not perform OCR on them. Useless for scanned documents.

**Best for:** Quick extraction from native PDFs, CPU-only environments, preprocessing before feeding to an LLM.

### 5. LlamaParse (commercial)

**The managed/API option.**

Part of the LlamaIndex ecosystem. Uses "Agentic OCR" -- vision + LLM-driven parsing to interpret structure. Handles charts, tables, images, handwriting ([LlamaIndex](https://www.llamaindex.ai/insights/best-image-to-text-converter)). Community reports indicate it handles tables better than Docling in some cases ([Reddit r/LangChain](https://www.reddit.com/r/LangChain/comments/1iu0ru4/whats_the_best_pdf_extractor_for_rag_llamaparse/)).

**Trade-off:** Not open-source, requires API calls, costs money at scale.

### 6. Direct VLM Parsing (Gemini 2.0 / GPT-4o)

An increasingly popular approach: skip dedicated PDF parsers entirely and send each page as an image to a frontier VLM. Gemini 2.0 Flash is a common choice for cost-effective parsing at scale ([Reddit r/LangChain](https://www.reddit.com/r/LangChain/comments/1iu0ru4/whats_the_best_pdf_extractor_for_rag_llamaparse/)). The VLM returns structured markdown with image descriptions inline.

**Trade-off:** API cost per page, latency, not fully local/private.

---

## Multimodal RAG Architectures

There are three primary architectural patterns emerging for handling PDFs with both text and images in RAG:

### Architecture 1: Parse + Describe + Dual-Index

The most common production pattern. Extract text and images separately, generate text descriptions of images using a VLM, embed both text chunks and image descriptions, retrieve from a unified index.

**Pipeline:**
1. Parse PDF with Marker/Docling/MinerU
2. Extract images as separate files
3. Send each image to VLM (GPT-4o, Claude, Gemini) for rich text description
4. Chunk text, embed text chunks
5. Embed image descriptions (optionally also embed raw images with CLIP)
6. Store everything in vector DB with metadata linking images to source pages
7. At query time, retrieve relevant chunks; if an image description matches, return the actual image alongside the text answer

**Used by:** Unstructured.io's multimodal RAG pipeline ([Unstructured blog](https://unstructured.io/blog/multimodal-rag-enhancing-rag-outputs-with-image-results)), LangChain's multi-vector retriever ([LangChain blog](https://blog.langchain.com/semi-structured-multi-modal-rag/)).

**Pros:** Mature tooling, works with any embedding model, images are genuinely searchable via their descriptions.
**Cons:** VLM description cost, descriptions can lose nuance, two-step process.

### Architecture 2: Vision-First Retrieval (ColPali / ColQwen)

Treat PDF pages as images. Embed entire pages using a vision-language model. Retrieve pages based on visual similarity to the query, then send retrieved page images + query to a VLM for answer generation.

**Pipeline:**
1. Convert PDF pages to images
2. Embed each page image using ColQwen2/ColPali (multi-vector embeddings)
3. Store page embeddings in Qdrant (with MaxSim multi-vector comparison)
4. At query time, embed the text query, find most similar pages
5. Send retrieved page images + query to a VLM (Qwen2-VL, Claude, GPT-4o) for answer generation

**Used by:** HuggingFace cookbook pipeline ([HuggingFace](https://huggingface.co/learn/cookbook/en/multimodal_rag_using_document_retrieval_and_reranker_and_vlms)), DecodingAI's ColPali RAG web app ([DecodingAI](https://www.decodingai.com/p/the-king-of-multi-modal-rag-colpali)).

**Pros:** No OCR pipeline needed, preserves all visual information (tables, charts, layout), dramatically simpler architecture.
**Cons:** Requires GPU for embedding, page-level granularity (not paragraph-level), storage-heavy due to multi-vector embeddings.

### Architecture 3: Dual-Pipeline with Knowledge Graph (RAG-Anything)

The most comprehensive approach. Parse documents into text and image buckets. Process each through parallel pipelines for entity extraction and embedding. Merge into a unified knowledge graph + vector index.

**Pipeline:**
1. MinerU (or Docling) parses PDF into text bucket + image bucket
2. Text pipeline: LLM extracts entities/relationships, text chunks get embedded
3. Image pipeline: VLM analyzes each image, extracts entities/relationships from visual content, generates descriptions that get embedded
4. Merge both into unified knowledge graph (nodes + edges) and unified vector DB
5. Hybrid retrieval: vector similarity + graph traversal

**Used by:** RAG-Anything (HKUDS/HKU, built on LightRAG) ([GitHub](https://github.com/HKUDS/RAG-Anything)), integrates with Milvus ([Milvus blog](https://milvus.io/blog/multimodal-rag-made-simple-rag-anything-milvus-instead-of-20-separate-tools.md)).

**Pros:** Most thorough understanding of document content, cross-modal entity linking, handles the most complex documents.
**Cons:** Highest complexity, highest cost (every image goes through VLM), requires knowledge graph infrastructure.

### Architecture 4: Native Multimodal Embeddings

The newest approach. Use a single embedding model that natively handles text, images, and PDFs in a unified vector space. No separate image description step needed.

**Pipeline:**
1. Parse PDF into chunks (text + images)
2. Embed everything with Gemini Embedding 2 (supports text, images, PDFs natively)
3. Store in single vector index
4. Query with text, retrieve the most similar content across all modalities

**Used by:** Early adopters using Gemini Embedding 2 ([Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-embedding-2/)).

**Pros:** Simplest possible architecture, true cross-modal search.
**Cons:** API-dependent (Gemini), still in preview, limited to 6 pages per PDF embedding request.

---

## Visual Document Retrieval (ColPali/ColQwen)

### What is ColPali?

ColPali ([arxiv 2407.01449](https://arxiv.org/abs/2407.01449)) represents a fundamental paradigm shift: instead of extracting text from documents, it feeds document images directly to a Vision-Language Model. The model splits each image into patches, processes them through a vision transformer, and generates contextualized multi-vector embeddings that capture both textual content and spatial relationships.

Key insight: during indexing, the vision transformer encodes document images by splitting them into patches, which become "soft" tokens for the language model. This produces high-quality contextualized patch embeddings. These are then projected to 128 dimensions for efficient storage, creating multi-vector document representations ([DecodingAI](https://www.decodingai.com/p/the-king-of-multi-modal-rag-colpali)).

### Model Evolution

| Model | Base VLM | When | Performance (ViDoRe) |
|---|---|---|---|
| ColPali v1.2 | PaliGemma-3B | Mid 2024 | Baseline |
| ColQwen2 v1.0 | Qwen2-VL | Late 2024 | Significant improvement |
| ColQwen2.5 v0.2 | Qwen2.5-VL | 2025 | Current recommended |
| ColSmol | SmolVLM | 2025 | Lighter weight option |
| ColNomic Embed 7B | Nomic | April 2025 | 62.7 NDCG@5 on ViDoRe-v2, SOTA |

Source: [GitHub illuin-tech/colpali](https://github.com/illuin-tech/colpali), [Nomic](https://www.nomic.ai/news/nomic-embed-multimodal)

### Byaldi -- The Simple Wrapper

[Byaldi](https://github.com/AnswerDotAI/byaldi) (by Answer.AI) provides a RAGatouille-style API for ColPali models:

```python
from byaldi import RAGMultiModalModel

RAG = RAGMultiModalModel.from_pretrained("vidore/colqwen2-v1.0")
RAG.index(input_path="docs/", index_name="my_index")
results = RAG.search("What were Q3 revenue trends?", k=5)
```

### ColiVara -- Hosted API

[ColiVara](https://github.com/nomic-ai/colpali) provides a retrieval API that allows storing, searching, and retrieving documents based on their visual embeddings. Web-first implementation of ColPali using ColQwen2 ([GitHub](https://github.com/nomic-ai/colpali)).

### When to Use ColPali vs Traditional Parsing

**Use ColPali when:**
- Documents are visually rich (charts, tables, diagrams dominate)
- Page-level retrieval granularity is acceptable
- You want to avoid complex OCR pipelines
- You have GPU resources for embedding

**Use traditional parsing when:**
- You need paragraph-level or sentence-level retrieval
- Documents are primarily text
- You need to extract and reuse specific text passages
- You are running on CPU only

---

## Multimodal Embedding Models

### Gemini Embedding 2 (March 2026)

Google's first natively multimodal embedding model. Maps text, images, video, audio, and documents into a single unified 3072-dimensional embedding space ([Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-embedding-2/)).

- **Text:** up to 8192 input tokens
- **Images:** up to 6 images per request (PNG, JPEG)
- **Video:** up to 120 seconds (MP4, MOV)
- **Audio:** native audio embedding without transcription
- **Documents:** directly embed PDFs up to 6 pages
- **Interleaved input:** pass multiple modalities in a single request
- **Matryoshka dimensions:** 3072, 1536, 768

Real-world results: Paramount Skydance achieved 85.3% text-to-video Recall@1. Sparkonomy saw semantic similarity scores for text-image and text-video pairs jump from 0.4 to 0.8 ([Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-embedding-2/)).

### Nomic Embed Multimodal (April 2025)

Open-source multimodal embedding model from Nomic. Achieves state-of-the-art on ViDoRe-v2 visual document retrieval benchmark ([Nomic](https://www.nomic.ai/news/nomic-embed-multimodal)).

- **ColNomic Embed Multimodal 7B:** 62.7 NDCG@5 on ViDoRe-v2 (+2.8 over previous SOTA)
- **Nomic Embed Multimodal 7B:** single-vector model for RAG workflows
- **3B variants:** lighter weight options
- Processes interleaved text, images, and screenshots

Key advantage: fully open-source, runs locally, Apache 2.0 license ([HuggingFace](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b)).

### CLIP and Variants

Still widely used for image-specific embedding. The standard approach for Architecture 1 (Parse + Describe + Dual-Index):
- Embed images with CLIP, embed text descriptions with a text embedding model
- Or use CLIP for both text and image in a shared space
- Retrieve using similarity search across both ([LangChain blog](https://blog.langchain.com/semi-structured-multi-modal-rag/))

**Limitation:** CLIP's text understanding is weaker than dedicated text embedding models. Multi-modal embeddings like Gemini Embedding 2 and Nomic Embed are closing this gap.

### Comparison

| Model | Open Source | Modalities | Dimensions | Local | Best Use |
|---|---|---|---|---|---|
| Gemini Embedding 2 | No (API) | Text, Image, Video, Audio, PDF | 3072 | No | Cross-modal search, simplest pipeline |
| Nomic Embed Multimodal 7B | Yes (Apache 2.0) | Text, Image, PDF | Varies | Yes | Open-source visual doc retrieval |
| ColQwen2.5 | Yes | Document images | 128 (multi-vector) | Yes | Page-level visual retrieval |
| CLIP (ViT-L/14) | Yes | Text, Image | 768 | Yes | Image-text matching, legacy |
| OpenAI text-embedding-3-large | No (API) | Text only | 3072 | No | Text-only RAG (pair with CLIP for images) |

---

## Image Handling Strategies for RAG

The core challenge: how do you make images inside PDFs searchable and retrievable? Here are the current approaches ranked by sophistication:

### Strategy 1: VLM Description + Text Embedding (Most Common)

Extract images, send to VLM for description, embed the descriptions as text.

```
Image -> GPT-4o/Claude/Gemini -> "Bar chart showing Q3 revenue of $3.1M..." -> text-embedding-3-large -> vector DB
```

**Pros:** Works with any text embedding model, descriptions are human-readable.
**Cons:** Descriptions can miss nuance, VLM API cost per image, lossy transformation.

This is the approach used by Unstructured.io: "leverage frontier multimodal LLMs to generate detailed image descriptions. These descriptions can then be seamlessly integrated into RAG workflows. When one of these image descriptions appears in a retrieved chunk, recreate the image using the base64 encoding stored in the chunk's metadata" ([Unstructured](https://unstructured.io/blog/multimodal-rag-enhancing-rag-outputs-with-image-results)).

### Strategy 2: Dual Embedding (CLIP + Text)

Embed images directly with CLIP and text with a text model. Store both in same vector DB with metadata.

```
Image -> CLIP -> image_embedding -> vector DB (with base64 image in metadata)
Text  -> text-embedding -> text_embedding -> vector DB
```

**Pros:** No VLM cost per image, captures visual features directly.
**Cons:** CLIP-text alignment imperfect, harder to debug what was matched.

### Strategy 3: Native Multimodal Embedding

Use Gemini Embedding 2 or Nomic Embed Multimodal to embed text and images in the same space natively.

```
Image -> Gemini Embedding 2 -> vector -> vector DB
Text  -> Gemini Embedding 2 -> vector -> vector DB
Query -> Gemini Embedding 2 -> vector -> similarity search across both
```

**Pros:** Simplest architecture, true cross-modal search, no separate image processing.
**Cons:** API dependency (Gemini), newer and less battle-tested, Gemini limited to 6 pages per PDF request.

### Strategy 4: Page-Level Visual Embedding (ColPali)

Skip image extraction entirely. Embed whole pages as images.

```
PDF page -> ColQwen2 -> multi-vector page embedding -> Qdrant (MaxSim)
Query -> ColQwen2 -> query embedding -> find most similar pages
```

**Pros:** Preserves ALL visual context, no parsing pipeline needed.
**Cons:** Page-level granularity only, requires GPU, heavier storage.

### Preserving Image Context

Regardless of strategy, preserving the relationship between images and their surrounding text is critical:

- **Caption extraction:** Extract figure captions and keep them linked to the image
- **Surrounding text windows:** Include N sentences before/after an image reference in the image's metadata
- **Section awareness:** Tag images with their document section/heading hierarchy
- **Bounding box metadata:** Store page coordinates for spatial context ([customgpt.ai](https://customgpt.ai/rag-chunking-strategies/))

Best practice from the NASA offline RAG pipeline: "PDFs -> Docling -> super clean Markdown + extracted figures as separate PNGs. Every image/figure -> MiniCPM-V-2.6 (local 4090) -> rich textual descriptions. All text (original MD + vision captions + audio transcripts) become chunks in the same index" ([Reddit r/Rag](https://www.reddit.com/r/Rag/comments/1oyt2n1/fully_offline_multimodal_rag_for_nasa_life/)).

---

## End-to-End Pipeline Recommendations

### Recommended Pipeline: Production Multimodal RAG

For a production-quality system that handles text AND images from PDFs:

```
PDF Documents
    |
    v
[Marker (--use_llm) or Docling]  -- Parse to Markdown + extract images
    |
    +---> Text chunks (with section metadata)
    |        |
    |        v
    |     [text-embedding-3-large or BGE-M3]
    |        |
    |        v
    |     Vector DB (text index)
    |
    +---> Extracted images (with captions + surrounding text)
             |
             v
          [GPT-4o / Claude / Gemini Flash] -- Generate rich descriptions
             |
             +---> Image descriptions -> embed -> Vector DB (text index, same collection)
             +---> Base64 images -> stored as metadata for display

Query Time:
    Query -> embed -> search unified index
    Retrieved chunks (text + image descriptions)
    If image description in results -> include actual image
    Send query + context (text + images) -> VLM -> answer
```

### Recommended Pipeline: Simple/Fast Multimodal RAG

For a simpler system where speed and simplicity matter more:

```
PDF Documents
    |
    v
[pdf2image] -- Convert each page to image
    |
    v
[ColQwen2.5 via Byaldi] -- Embed page images
    |
    v
[Qdrant] -- Store multi-vector embeddings

Query Time:
    Query -> ColQwen2.5 -> find top-k pages
    (Optional) Reranker (MonoQwen2-VL) -> refine results
    Top pages + query -> Qwen2-VL / Claude / GPT-4o -> answer
```

### Recommended Pipeline: Fully Local/Offline

For maximum privacy and no API dependencies:

```
PDF Documents
    |
    v
[MinerU] -- Parse to text + image buckets (fully local)
    |
    +---> Text -> [BGE-M3 or Nomic Embed] -> local vector DB (Qdrant, Milvus, ChromaDB)
    +---> Images -> [MiniCPM-V-2.6 or Qwen2-VL local] -> descriptions -> embed -> same vector DB

Query Time:
    Query -> embed -> search -> local LLM (Llama 3, Mistral) -> answer
```

This is the approach validated by the NASA Life Sciences offline RAG project ([Reddit r/Rag](https://www.reddit.com/r/Rag/comments/1oyt2n1/fully_offline_multimodal_rag_for_nasa_life/)).

### Recommended Pipeline: Maximum Comprehension (Knowledge Graph)

For the most thorough understanding of complex multimodal documents:

```
pip install raganything

PDF Documents
    |
    v
[RAG-Anything (MinerU 2.0 backend)]
    |
    +---> Text pipeline: entity extraction -> knowledge graph + embeddings
    +---> Image pipeline: VLM analysis -> entity extraction -> knowledge graph + embeddings
    |
    v
[Merged knowledge graph + unified vector index]

Query Time:
    Query -> hybrid retrieval (vector + graph traversal) -> LLM -> answer
```

Source: [RAG-Anything GitHub](https://github.com/HKUDS/RAG-Anything)

---

## Code Examples

### Example 1: Marker to Markdown with Image Extraction

```bash
pip install marker-pdf
```

```python
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser

config = {"output_format": "json"}  # JSON preserves image references
config_parser = ConfigParser(config)
converter = PdfConverter(config=config_parser.generate_config_dict())

rendered = converter("document.pdf")
# rendered.markdown -- full markdown text
# rendered.images -- dict of extracted images
# rendered.metadata -- table of contents, page info
```

For highest quality with LLM:
```bash
marker_single document.pdf --output_dir output/ --use_llm --output_format json
```

### Example 2: ColPali Visual Retrieval with Byaldi

```python
from byaldi import RAGMultiModalModel

# Load model
RAG = RAGMultiModalModel.from_pretrained("vidore/colqwen2-v1.0")

# Index documents (PDF pages converted to images internally)
RAG.index(
    input_path="documents/",
    index_name="my_docs",
    store_collection_with_index=False,
    overwrite=True
)

# Search
results = RAG.search("What were the revenue trends in Q3?", k=5)
for result in results:
    print(f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}")
```

### Example 3: ColQwen2 + Qdrant + Claude (Full Pipeline)

From the DecodingAI tutorial ([DecodingAI](https://www.decodingai.com/p/the-king-of-multi-modal-rag-colpali)):

```python
import torch
from colpali_engine.models import ColQwen2, ColQwen2Processor
from qdrant_client import QdrantClient, models
from transformers.utils.import_utils import is_flash_attn_2_available

# Load ColQwen2
model = ColQwen2.from_pretrained(
    "vidore/colqwen2-v1.0",
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
).eval()
processor = ColQwen2Processor.from_pretrained("vidore/colqwen2-v1.0")

# Set up Qdrant with multi-vector support
qdrant = QdrantClient(url="YOUR_QDRANT_URL", api_key="YOUR_KEY")
qdrant.create_collection(
    collection_name="pdf_pages",
    vectors_config=models.VectorParams(
        size=128,
        distance=models.Distance.COSINE,
        multivector_config=models.MultiVectorConfig(
            comparator=models.MultiVectorComparator.MAX_SIM
        ),
    )
)
```

### Example 4: Docling + LlamaIndex RAG

From the Docling documentation ([Docling docs](https://docling-project.github.io/docling/examples/rag_llamaindex/)):

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from docling.document_converter import DocumentConverter

# Convert PDF
converter = DocumentConverter()
doc = converter.convert("paper.pdf")

# Access structured content
for element in doc.document.body:
    if element.label == "figure":
        # Handle image
        image = element.image
        caption = element.caption
    elif element.label == "table":
        # Handle table
        table_md = element.export_to_markdown()
    else:
        # Handle text
        text = element.text
```

### Example 5: Gemini Embedding 2 Multimodal Search

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

# Embed a PDF page image
result = genai.embed_content(
    model="models/gemini-embedding-2-preview",
    content=[image_bytes],  # PIL Image or bytes
    task_type="RETRIEVAL_DOCUMENT"
)
image_embedding = result['embedding']  # 3072-dim vector

# Embed a text query
result = genai.embed_content(
    model="models/gemini-embedding-2-preview",
    content="What is the revenue breakdown?",
    task_type="RETRIEVAL_QUERY"
)
query_embedding = result['embedding']  # Same 3072-dim space

# Cosine similarity works across modalities
```

### Example 6: RAG-Anything Setup

```python
pip install raganything

from raganything import RAGAnything

rag = RAGAnything(
    working_dir="./rag_storage",
    llm_model="gpt-4o-mini",
    embedding_model="text-embedding-3-large",
    vlm_model="gpt-4o",  # For image understanding
)

# Ingest a multimodal PDF
rag.process_document("financial_report.pdf")

# Query across text and images
answer = rag.query("What were the revenue trends shown in the Q3 charts?")
```

---

## Decision Framework

### Choose Your Parser

```
Is the PDF native (selectable text)?
  YES -> Start with PyMuPDF4LLM (fastest, simplest)
         If quality insufficient -> upgrade to Marker
  NO (scanned) ->
    Is it a scanned book?
      YES -> pdf-craft (specialized)
      NO ->
        CJK content?
          YES -> MinerU (best CJK support)
          NO ->
            Need RAG framework integration?
              YES -> Docling (LlamaIndex/LangChain native)
              NO -> Marker (best all-rounder)
```

### Choose Your RAG Architecture

```
What matters most?

SIMPLICITY (fewest moving parts):
  -> ColPali/ColQwen via Byaldi + VLM for answer generation

PRECISION (paragraph-level text retrieval):
  -> Marker/Docling + text embeddings + VLM image descriptions

COMPREHENSION (complex multi-modal documents):
  -> RAG-Anything (MinerU + knowledge graph + dual pipeline)

PRIVACY (fully offline):
  -> MinerU + local VLM (MiniCPM-V / Qwen2-VL) + local embeddings (BGE-M3)

SIMPLEST POSSIBLE (API-OK):
  -> Gemini Embedding 2 (native multimodal embeddings, single model)
```

### Choose Your Image Embedding Strategy

```
Do images contain critical searchable content (charts, tables, diagrams)?
  YES ->
    GPU available?
      YES -> ColPali/ColQwen page-level visual embeddings
             OR VLM descriptions + text embeddings (more granular)
      NO  -> VLM descriptions (API) + text embeddings
  NO (decorative images) ->
    Skip image embedding, text-only RAG is fine
```

---

## Key Takeaways

1. **Marker is the safest default PDF parser** for most use cases. Use `--use_llm` for accuracy-critical documents.

2. **ColPali/ColQwen has changed the game** for visually-rich documents. If you care about charts, tables, and layout, the vision-first approach is dramatically simpler and increasingly competitive with traditional parsing.

3. **Gemini Embedding 2 is the biggest recent development** -- native multimodal embeddings in a unified space. Still in preview, but it simplifies the architecture to a single embedding model for text + images + PDFs.

4. **RAG-Anything is the most comprehensive open-source solution** for complex multimodal documents, combining MinerU parsing with knowledge graphs. High setup cost but highest comprehension.

5. **The "describe images with VLM" approach remains the most practical** for production systems. It works with any embedding model and any vector DB, and the descriptions serve as an interpretable intermediate representation.

6. **For fully offline/private pipelines**, the stack is: MinerU + MiniCPM-V or Qwen2-VL (local) + BGE-M3 or Nomic Embed (local) + Qdrant or ChromaDB (local). Validated by the NASA Life Sciences project.

7. **Context preservation is the hardest unsolved problem.** Even the best parsers struggle to reliably keep images in the right context window relative to surrounding text. Explicit metadata linking (section headers, captions, bounding boxes, surrounding text windows) is essential.

8. **Nomic Embed Multimodal** is the best open-source option for unified text/image embeddings, achieving state-of-the-art on ViDoRe-v2 with Apache 2.0 licensing.
