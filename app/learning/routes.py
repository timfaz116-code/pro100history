import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Topic, Task, TestResult, UserTopicProgress
from app.extensions import db

learning_bp = Blueprint('learning', __name__)


@learning_bp.route('/topics')
@login_required
def topics():
    all_topics = Topic.query.order_by(Topic.sort_order).all()
    topic_list = []
    for t in all_topics:
        up = UserTopicProgress.query.filter_by(
            user_id=current_user.id, topic_id=t.id
        ).first()
        progress = up.progress_percent if up else 0
        status = up.status if up else 'not_started'
        topic_list.append({
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'materials_count': t.materials_count,
            'tasks_count': t.tasks_count,
            'progress': progress,
            'status': status,
        })
    return render_template('learning/topics.html', topics=topic_list)


@learning_bp.route('/tasks/<int:topic_id>')
@login_required
def tasks(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    all_tasks = Task.query.filter_by(topic_id=topic_id).all()
    tasks_data = []
    for t in all_tasks:
        tasks_data.append({
            'id': t.id,
            'question': t.question,
            'options': json.loads(t.options),
            'correct_answer': t.correct_answer,
            'explanation': t.explanation,
        })
    return render_template('learning/tasks.html', topic=topic, tasks=tasks_data)


@learning_bp.route('/submit_test', methods=['POST'])
@login_required
def submit_test():
    data = request.get_json()
    topic_id = data.get('topic_id')
    answers = data.get('answers', {})

    topic = Topic.query.get_or_404(topic_id)
    all_tasks = Task.query.filter_by(topic_id=topic_id).all()

    correct = 0
    total = len(all_tasks)
    details = []

    for task in all_tasks:
        user_answer = answers.get(str(task.id), '')
        is_correct = user_answer == task.correct_answer
        if is_correct:
            correct += 1
        details.append({
            'question': task.question,
            'user_answer': user_answer,
            'correct_answer': task.correct_answer,
            'explanation': task.explanation,
            'is_correct': is_correct,
        })

    percent = round((correct / total) * 100) if total > 0 else 0

    result = TestResult(
        user_id=current_user.id,
        topic_id=topic_id,
        score=correct,
        total=total,
        answers=json.dumps(answers, ensure_ascii=False),
    )
    db.session.add(result)

    up = UserTopicProgress.query.filter_by(
        user_id=current_user.id, topic_id=topic_id
    ).first()
    if not up:
        up = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id,
            progress_percent=0,
            status='not_started',
        )
        db.session.add(up)

    if percent >= 80:
        up.progress_percent = 100
        up.status = 'completed'
    elif percent >= 40:
        up.progress_percent = 50
        up.status = 'in_progress'
    else:
        up.progress_percent = 10
        up.status = 'in_progress'

    db.session.commit()

    return jsonify({
        'correct': correct,
        'total': total,
        'percent': percent,
        'details': details,
    })


@learning_bp.route('/test_result/<int:result_id>')
@login_required
def test_result(result_id):
    result = TestResult.query.get_or_404(result_id)
    if result.user_id != current_user.id:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    topic = Topic.query.get(result.topic_id)
    return render_template(
        'learning/test_result.html',
        result=result,
        topic=topic,
    )
