from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'w') as f:
        json.dump({"total": 0, "answers": {}}, f)

QUESTIONS = [
]

@app.route('/')
def index():
    return render_template('index.html', questions=QUESTIONS)

@app.route('/submit', methods=[''])
def submit():
    if request.method != '':
        return redirect(url_for('index'))

    answers = {}
    for q in QUESTIONS:
        answer = request.form.get(f'q{q["id"]}')
        if answer:
            answers[str(q["id"])] = answer

    try:
        with open(RESULTS_FILE, 'r+') as f:
            data = json.load(f)
            data['total'] += 1
            for q_id, answer in answers.items():
                if q_id not in data['answers']:
                    data['answers'][q_id] = {}
                if answer not in data['answers'][q_id]:
                    data['answers'][q_id][answer] = 0
                data['answers'][q_id][answer] += 1
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")

    return redirect(url_for('results'))

@app.route('/results')
def results():
    try:
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"total": 0, "answers": {}}

    results_data = []
    for q in QUESTIONS:
        q_id = str(q['id'])
        if q_id in data['answers']:
            question_results = []
            total_for_question = sum(data['answers'][q_id].values())
            for option in q['options']:
                count = data['answers'][q_id].get(option, 0)
                percentage = (count / total_for_question) * 100 if total_for_question > 0 else 0
                question_results.append({
                    'option': option,
                    'count': count,
                    'percentage': round(percentage, 1)
                })
            results_data.append({
                'question': q['text'],
                'results': question_results
            })

    return render_template('results.html',
                         total_responses=data['total'],
                         results=results_data)

if __name__ == "__main__":
    app.run(debug=True)