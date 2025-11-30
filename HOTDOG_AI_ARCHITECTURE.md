# HOTDOG AI Document Processing Architecture
**H**ierarchical **O**rchestrated **T**horough **D**ocument **O**versight & **G**uidance

**Date**: 2025-11-29
**Purpose**: Dynamic, user-centric AI architecture for exhaustive document analysis
**Focus**: PDF page accuracy, smart deduplication, flexible question sets, token efficiency

---

## Design Philosophy

**User-Centric Principles**:
1. **Purpose-Driven**: Every component serves the user's need for accurate bid spec analysis
2. **Flexible by Design**: Questions, sections, and experts adapt to each document
3. **Information Preservation**: Never lose details through deduplication or processing
4. **Citation Integrity**: PDF page numbers are first-class data, never optional metadata
5. **Exhaustive Coverage**: Process every page, answer every question, within token limits

**Not NEXUS**: This is a fresh design optimized for document analysis, not adapted from match prediction.

---

## Core Requirements

### 1. Perfect PDF Page Number Preservation
**Problem**: Currently broken - page numbers show in exports but not browser display
**Solution**: Page numbers are **mandatory metadata** attached to every answer at every stage

**Requirements**:
- ✅ Page numbers captured during extraction (Layer 0)
- ✅ Page numbers passed to AI in every prompt (Layer 3)
- ✅ Page numbers parsed from AI responses (Layer 3)
- ✅ Page numbers aggregated during deduplication (Layer 4)
- ✅ Page numbers displayed in browser AND exports (Layer 6)
- ✅ Page numbers validated at each layer (error if missing)

### 2. Smart Deduplication
**Problem**: 80% similarity can lose nuanced details
**Solution**: Semantic clustering with information merging

**Requirements**:
- ✅ Detect similar answers (embedding-based similarity)
- ✅ Merge complementary information (not replace)
- ✅ Preserve unique details from each occurrence
- ✅ Aggregate all page citations
- ✅ Track answer evolution across windows

**Example**:
- Window 1, Page 10: "Vinyl ester resin required"
- Window 5, Page 23: "Vinyl ester resin per ASTM F1216"
- Window 10, Page 41: "Resin shall cure at 180°F minimum"

**Bad Deduplication** (current): Keep only first answer, lose pages 23, 41
**Smart Deduplication** (HOTDOG): Merge into "Vinyl ester resin per ASTM F1216, shall cure at 180°F minimum <PDF pg 10, 23, 41>"

### 3. Exhaustive Document Coverage
**Problem**: Token limits can truncate analysis
**Solution**: Intelligent windowing with token budget management

**Requirements**:
- ✅ All pages processed (no skipping)
- ✅ All questions attempted (no omissions)
- ✅ Token budget tracked per window
- ✅ Dynamic prompt sizing based on remaining budget
- ✅ Overflow handling (split large sections if needed)

### 4. Dynamic Question Structure
**Problem**: Hardcoded 105 questions in 9 categories won't scale
**Solution**: Configuration-driven question sets

**Requirements**:
- ✅ Questions loaded from JSON/database
- ✅ Section headings configurable
- ✅ Number of questions variable (50-500+)
- ✅ Section groupings flexible
- ✅ Expert agents generated dynamically per section

**Example Configurations**:

**Config A - CIPP Bid Specs** (Current):
```json
{
  "sections": [
    {"name": "General Project Information", "questions": ["Q1", "Q2", ...]},
    {"name": "Materials & Equipment", "questions": ["Q28", "Q29", ...]},
    ...
  ]
}
```

**Config B - Construction Safety Audit**:
```json
{
  "sections": [
    {"name": "Safety Protocols", "questions": ["S1", "S2", ...]},
    {"name": "Hazard Identification", "questions": ["H1", "H2", ...]},
    ...
  ]
}
```

**Config C - Contract Review**:
```json
{
  "sections": [
    {"name": "Payment Terms", "questions": ["P1", "P2", ...]},
    {"name": "Dispute Resolution", "questions": ["D1", "D2", ...]},
    ...
  ]
}
```

### 5. Dynamic Expert Generation
**Problem**: Hardcoded agent prompts don't adapt to new question types
**Solution**: AI-generated expert personas from section metadata

**Requirements**:
- ✅ Section heading → AI persona generation
- ✅ Persona includes: name, expertise, system prompt, strategy
- ✅ Persona optimized for question types in that section
- ✅ Persona caching (reuse for similar section names)
- ✅ Fallback generic persona if generation fails

**Process**:
```
Input: Section name "Materials & Equipment Specifications"
      ↓
AI Persona Generator Call:
  "Create an expert AI persona for analyzing construction bid
   specifications in the category: Materials & Equipment Specifications.

   Output format:
   - Expert Name: [descriptive name]
   - Specialization: [1-2 sentence description]
   - System Prompt: [detailed instructions for this expert]
   - Question Strategy: [how to approach questions in this domain]"
      ↓
Output: {
  "name": "Materials & Standards Compliance Specialist",
  "specialization": "Expert in construction materials specifications, ASTM standards, equipment requirements, and material testing protocols for infrastructure projects.",
  "system_prompt": "You are a materials engineering specialist with 20 years experience in CIPP and infrastructure rehabilitation. Extract factual information about: pipe materials, resin specifications, liner construction, curing methods, ASTM/AWWA standards, equipment requirements, and material testing. Always cite PDF page numbers as <PDF pg X>. Be precise with measurements, specifications, and standard references.",
  "strategy": "systematic_extraction"
}
```

---

## HOTDOG AI Architecture Overview

