# PDF-to-Markdown Conversion with Image Processing for RAG/Semantic Search

## Landscape Research -- April 2026

This document compiles findings from X.com discussions, blog posts, and community conversations about the current state of PDF-to-Markdown conversion with image handling for RAG pipelines.

---

## 1. The Two Paradigms: Parse-Then-Embed vs. Visual Retrieval

The field has split into two fundamentally different approaches, and practitioners are increasingly vocal about which works better for different use cases.

### Paradigm A: Traditional Parse-Then-Embed

The standard pipeline: PDF -> parse text/tables/images -> convert to markdown -> chunk -> embed -> vector DB. Tools like Marker, Docling, MinerU, and PyMuPDF4LLM fall into this category.

### Paradigm B: Visual Retrieval (ColPali/ColQwen)

Skip OCR entirely. Screenshot each PDF page, embed the image directly using a vision-language model with late interaction scoring (ColBERT-style multi-vector), and retrieve pages visually. The ColPali family of models pioneered this.

**Key insight from the community:** These are not mutually exclusive. The leading production pipelines are increasingly hybrid -- using visual retrieval for search/ranking and traditional parsing for the generation step.

---

## 2. PDF-to-Markdown Parsers: What Practitioners Actually Use

### Tier 1: The Production-Ready Tools

#### Marker (by Datalab/Vik Paruchuri)

- **GitHub:** 19K+ stars
- **What it does:** Converts PDF, DOCX, PPTX, XLSX, HTML, EPUB to Markdown/JSON. Uses Surya OCR. Supports GPU, CPU, Apple MPS.
- **Key differentiator:** The `--use_llm` flag layers an LLM (e.g., Gemini Flash) on top for accuracy-critical documents. Without it, fast local conversion. With it, near-perfect output on messy layouts.
- **Performance:** ~25 pages/sec throughput on H100 in batch mode ([themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026))

