from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import ChatMessage

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': 'Отсутствует сообщение'}), 400

    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    conversation_id = data.get('conversation_id', 'default')

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
    messages = ChatMessage.query.filter_by(conversation_id=conversation_id)\
        .order_by(ChatMessage.created_at.asc()).all()
    return jsonify([{
        'role': m.role,
        'content': m.content,
    } for m in messages])
