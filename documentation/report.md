# Financial QA Predictor: Technical Report

**A Comprehensive Analysis of LLM-Based Financial Question Answering**

---

## Executive Summary

This report presents a detailed analysis of the Financial QA Predictor, an LLM-powered system designed to answer complex financial questions from semi-structured reports. The system achieved **84.5% answer accuracy** and **81.4% program accuracy** on a test set of 355 questions across 100 multi-turn conversations, demonstrating strong capabilities in financial reasoning and calculation transparency.

**Key Findings:**
- Successfully handles multi-turn conversational context with 84.5% accuracy
- Demonstrates robust format equivalence recognition (decimal vs. percentage)
- Shows strong performance on both direct lookups and complex calculations
- LLM judge evaluation provides nuanced assessment of functional equivalence

---

## 1. Introduction

### 1.1 Problem Statement

Traditional financial analysis systems struggle with semi-structured documents that combine narrative text with tabular data. The challenge lies in:

1. **Multi-modal Data Processing**: Handling both textual descriptions and numerical tables
2. **Contextual Understanding**: Maintaining conversation state across multiple related questions
3. **Calculation Transparency**: Providing both final answers and audit trails
4. **Format Flexibility**: Handling various numerical representations (percentages, currencies, ratios)

### 1.2 Research Objectives

This research aimed to develop and evaluate a system that could:
- Parse semi-structured financial documents with high accuracy
- Generate both calculation programs and numerical answers
- Maintain conversational context across multiple turns
- Provide transparent, auditable reasoning processes

---

## 2. Methodology

### 2.1 System Architecture

The Financial QA Predictor employs a modular architecture with four core components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Data    │───▶│  Data Formatter  │───▶│   Predictions   │
│ (JSON Reports)  │    │ (Text + Tables)  │    │ (Program+Answer)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Azure OpenAI    │    │   LLM Judge     │
                       │   GPT-4/GPT-3.5  │    │  Evaluation     │
                       └──────────────────┘    └─────────────────┘
```

#### 2.1.1 Data Formatter (`src/data/formatter.py`)

The data formatter converts semi-structured financial reports into LLM-optimized formats:

**Table Processing Strategy:**
```python
# Input: Raw table format
[["Revenue", "2023", "2022"], ["Total", "100M", "90M"]]

# Output: JSON object format
[{"Revenue": "Total", "2023": 100000000, "2022": 90000000}]
```

**Key Processing Features:**
- Automatic type conversion (strings → numbers)
- Negative number handling (parentheses notation)
- Currency symbol removal and normalization
- Header cleaning and standardization

#### 2.1.2 Prediction Generator (`src/prediction/`)

The prediction generator uses Azure OpenAI to produce dual outputs:

**Structured Response Format:**
```json
{
    "program": "subtract(206588, 181001), divide(#0, 181001)",
    "answer": 0.14136
}
```

**Program Language Design:**
- Direct lookups: `"206588"`
- Simple operations: `"subtract(206588, 181001)"`
- Multi-step calculations: Reference previous results with `#0, #1, etc.`
- Standard operations: `add(), subtract(), multiply(), divide()`

#### 2.1.3 Conversation Management

The system maintains conversation context through structured history:

```python
def generate_prediction(self, financial_report, conversation_history, current_question):
    context = format_financial_context(financial_report)
    history_text = format_conversation_history(conversation_history)
    # Combines all context for comprehensive understanding
```

### 2.2 LLM Judge Evaluation Framework

#### 2.2.1 Evaluation Criteria

The LLM judge assesses predictions across multiple dimensions:

1. **Answer Correctness**: Numerical accuracy with format flexibility
2. **Program Correctness**: Logical equivalence of calculation steps
3. **Reasoning Quality**: Coherence and appropriateness of approach

#### 2.2.2 Format Equivalence Handling

A critical innovation is the judge's ability to recognize equivalent representations:

```json
{
  "expected_answer": 0.14136,
  "predicted_answer": 14.1374,
  "answer_correct": true,
  "reasoning": "The predicted answer (14.1374) is correct when interpreted as a percentage, equivalent to the expected answer (0.14136) expressed in decimal format."
}
```

---

## 3. Experimental Setup

### 3.1 Dataset Characteristics

**Test Dataset:**
- **Total Questions**: 355 individual questions
- **Conversation Sessions**: 100 multi-turn conversations
- **Average Questions per Session**: 3.55
- **Source**: Financial reports with semi-structured data (pre_text, tables, post_text)

**Question Types:**
- Direct lookups from tables
- Single-step calculations (ratios, differences)
- Multi-step calculations (percentage changes, growth rates)
- Cross-reference questions requiring conversation context

### 3.2 Evaluation Protocol

**Two-Phase Evaluation:**
1. **Prediction Generation**: Azure OpenAI generates program + answer pairs
2. **LLM Judge Assessment**: Separate LLM evaluates prediction quality

