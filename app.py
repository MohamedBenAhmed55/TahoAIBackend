import openai
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from flask_cors import CORS


client = OpenAI()

# Import configuration
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Import models
from models import Report

# Set OpenAI API Key
openai.api_key = app.config['OPENAI_API_KEY']

# Home route
@app.route('/')
def home():
    return "Welcome to the Report Management System"

# Get all reports
@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Report.query.all()
    return jsonify([report.to_dict() for report in reports])

# Get report details by id
@app.route('/reports/<int:id>', methods=['GET'])
def get_report(id):
    report = Report.query.get_or_404(id)
    return jsonify(report.to_dict())

from flask import abort

@app.route('/reports', methods=['POST'])
def create_report():
    data = request.json

    # Basic validation
    if not data or 'title' not in data or 'summary' not in data:
        abort(400, description="Invalid input: 'title' and 'summary' are required.")

    report = Report(
        title=data['title'],
        summary=data['summary'],
        content=data.get('content', ''),
        evaluation=data.get('evaluation', 'Needs Review')
    )
    try:
        db.session.add(report)
        db.session.commit()
        # generate_topics(report)
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"An error occurred: {str(e)}")

    return jsonify(report.to_dict()), 201


# Update a report
@app.route('/reports/<int:id>', methods=['PUT'])
def update_report(id):
    report = Report.query.get_or_404(id)
    data = request.json

    report.title = data.get('title', report.title)
    report.summary = data.get('summary', report.summary)
    report.content = data.get('content', report.content)
    report.evaluation = data.get('evaluation', report.evaluation)

    db.session.commit()

    # Re-trigger topic generation
    generate_topics(report)

    return jsonify(report.to_dict())

# Delete a report
@app.route('/reports/<int:id>', methods=['DELETE'])
def delete_report(id):
    report = Report.query.get_or_404(id)
    db.session.delete(report)
    db.session.commit()
    return '', 204

# Generate topics for re-evaluation using OpenAI
def generate_topics(report):
    # Use the new OpenAI API to generate re-evaluation topics
    prompt = f"Based on the following evaluation, generate a list of topics to be re-evaluated: {report.evaluation}"

    # Use the new OpenAI API format
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use "gpt-4" if you prefer
        messages=[
            {"role": "system", "content": "You are an assistant generating topics for report re-evaluation."},
            {"role": "user", "content": prompt}
        ]
    )

    topics = response['choices'][0]['message']['content'].strip()

    # Print or save the generated topics (as needed)
    print(f"Generated topics for report {report.id}: {topics}")


if __name__ == '__main__':
    app.run(debug=True)
