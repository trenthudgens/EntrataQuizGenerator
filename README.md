# AI Quiz Generator

A Flask-based quiz app that uses Claude AI (via Langchain) to generate custom multiple choice quizzes on any topic.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key as an environment variable:
```bash
# Linux/Mac
export ANTHROPIC_API_KEY=your_actual_api_key_here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_actual_api_key_here"
```

3. Run the app:
```bash
python app.py
```

4. Open your browser to: `http://localhost:5000`

## How It Works

1. User enters a topic (e.g., "photosynthesis", "neural networks", "ancient rome")
2. Claude AI generates 5 custom multiple choice questions via Langchain
3. Questions are validated using Pydantic models for structured output
4. User completes the quiz and receives instant feedback

## Tech Stack

- **Backend**: Flask
    - Selected due to familiarity, and not needing the extra overhead of Django.
- **AI**: Claude 4.5 Sonnet via Langchain
    - My favorite model - Proven accuracy, professionalism, and low levels of risk.
    - I used Langchain to handle LLM flow since I am familiar with Langchain4J and this project was a great way to get familiar with Pydantic and Langchain in it's native language.
- **Validation**: Pydantic for structured outputs
    - Forces LLM to respond in structured formats, prevents type errors and overall improves reliability
- **Frontend**: Vanilla JavaScript with clean CSS
    - Single page app to reduce number of moving parts. I didn't want a bunch of frontend dependencies.

## Overview Of Major Design Elements
### 1. Pydantic Models (Structured Output Schema)

```python
class QuizQuestion(BaseModel):
    question: str              # The question text
    options: List[str]         # Exactly 4 answer options
    correct_index: int         # Index (0-3) of correct answer
    reasoning: List[str]       # 4 explanations (one per option) - This prevents two separate calls to the LLM

class QuizSet(BaseModel):
    questions: List[QuizQuestion]  # Exactly 5 questions
```
### 2. Flask

  - Initializes with random secret key for session management
  - Sessions store quiz questions for grading

### 3. /generate Endpoint (POST)

  - Takes topic from request JSON
  - Creates structured LLM with QuizSet schema
  - Sends prompt to Claude requesting 5 questions with reasoning
  - Stores questions in session
  - Returns questions to frontend

### 4. /submit Endpoint (POST)

  - Takes user answers from request JSON
  - Retrieves stored questions from session
  - Compares each answer to correct index
  - Returns score, percentage, and detailed results including:
    - User's answer
    - Correct answer
    - Reasoning for wrong answers


## Challenges
- Claude Code issues:
    - Sonnet 4.5 had some trouble using up-to-date info just due to the model training cutoff date
    - It didn't know that 4.5 had been released
    - Old knowledge of langchain
    - Wanted to use too many dependencies and overall wanted to write verbose code, which had to be curbed via prompting and manual edits
- Environment issues:
    - I hadn't install