### Layer Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   LAYER 0: Document Ingestion                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ • PDF uploaded by user                                     │  │
│  │ • PyMuPDF extracts text with page numbers                 │  │
│  │ • Output: [(page_num, text), (page_num, text), ...]       │  │
│  │ • Metadata: {total_pages, file_name, upload_time}         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 1: Dynamic Configuration Loader              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ • Load question configuration (JSON/DB)                   │  │
│  │ • Parse sections and questions                            │  │
│  │ • Count: N sections, M total questions                    │  │
│  │ • Output: {sections[], questions[], section_map{}}        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│           LAYER 2: Dynamic Expert Persona Generation            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ FOR EACH SECTION:                                          │  │
│  │   1. Check cache: Have we seen this section before?       │  │
│  │   2. If NO:                                                │  │
│  │      a. Call AI: "Generate expert persona for {section}"  │  │
│  │      b. Parse response → {name, specialization, prompt}   │  │
│  │      c. Store in cache                                     │  │
│  │   3. If YES: Retrieve cached persona                      │  │
│  │                                                             │  │
│  │ • Output: {section_id → expert_persona}                   │  │
│  │ • Example: "Materials" → MaterialsSpecialist{...}         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│         LAYER 3: Windowed Multi-Expert Processing (CORE)        │
│                                                                   │
│  FOR EACH 3-PAGE WINDOW:                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Window = Pages [P, P+1, P+2]                               │  │
│  │                                                             │  │
│  │ 1. Token Budget Check:                                     │  │
│  │    • Calculate tokens available                            │  │
│  │    • Adjust prompt length if needed                        │  │
│  │                                                             │  │
│  │ 2. Expert Routing:                                         │  │
│  │    • Group questions by section                            │  │
│  │    • Route each section to its expert                      │  │
│  │                                                             │  │
│  │ 3. Parallel Expert Calls:                                  │  │
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │    │ Expert A     │  │ Expert B     │  │ Expert C     │   │  │
│  │    │ Questions    │  │ Questions    │  │ Questions    │   │  │
│  │    │ 1-15         │  │ 16-27        │  │ 28-45        │   │  │
│  │    │              │  │              │  │              │   │  │
│  │    │ ↓ AI Call   │  │ ↓ AI Call   │  │ ↓ AI Call   │   │  │
│  │    │              │  │              │  │              │   │  │
│  │    │ ↓ Answers   │  │ ↓ Answers   │  │ ↓ Answers   │   │  │
│  │    └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │                                                             │  │
│  │ 4. Response Parsing:                                       │  │
│  │    • Extract answers                                       │  │
│  │    • Parse PDF page citations: <PDF pg X>                 │  │
│  │    • Calculate confidence scores                           │  │
│  │    • VALIDATE: Ensure page numbers present                │  │
│  │                                                             │  │
│  │ 5. Output per window:                                      │  │
│  │    {                                                        │  │
│  │      question_id → {                                       │  │
│  │        answer: "text",                                     │  │
│  │        pages: [10, 11, 12],  ← MANDATORY                  │  │
│  │        confidence: 0.85,                                   │  │
│  │        expert: "MaterialsSpecialist",                      │  │
│  │        window: 5                                           │  │
│  │      }                                                      │  │
│  │    }                                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│          LAYER 4: Smart Accumulation & Deduplication            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ FOR EACH NEW ANSWER:                                       │  │
│  │                                                             │  │
│  │ 1. Semantic Similarity Check:                              │  │
│  │    • Compare with existing answers for this question      │  │
│  │    • Use embedding cosine similarity                       │  │
│  │    • Threshold: 0.80 (80% similar)                        │  │
│  │                                                             │  │
│  │ 2. IF SIMILAR ANSWER EXISTS:                              │  │
│  │    a. Information Merge:                                   │  │
│  │       • Combine unique details from both answers          │  │
│  │       • Keep more specific version as base                │  │
│  │       • Append complementary information                   │  │
│  │    b. Page Citation Aggregation:                          │  │
│  │       • Merge page lists: [10] + [23, 41] = [10, 23, 41] │  │
│  │       • Remove duplicates, sort ascending                  │  │
│  │    c. Confidence Update:                                   │  │
│  │       • Use highest confidence score                       │  │
│  │       • Or weighted average if both high                   │  │
│  │                                                             │  │
│  │ 3. IF NO SIMILAR ANSWER:                                  │  │
│  │    • APPEND as new answer entry                           │  │
│  │    • Rank by confidence for display                       │  │
│  │                                                             │  │
│  │ 4. Data Structure:                                         │  │
│  │    accumulated_answers = {                                 │  │
│  │      question_id: [                                        │  │
│  │        {                                                    │  │
│  │          text: "merged answer",                            │  │
│  │          pages: [10, 23, 41, 67],  ← ALL CITATIONS       │  │
│  │          confidence: 0.90,                                 │  │
│  │          expert: "MaterialsSpecialist",                    │  │
│  │          windows: [1, 5, 10, 15],                         │  │
│  │          created: timestamp,                               │  │
│  │          updated: timestamp                                │  │
│  │        },                                                   │  │
│  │        {...}  ← Additional distinct answers               │  │
│  │      ]                                                      │  │
│  │    }                                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│             LAYER 5: Token Budget Manager (GUARDIAN)            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Tracks and manages token usage to ensure exhaustive        │  │
│  │ coverage within OpenAI limits                              │  │
│  │                                                             │  │
│  │ BEFORE EACH WINDOW:                                        │  │
│  │   1. Calculate tokens used so far                          │  │
│  │   2. Calculate tokens remaining in budget                  │  │
│  │   3. Estimate tokens needed for this window                │  │
│  │   4. IF insufficient:                                      │  │
│  │      • Reduce context length (truncate text)              │  │
│  │      • Prioritize unanswered questions                     │  │
│  │      • Split window into smaller chunks                    │  │
│  │   5. ELSE: Proceed with full context                      │  │
│  │                                                             │  │
│  │ TRACKING:                                                   │  │
│  │   • Prompt tokens per window                               │  │
│  │   • Completion tokens per window                           │  │
│  │   • Total tokens per document                              │  │
│  │   • Questions answered vs remaining                        │  │
│  │                                                             │  │
│  │ STRATEGY:                                                   │  │
│  │   • Max tokens per request: 4000 prompt + 16000 completion│  │
│  │   • Reserve 20% buffer for safety                          │  │
│  │   • Prioritize unanswered questions over refinement        │  │
│  │   • Log warnings if approaching limits                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│             LAYER 6: Output Compilation & Export                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. Unitary Log Table (Browser Display):                   │  │
│  │    • 1 row per question                                    │  │
│  │    • Show highest-confidence answer                        │  │
│  │    • Display all page citations: <PDF pg 10, 23, 41>     │  │
│  │    • Confidence badge: 🟢 High / 🟡 Medium / 🔴 Low      │  │
│  │                                                             │  │
│  │ 2. Footnotes Section:                                      │  │
│  │    • Aggregate all unique footnotes                        │  │
│  │    • Include page citations for each                       │  │
│  │    • Deduplicate similar footnotes                         │  │
│  │                                                             │  │
│  │ 3. Excel Export:                                           │  │
│  │    Sheet 1 - "Analysis Results":                           │  │
│  │    ┌────────────┬─────────┬────────────┬───────┬────────┐ │  │
│  │    │ Question   │ Answer  │ Confidence │ Pages │ Expert │ │  │
│  │    ├────────────┼─────────┼────────────┼───────┼────────┤ │  │
│  │    │ Q1: Name?  │ XYZ Proj│ High (0.9) │ 1,3,5 │ GenPro │ │  │
│  │    │ Q28: Resin?│ Vinyl...│ High (0.85)│10,23  │ MatSpe │ │  │
│  │    └────────────┴─────────┴────────────┴───────┴────────┘ │  │
│  │                                                             │  │
│  │    Sheet 2 - "All Answers" (if multiple per question):    │  │
│  │    • Shows all answer variants                             │  │
│  │    • Sorted by confidence                                  │  │
│  │                                                             │  │
│  │    Sheet 3 - "Metadata":                                   │  │
│  │    • Document name, pages, processing time                 │  │
│  │    • Token usage statistics                                │  │
│  │    • Expert personas used                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Layer Specifications

### LAYER 0: Document Ingestion

**Purpose**: Extract text from PDF with perfect page number preservation

**Input**:
- PDF file uploaded by user
- File path: `/tmp/uploads/bid_spec_xyz.pdf`

**Process**:
```python
def extract_pdf_with_pages(pdf_path):
    """
    Extract text from PDF with page numbers as first-class data.

    Returns:
        List[PageData]: [{page_num: int, text: str, char_count: int}, ...]
    """
    pages = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        pages.append({
            'page_num': page_num + 1,  # 1-indexed for user display
            'text': text,
            'char_count': len(text),
            'has_content': len(text.strip()) > 50  # Detect blank pages
        })

    doc.close()

    metadata = {
        'total_pages': len(pages),
        'total_chars': sum(p['char_count'] for p in pages),
        'file_name': os.path.basename(pdf_path),
        'extraction_time': datetime.now()
    }

    return pages, metadata
```

**Output**:
```json
{
  "pages": [
    {"page_num": 1, "text": "BID SPECIFICATION...", "char_count": 3421},
    {"page_num": 2, "text": "Project Name: XYZ...", "char_count": 2890},
    ...
  ],
  "metadata": {
    "total_pages": 120,
    "total_chars": 245000,
    "file_name": "cipp_bid_2024.pdf"
  }
}
```

