# ConvFinQA-agent-eval
A prototype LLM agent for answering conversational financial questions using the ConvFinQA dataset, capable of reasoning over text, tables, and figures from financial documents.

We’d like you to please demonstrate a LLM Agent driven prototype that can answer conversational dialogue questions based on financial documents (texts, tables, figures etc.). The dataset we'd like you to use is the train.json of ConvFinQA.

We would like to see what you can build with the data provided. Feel free to present the results in any format you prefer and explore any additional ideas you have with the dataset. You may use any model or architecture of your choice. The goal is to demonstrate your knowledge and experience. We are particularly interested in the logic and reasoning  behind your choice of accuracy metrics and your ability to communicate your solutions and ideas effectively.

ConvFinQA dataset builds the conversation flow based on the decomposition and concatenation of the multi-step reasoning programs (the solutions of the multi-hop questions) in the existing FinQA (Chen et al., 2021) dataset.

What we are looking for:

- A working solution that answers financial questions using semi-structured text.
    - We recommend using an LLM API or a model that runs locally on a standard laptop.
- Clear reasoning behind your chosen solution approach.
- Good coding practices and clear communication of ideas.
    - DRY, modular code
    - Well-organized code with thoughtful levels of abstraction
    - Clear documentation for setup and execution
- Demonstration of your expertise in building LLM-powered applications and understanding of the ecosystem.
- Future improvements you would consider given more time
    - **You don't have to implement all your ideas, but do communicate them to us.**
- An honest assessment of your system's strengths and limitations

Please note:

- A purely RAG (Retrieval-Augmented Generation) solution is insufficient. We expect a solution more appropriate to this task than semantically searching the dataset and generating a response.

Conversation level
The following three files have entries for each full conversation:

train.json (3,037 examples)

Each entry has the following fields:

General fields for all data:
"pre_text": the texts before the table;
"post_text": the text after the table;
"table": the table;
"id": unique example id. 

The "annotation" field contains the major information for the conversations. If the conversation is the Type I simple conversation, i.e., the decomposition from one FinQA question, then we have the following fields for "annotation" fields:

"annotation": {
  "original_program": original FinQA question;
  "dialogue_break": the conversation, as a list of question turns. 
  "turn_program": the ground truth program for each question, corresponding to the list in "dialogue_break".
  "qa_split": this field indicates the source of each question turn - 0 if from the decomposition of the first FinQA question, 1 if from the second. For the Type I simple conversations, this field is all 0s. 
  "exe_ans_list": the execution results of each question turn. 
}
Apart from "annotation" field, we also have the "qa" field for the original FinQA question.

If the conversation is the Type II complex conversation, i.e., the decomposition from two FinQA questions, then "qa_split" field will have set of 0s first (turns from the first FinQA question), then followed by 1s (turns from the second FinQA question). We will also two fields "original_program_0" and "original_program_1" for the two original FinQA questions. Apart from "annotation" field, We have the "qa_0" and "qa_1" fields for the original two FinQA questions.