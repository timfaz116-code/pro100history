from flask import Blueprint, request, jsonify, render_template_string
from app.extensions import db
from app.models import ChatMessage

chatbot_bp = Blueprint('chatbot', __name__)


def ensure_table():
    from sqlalchemy import inspect
    if not inspect(db.engine).has_table('chat_messages'):
        db.create_all()


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': 'Отсутствует сообщение'}), 400

    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    conversation_id = data.get('conversation_id', 'default')

    ensure_table()

    history = ChatMessage.query.filter_by(conversation_id=conversation_id)\
        .order_by(ChatMessage.created_at.asc()).all()

    history_list = [{'role': m.role, 'content': m.content} for m in history]

    user_msg = ChatMessage(conversation_id=conversation_id, role='user', content=message)
    db.session.add(user_msg)
    db.session.commit()

    try:
        from app.chatbot.rag import get_answer
        result = get_answer(message, history_list)
        answer = result.get('answer', '')

        bot_msg = ChatMessage(conversation_id=conversation_id, role='assistant', content=answer)
        db.session.add(bot_msg)
        db.session.commit()

        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка при обработке запроса: {str(e)}'}), 500


@chatbot_bp.route('/api/chat/history', methods=['GET'])
def get_history():
    conversation_id = request.args.get('conversation_id', 'default')
    ensure_table()
    messages = ChatMessage.query.filter_by(conversation_id=conversation_id)\
        .order_by(ChatMessage.created_at.asc()).all()
    return jsonify([{
        'role': m.role,
        'content': m.content,
    } for m in messages])


PDF_VIEWER_TEMPLATE = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Учебник</title>
<style>body{margin:0;height:100vh}embed{width:100%;height:100%}</style>
</head><body><embed src="https://raw.githubusercontent.com/timfaz116-code/pro100history/main/knowledge/history_textbook.pdf#page={{ page }}" type="application/pdf"></body></html>'''


@chatbot_bp.route('/api/pdf/viewer')
def pdf_viewer():
    page = request.args.get('page', '1')
    return render_template_string(PDF_VIEWER_TEMPLATE, page=page)