**Validation**:
- ✅ All pages have page_num field
- ✅ Page numbers are sequential (1, 2, 3, ...)
- ✅ No missing pages
- ✅ Text extracted for all pages (warn if blank)

---

### LAYER 1: Dynamic Configuration Loader

**Purpose**: Load question configuration dynamically (not hardcoded)

**Input Sources**:
1. **JSON File**: `configs/cipp_questions.json`
2. **Database**: `question_configs` table
3. **User Upload**: Custom question set

**Configuration Schema**:
```json
{
  "config_name": "CIPP Bid Specification Analysis",
  "version": "2.0",
  "sections": [
    {
      "section_id": "general_info",
      "section_name": "General Project Information",
      "description": "Project metadata, owner, contract details",
      "questions": [
        {
          "id": "Q1",
          "text": "What is the project name?",
          "required": true,
          "expected_answer_type": "string"
        },
        {
          "id": "Q2",
          "text": "Who is the project owner?",
          "required": true,
          "expected_answer_type": "string"
        },
        ...
      ]
    },
    {
      "section_id": "materials",
      "section_name": "Materials & Equipment Specifications",
      "description": "Pipe materials, resins, liners, ASTM standards",
      "questions": [
        {
          "id": "Q28",
          "text": "What resin type is required?",
          "required": true,
          "expected_answer_type": "technical_spec"
        },
        ...
      ]
    },
    ...
  ]
}
```

**Process**:
```python
class ConfigurationLoader:
    def load_config(self, source):
        """
        Load question configuration from JSON/DB/user upload.

        Returns:
            ParsedConfig: {
                sections: List[Section],
                questions: List[Question],
                section_map: Dict[section_id -> Section],
                question_map: Dict[question_id -> Question]
            }
        """
        # Load raw config
        if source.endswith('.json'):
            config_data = self._load_json(source)
        elif source == 'database':
            config_data = self._load_from_db()
        else:
            raise ValueError(f"Unknown config source: {source}")

        # Parse into structured objects
        sections = []
        questions = []

        for section_data in config_data['sections']:
            section = Section(
                id=section_data['section_id'],
                name=section_data['section_name'],
                description=section_data.get('description', ''),
                questions=[]
            )

            for q_data in section_data['questions']:
                question = Question(
                    id=q_data['id'],
                    text=q_data['text'],
                    section_id=section.id,
                    required=q_data.get('required', True),
                    expected_type=q_data.get('expected_answer_type', 'string')
                )
                section.questions.append(question)
                questions.append(question)

            sections.append(section)

        # Create lookup maps
        section_map = {s.id: s for s in sections}
        question_map = {q.id: q for q in questions}

        return ParsedConfig(
            sections=sections,
            questions=questions,
            section_map=section_map,
            question_map=question_map,
            metadata={'name': config_data['config_name'], 'version': config_data['version']}
        )
```

**Output**:
```python
ParsedConfig(
    sections=[
        Section(id='general_info', name='General Project Information', questions=[Q1, Q2, ...]),
        Section(id='materials', name='Materials & Equipment', questions=[Q28, Q29, ...]),
        ...
    ],
    total_questions=105,
    total_sections=9
)
```

**Validation**:
- ✅ All questions have unique IDs
- ✅ All sections have at least 1 question
- ✅ Question IDs referenced correctly
- ✅ No orphaned questions (every question belongs to a section)

---

### LAYER 2: Dynamic Expert Persona Generation

**Purpose**: Generate AI expert personas dynamically from section metadata

**Key Insight**: Instead of hardcoding expert prompts, use AI to create experts that match the section perfectly.

**Process Flow**:

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: Section Object                                        │
│   • ID: "materials"                                          │
│   • Name: "Materials & Equipment Specifications"            │
│   • Description: "Pipe materials, resins, ASTM standards"   │
│   • Questions: [Q28, Q29, Q30, ...]                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Check Expert Cache                                   │
│   cache_key = hash(section_name)                            │
│   if cache_key in expert_cache:                             │
│       return cached_expert  ← REUSE                         │
└─────────────────────────────────────────────────────────────┘
                          ↓ (cache miss)
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Generate Expert Persona via AI                      │
│                                                               │
│   AI Prompt:                                                 │
│   """                                                         │
│   You are an expert AI architect. Design a specialized      │
│   AI persona for document analysis.                         │
│                                                               │
│   Section: Materials & Equipment Specifications             │
│   Description: Pipe materials, resins, liners, ASTM         │
│   Sample Questions:                                          │
│   - What resin type is required?                            │
│   - What ASTM standards apply?                              │
│   - What liner thickness is specified?                      │
│                                                               │
│   Generate:                                                  │
│   1. Expert Name: [creative, descriptive name]              │
│   2. Specialization: [2-3 sentences of expertise]          │
│   3. System Prompt: [detailed instructions for this expert] │
│   4. Citation Strategy: [how to extract page numbers]       │
│   5. Answer Format: [structure of responses]                │
│                                                               │
│   Output as JSON.                                            │
│   """                                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Parse AI Response                                   │
│                                                               │
│   Response:                                                  │
│   {                                                           │
│     "expert_name": "CIPP Materials & Standards Specialist", │
│     "specialization": "Expert in polymer resin chemistry,   │
│       ASTM/AWWA standards for pipe rehabilitation, felt     │
│       liner construction, and curing methodologies. 20+     │
│       years in infrastructure materials engineering.",      │
│     "system_prompt": "You are a materials engineering       │
│       specialist with deep expertise in CIPP technology.    │
│       Extract factual information about:\n                  │
│       - Resin types (polyester, vinyl ester, epoxy)\n      │
│       - ASTM standards (F1216, F1743, D5813, etc.)\n       │
│       - Liner specifications (thickness, felt type)\n       │
│       - Curing methods (steam, hot water, UV, ambient)\n   │
│       - Equipment requirements\n                            │
│       Always cite PDF page numbers: <PDF pg X>\n           │
│       Be precise with measurements and standard numbers.",  │
│     "citation_strategy": "Extract page numbers from source  │
│       text. Include in every answer as: <PDF pg X>",       │
│     "answer_format": "Direct, factual answer with specific │
│       measurements, standards, or requirements. Cite pages."│
│   }                                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Create Expert Object & Cache                        │
│                                                               │
│   expert = ExpertPersona(                                    │
│       id=generate_id(section.id + "_expert"),               │
│       name="CIPP Materials & Standards Specialist",         │
│       section_id=section.id,                                │
│       system_prompt=parsed['system_prompt'],                │
│       specialization=parsed['specialization'],              │
│       citation_strategy=parsed['citation_strategy'],        │
│       answer_format=parsed['answer_format'],                │
│       created_at=now(),                                      │
│       cache_key=hash(section.name)                          │
│   )                                                           │
│                                                               │
│   expert_cache[cache_key] = expert  ← STORE FOR REUSE      │
│                                                               │
│   return expert                                              │
└─────────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
class ExpertPersonaGenerator:
    def __init__(self, openai_client, cache_store):
        self.client = openai_client
        self.cache = cache_store  # Redis or in-memory dict

    def generate_expert(self, section: Section) -> ExpertPersona:
        """
        Generate or retrieve cached expert persona for a section.

        Args:
            section: Section object with name, description, questions

        Returns:
            ExpertPersona: Complete expert configuration
        """
        # Check cache first
        cache_key = self._make_cache_key(section.name)
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"Expert cache HIT for section: {section.name}")
            return ExpertPersona.from_json(cached)

        logger.info(f"Expert cache MISS - generating for: {section.name}")

        # Build generation prompt
        sample_questions = '\n'.join([f"- {q.text}" for q in section.questions[:5]])

        prompt = f"""You are an expert AI architect designing specialized document analysis personas.

Create an expert AI persona for analyzing construction/engineering bid specifications.

**Section Details:**
- Name: {section.name}
- Description: {section.description}
- Sample Questions:
{sample_questions}

**Generate the following (output as JSON):**

1. **expert_name**: A creative, descriptive name for this expert (e.g., "CIPP Materials & Standards Compliance Specialist")

2. **specialization**: 2-3 sentences describing this expert's domain knowledge and experience

3. **system_prompt**: Detailed instructions for this expert including:
   - Areas of expertise
   - Types of information to extract
   - Required citation format: <PDF pg X>
   - Precision requirements (measurements, standards, etc.)
   - Answer style (factual, concise, technical)

4. **citation_strategy**: How this expert should extract and include PDF page numbers

5. **answer_format**: Structure and style of answers this expert should produce

**CRITICAL**: The expert MUST always include PDF page citations in format: <PDF pg X>

Output only valid JSON, no markdown formatting."""

        # Call AI to generate expert
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert AI architect."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Some creativity for persona generation
            response_format={"type": "json_object"}
        )

        # Parse response
        expert_data = json.loads(response.choices[0].message.content)

        # Validate required fields
        required_fields = ['expert_name', 'specialization', 'system_prompt',
                          'citation_strategy', 'answer_format']
        for field in required_fields:
            if field not in expert_data:
                raise ValueError(f"Expert generation missing field: {field}")

        # Create expert object
        expert = ExpertPersona(
            id=f"{section.id}_expert",
            name=expert_data['expert_name'],
            section_id=section.id,
            section_name=section.name,
            system_prompt=expert_data['system_prompt'],
            specialization=expert_data['specialization'],
            citation_strategy=expert_data['citation_strategy'],
            answer_format=expert_data['answer_format'],
            created_at=datetime.now()
        )

        # Cache for future use
        self.cache.set(cache_key, expert.to_json(), ttl=86400 * 30)  # 30 days

        logger.info(f"Generated expert: {expert.name}")
        return expert

    def _make_cache_key(self, section_name: str) -> str:
        """Generate consistent cache key from section name."""
        normalized = section_name.lower().strip()
        return f"expert:{hashlib.sha256(normalized.encode()).hexdigest()[:16]}"
