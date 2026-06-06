from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import Lesson, Topic, TestResult, UserTopicProgress, Task

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def dashboard():
    lessons = Lesson.query.filter(
        Lesson.status == 'planned'
    ).order_by(Lesson.date).limit(5).all()

    topics = Topic.query.order_by(Topic.sort_order).all()
    total_topics = len(topics)
    completed_topics = UserTopicProgress.query.filter_by(
        user_id=current_user.id, status='completed'
    ).count()

    total_progress = 0
    if total_topics > 0:
        total_progress = round((completed_topics / total_topics) * 100)

    results = TestResult.query.filter_by(user_id=current_user.id).all()
    total_tests = len(results)
    avg_score = 0
    if total_tests > 0:
        avg_score = round(sum(r.score / r.total * 100 for r in results) / total_tests)

    recent_results = TestResult.query.filter_by(
        user_id=current_user.id
    ).order_by(TestResult.completed_at.desc()).limit(5).all()

    weak_topics = []
    strong_topics = []
    for t in topics:
        tr = TestResult.query.filter_by(user_id=current_user.id, topic_id=t.id).all()
        if tr:
            avg = sum(r.score / r.total * 100 for r in tr) / len(tr)
            if avg < 40:
                weak_topics.append({'name': t.name, 'avg': round(avg)})
            elif avg >= 80:
                strong_topics.append({'name': t.name, 'avg': round(avg)})

    return render_template(
        'dashboard/dashboard.html',
        lessons=lessons,
        total_progress=total_progress,
        total_topics=total_topics,
        completed_topics=completed_topics,
        total_tests=total_tests,
        avg_score=avg_score,
        recent_results=recent_results,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
    )


@dashboard_bp.route('/schedule')
@login_required
def schedule():
    lessons = Lesson.query.order_by(Lesson.date).all()
    return render_template('dashboard/schedule.html', lessons=lessons)


@dashboard_bp.route('/progress')
@login_required
def progress():
    topics = Topic.query.order_by(Topic.sort_order).all()
    total_topics = len(topics)
    completed_topics = UserTopicProgress.query.filter_by(
        user_id=current_user.id, status='completed'
    ).count()

    total_progress = 0
    if total_topics > 0:
        total_progress = round((completed_topics / total_topics) * 100)

    results = TestResult.query.filter_by(user_id=current_user.id).all()
    total_tests = len(results)
    total_tasks_done = sum(r.total for r in results)
    avg_score = 0
    if total_tests > 0:
        avg_score = round(sum(r.score / r.total * 100 for r in results) / total_tests)

    topic_progress_list = []
    for t in topics:
        up = UserTopicProgress.query.filter_by(
            user_id=current_user.id, topic_id=t.id
        ).first()
        progress_pct = up.progress_percent if up else 0
        status = up.status if up else 'not_started'

        tr = TestResult.query.filter_by(user_id=current_user.id, topic_id=t.id).all()
        topic_avg = 0
        if tr:
            topic_avg = round(sum(r.score / r.total * 100 for r in tr) / len(tr))

        topic_progress_list.append({
            'name': t.name,
            'description': t.description,
            'progress': progress_pct,
            'status': status,
            'avg_score': topic_avg,
            'tasks_count': t.tasks_count,
            'materials_count': t.materials_count,
        })

    weak_topics = [tp for tp in topic_progress_list if tp['avg_score'] > 0 and tp['avg_score'] < 40]
    strong_topics = [tp for tp in topic_progress_list if tp['avg_score'] >= 80]

    return render_template(
        'dashboard/progress.html',
        total_progress=total_progress,
        total_topics=total_topics,
        completed_topics=completed_topics,
        total_tests=total_tests,
        total_tasks_done=total_tasks_done,
        avg_score=avg_score,
        topic_progress_list=topic_progress_list,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
    )
