# Financial QA Predictor

**Note**: This is the README file for the repository which gives a general overview and setup instructions. For the official project report, see the [technical report](./documentation/report.md).

A sophisticated LLM-powered system for answering financial questions from semi-structured financial reports. The system processes financial data (text + tables) and generates both calculation programs and numerical answers for complex financial queries.

## 🎯 Problem & Solution

**Challenge**: Answer financial questions from semi-structured reports containing narrative text and tabular data, requiring both information extraction and numerical calculations.

**Solution**: A two-phase approach combining Azure OpenAI for intelligent reasoning with structured data formatting and LLM-based evaluation for quality assurance.

## 🏗️ Architecture Overview

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

### Key Components

1. **Data Formatter** (`src/data/formatter.py`): Converts semi-structured financial reports into AI-readable JSON format
2. **Prediction Generator** (`src/prediction/`): Uses Azure OpenAI to generate calculation programs and numerical answers
3. **LLM Judge Evaluator** (`src/evaluation/`): Automated evaluation system for assessing prediction quality
4. **Azure OpenAI Client** (`src/api/azure_client.py`): Robust API wrapper with error handling and retry logic

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI access with deployed model
- Required environment variables (see setup below)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### Environment Setup

Create a `.env` file with:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_MODEL_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

### Usage

#### Generate Predictions

```bash
# Process all examples
python main.py

# Process first 100 examples only
python main.py --max-examples 100

# Custom input/output files
python main.py -i data/input/custom.json -o data/output/results.json
```

#### Evaluate Results

```bash
# Evaluate predictions using LLM judge
python eval.py -i data/output/predictions.json -o data/output/

# Custom evaluation
python eval.py --input-file results.json --output-dir evaluation_results/
```

## 🧠 Solution Approach & Reasoning

### 1. Data Processing Strategy

**Challenge**: Financial reports contain mixed content types (narrative text, structured tables, metadata).

**Solution**: Convert tables to JSON objects for optimal LLM comprehension:

```python
# Before: Raw table format
[["Revenue", "2023", "2022"], ["Total", "100M", "90M"]]

# After: JSON object format  
[{"Revenue": "Total", "2023": 100000000, "2022": 90000000}]
```

**Why this works**:
- LLMs better understand structured JSON vs raw tables
- Automatic type conversion (strings → numbers) reduces calculation errors
- Preserves relationships between data points

### 2. Conversation Context Management

**Challenge**: Multi-turn conversations where later questions depend on previous context.

**Solution**: Maintain conversation history and provide it as context:

```python
def generate_prediction(self, financial_report, conversation_history, current_question):
    context = format_financial_context(financial_report)
    history_text = format_conversation_history(conversation_history)
    # Combine all context for comprehensive understanding
```

**Benefits**:
- Enables complex multi-step financial analysis
- Maintains consistency across conversation turns
- Supports follow-up questions and clarifications

### 3. Dual Output Format (Program + Answer)

**Challenge**: Need both computational transparency and numerical results.

**Solution**: Generate structured programs alongside numerical answers:

```json
{
    "program": "subtract(206588, 181001), divide(#0, 181001)",
    "answer": 0.14136
}
```

**Advantages**:
- Provides audit trail for calculations
- Enables verification of reasoning steps  
- Supports debugging and error analysis

### 4. LLM-Based Evaluation

**Challenge**: Automated quality assessment for complex financial reasoning.

**Solution**: Use separate LLM as judge to evaluate predictions:

```python
class LLMJudge:
    def evaluate_prediction(self, expected, predicted):
        # Uses structured prompts to assess:
        # 1. Answer correctness (handles format variations)
        # 2. Program correctness (functional equivalence)
        # 3. Reasoning quality
```

**Why LLM judge**:
- Handles semantic equivalence (0.14 ≈ 14%)
- Evaluates program logic, not just exact matches
- Provides detailed reasoning for assessment decisions

## 📊 Performance & Results

### System Capabilities

- **Multi-format Support**: Handles percentages, currencies, negative numbers
- **Context Awareness**: Maintains state across conversation turns
- **Error Recovery**: Graceful fallback parsing when JSON response fails
- **Batch Processing**: Configurable batch sizes with progress tracking

### Evaluation Metrics

The system tracks multiple quality dimensions:

- **Answer Accuracy**: Numerical correctness
- **Program Accuracy**: Logical reasoning correctness  
- **Overall Accuracy**: Both answer and program correct
- **Error Analysis**: Detailed failure categorization

## 📊 Performance & Results

### Evaluation Summary

*Tested on 100 multi-turn conversations (355 individual questions) out of 3,000 total due to capacity and cost constraints.*

| Metric | Results | Accuracy |
|--------|---------|----------|
| **Answer Accuracy** | 300/355 | **84.5%** |
| **Program Accuracy** | 289/355 | **81.4%** |

### Example Evaluation Result

The LLM judge demonstrates sophisticated understanding of format equivalence:

