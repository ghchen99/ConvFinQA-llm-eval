# ConvFinQA-Agent Evaluation Task Specification (Refined)

## Objective

Design and implement a **prototype LLM agent** capable of answering **multi-turn, conversational financial questions** using **semi-structured documents**. The prototype must be capable of **multi-step numerical and logical reasoning** over **text, tables, and figures** within financial reports, leveraging the **ConvFinQA dataset (train.json)**.

## Dataset Summary

The dataset consists of **3,037 conversation examples**. Each entry simulates a financial question answering scenario built from **financial report documents**, with the conversation evolving through **multi-step reasoning**.

Given a financial report containing both the textual content and structured table, the user asks a sequence of questions where later questions may depend on previous questions to answer. The target is to generate the reasoning program to be executed to get the answer to the last question:

| Field | Description |
|-------|-------------|
| `pre_text` | Text appearing before the financial table in the original document (e.g., notes on share repurchases, description of performance graph) |
| `post_text` | Text appearing after the financial table |
| `filename` | Source document identifier (e.g., "UPS/2009/page_33.pdf") |
| `table_ori` | The original financial table data |
| `table` | Normalized version of the financial table |
| `id` | Unique identifier for the dataset entry |

### Question-Answer Components

Each entry typically contains one or two original FinQA questions (`qa_0` and `qa_1`), which include:

| Field | Description |
|-------|-------------|
| `question` | The natural language question (e.g., "what is the roi of an investment in ups in 2004 and sold in 2006?") |
| `answer` | The correct numerical or textual response (e.g., "-8.9%") |
| `explanation` | Additional context or explanation (may be empty) |
| `ann_table_rows` | The table rows annotated as relevant to the question |
| `steps` | The mathematical operations to derive the answer, with specific operators, arguments, and results |
| `program` | The execution program in a structured format (e.g., "subtract(91.06, const_100), divide(#0, const_100)") |
| `gold_inds` | The relevant table content used for answering |
| `exe_ans` | The numerical answer (e.g., -0.0894) |
| `program_re` | Alternative representation of the program |

### Conversational Breakdown

The `annotation` field breaks down the complex financial questions into a multi-turn conversation:

| Field | Description |
|-------|-------------|
| `dialogue_break` | The conversation turns split into individual questions |
| `turn_program` | The required calculation program at each conversation turn |
| `qa_split` | Indicates which original FinQA question each turn belongs to (0 or 1) |
| `exe_ans_list` | The expected numerical answers for each conversation turn |
| `original_program_0` | The calculation program for the first FinQA question |
| `original_program_1` | The calculation program for the second FinQA question |
| `step_list` | The sequence of operations needed across all turns |
| `answer_list` | The corresponding results of each operation |

Types of Conversations:
* **Type I (Simple)**: Derived from a single FinQA program
* **Type II (Complex)**: Combines two FinQA programs in one conversation

## Deliverables

You are expected to build a **working prototype** that:
* Accepts a **conversational question** and returns a **context-aware, numerically and logically sound answer**
* Is capable of **multi-step reasoning**, not just direct retrieval or generation
* Uses the `train.json` ConvFinQA file as its primary data source

You may use **any model or architecture** (LLM APIs, local models, hybrid neural-symbolic systems, etc.).

## What We Are Looking For

### ✅ Technical Capabilities
* Correctness and reasoning through **multi-step numerical operations**
* Understanding of **context across turns** in a conversation
* Use of **structured data (tables)** and **unstructured data (text)**

### ✅ Solution Quality
* Logical decomposition of financial questions
* Use of **program execution** or **intermediate reasoning steps**
* Not solely reliant on RAG (Retrieval-Augmented Generation)

### ✅ Code Quality
* DRY principles and modular structure
* Good documentation and clear abstraction levels
* Reproducibility (instructions for setup and running)

### ✅ Communication
* Clear explanation of:
   * System architecture and data processing pipeline
   * Reasoning approach and design decisions
   * Accuracy metrics used and why
   * Future ideas/improvements
   * Honest assessment of strengths and limitations

## Evaluation Expectations

Your submission will be evaluated based on:
* **Functionality**: Can the system correctly follow and respond to multi-turn financial questions?
* **Reasoning**: Does it perform correct intermediate logical and mathematical steps?
* **Architecture Design**: Is the solution clean, modular, and extensible?
* **Analysis**: Are your metrics and evaluation methodology well-justified?
* **Creativity**: Did you go beyond basic solutions (e.g., basic semantic retrieval)?

## Future Improvements (Optional, but Encouraged)

Please describe:
* What improvements or optimizations you would prioritize next (e.g., graph reasoning, better number extraction, symbolic execution)
* How you might scale or productionize this system
* Ideas for extending to multimodal inputs (e.g., images of figures)

## Clarification Summary

| Aspect | Expectation |
|--------|-------------|
| Dataset | ConvFinQA `train.json` only |
| Input | Multi-turn questions involving tables, text, and logic |
| Output | Answers to each turn, possibly with intermediate steps |
| Modeling Approach | Open (LLMs, hybrid, programmatic reasoning encouraged) |
| No-go for RAG-only | RAG without reasoning or program execution is insufficient |
| Evaluation Criteria | Accuracy, reasoning ability, modular code, documentation, and clarity |
| Optional Add-ons | Error analysis, visualizations, future roadmap |
