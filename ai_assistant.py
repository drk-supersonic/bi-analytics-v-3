import streamlit as st
from huggingface_hub import InferenceClient

# Инициализация клиента
@st.cache_resource
def get_hf_client():
    return InferenceClient(token=st.secrets["HF_TOKEN"])

client = get_hf_client()

# System prompt для вашего помощника
SYSTEM_PROMPT = """Ты - помощник сервиса на Streamlit.
Твоя задача - помогать пользователям разобраться с функциями сервиса.
Отвечай кратко, понятно и по делу на русском языке."""

# Инициализация истории чата
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_ai_response(user_message):
    """Получить ответ от AI"""
    try:
        # Формируем полный промпт с историей
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Добавляем историю (последние 5 сообщений для экономии)
        for msg in st.session_state.chat_history[-5:]:
            messages.append(msg)

        # Добавляем новое сообщение
        messages.append({"role": "user", "content": user_message})

        # Запрос к API
        response = client.chat_completion(
            messages=messages,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Ошибка: {str(e)}"

# UI помощника в боковой панели
with st.sidebar:
    st.markdown("### 💬 AI Помощник")
    st.markdown("---")

    # Отображаем историю чата
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**Вы:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")

    st.markdown("---")

    # Поле ввода
    user_input = st.text_input("Задайте вопрос:", key="user_input")

    col1, col2 = st.columns([3, 1])
    with col1:
        send_button = st.button("Отправить", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️", use_container_width=True)

    # Обработка отправки
    if send_button and user_input:
        with st.spinner("AI думает..."):
            # Добавляем сообщение пользователя
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            # Получаем ответ AI
            ai_response = get_ai_response(user_input)

            # Добавляем ответ AI
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_response
            })

            st.rerun()

    # Очистка чата
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