```

**Example Output**:

For section "Safety & Environmental Compliance":

```json
{
  "expert_name": "Safety & Environmental Compliance Officer",
  "specialization": "Expert in OSHA regulations, environmental permitting (NPDES, air quality), confined space procedures, traffic control planning, and emergency response protocols for construction projects. Certified in hazardous materials management and municipal infrastructure safety standards.",
  "system_prompt": "You are a safety and environmental compliance specialist with expertise in construction site safety, environmental regulations, and permit requirements. Extract information about:\n- OSHA safety requirements and procedures\n- Environmental permits (NPDES, stormwater, air quality)\n- Confined space entry protocols\n- Traffic control and public safety measures\n- Hazardous materials handling\n- Emergency response plans\n- Safety training and certification requirements\n\nAlways cite PDF page numbers as: <PDF pg X>\nBe specific about regulatory requirements, permit types, and safety procedures.",
  "citation_strategy": "Extract page numbers from the source document and include them in every answer using the format <PDF pg X>. If information spans multiple pages, list all relevant pages: <PDF pg 12, 15, 18>",
  "answer_format": "Factual, regulatory-focused answers. Include specific requirement names, permit types, and procedural steps. Cite all relevant PDF pages."
}
```

**Fallback Strategy**:

If expert generation fails (API error, timeout, invalid response):

```python
def create_generic_expert(section: Section) -> ExpertPersona:
    """Fallback generic expert if generation fails."""
    return ExpertPersona(
        id=f"{section.id}_expert",
        name=f"{section.name} Specialist",
        section_id=section.id,
        system_prompt=f"""You are a document analysis expert specializing in {section.name}.

Extract factual information from construction bid specifications related to this category.

Always cite PDF page numbers in your answers using the format: <PDF pg X>

Be precise, factual, and thorough in your responses.""",
        specialization=f"Expert in {section.name} for construction document analysis.",
        citation_strategy="Include <PDF pg X> in all answers",
        answer_format="Direct, factual answers with page citations"
    )
```

**Benefits**:
- ✅ Adapts to ANY section name (not hardcoded)
- ✅ Optimizes expert for specific question types
- ✅ Reuses cached experts (cost efficient)
- ✅ Falls back gracefully if generation fails
- ✅ Enforces PDF citation requirement in system prompt

---

### LAYER 3: Windowed Multi-Expert Processing (CORE ENGINE)

**Purpose**: Process PDF in 3-page windows with parallel expert calls and mandatory page citation

**This is the heart of HOTDOG AI where actual document analysis happens.**

**Window Processing Flow**:

```
FOR each 3-page window in document:
  ↓
┌─────────────────────────────────────────────────────────────┐
│ WINDOW n: Pages [P, P+1, P+2]                                │
│                                                               │
│ Example: Window 5 = Pages [13, 14, 15]                      │
│ Combined text: ~6000 characters                              │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Token Budget Check (Layer 5 Guardian)               │
│   • Tokens used so far: 45,000                              │
│   • Tokens remaining: 35,000                                 │
│   • Estimated for this window: 8,000                         │
│   • Status: ✅ PROCEED                                       │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Route Questions to Experts                          │
│                                                               │
│   All 105 questions grouped by section:                     │
│   • General Info (Q1-Q15) → GeneralProjectExpert            │
│   • Materials (Q28-Q45) → MaterialsSpecialist               │
│   • Safety (Q70-Q80) → SafetyComplianceOfficer              │
│   ... (all 9 sections)                                       │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Build Expert Prompts                                │
│                                                               │
│   For MaterialsSpecialist:                                   │
│   ┌───────────────────────────────────────────────────────┐ │
│   │ SYSTEM: {expert.system_prompt}                        │ │
│   │                                                         │ │
│   │ USER:                                                   │ │
│   │ You are analyzing pages 13-15 of a bid specification. │ │
│   │                                                         │ │
│   │ **CRITICAL**: For every answer you provide, you MUST  │ │
│   │ include PDF page citations in this exact format:      │ │
│   │ <PDF pg 13> or <PDF pg 13, 14> for multi-page info.  │ │
│   │                                                         │ │
│   │ Current pages being analyzed: 13, 14, 15              │ │
│   │                                                         │ │
│   │ Context (from pages 13-15):                            │ │
│   │ [TEXT FROM PAGES 13-15]                                │ │
│   │                                                         │ │
│   │ Questions:                                              │ │
│   │ Q28. What resin type is required?                      │ │
│   │ Q29. What ASTM standards apply to materials?          │ │
│   │ Q30. What liner thickness is specified?               │ │
│   │ ...                                                     │ │
│   │                                                         │ │
│   │ Output format (JSON):                                  │ │
│   │ {                                                       │ │
│   │   "Q28": {                                             │ │
│   │     "answer": "Your answer here <PDF pg X>",          │ │
│   │     "confidence": 0.85,                                │ │
│   │     "pages": [13, 14]                                 │ │
│   │   },                                                    │ │
│   │   ...                                                   │ │
│   │ }                                                       │ │
│   └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Parallel Expert API Calls                           │
│                                                               │
│   async def process_all_experts():                          │
│       tasks = []                                             │
│       for expert in active_experts:                         │
│           task = call_expert_async(expert, window_context)  │
│           tasks.append(task)                                 │
│       results = await asyncio.gather(*tasks)                │
│       return results                                         │
│                                                               │
│   Executes 9-10 AI calls IN PARALLEL                        │
│   Typical latency: 3-5 seconds (vs 30s sequential)         │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Parse Expert Responses                              │
│                                                               │
│   MaterialsSpecialist response:                             │
│   {                                                           │
│     "Q28": {                                                 │
│       "answer": "Vinyl ester resin per ASTM F1216 <PDF pg 13>",│
│       "confidence": 0.90,                                    │
│       "pages": [13]                                         │
│     },                                                        │
│     "Q29": {                                                 │
│       "answer": "ASTM F1216, F1743, D5813 <PDF pg 13, 14>",│
│       "confidence": 0.95,                                    │
│       "pages": [13, 14]                                     │
│     },                                                        │
│     ...                                                       │
│   }                                                           │
│                                                               │
│   VALIDATION for each answer:                                │
│   ✅ Has "answer" field                                      │
│   ✅ Has "pages" array with at least one page number        │
│   ✅ Page numbers are within current window [13,14,15]      │
│   ✅ Answer text contains "<PDF pg X>" citation             │
│   ❌ REJECT if missing pages or citation                    │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Confidence Scoring                                  │
│                                                               │
│   For each answer, calculate confidence if not provided:    │
│   - Length & specificity (longer, detailed = higher)        │
│   - Presence of concrete facts (numbers, standards, dates)  │
│   - Hedge words ("may", "unclear") → lower                  │
│   - Definitive language ("shall", "required") → higher      │
│                                                               │
│   Score range: 0.0 (no confidence) to 1.0 (certain)        │
│   Classification: High ≥0.7, Medium 0.4-0.7, Low <0.4       │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Window Results                                       │
│   {                                                           │
│     window_num: 5,                                           │
│     pages: [13, 14, 15],                                    │
│     answers: {                                               │
│       "Q28": {                                              │
│         answer: "Vinyl ester resin per ASTM F1216 <PDF pg 13>",│
│         pages: [13],                                        │
│         confidence: 0.90,                                    │
│         expert: "MaterialsSpecialist",                      │
│         window: 5                                            │
│       },                                                      │
│       "Q29": {...},                                          │
│       ... (all answers from all experts)                    │
│     },                                                        │
│     tokens_used: 7842,                                       │
│     processing_time: 4.2s                                    │
│   }                                                           │
└─────────────────────────────────────────────────────────────┘
  ↓
  Pass to Layer 4 (Accumulation)