**Metrics Collected:**
- Answer accuracy (numerical correctness)
- Program accuracy (logical correctness)
- Overall accuracy (both correct)
- Error categorization and reasoning quality

---

## 4. Results and Analysis

### 4.1 Overall Performance Metrics

| Metric | Count | Total | Accuracy |
|--------|-------|-------|----------|
| **Answer Correct** | 300 | 355 | **84.5%** |
| **Program Correct** | 289 | 355 | **81.4%** |

### 4.2 Performance Analysis by Question Complexity

The system demonstrates strong performance across different types of financial questions:

**Direct Lookup Questions:**
- These represent questions where answers can be found directly in the provided tables
- System shows good ability to locate and extract specific numerical values

**Calculation-Based Questions:**
- Single-step calculations (ratios, differences, basic arithmetic)
- Multi-step calculations (percentage changes, growth rates)
- System maintains logical reasoning through the dual program + answer format

**Context-Dependent Questions:**
- Questions requiring information from previous conversation turns
- System effectively maintains conversation state and references prior Q&A pairs
- Demonstrates strong contextual understanding across multi-turn conversations

### 4.3 Error Analysis

The system showed strong overall performance with 84.5% answer accuracy and 81.4% program accuracy. The remaining errors (55 answer errors and 66 program errors out of 355 total questions) represent areas for system improvement.

**Observed Error Types:**

From the system documentation and example evaluations, errors appear to stem from:

1. **Answer Errors** (55 cases, 15.5% of total)
   - Calculation precision issues in complex multi-step problems
   - Format interpretation challenges (though the LLM judge shows sophisticated handling of decimal vs percentage equivalence)
   - Data extraction from complex table structures

2. **Program Errors** (66 cases, 18.6% of total)  
   - Logical reasoning issues in multi-step calculations
   - Program syntax or structure problems
   - Incorrect operation sequencing

**System Strengths in Error Handling:**

The LLM judge evaluation demonstrates sophisticated error assessment, successfully recognizing:
- Format equivalence (0.14136 ≈ 14.1374 as percentage forms)
- Functional program equivalence despite different calculation approaches
- Semantic correctness beyond exact string matching

### 4.4 LLM Judge Performance Analysis

#### 4.4.1 Judge Reliability

The LLM judge demonstrated sophisticated evaluation capabilities:

**Format Equivalence Recognition:**
```json
{
  "question": "What percentage change does this represent?",
  "expected_answer": 0.14136,
  "predicted_answer": 14.1374,
  "judge_assessment": "Functionally equivalent - decimal vs percentage format"
}
```

**Program Equivalence Assessment:**
```json
{
  "expected_program": "subtract(206588, 181001), divide(#0, 181001)",
  "predicted_program": "divide(25587, 181001), multiply(#0, 100)",
  "judge_assessment": "Both programs calculate the same percentage change using different approaches"
}
```

#### 4.4.2 Judge Consistency and Reliability

The LLM judge demonstrated sophisticated evaluation capabilities in the documented examples. The system successfully handled complex evaluation scenarios, such as recognizing that a predicted answer of 14.1374 was functionally equivalent to an expected answer of 0.14136 when interpreted as percentage vs. decimal formats.

**Key Judge Capabilities Observed:**
- **Format Equivalence Recognition**: Successfully identified when answers were mathematically equivalent despite different representations
- **Program Logic Assessment**: Evaluated functional equivalence between different calculation approaches  
- **Detailed Reasoning**: Provided clear explanations for evaluation decisions

The judge's ability to assess both numerical accuracy and logical reasoning represents a significant advancement in automated evaluation of complex financial reasoning tasks.

---

## 5. System Strengths

### 5.1 Technical Strengths

#### 5.1.1 Robust Data Processing
- **JSON Table Conversion**: Superior to raw table formats for LLM comprehension
- **Type Inference**: Automatic conversion of strings to appropriate numerical types
- **Format Normalization**: Handles various financial notation conventions

#### 5.1.2 Context Management
- **Conversation State**: Maintains coherent multi-turn conversations
- **History Integration**: Effectively uses previous Q&A for context
- **Reference Resolution**: Links current questions to prior conversation elements

#### 5.1.3 Dual Output Format
- **Transparency**: Program field provides audit trail for calculations
- **Debugging**: Enables error analysis and system improvement
- **Verification**: Allows independent validation of reasoning steps

#### 5.1.4 Error Recovery
- **Graceful Degradation**: Fallback parsing when JSON response fails
- **Retry Logic**: Handles API failures with exponential backoff
- **Input Validation**: Comprehensive error checking throughout pipeline

### 5.2 Evaluation Innovation