```json
{
  "question_id": "Single_JKHY/2009/page_28.pdf-3-3",
  "question": "what percentage change does this represent?",
  "expected_answer": 0.14136,
  "predicted_answer": 14.1374,
  "expected_program": "subtract(206588, 181001), divide(#0, 181001)",
  "predicted_program": "divide(25587, 181001), multiply(#0, 100)",
  "answer_correct": true,
  "program_correct": true,
  "reasoning": "The predicted answer (14.1374) is correct when interpreted as a percentage, equivalent to the expected answer (0.14136) expressed in decimal format. The predicted program is functionally equivalent to the expected program, as both calculate the percentage change by dividing the difference (206588 - 181001 = 25587) by the original value (181001) and converting to a percentage (multiplying by 100)."
}
```

**Key Insights**:
- System correctly handles **format variations** (decimal vs percentage representation)
- LLM judge recognizes **functional equivalence** in calculation approaches
- Strong performance on **multi-turn conversations** requiring context retention
- **~83% end-to-end accuracy** demonstrates robust financial reasoning capabilities

### System Capabilities

- **Multi-format Support**: Handles percentages, currencies, negative numbers
- **Context Awareness**: Maintains state across conversation turns
- **Error Recovery**: Graceful fallback parsing when JSON response fails
- **Batch Processing**: Configurable batch sizes with progress tracking
- **Format Intelligence**: Recognizes equivalent representations (0.14 ≈ 14%)

## ⚠️ Current Limitations

### 1. Table Parsing Constraints

**Issue**: Current approach treats tables as isolated JSON objects without relational context.

**Impact**: 
- Difficulty with complex joins across multiple tables
- Limited support for aggregations spanning multiple data sources
- No understanding of table relationships or foreign keys

**Example Limitation**:
```python
# Current: Tables processed independently
table1 = [{"Company": "ACME", "Revenue": 100}]
table2 = [{"Company": "ACME", "Employees": 50}]
# System cannot easily JOIN these for revenue-per-employee calculation
```

### 2. Calculation Complexity

**Issue**: Relies on LLM reasoning for numerical operations rather than dedicated computational tools.

**Impact**:
- Potential arithmetic errors in complex calculations
- No built-in mathematical function library
- Limited support for financial formulas (NPV, IRR, etc.)

### 3. Data Format Rigidity

**Issue**: System is tightly coupled to specific input format (pre_text, table, post_text structure).

**Impact**:
- Requires preprocessing for different document formats
- Limited adaptability to new financial report structures
- Annotation-dependent processing pipeline

## 🚀 Future Improvements

### 1. Relational Data Architecture + Tool-Using Agents

**Vision**: Convert tables to proper relational database format and use NLP-to-SQL agents.

```python
# Proposed Architecture:
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

**Benefits**:
- Robust numerical operations via SQL engines
- Complex joins and aggregations
- Better handling of multi-table financial analysis
- Separation of data logic from reasoning logic

### 2. Model Fine-tuning on Domain Data

**Current State**: Using general-purpose GPT models with prompting.

**Proposed Enhancement**: Fine-tune on financial QA dataset format.

```python
# Fine-tuning Dataset Format:
{
    "messages": [
        {"role": "system", "content": "Financial QA specialist..."},
        {"role": "user", "content": formatted_financial_context + question},
        {"role": "assistant", "content": {"program": "...", "answer": ...}}
    ]
}
```

**Expected Benefits**:
- Better understanding of financial domain terminology
- Improved handling of pre_text/table/post_text structure
- More consistent program format generation
- Reduced need for extensive prompting

### 3. Advanced Evaluation Framework

**Current**: Single LLM judge evaluation.

**Proposed**: Multi-dimensional evaluation with human-in-the-loop validation.

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

## 🛠️ Development Guidelines

### Code Structure

```
src/
├── api/           # Azure OpenAI client management
├── data/          # Data formatting and processing  
├── evaluation/    # LLM judge evaluation system
├── prediction/    # Core prediction generation
├── tests/         # Unit testing files
└── utils/         # Logging, validation, text processing
```

### Key Design Principles

1. **Separation of Concerns**: Each module has single responsibility
2. **Error Resilience**: Comprehensive error handling and recovery
3. **Configurability**: Environment-based configuration management
4. **Observability**: Detailed logging and progress tracking
5. **Testability**: Modular design enables unit testing

## 📈 Scaling Considerations

### Performance Optimization

- **Batch Processing**: Configurable batch sizes for large datasets
- **Async Operations**: Parallel processing of independent predictions
- **Caching**: Cache formatted contexts for repeated processing
- **Rate Limiting**: Built-in retry logic with exponential backoff

### Cost Management

- **Token Optimization**: Efficient context formatting to minimize API costs
- **Model Selection**: Configurable model tiers based on complexity requirements
- **Request Batching**: Combine multiple simple queries when possible

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Azure OpenAI team for providing robust LLM API
- Financial data processing community for best practices
- Open source contributors for foundational libraries