```

**Critical Implementation Details**:

**1. Mandatory Page Citation Enforcement**:

```python
def validate_answer(answer_obj, window_pages):
    """Strict validation of answer structure and page citations."""

    # Check required fields
    if 'answer' not in answer_obj:
        raise ValidationError("Missing 'answer' field")
    if 'pages' not in answer_obj:
        raise ValidationError("Missing 'pages' field")

    # Validate pages array
    if not isinstance(answer_obj['pages'], list):
        raise ValidationError("'pages' must be an array")
    if len(answer_obj['pages']) == 0:
        raise ValidationError("'pages' array is empty - PDF citations required")

    # Validate page numbers are in current window
    for page in answer_obj['pages']:
        if page not in window_pages:
            logger.warning(f"Page {page} not in current window {window_pages}")
            # Don't reject, but log for investigation

    # Validate answer text contains citation marker
    if '<PDF pg' not in answer_obj['answer']:
        logger.warning(f"Answer missing <PDF pg> citation marker: {answer_obj['answer'][:100]}")
        # Inject citation if missing
        answer_obj['answer'] = f"{answer_obj['answer']} <PDF pg {', '.join(map(str, answer_obj['pages']))}>"

    return True
```

**2. Parallel Expert Execution**:

```python
import asyncio
from typing import List, Dict

class MultiExpertProcessor:
    def __init__(self, experts: List[ExpertPersona], openai_client):
        self.experts = experts
        self.client = openai_client

    async def process_window(self, window_data, questions_by_section):
        """
        Process all experts in parallel for this window.

        Args:
            window_data: {pages: [13,14,15], text: "..."}
            questions_by_section: {section_id: [Question, ...]}

        Returns:
            Dict[question_id -> answer_data]
        """
        # Create tasks for each expert
        tasks = []
        for expert in self.experts:
            section_questions = questions_by_section.get(expert.section_id, [])
            if section_questions:
                task = self._call_expert_async(expert, window_data, section_questions)
                tasks.append(task)

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results from all experts
        all_answers = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Expert call failed: {result}")
                continue
            all_answers.update(result)

        return all_answers

    async def _call_expert_async(self, expert, window_data, questions):
        """Call single expert asynchronously."""
        prompt = self._build_expert_prompt(expert, window_data, questions)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": expert.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            answers = json.loads(response.choices[0].message.content)

            # Validate each answer
            for q_id, answer_data in answers.items():
                self._validate_answer(answer_data, window_data['pages'])

            return answers

        except Exception as e:
            logger.error(f"Expert {expert.name} failed: {e}")
            return {}

    def _build_expert_prompt(self, expert, window_data, questions):
        """Build comprehensive prompt for expert."""
        pages_str = ', '.join(map(str, window_data['pages']))

        questions_text = '\n'.join([f"{q.id}. {q.text}" for q in questions])

        prompt = f"""You are analyzing pages {pages_str} of a bid specification document.

**CRITICAL REQUIREMENT**: For EVERY answer, you MUST include PDF page citations.
Format: <PDF pg X> or <PDF pg X, Y> for multi-page information.

Current pages: {pages_str}

**Document Context (pages {pages_str})**:
{window_data['text']}

**Questions to answer**:
{questions_text}

**Output Requirements**:
1. Answer every question based on information in these pages
2. If no information found, state "Not specified in pages {pages_str}" <PDF pg {pages_str}>
3. Include page citations in EVERY answer
4. Provide confidence score (0.0-1.0) for each answer
5. List relevant page numbers in "pages" array

**Output format (JSON)**:
{{
  "Q1": {{
    "answer": "Your answer with citation <PDF pg X>",
    "confidence": 0.85,
    "pages": [13, 14]
  }},
  ...
}}"""

        return prompt