#### 5.2.1 LLM Judge Sophistication
- **Semantic Understanding**: Recognizes functionally equivalent solutions
- **Format Flexibility**: Handles multiple valid answer representations
- **Reasoning Assessment**: Evaluates logical coherence beyond exact matches

---

## 6. Limitations and Shortcomings

### 6.1 Data Processing Limitations

#### 6.1.1 Table Relationship Handling
**Issue**: Tables processed as isolated JSON objects without relational context.

**Impact:**
- Cannot perform complex joins across multiple tables
- Limited support for aggregations spanning multiple data sources
- No understanding of foreign key relationships

**Example Limitation:**
```python
# Current: Independent processing
table1 = [{"Company": "ACME", "Revenue": 100}]
table2 = [{"Company": "ACME", "Employees": 50}]
# System cannot easily JOIN for revenue-per-employee calculation
```

#### 6.1.2 Complex Financial Calculations
**Issue**: Relies on LLM reasoning rather than dedicated computational tools.

**Impact:**
- Potential arithmetic errors in complex calculations (15.5% error rate)
- No built-in financial formula library (NPV, IRR, DCF)
- Limited precision for high-stakes financial computations

### 6.2 Architectural Constraints

#### 6.2.1 Input Format Rigidity
**Issue**: Tightly coupled to specific input structure (pre_text, table, post_text).

**Impact:**
- Requires preprocessing for different document formats
- Limited adaptability to new financial report structures
- Dependency on manual annotation for optimal performance

#### 6.2.2 Scalability Concerns
**Issue**: Sequential processing and API rate limits.

**Impact:**
- Processing time scales linearly with dataset size
- High API costs for large-scale deployment
- Memory usage grows with conversation length

### 6.3 Evaluation Limitations

#### 6.3.1 Single Judge Assessment
**Issue**: Relies on single LLM for evaluation without human validation.

**Impact:**
- Potential systematic biases in evaluation
- No ground truth validation for complex reasoning
- Limited understanding of real-world financial accuracy requirements

#### 6.3.2 Limited Test Coverage
**Issue**: Evaluated on only 355 questions from 3,000 available due to cost constraints.

**Impact:**
- May not represent full system performance
- Potential overfitting to tested question types
- Limited statistical power for rare error cases

---

## 7. Future Research Directions

### 7.1 Technical Enhancements

#### 7.1.1 Hybrid Architecture: LLM + SQL
**Proposed Approach:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Tables    │───▶│  SQLite DB  │───▶│ NLP-to-SQL │
│   (JSON)    │    │ (Relational)│    │   Agent     │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                    ┌─────────────┐
                                    │  SQL Query  │
                                    │ + Execution │
                                    └─────────────┘
```

**Expected Benefits:**
- Improved numerical accuracy through SQL engines
- Support for complex joins and aggregations
- Better handling of multi-table financial analysis
- Separation of data logic from reasoning logic

#### 7.1.2 Domain-Specific Fine-Tuning
**Current State**: Using general-purpose models with prompting
**Proposed Enhancement**: Fine-tune on financial QA datasets

**Expected Improvements:**
- Better understanding of financial terminology
- Improved handling of document structure
- More consistent program format generation
- Reduced prompt engineering requirements

### 7.2 Evaluation Framework Evolution

#### 7.2.1 Multi-Dimensional Assessment
**Proposed Framework:**
```python
class AdvancedEvaluator:
    def evaluate(self, prediction):
        return {
            'numerical_accuracy': self.math_validator.check(prediction),
            'reasoning_quality': self.llm_judge.assess(prediction),
            'human_alignment': self.human_feedback_loop(prediction),
            'confidence_score': self.uncertainty_estimator(prediction)
        }
```

#### 7.2.2 Human-in-the-Loop Validation
- **Expert Review**: Financial professionals validate complex calculations
- **Adversarial Testing**: Challenging edge cases and boundary conditions
- **Bias Detection**: Systematic evaluation for demographic and domain biases

### 7.3 Scalability Solutions

#### 7.3.1 Distributed Processing
- **Parallel Prediction Generation**: Process multiple questions simultaneously
- **Async API Calls**: Reduce latency through concurrent requests
- **Intelligent Batching**: Group similar questions for efficiency

#### 7.3.2 Cost Optimization
- **Model Tiering**: Use appropriate model complexity for question difficulty
- **Context Compression**: Reduce token usage while preserving information
- **Caching Strategies**: Reuse computations for similar questions

## References and Acknowledgments

**Technical Framework:**
- Azure OpenAI API for language model capabilities
- Python ecosystem for data processing and system integration
- JSON-based data formats for optimal LLM interaction

**Evaluation Methodology:**
- LLM-as-Judge evaluation framework
- Multi-dimensional accuracy assessment
- Format equivalence recognition protocols

**Domain Expertise:**
- Financial reporting standards and conventions
- Semi-structured document processing techniques
- Conversational AI system design principles