Vik Paruchuri (@VikParuchuri) on X (Feb 2025):
> "We've improved marker (PDF -> markdown) a lot in 3 months -- accuracy and speed now beat llamaparse, mathpix, and docling. We shipped: LLM mode that augments marker with models like gemini flash, improved math w/inline math, links and references, better tables and forms." ([x.com](https://x.com/VikParuchuri/status/1892275032916713814))

Datalab (@datalabto) also announced **Marker Prompt API** and **Forge Parse** -- a playground to iterate and evaluate parsing quality, after processing 250M+ pages:
> "After processing 250M+ pages, we cracked the code on why LLMs fail at PDF parsing (and how to fix it). The secret sauce isn't prompting. It's purpose-built architecture." ([x.com](https://x.com/datalabto))

#### Docling (by IBM Research)

- **GitHub:** 20K+ stars
- **What it does:** Parses PDF, DOCX, PPTX, XLSX, HTML, images, audio. Outputs structured `DoclingDocument` format preserving semantic hierarchy.
- **Key differentiator:** First-class integrations with LlamaIndex, LangChain, Crew AI, Haystack. Linux Foundation AI project. Also supports VLMs (GraniteDocling) and MCP server for agentic use.
- **Best for:** Enterprise document processing, structured extraction

Kalyan KS (@kalyan_kpl) on X:
> "Docling is one of the most popular document parsers for LLM RAG. Docling extracts content from any of the documents (PDF, DOCX, PPTX, XLSX, Images, HTML, AsciiDoc & Markdown) and exports to HTML, Markdown and JSON." ([x.com](https://x.com/kalyan_kpl/status/1868572964792451270))

#### MinerU (by OpenDataLab/Shanghai AI Lab)

- **GitHub:** 30K+ stars (most starred tool in this category)
- **What it does:** PDF -> Markdown/JSON with advanced layout detection. Uses PaddleOCR. Supports NVIDIA, AMD, and a dozen Chinese accelerator platforms.
- **Key differentiator:** Best layout detection for complex documents, especially CJK content. MinerU 2.5 integrates with vLLM for high-throughput inference. Now integrated into RAGFlow as a parser option.
- **Real-world use:** Used in Intern-S1's training data pipeline -- "page-level PDF parsing with a hybrid OCR and VLM pipeline (MinerU + InternVL/Qwen-VL)" raised science content purity from ~2% to 50%. ([x.com](https://x.com/gm8xx8/status/1959222471183225033))

vLLM (@vllm_project) on X:
> "vLLM x MinerU: Document Parsing at Lightning Speed! MinerU 2.5 delivers: Instant parsing, deeper understanding for complex docs, optimized cost -- even consumer GPUs can fly." ([x.com](https://x.com/vllm_project/status/1976968858415005841))

#### PyMuPDF4LLM

- **GitHub:** 2K+ stars
- **What it does:** Thin extension of PyMuPDF for LLM-ready Markdown extraction. No ML models, no GPU.
- **Key differentiator:** Fastest option for native (non-scanned) PDFs. Zero dependencies beyond PyMuPDF.
- **Limitation:** No OCR -- useless for scanned documents, no formula recognition.

### Tier 2: Notable Alternatives

| Tool | Notes |
|------|-------|
| **pdf-craft** (4.6K stars) | Purpose-built for scanned books. Uses DeepSeek OCR. Fully local/offline. |
| **Nutrient pdf-to-markdown** | Commercial tool. On their 200-document hand-annotated benchmark, "beats out every other major parser for speed and reading order while matching accuracy." ([x.com](https://x.com/micLivs/status/2039773065542778909)) |
| **MarkItDown** (Microsoft, 91K stars) | Converts PDF, DOCX, PPTX, XLSX, images, audio, HTML, ZIP to markdown. Very popular but produces zero structured markdown (no headings, no tables) from complex documents. |
| **LlamaParse** | Commercial (LlamaIndex). Good but Marker claims to have surpassed it on accuracy/speed as of Feb 2025. |
| **Vision Parse** | Uses Vision LLMs (Gemini, Ollama, OpenAI) to parse PDFs to markdown. Novel VLM-first approach. |

### The Benchmark Reality Check

Jonathan Rhyne (@jdrhyne) ran the most rigorous public comparison, testing 7 parsers across 1,258 documents on 3 benchmarks (READoc, SCORE-Bench, internal pilot):

> "4 out of 7 'PDF to Markdown' tools produce zero structure markdown. Of those seven parsers, only three produced any markdown structure at all -- Nutrient pdf-to-markdown (265 headings, 398 table rows), pymupdf4llm (258 headings, 422 table rows), and docling (287 headings, 420 table rows). The other four -- markitdown (Microsoft, 91K GitHub stars), pypdf, markit-ai, and liteparse (LlamaIndex) -- produced zero headings and zero tables from a 245-page document packed with both." ([x.com](https://x.com/jdrhyne/status/2043521289550184917))

He also noted a critical gap:
> "I tested seven parsers. Zero extracted any figures. Not ours, not docling, not pymupdf4llm, not any of them."

His taxonomy of parsing approaches:
1. **Heuristic parsers** (PyMuPDF4LLM, Docling, Nutrient): Read PDF internal structure. No AI, no GPU. Milliseconds per doc. Zero hallucination. But nothing on scanned docs.
2. **Hybrid pipelines** (Marker, MinerU, Nutrient Vision): ML-based layout detection + rule-based extraction + specialized models for tables/formulas. Best balance of accuracy and determinism.
3. **Vision Language Models** (Gemini, GPT-4o as parser): Render each page as image, feed to VLM. Most flexible but slowest and can hallucinate.

---

## 3. The ColPali/ColQwen Revolution: Visual Retrieval Without OCR

This is the "paradigm shift" discussion dominating the space.

### What ColPali Does

ColPali uses a vision-language model (originally PaliGemma, later Qwen2-VL for ColQwen) to directly embed screenshots of PDF pages into multi-vector representations (like ColBERT). The query is embedded into the same space. Late-interaction scoring (MaxSim) finds relevant pages.

Manuel Faysse (@ManuelFaysse), ColPali creator, on X (July 2024):
> "Introducing 'ColPali: Efficient Document Retrieval with Vision Language Models'! We use Vision LLMs + late interaction to improve document retrieval (RAG, search engines, etc.), solely using the image representation of document pages!" ([x.com](https://x.com/ManuelFaysse/status/1808060330347524275))

Omar Khattab (@lateinteraction), ColBERT creator, endorsed it:
> "ColPali is a late interaction / ColBERT model that uses Vision LMs to index documents *visually* into multi-vector representations. Massive gains over converting documents to text or using Vision LMs without late interaction!" ([x.com](https://x.com/lateinteraction/status/1808133604679340270))

### The Key Benchmark Results

On the ViDoRe (Visual Document Retrieval) benchmark, ColPali achieved nDCG@5 of 81.3, compared to 65-75 for text-based retrieval (BM25 or BGE-M3) using industry-strength OCR pipelines ([Vespa Blog](https://blog.vespa.ai/retrieval-with-vision-language-models-colpali/)).

Jo Kristian Bergum (@jobergum), Vespa Chief Scientist, has been the most vocal advocate:
> "ColPali is probably one of the most significant innovations in complex document retrieval. Visual embeddings allow the inclusion of complex elements such as charts, tables, and figures without the complexity of OCR and ad-hoc extraction routines." ([x.com](https://x.com/jobergum/status/1812917815701074371))

> "GPT4o is more accurate with screenshots of the PDF than with OCR text. F1 30.5 to 44.9." ([x.com](https://x.com/jobergum/status/1813471636131074225))

### Evolution: ColQwen, ModernVBERT, and Nomic Embed Multimodal

The ColPali architecture has spawned a wave of successors:

- **ColQwen2**: Uses Qwen2-VL instead of PaliGemma. Leonie (@helloiamleonie) published a tutorial: "Multimodal RAG over PDFs with ColQwen2 (without any OCR, layout detection, or chunking)." ([x.com](https://x.com/helloiamleonie/status/1962482840810975527))

- **ModernVBERT**: Announced by Merve (@mervenoyann) -- "a super efficient vision-language retriever for documents. Most retrievers (like ColPali) base off of causal attention which is suboptimal for retrieving, so they train a dual encoder. ColModernVBERT gets +10.6 points in nDCG@5." Matches models 10x its size. ([x.com](https://x.com/mervenoyann/status/1974027641033261106))

- **Nomic Embed Multimodal 7B** (@nomic_ai): "Open source multimodal embedding models for text, images, PDFs, and charts. SOTA on visual document retrieval. Two variants (Colbert + dense models). Apache 2.0 License." ([x.com](https://x.com/nomic_ai/status/1907464719717327088))

- **vdr-2b-multi-v1** (LlamaIndex): Jerry Liu (@jerryjliu0) announced "a fully open-source visual embedding model for your most complex, multilingual documents. Produces single dense vectors for visual document retrieval, enabling efficient large-scale systems." ([x.com](https://x.com/jerryjliu0/status/1878491439291842618))

---

## 4. Multimodal Embedding Models: The New Frontier

Beyond ColPali-style retrieval, a new class of natively multimodal embedding models is emerging that can embed text, images, video, audio, and documents into a single vector space.

### Gemini Embedding 2

Google announced "the first fully multimodal embedding model built on the Gemini architecture. Provides semantic understanding across 100+ languages -- and support for modalities across text, images, video, audio and documents (PDFs) in a shared vector space." Can directly embed PDFs up to 6 pages long. ([x.com](https://x.com/googledevs/status/2031411032845885725))

### Voyage Multimodal-3

Voyage AI (@VoyageAI): "Most multimodal embedding models mimic CLIP and use separate networks for images & text. In contrast, voyage-multimodal-3 processes both text and visuals within the same transformer." ([x.com](https://x.com/VoyageAI/status/1856379552358154433))

---

## 5. End-to-End Multimodal RAG Frameworks

### RAG-Anything (HKUDS)

The most discussed new framework. Hit 5K+ GitHub stars in 3 months.

Chao Huang (@huang_chao4969):
> "The demand for Beyond Text, multi-modal RAG is HUGE! Modern documents are rich with images, tables, charts, and equations -- traditional text-only RAG just isn't enough anymore." ([x.com](https://x.com/huang_chao4969/status/1970172316211650567))

RAG-Anything wraps LightRAG with multimodal document processing:
- Uses MinerU for document parsing (splits into text and image buckets)
- Text gets OCR'd and embedded normally
- Images get captured as screenshots and processed by VLMs
- Both streams merge into a unified knowledge graph
- Supports 10+ document formats
- "Just several lines of code to get started" ([x.com](https://x.com/huang_chao4969/status/1960931876077756449))

From a detailed practitioner review ([mejba.me](https://www.mejba.me/blog/rag-anything-multimodal-rag-guide)):
> "I had a 47-page financial report. Scanned PDF. Bar charts on every other page. Revenue tables rendered as images. The kind of document that makes every RAG system shrug and say 'here's some garbled text I found between the headers.' [...] RAG Anything solves this in a fundamentally different way. Instead of treating images as an afterthought to be converted into text, it processes them as a first-class data type with their own embedding space."

### M3DocRAG (Bloomberg)

Bloomberg's multi-modal RAG framework that uses ColPali + Qwen2-VL for multi-page, multi-document understanding. Specifically handles charts, figures, and text. ([x.com](https://x.com/_reachsumit/status/1854742151210713270))

### ImageRAG

Combines ColPali's ColQwen image embeddings with Ollama LLaMA 3.2 Vision for a lightweight local multimodal RAG system with PDF support. ([x.com](https://x.com/kalyan_kpl/status/1860520658154979777))

---

## 6. The "Gemini Flash Just Solved PDF Parsing" Debate

One of the most contested claims in the space.

Deedy (@deedydas) on X (Feb 2025):
> "PDF parsing is pretty much solved at scale now. Gemini 2 Flash's $0.40/M tokens and 1M token context means you can now parse 6000 long PDFs at near perfect quality for $1." ([x.com](https://x.com/deedydas/status/1887556219080220683))

Google Cloud Tech shared a technique for using Gemini to generate markdown from PDFs "well-suited for indexing into a RAG datastore." ([x.com](https://x.com/GoogleCloudTech/status/1876329134080536880))

**Counterpoints from practitioners:**

Simon Willison (@simonw):
> "One disappointment with Gemini 2.0 Flash is that the maximum output tokens remains at just 8,192 (same as the 1.5 series) -- which limits its utility for whole-document transformation tasks like translation or PDF-to-Markdown." ([x.com](https://x.com/simonw/status/1867239706729316459))

Marker's approach (Vik Paruchuri) incorporates this insight -- the `--use_llm` flag uses Gemini Flash to augment (not replace) the core parsing pipeline, handling edge cases where heuristic parsing fails.

Real-world example: Amjad Masad (Replit CEO) used Gemini Flash to OCR the JFK Files into searchable text on GitHub. ([x.com](https://x.com/amasad/status/1902180507825377580))

---

## 7. Pain Points and Gotchas Practitioners Report

### Figure Extraction Remains Unsolved (for most tools)

Jonathan Rhyne's testing showed zero of seven parsers extracted figures. This is the single biggest gap in the current tool landscape. Visual retrieval (ColPali-style) sidesteps this entirely.

### Markdown Quality Varies Wildly

The Nutrient benchmark revealed that popular tools like Microsoft's MarkItDown (91K stars) produce "zero-structure" markdown -- no headings, no tables. Star count is not a proxy for quality.

> "Markdown is the right output format for this. It's 15% more token-efficient than JSON and 70-90% more efficient than HTML for the same content. LLMs were trained on markdown and understand it natively. Markdown headings create natural chunking boundaries for RAG." ([x.com](https://x.com/jdrhyne/status/2043521289550184917))

### Scanned vs. Native PDF: Completely Different Problems

- Native PDFs (selectable text): PyMuPDF4LLM works fine, no GPU needed
- Scanned PDFs: Require OCR pipeline (Marker, MinerU, Docling, or VLM approach)
- The workflow most developers actually have: "a mix of digital and scanned PDFs" -- hybrid pipelines are essential

### Cost at Scale

VLM-based parsing (sending every page through GPT-4o or Gemini) gets expensive fast. Marker's approach of using VLMs only for problem pages (the `--use_llm` flag as augmentation, not replacement) is the emerging best practice.

### Image Handling in Markdown

Even parsers that detect images often just leave `![image](path)` references. For RAG, you need either:
1. Image captions generated by a VLM (stored alongside text chunks)
2. Multimodal embeddings (embed the image directly)
3. Visual retrieval (ColPali-style, skip text entirely)

---

## 8. Recommended Approaches by Use Case

### Use Case 1: Simple PDF text extraction for RAG

**Recommended:** PyMuPDF4LLM (for native PDFs) or Marker (for mixed native/scanned)
- Fast, local, deterministic
- Pipe markdown output through your standard chunking/embedding pipeline

### Use Case 2: Complex documents with charts, tables, figures

**Recommended:** Hybrid approach
1. Parse with Marker (--use_llm) or MinerU for text + table extraction
2. Use ColPali/ColQwen for visual retrieval as a re-ranker or parallel retrieval path
3. Pass retrieved page screenshots to a VLM (GPT-4o, Gemini) at query time for generation

### Use Case 3: Enterprise-scale document processing

**Recommended:** Docling + RAG framework integration (LlamaIndex/LangChain)
- Structured DoclingDocument output preserves document semantics
- First-class framework integrations reduce glue code
- MinerU integration in RAGFlow is another option

### Use Case 4: Research papers / academic content

**Recommended:** MinerU (best layout detection, formula support) or Marker with LLM mode
- CJK content: MinerU is the clear winner
- Math-heavy: Marker's improved inline math support or MinerU

### Use Case 5: "I don't want to think about this"

**Recommended:** RAG-Anything
- Wraps MinerU + LightRAG with multimodal processing
- Handles text and images as first-class citizens
- Few lines of code to get a working pipeline

---

## 9. Key Takeaways

1. **The ColPali family is a genuine paradigm shift** for document retrieval. It eliminates the entire OCR/layout/chunking pipeline for the retrieval step. Multiple credible voices (Vespa, ColBERT creator, HuggingFace engineers) agree this is "one of the most significant innovations in complex document retrieval."

2. **For the generation step, you still need text.** ColPali finds the right page; then you need a VLM to read it or a parser to extract the content. The best production systems use ColPali for retrieval + traditional parsing for generation context.

3. **Marker is the current Swiss Army knife.** Most versatile, actively developed, and the LLM-augmentation approach (use Gemini Flash as a fallback, not a primary parser) is the smartest architecture for balancing cost, speed, and accuracy.

4. **Figure extraction is the biggest unsolved gap.** No parser reliably extracts and preserves figures with context. Visual retrieval bypasses this but doesn't give you structured data.

5. **Gemini Embedding 2 and Nomic Embed Multimodal are changing retrieval.** The ability to natively embed PDFs, images, and text into a shared vector space simplifies the pipeline dramatically.

6. **Markdown is the right output format for LLMs.** 15% more token-efficient than JSON, 70-90% more than HTML. Headings create natural chunk boundaries.

7. **Most popular tools are not the best tools.** Microsoft's MarkItDown has 91K stars but produces zero-structure markdown. Always benchmark on your actual documents.

---

## Sources

### X.com Posts Referenced
- Manuel Faysse (ColPali creator): [x.com/ManuelFaysse/status/1808060330347524275](https://x.com/ManuelFaysse/status/1808060330347524275)
- Omar Khattab (ColBERT creator): [x.com/lateinteraction/status/1808133604679340270](https://x.com/lateinteraction/status/1808133604679340270)
- Jo Kristian Bergum (Vespa): [x.com/jobergum/status/1812917815701074371](https://x.com/jobergum/status/1812917815701074371)
- Vik Paruchuri (Marker): [x.com/VikParuchuri/status/1892275032916713814](https://x.com/VikParuchuri/status/1892275032916713814)
- Jonathan Rhyne (benchmark): [x.com/jdrhyne/status/2043521289550184917](https://x.com/jdrhyne/status/2043521289550184917)
- Leonie (ColQwen2 tutorial): [x.com/helloiamleonie/status/1962482840810975527](https://x.com/helloiamleonie/status/1962482840810975527)
- Merve (ModernVBERT): [x.com/mervenoyann/status/1974027641033261106](https://x.com/mervenoyann/status/1974027641033261106)
- Nomic AI: [x.com/nomic_ai/status/1907464719717327088](https://x.com/nomic_ai/status/1907464719717327088)
- Jerry Liu (vdr-2b-multi): [x.com/jerryjliu0/status/1878491439291842618](https://x.com/jerryjliu0/status/1878491439291842618)
- Deedy (Gemini Flash): [x.com/deedydas/status/1887556219080220683](https://x.com/deedydas/status/1887556219080220683)
- Simon Willison (Gemini limitation): [x.com/simonw/status/1867239706729316459](https://x.com/simonw/status/1867239706729316459)
- Google Devs (Gemini Embedding 2): [x.com/googledevs/status/2031411032845885725](https://x.com/googledevs/status/2031411032845885725)
- Chao Huang (RAG-Anything): [x.com/huang_chao4969/status/1970172316211650567](https://x.com/huang_chao4969/status/1970172316211650567)
- Kalyan KS (Docling): [x.com/kalyan_kpl/status/1868572964792451270](https://x.com/kalyan_kpl/status/1868572964792451270)
- vLLM (MinerU): [x.com/vllm_project/status/1976968858415005841](https://x.com/vllm_project/status/1976968858415005841)
- Datalab (Marker Prompt API): [x.com/datalabto](https://x.com/datalabto)
- Voyage AI: [x.com/VoyageAI/status/1856379552358154433](https://x.com/VoyageAI/status/1856379552358154433)
- Google Cloud Tech: [x.com/GoogleCloudTech/status/1876329134080536880](https://x.com/GoogleCloudTech/status/1876329134080536880)
- Amjad Masad (JFK Files): [x.com/amasad/status/1902180507825377580](https://x.com/amasad/status/1902180507825377580)

### Blog Posts & Articles
- Vespa Blog -- ColPali retrieval: [blog.vespa.ai/retrieval-with-vision-language-models-colpali](https://blog.vespa.ai/retrieval-with-vision-language-models-colpali/)
- Menon Lab -- PDF-to-Markdown tools comparison 2026: [themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)
- Mejba Ahmed -- RAG-Anything guide: [mejba.me](https://www.mejba.me/blog/rag-anything-multimodal-rag-guide)

### GitHub Repositories
- Marker: [github.com/VikParuchuri/marker](https://github.com/VikParuchuri/marker)
- Docling: [github.com/docling-project/docling](https://github.com/docling-project/docling)
- MinerU: [github.com/opendatalab/MinerU](https://github.com/opendatalab/MinerU)
- RAG-Anything: [github.com/HKUDS/RAG-Anything](https://github.com/HKUDS/RAG-Anything)
- PyMuPDF4LLM: [github.com/pymupdf/pymupdf4llm](https://github.com/pymupdf/pymupdf4llm)
- pdf-craft: [github.com/oomol-lab/pdf-craft](https://github.com/oomol-lab/pdf-craft)
- ColPali (Vespa example): [vespa-engine.github.io/pyvespa/examples/colpali-document-retrieval-vision-language-models-cloud.html](https://vespa-engine.github.io/pyvespa/examples/colpali-document-retrieval-vision-language-models-cloud.html)