```

**Output Example** from Window 5 (pages 13-15):

```json
{
  "window_num": 5,
  "pages": [13, 14, 15],
  "answers": {
    "Q1": {
      "answer": "XYZ Sewer Rehabilitation Project <PDF pg 13>",
      "pages": [13],
      "confidence": 0.95,
      "expert": "GeneralProjectExpert",
      "window": 5
    },
    "Q28": {
      "answer": "Vinyl ester resin conforming to ASTM F1216 <PDF pg 13, 14>",
      "pages": [13, 14],
      "confidence": 0.92,
      "expert": "MaterialsSpecialist",
      "window": 5
    },
    "Q29": {
      "answer": "ASTM F1216, F1743, D5813 for resin and liner specifications <PDF pg 14>",
      "pages": [14],
      "confidence": 0.90,
      "expert": "MaterialsSpecialist",
      "window": 5
    },
    "Q70": {
      "answer": "Confined space entry requires OSHA 1910.146 compliance, atmospheric testing, and rescue plan <PDF pg 15>",
      "pages": [15],
      "confidence": 0.88,
      "expert": "SafetyComplianceOfficer",
      "window": 5
    }
  },
  "tokens_used": 8234,
  "processing_time_seconds": 4.3,
  "expert_count": 9
}
```

---

### LAYER 4: Smart Accumulation & Deduplication

**Purpose**: Merge answers from multiple windows intelligently without losing information

**Key Challenge**: Same question asked across 33 windows = 33 potential answers per question. How to consolidate without losing details?

**Solution**: Semantic clustering + information merging + citation aggregation

**Process Flow**:

```
New Answer from Window 5:
  Q28: "Vinyl ester resin per ASTM F1216 <PDF pg 13, 14>"
  pages: [13, 14]
  confidence: 0.92
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Check Existing Answers for Q28                      │
│                                                               │
│   accumulated_answers[Q28] = [                               │
│     {                                                         │
│       answer: "Vinyl ester resin required <PDF pg 3>",      │
│       pages: [3],                                            │
│       confidence: 0.75,                                      │
│       windows: [1]                                           │
│     }                                                         │
│   ]                                                           │
│                                                               │
│   Found 1 existing answer                                    │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Calculate Semantic Similarity                       │
│                                                               │
│   existing: "Vinyl ester resin required"                    │
│   new:      "Vinyl ester resin per ASTM F1216"             │
│                                                               │
│   Method: Cosine similarity on embeddings                    │
│   Similarity score: 0.87 (87% similar)                      │
│   Threshold: 0.80                                            │
│   Result: SIMILAR → Merge information                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Information Merging Strategy                        │
│                                                               │
│   Identify unique information in each:                      │
│   - Existing: "required" (vague)                            │
│   - New: "per ASTM F1216" (specific standard reference)     │
│                                                               │
│   Merge strategy: Keep more specific version, add details   │
│                                                               │
│   Merged answer:                                             │
│   "Vinyl ester resin per ASTM F1216 required <PDF pg 3, 13, 14>"│
│                                                               │
│   Why: New answer is more specific (includes standard),     │
│         but preserve "required" wording from original        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Page Citation Aggregation                           │
│                                                               │
│   Existing pages: [3]                                        │
│   New pages: [13, 14]                                        │
│                                                               │
│   Merge: [3] + [13, 14] = [3, 13, 14]                      │
│   Remove duplicates: N/A                                     │
│   Sort ascending: [3, 13, 14] ✅                            │
│                                                               │
│   Updated answer:                                            │
│   "Vinyl ester resin per ASTM F1216 required <PDF pg 3, 13, 14>"│
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Confidence Update                                   │
│                                                               │
│   Existing confidence: 0.75                                  │
│   New confidence: 0.92                                       │
│                                                               │
│   Strategy: Use HIGHEST confidence (more specific answer)   │
│   Updated confidence: 0.92                                   │
│                                                               │
│   Rationale: The answer with standard reference (F1216)     │
│   is more authoritative than vague "required"               │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Update Accumulated Answer                           │
│                                                               │
│   accumulated_answers[Q28] = [                               │
│     {                                                         │
│       answer: "Vinyl ester resin per ASTM F1216 required <PDF pg 3, 13, 14>",│
│       pages: [3, 13, 14],                                   │
│       confidence: 0.92,                                      │
│       windows: [1, 5],                                       │
│       expert: "MaterialsSpecialist",                        │
│       created_window: 1,                                     │
│       last_updated_window: 5,                               │
│       merge_count: 1                                         │
│     }                                                         │
│   ]                                                           │
└─────────────────────────────────────────────────────────────┘
```

**Edge Case: Complementary Information (NOT Duplication)**

```
Window 1, Page 3:
  Q28: "Vinyl ester resin required"

Window 5, Pages 13-14:
  Q28: "Vinyl ester resin per ASTM F1216"

Window 10, Page 41:
  Q28: "Resin shall cure at minimum 180°F"

Window 15, Page 67:
  Q28: "Minimum wall thickness after curing: 6mm"
