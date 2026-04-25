const messagesArea = document.getElementById('messagesArea');
const welcomeScreen = document.getElementById('welcomeScreen');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');

let isProcessing = false;

function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function useSuggestion(btn) {
    const span = btn.querySelector('span');
    const text = btn.textContent.replace(span.textContent, '').trim();
    questionInput.value = text;
    autoResize(questionInput);
    sendMessage();
}

function scrollToBottom() {
    messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
}

function addMessage(role, content, tools) {
    // Hide welcome on first message
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-content';

    if (role === 'agent') {
        bubble.innerHTML = formatMarkdown(content);
        if (tools && tools.length > 0) {
            const toolsDiv = document.createElement('div');
            toolsDiv.className = 'tools-used';
            tools.forEach(t => {
                const pill = document.createElement('span');
                pill.className = 'tool-pill';
                pill.textContent = t.tool_name;
                toolsDiv.appendChild(pill);
            });
            bubble.appendChild(toolsDiv);
        }
    } else {
        bubble.textContent = content;
    }

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    messagesArea.appendChild(msg);
    scrollToBottom();
    return msg;
}

function addTypingIndicator() {
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    const msg = document.createElement('div');
    msg.className = 'message agent';
    msg.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-content';
    bubble.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">
            Analisando e consultando BigQuery...
        </div>
    `;

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    messagesArea.appendChild(msg);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

function formatMarkdown(text) {
    if (!text) return '';
    let html = text
        // Bold
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Headers
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        // List items
        .replace(/^\* (.+)$/gm, '<li>$1</li>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        // Wrap li groups in ul
        .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
        // Paragraphs
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    return '<p>' + html + '</p>';
}

async function sendMessage() {
    const question = questionInput.value.trim();
    if (!question || isProcessing) return;

    isProcessing = true;
    sendBtn.disabled = true;
    questionInput.value = '';
    autoResize(questionInput);

    addMessage('user', question);
    addTypingIndicator();

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });

        removeTypingIndicator();

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            const detail = err.detail || `Erro ${res.status}`;
            addMessage('agent', `⚠️ **Erro:** ${detail}`);
            return;
        }

        const data = await res.json();
        addMessage('agent', data.answer, data.tools_used);

    } catch (err) {
        removeTypingIndicator();
        addMessage('agent', `⚠️ **Erro de conexão:** Não foi possível conectar ao servidor. Verifique se ele está rodando.`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// Focus input on load
questionInput.focus();
