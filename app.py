from flask import Flask, render_template, request, jsonify, session
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from typing import List
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Pydantic models for structured output
class QuizOption(BaseModel):
    text: str = Field(description="The text of this answer option")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="Exactly 4 answer options")
    correct_index: int = Field(description="Index (0-3) of the correct answer")
    reasoning: List[str] = Field(description="Exactly 4 explanations, one for each option explaining why it's correct or incorrect")

class QuizSet(BaseModel):
    questions: List[QuizQuestion] = Field(description="Exactly 5 quiz questions")

# Initialize Claude model
llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@app.route('/')
def index():
    return render_template('quiz.html')

@app.route('/generate', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topic', '').strip()

    if not topic:
        return jsonify({'error': 'Please provide a topic'}), 400

    # Create structured output LLM - let langchain pick the right method for Anthropic
    structured_llm = llm.with_structured_output(QuizSet)

    # Generate questions
    prompt = f"""Create a multiple choice quiz about the topic: {topic}

You must generate exactly 5 quiz questions.

For each question, provide:
1. A clear, educational question text
2. Exactly 4 answer options (as a list of strings)
3. The correct_index (0, 1, 2, or 3) indicating which option is correct
4. Exactly 4 reasoning explanations (as a list of strings) - one for each option explaining why it's correct or incorrect

Example reasoning for an incorrect option: "This is incorrect because..."
Example reasoning for the correct option: "This is correct because..."

Make the questions educational and appropriate difficulty for someone learning about {topic}."""

    try:
        quiz_set = structured_llm.invoke(prompt)

        # Convert to format frontend expects
        questions = []
        for idx, q in enumerate(quiz_set.questions):
            questions.append({
                'id': idx + 1,
                'question': q.question,
                'options': q.options,
                'correct': q.correct_index,
                'reasoning': q.reasoning
            })

        # Store in session for grading
        session['questions'] = questions

        return jsonify({'questions': questions})

    except Exception as e:
        import traceback
        print(f"Error generating quiz: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to generate quiz: {str(e)}'}), 500

@app.route('/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    answers = data.get('answers', {})
    questions = session.get('questions', [])

    if not questions:
        return jsonify({'error': 'No quiz in session'}), 400

    score = 0
    results = []

    for question in questions:
        qid = str(question['id'])
        user_answer = int(answers.get(qid, -1))
        is_correct = user_answer == question['correct']

        if is_correct:
            score += 1

        results.append({
            'question': question['question'],
            'correct': is_correct,
            'user_answer': question['options'][user_answer] if 0 <= user_answer < len(question['options']) else 'No answer',
            'correct_answer': question['options'][question['correct']],
            'reasoning': question['reasoning'][user_answer] if 0 <= user_answer < len(question['reasoning']) else ''
        })

    return jsonify({
        'score': score,
        'total': len(questions),
        'percentage': round((score / len(questions)) * 100, 1),
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
