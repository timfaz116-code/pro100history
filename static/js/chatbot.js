document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('chatbotBtn');
    var widget = document.getElementById('chatbotWidget');
    var overlay = document.getElementById('chatbotOverlay');
    var closeBtn = document.getElementById('chatbotClose');
    var messagesEl = document.getElementById('chatbotMessages');
    var input = document.getElementById('chatbotInput');
    var sendBtn = document.getElementById('chatbotSend');

    if (!btn || !widget) return;

    function openChat() {
        widget.classList.add('chatbot-widget--open');
        overlay.classList.add('chatbot-overlay--visible');
        input.focus();
    }

    function closeChat() {
        widget.classList.remove('chatbot-widget--open');
        overlay.classList.remove('chatbot-overlay--visible');
    }

    btn.addEventListener('click', openChat);
    closeBtn.addEventListener('click', closeChat);
    overlay.addEventListener('click', closeChat);

    function addMessage(text, isUser) {
        var div = document.createElement('div');
        div.className = 'chatbot-message chatbot-message--' + (isUser ? 'user' : 'bot');

        if (!isUser) {
            var avatar = document.createElement('div');
            avatar.className = 'chatbot-message__avatar';
            avatar.textContent = 'И';
            div.appendChild(avatar);
        }

        var content = document.createElement('div');
        content.className = 'chatbot-message__content';

        if (isUser) {
            var p = document.createElement('p');
            p.textContent = text;
            content.appendChild(p);
        } else {
            content.innerHTML = text;
        }

        div.appendChild(content);
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping() {
        var div = document.createElement('div');
        div.className = 'chatbot-message chatbot-message--bot';
        div.id = 'chatbotTyping';
        var avatar = document.createElement('div');
        avatar.className = 'chatbot-message__avatar';
        avatar.textContent = 'И';
        div.appendChild(avatar);
        var content = document.createElement('div');
        content.className = 'chatbot-message__content';
        content.innerHTML = '<div class="chatbot-typing"><span></span><span></span><span></span></div>';
        div.appendChild(content);
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function hideTyping() {
        var typing = document.getElementById('chatbotTyping');
        if (typing) typing.remove();
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    function sendMessage() {
        var text = input.value.trim();
        if (!text) return;

        addMessage(text, true);
        input.value = '';
        input.focus();
        showTyping();

        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }),
        })
            .then(function (res) {
                if (!res.ok) return res.json().then(function (d) { throw new Error(d.error || 'Ошибка сервера'); });
                return res.json();
            })
            .then(function (data) {
                hideTyping();
                if (data.error) {
                    addMessage('<p class="chatbot-error">' + escapeHtml(data.error) + '</p>', false);
                    return;
                }
                var answer = data.answer || 'Не удалось получить ответ.';
                var html = '<p>' + escapeHtml(answer).replace(/\n/g, '<br>') + '</p>';
                if (data.sources && data.sources.length > 0) {
                    html += '<div class="chatbot-sources"><div class="chatbot-sources__title">Источники:</div>';
                    data.sources.forEach(function (s, i) {
                        var page = s.page ? ' (стр. ' + s.page + ')' : '';
                        html += '<div class="chatbot-sources__item">' + escapeHtml(s.fragment) + page + '</div>';
                    });
                    html += '</div>';
                }
                addMessage(html, false);
            })
            .catch(function (err) {
                hideTyping();
                addMessage('<p class="chatbot-error">Ошибка: ' + escapeHtml(err.message || 'Не удалось получить ответ от помощника.') + '</p>', false);
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
});
