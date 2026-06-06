from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': 'Отсутствует сообщение'}), 400

    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    try:
        from app.chatbot.rag import get_answer
        result = get_answer(message)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Ошибка при обработке запроса: {str(e)}'}), 500