```

**Similarity Analysis**:
- Answer 1 vs Answer 2: 87% similar → MERGE
- Merged 1+2 vs Answer 3: 45% similar → SEPARATE (different aspect: curing temp)
- Merged 1+2 vs Answer 4: 40% similar → SEPARATE (different aspect: thickness)
- Answer 3 vs Answer 4: 30% similar → SEPARATE (both distinct)

**Final Accumulated State for Q28**:

```python
accumulated_answers["Q28"] = [
    {
        "answer": "Vinyl ester resin per ASTM F1216 required <PDF pg 3, 13, 14>",
        "pages": [3, 13, 14],
        "confidence": 0.92,
        "type": "material_specification",
        "windows": [1, 5]
    },
    {
        "answer": "Resin shall cure at minimum 180°F <PDF pg 41>",
        "pages": [41],
        "confidence": 0.85,
        "type": "curing_requirement",
        "windows": [10]
    },
    {
        "answer": "Minimum wall thickness after curing: 6mm <PDF pg 67>",
        "pages": [67],
        "confidence": 0.88,
        "type": "dimensional_requirement",
        "windows": [15]
    }
]
```

**Display Strategy**:
- **Browser**: Show highest-confidence answer (first one), with "+ 2 more details" link
- **Export**: Include ALL three answers in separate rows

**Implementation**:

```python
class SmartAccumulator:
    def __init__(self, embedding_model):
        self.answers = {}  # {question_id: [AnswerEntry, ...]}
        self.embedder = embedding_model
        self.similarity_threshold = 0.80

    def accumulate(self, question_id, new_answer_data):
        """
        Intelligently accumulate new answer with existing answers.

        Args:
            question_id: str
            new_answer_data: {
                answer: str,
                pages: List[int],
                confidence: float,
                expert: str,
                window: int
            }
        """
        # Initialize if first answer for this question
        if question_id not in self.answers:
            self.answers[question_id] = []
            self.answers[question_id].append(new_answer_data)
            logger.info(f"{question_id}: First answer added")
            return

        # Calculate similarity with all existing answers
        new_embedding = self.embedder.embed(new_answer_data['answer'])

        best_match = None
        best_similarity = 0.0

        for existing in self.answers[question_id]:
            existing_embedding = self.embedder.embed(existing['answer'])
            similarity = cosine_similarity(new_embedding, existing_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing

        # Decision: Merge or Append?
        if best_similarity >= self.similarity_threshold:
            # MERGE: Similar enough to be same information
            logger.info(f"{question_id}: Merging (similarity: {best_similarity:.2f})")
            self._merge_answers(best_match, new_answer_data)
        else:
            # APPEND: Distinct information
            logger.info(f"{question_id}: Appending as new variant (similarity: {best_similarity:.2f})")
            self.answers[question_id].append(new_answer_data)
            # Sort by confidence (highest first)
            self.answers[question_id].sort(key=lambda x: x['confidence'], reverse=True)

    def _merge_answers(self, existing, new):
        """
        Merge two similar answers, preserving all information and citations.

        Strategy:
        1. Use more specific/detailed answer as base
        2. Add unique details from other answer
        3. Aggregate all page citations
        4. Use highest confidence score
        """
        # Determine which answer is more specific
        if len(new['answer']) > len(existing['answer']) * 1.2:
            # New answer significantly longer/more detailed
            base_answer = new['answer']
            supplemental = existing['answer']
        else:
            # Existing answer is base
            base_answer = existing['answer']
            supplemental = new['answer']

        # Extract unique information from supplemental
        # (simplified: in production, use NLP to extract unique clauses)
        unique_info = self._extract_unique_info(base_answer, supplemental)

        # Merge answer text
        if unique_info:
            merged_text = f"{base_answer}. {unique_info}"
        else:
            merged_text = base_answer

        # Aggregate page citations
        all_pages = sorted(set(existing['pages'] + new['pages']))

        # Update citation markers in text
        merged_text = self._update_citations(merged_text, all_pages)

        # Update existing answer in place
        existing['answer'] = merged_text
        existing['pages'] = all_pages
        existing['confidence'] = max(existing['confidence'], new['confidence'])
        existing['windows'] = existing.get('windows', [existing.get('window')]) + [new['window']]
        existing['merge_count'] = existing.get('merge_count', 0) + 1
        existing['last_updated'] = datetime.now()

    def _extract_unique_info(self, base, supplemental):
        """Extract information in supplemental that's not in base."""
        # Simplified version: check for unique phrases
        base_words = set(base.lower().split())
        supp_words = set(supplemental.lower().split())
        unique_words = supp_words - base_words

        if len(unique_words) > 3:  # Has meaningful unique content
            # Return phrases from supplemental containing unique words
            # (production: use NLP chunking)
            return supplemental
        return ""

    def _update_citations(self, text, pages):
        """Update <PDF pg X> markers with all relevant pages."""
        # Remove old citation markers
        text = re.sub(r'<PDF pg [0-9, ]+>', '', text)

        # Add new aggregated citation
        pages_str = ', '.join(map(str, pages))
        return f"{text.strip()} <PDF pg {pages_str}>"

    def get_display_answer(self, question_id):
        """Get primary answer for browser display (highest confidence)."""
        if question_id not in self.answers or not self.answers[question_id]:
            return None

        # Already sorted by confidence
        return self.answers[question_id][0]

    def get_all_answers(self, question_id):
        """Get all answer variants for export."""
        return self.answers.get(question_id, [])
```

**Benefits of Smart Accumulation**:
- ✅ Never loses information (everything preserved or merged)
- ✅ Aggregates all page citations (perfect PDF references)
- ✅ Prioritizes more specific/detailed answers
- ✅ Handles complementary information correctly (separate answers)
- ✅ Confidence-weighted ranking for display

---

### LAYER 5: Token Budget Manager (Guardian)

**Purpose**: Ensure exhaustive coverage within OpenAI token limits

**Challenge**:
- 100-page PDF × 33 windows × 105 questions = massive token usage
- OpenAI limit: 16,384 tokens output (gpt-4), 4,096 input (varies by model)
- Must process ALL pages and ALL questions without hitting limits

**Solution**: Dynamic prompt sizing + priority system + overflow handling

**Token Budget Tracking**:

```python
class TokenBudgetManager:
    def __init__(self, max_tokens_per_request=4000):
        self.max_prompt_tokens = max_tokens_per_request
        self.max_completion_tokens = 16000  # gpt-4 limit
        self.total_tokens_used = 0
        self.window_token_usage = []
        self.safety_buffer = 0.8  # Use 80% of max to be safe

    def check_budget_before_window(self, window_num, context_text, question_count):
        """
        Check if we have enough tokens for this window.
        Adjust prompt if needed.

        Returns:
            adjusted_context: str (possibly truncated)
            can_proceed: bool
        """
        # Estimate tokens for this window
        base_prompt_tokens = self._estimate_tokens(context_text)
        question_tokens = question_count * 50  # ~50 tokens per question
        estimated_completion = question_count * 150  # ~150 tokens per answer

        total_estimate = base_prompt_tokens + question_tokens + estimated_completion

        logger.info(f"Window {window_num} token estimate: {total_estimate}")
        logger.info(f"  - Context: {base_prompt_tokens}")
        logger.info(f"  - Questions: {question_tokens}")
        logger.info(f"  - Estimated completion: {estimated_completion}")

        # Check if within limits
        max_allowed = self.max_prompt_tokens * self.safety_buffer

        if base_prompt_tokens > max_allowed:
            # Context too long, need to truncate
            logger.warning(f"Context exceeds budget ({base_prompt_tokens} > {max_allowed})")
            adjusted_context = self._truncate_context(context_text, max_allowed)
            logger.info(f"Truncated context to {self._estimate_tokens(adjusted_context)} tokens")
            return adjusted_context, True

        return context_text, True

    def _estimate_tokens(self, text):
        """Estimate token count (rough: 4 chars ≈ 1 token)."""
        return len(text) // 4

    def _truncate_context(self, text, max_tokens):
        """
        Intelligently truncate context to fit budget.
        Preserve beginning and end (most important sections).
        """
        target_chars = max_tokens * 4

        if len(text) <= target_chars:
            return text

        # Keep first 60% and last 40%
        keep_start = int(target_chars * 0.6)
        keep_end = int(target_chars * 0.4)

        truncated = text[:keep_start] + "\n\n[... middle section truncated ...]\n\n" + text[-keep_end:]

        return truncated

    def record_usage(self, window_num, prompt_tokens, completion_tokens):
        """Record actual token usage after API call."""
        total = prompt_tokens + completion_tokens
        self.total_tokens_used += total

        self.window_token_usage.append({
            'window': window_num,
            'prompt': prompt_tokens,
            'completion': completion_tokens,
            'total': total
        })

        logger.info(f"Window {window_num} actual tokens: {total} (prompt: {prompt_tokens}, completion: {completion_tokens})")
        logger.info(f"Total tokens used: {self.total_tokens_used}")

    def get_statistics(self):
        """Get token usage statistics."""
        if not self.window_token_usage:
            return {}

        total_prompt = sum(w['prompt'] for w in self.window_token_usage)
        total_completion = sum(w['completion'] for w in self.window_token_usage)
        avg_per_window = self.total_tokens_used / len(self.window_token_usage)

        return {
            'total_tokens': self.total_tokens_used,
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'windows_processed': len(self.window_token_usage),
            'avg_tokens_per_window': avg_per_window,
            'estimated_cost_usd': self.total_tokens_used * 0.00003  # Rough estimate
        }
```

**Priority System for Questions**:

If token budget is tight, prioritize unanswered questions:

```python
def prioritize_questions(all_questions, answered_so_far):
    """
    Prioritize questions to maximize coverage.

    Returns:
        priority_questions: List[Question] sorted by priority
    """
    unanswered = [q for q in all_questions if q.id not in answered_so_far]
    partially_answered = [q for q in all_questions if q.id in answered_so_far
                         and answered_so_far[q.id]['confidence'] < 0.7]
    well_answered = [q for q in all_questions if q.id in answered_so_far
                    and answered_so_far[q.id]['confidence'] >= 0.7]

    # Priority: unanswered > partially > well-answered
    return unanswered + partially_answered + well_answered
```

---

### LAYER 6: Output Compilation & Export

**Purpose**: Present results to user in browser and export formats

**Browser Display** (Unitary Log Table):

```html
<table class="unitary-log-table">
  <thead>
    <tr>
      <th>Question</th>
      <th>Answer</th>
      <th>Confidence</th>
      <th>Pages</th>
    </tr>
  </thead>
  <tbody>
    <tr data-question-id="Q1">
      <td>Q1. What is the project name?</td>
      <td>
        <span class="confidence-badge high">🟢 High</span>
        XYZ Sewer Rehabilitation Project
        <span class="pdf-citation"><PDF pg 1, 3, 5></span>
        <button class="show-variants">+2 more details</button>
      </td>
      <td>0.95</td>
      <td>1, 3, 5</td>
    </tr>
    <tr data-question-id="Q28">
      <td>Q28. What resin type is required?</td>
      <td>
        <span class="confidence-badge high">🟢 High</span>
        Vinyl ester resin per ASTM F1216 required
        <span class="pdf-citation"><PDF pg 3, 13, 14></span>
        <button class="show-variants">+2 more details</button>
      </td>
      <td>0.92</td>
      <td>3, 13, 14</td>
    </tr>
  </tbody>
</table>

<!-- Variants Modal (hidden by default) -->
<div id="variants-modal" class="modal">
  <div class="modal-content">
    <h3>All Answer Variants for Q28</h3>
    <div class="variant">
      <strong>Answer 1 (Primary):</strong>
      Vinyl ester resin per ASTM F1216 required <PDF pg 3, 13, 14>
      <br>Confidence: 0.92 | Pages: 3, 13, 14
    </div>
    <div class="variant">
      <strong>Answer 2:</strong>
      Resin shall cure at minimum 180°F <PDF pg 41>
      <br>Confidence: 0.85 | Pages: 41
    </div>
    <div class="variant">
      <strong>Answer 3:</strong>
      Minimum wall thickness after curing: 6mm <PDF pg 67>
      <br>Confidence: 0.88 | Pages: 67
    </div>
  </div>
</div>
```

**Excel Export Format**:

**Sheet 1: "Analysis Results"**

| Question | Primary Answer | Confidence | Pages | Expert | Variants |
|----------|---------------|------------|-------|--------|----------|
| Q1: Project name? | XYZ Sewer Rehabilitation Project <PDF pg 1, 3, 5> | High (0.95) | 1, 3, 5 | GeneralProjectExpert | 0 |
| Q28: Resin type? | Vinyl ester resin per ASTM F1216 <PDF pg 3, 13, 14> | High (0.92) | 3, 13, 14 | MaterialsSpecialist | 2 |

**Sheet 2: "All Answer Variants"**

| Question | Answer Variant | Confidence | Pages | Type |
|----------|----------------|------------|-------|------|
| Q28: Resin type? | Vinyl ester resin per ASTM F1216 <PDF pg 3, 13, 14> | 0.92 | 3, 13, 14 | material_specification |
| Q28: Resin type? | Resin shall cure at minimum 180°F <PDF pg 41> | 0.85 | 41 | curing_requirement |
| Q28: Resin type? | Minimum wall thickness: 6mm <PDF pg 67> | 0.88 | 67 | dimensional_requirement |

**Sheet 3: "Metadata & Statistics"**

| Metric | Value |
|--------|-------|
| Document Name | cipp_bid_2024.pdf |
| Total Pages | 120 |
| Pages Analyzed | 120 (100%) |
| Total Questions | 105 |
| Questions Answered | 105 (100%) |
| Average Confidence | 0.86 (High) |
| High Confidence Answers | 89 (84.8%) |
| Medium Confidence | 14 (13.3%) |
| Low Confidence | 2 (1.9%) |
| Total Tokens Used | 124,582 |
| Estimated API Cost | $3.74 |
| Processing Time | 6 min 32 sec |
| Expert Personas Used | 9 |

---

## Complete Data Flow Example

**User uploads**: 50-page CIPP bid specification PDF

```
┌──────────────────────────────────────────────────────────────┐
│ USER ACTION: Upload "cipp_bid_2024.pdf" (50 pages)           │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ LAYER 0: Document Ingestion                                  │
│   • PyMuPDF extracts 50 pages with text                      │
│   • Output: [(1, text1), (2, text2), ..., (50, text50)]     │
│   • Metadata: {total_pages: 50, chars: 98,000}               │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ LAYER 1: Load Configuration                                  │
│   • Loads "CIPP Analysis v2.0" config                        │
│   • 9 sections, 105 questions                                │
│   • Section map created                                       │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ LAYER 2: Generate 9 Expert Personas                          │
│   FOR EACH SECTION:                                           │
│   • "General Info" → GeneralProjectExpert (generated)        │
│   • "Materials" → MaterialsSpecialist (generated)            │
│   • "Safety" → SafetyComplianceOfficer (generated)           │
│   ... (all 9 generated via AI, cached for reuse)            │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ LAYER 3-6: Process 17 Windows (50 pages ÷ 3)                │
│                                                               │
│ Window 1 (Pages 1-3):                                        │
│   L3: 9 experts process in parallel                          │
│   L4: Accumulate answers (first time, so just append)        │
│   L5: Token usage: 8,234 tokens                              │
│   L6: Display partial results in browser                     │
│                                                               │
│ Window 2 (Pages 4-6):                                        │
│   L3: 9 experts process                                      │
│   L4: Merge new answers with Window 1 results                │
│       • Q1: Similar to W1, merge pages [1,3] + [5] = [1,3,5]│
│       • Q28: New detail found, merge text + pages            │
│   L5: Token usage: 7,892 tokens (total: 16,126)             │
│   L6: Update browser display                                 │
│                                                               │
│ ... (Windows 3-16 process similarly)                        │
│                                                               │
│ Window 17 (Pages 49-50):                                     │
│   L3: Final expert processing                                │
│   L4: Final accumulation                                     │
│       • All 105 questions now have answers                   │
│       • Page citations aggregated across all windows         │
│   L5: Total tokens: 124,582                                  │
│   L6: Display complete unitary log                           │
│                                                               │
│ COMPLETION:                                                   │
│   • All 50 pages processed ✅                                │
│   • All 105 questions answered ✅                            │
│   • All PDF citations preserved ✅                           │
│   • Export ready ✅                                          │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ USER ACTION: Click "Export to Excel"                         │
│                                                               │
│   • Sheet 1: 105 primary answers with citations              │
│   • Sheet 2: All answer variants (if multiple)               │
│   • Sheet 3: Statistics and metadata                         │
│   • Downloaded: cipp_bid_2024_analysis.xlsx                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

1. **Phase 1: Foundation** (Week 1-2)
   - ✅ Fix existing PDF page number bug FIRST
   - ✅ Implement Layer 0 (Document Ingestion) with validation
   - ✅ Implement Layer 1 (Configuration Loader) with JSON schema

2. **Phase 2: Dynamic Experts** (Week 2-3)
   - ✅ Implement Layer 2 (Expert Persona Generation)
   - ✅ Test expert generation with various section types
   - ✅ Build expert cache system

3. **Phase 3: Core Processing** (Week 3-5)
   - ✅ Implement Layer 3 (Multi-Expert Processing)
   - ✅ Parallel execution with asyncio
   - ✅ Page citation validation
   - ✅ Implement Layer 5 (Token Budget Manager)

4. **Phase 4: Smart Accumulation** (Week 5-6)
   - ✅ Implement Layer 4 (Deduplication)
   - ✅ Semantic similarity using embeddings
   - ✅ Information merging logic

5. **Phase 5: Output & Testing** (Week 6-7)
   - ✅ Implement Layer 6 (Compilation & Export)
   - ✅ Browser display with confidence badges
   - ✅ Excel export with all sheets
   - ✅ End-to-end testing with real PDFs

**Total Timeline: 7 weeks**
**Infrastructure: Flask + Redis (optional) = $7-17/mo**

---

## Success Metrics

**Critical Requirements** (Must Have):
- ✅ PDF page numbers display correctly in browser AND exports
- ✅ Zero information loss during deduplication
- ✅ 100% question coverage (all 105 questions answered)
- ✅ 100% page coverage (all pages processed)
- ✅ Token limits respected (no API errors)

**Performance Targets**:
- 50-page document: < 8 minutes total processing
- Parallel expert execution: 3-5 seconds per window
- Answer quality: ≥ 90% accuracy (expert validation)

**Flexibility Goals**:
- Support variable question counts (50-500+)
- Support custom section headings
- Support any document type (PDF, DOCX, TXT)

---

**HOTDOG AI is purpose-built for document analysis, not adapted from another architecture.**

Every layer serves the user's core need: **exhaustive, accurate, citation-perfect bid specification analysis with complete flexibility**.
