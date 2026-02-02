import streamlit as st
from groq import Groq
import os

def get_groq_client():
    """Получение клиента Groq"""
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)
    return None

def render_ai_assistant():
    """Рендер AI помощника"""

    # Инициализация истории чата
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Контейнер с кастомным классом
    st.markdown('<div class="ai-assistant-container">', unsafe_allow_html=True)

    st.markdown("### 💬 AI Помощник")

    # Показываем историю
    for msg in st.session_state.chat_history[-3:]:
        if msg["role"] == "user":
            st.markdown(f"👤 **Вы:** {msg['content']}")
        else:
            st.markdown(f"🤖 **AI:** {msg['content']}")

    # Поле ввода
    question = st.text_area("Ваш вопрос:", key="ai_question", height=80)

    # Кнопки
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("Спросить AI", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️", use_container_width=True)

    # Обработка
    if ask_button and question:
        with st.spinner("AI думает..."):
            try:
                client = get_groq_client()
                if client:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Ты - помощник системы аналитики проектов. Отвечай кратко на русском языке."},
                            {"role": "user", "content": question}
                        ],
                        max_tokens=300,
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    st.error("❌ Не удалось подключиться к AI")
            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")

    # Очистка истории
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
