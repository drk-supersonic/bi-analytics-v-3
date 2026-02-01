"""
Страница авторизации
"""
import sys
import os
# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from auth import authenticate, generate_reset_token, reset_password, verify_reset_token, init_db, get_user_by_username
from utils import load_css, load_all_styles

# Инициализация базы данных
init_db()

# Настройка страницы
st.set_page_config(
    page_title="Авторизация - BI Analytics",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Загрузка CSS стилей из внешнего файла (включая шрифты)
load_all_styles()

# Дополнительные стили для страницы входа (скрытие боковой панели и ширина кнопок)
st.markdown("""
    <style>
    /* Скрытие боковой панели на странице входа */
    .stSidebar {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }
    /* Ширина кнопок на странице входа */
    .stButton > button {
        width: 100%;
    }

    /* Вертикальное расположение кнопок в форме */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }

    [data-testid="stForm"] .stColumn {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Отступ между кнопками */
    [data-testid="stForm"] .stFormSubmitButton {
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Если уже авторизован, перенаправляем
if st.session_state.get('authenticated', False):
    st.success("Вы уже авторизованы!")
    if st.button("Перейти к панели"):
        st.switch_page("project_visualization_app.py")
    st.stop()

# Определяем режим: вход или восстановление пароля
if 'reset_mode' not in st.session_state:
    st.session_state.reset_mode = False
if 'reset_token' not in st.session_state:
    st.session_state.reset_token = None

# Заголовок страницы (всегда показывается)
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #ffffff; font-size: 3rem; margin-bottom: 0.5rem;">🔐</h1>
        <h1 style="color: #ffffff; font-size: 2rem; margin-bottom: 0.5rem;">BI Analytics</h1>
        <p style="color: #a0a0a0; font-size: 1.1rem;">Войдите в систему для доступа к панели аналитики</p>
    </div>
""", unsafe_allow_html=True)

# Форма без контейнера

# Режим восстановления пароля по токену
if st.session_state.reset_mode and st.session_state.reset_token:
    st.subheader("Восстановление пароля")

    token = st.session_state.reset_token
    username = verify_reset_token(token)

    if not username:
        st.error("⚠️ Токен восстановления недействителен или истек")
        st.session_state.reset_mode = False
        st.session_state.reset_token = None
        if st.button("Вернуться к входу"):
            st.rerun()
        st.stop()

    st.info(f"Восстановление пароля для пользователя: **{username}**")

    new_password = st.text_input("Новый пароль", type="password", key="new_password")
    confirm_password = st.text_input("Подтвердите пароль", type="password", key="confirm_password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Сбросить пароль", type="primary"):
            if not new_password or len(new_password) < 6:
                st.error("Пароль должен содержать минимум 6 символов")
            elif new_password != confirm_password:
                st.error("Пароли не совпадают")
            else:
                if reset_password(token, new_password):
                    st.success("✅ Пароль успешно изменен!")
                    st.info("Теперь вы можете войти с новым паролем")
                    st.session_state.reset_mode = False
                    st.session_state.reset_token = None
                    if st.button("Перейти к входу"):
                        st.rerun()
                else:
                    st.error("Ошибка при сбросе пароля")

    with col2:
        if st.button("Отмена"):
            st.session_state.reset_mode = False
            st.session_state.reset_token = None
            st.rerun()

# Режим запроса восстановления пароля
elif st.session_state.reset_mode:
    st.subheader("Восстановление пароля")

    tab1, tab2 = st.tabs(["По имени пользователя", "По токену"])

    with tab1:
        username = st.text_input("Введите имя пользователя", key="reset_username")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Создать токен восстановления", type="primary"):
                if username:
                    user = get_user_by_username(username)
                    if user:
                        token = generate_reset_token(username)
                        if token:
                            # В реальном приложении здесь должна быть отправка email
                            # Для демонстрации показываем токен
                            st.success("✅ Токен восстановления создан!")
                            st.info(f"**Токен восстановления:** `{token}`")
                            st.warning("⚠️ В реальном приложении токен будет отправлен на email пользователя")
                            st.info("Для демонстрации скопируйте токен и используйте вкладку 'По токену'")

                            # Сохраняем токен в сессии для перехода к следующему шагу
                            st.session_state.reset_token = token
                            st.rerun()
                        else:
                            st.error("Ошибка при создании токена")
                    else:
                        st.error("Пользователь не найден")
                else:
                    st.warning("Введите имя пользователя")

        with col2:
            if st.button("Отмена"):
                st.session_state.reset_mode = False
                st.rerun()

    with tab2:
        token_input = st.text_input("Введите токен восстановления", key="token_input")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Использовать токен", type="primary"):
                if token_input:
                    username = verify_reset_token(token_input)
                    if username:
                        st.session_state.reset_token = token_input
                        st.rerun()
                    else:
                        st.error("⚠️ Токен недействителен или истек")
                else:
                    st.warning("Введите токен")

        with col2:
            if st.button("Отмена", key="cancel_token"):
                st.session_state.reset_mode = False
                st.rerun()

    st.markdown("---")
    if st.button("← Вернуться к входу"):
        st.session_state.reset_mode = False
        st.rerun()

# Режим входа
else:

    # Форма входа
    with st.form("login_form", clear_on_submit=False):
        st.markdown("### Вход в систему1")
        st.markdown("---")

        username = st.text_input(
            "👤 Имя пользователя",
            key="login_username",
            placeholder="Введите имя пользователя",
            autocomplete="off",
            value="",
        )

        password = st.text_input(
            "🔒 Пароль",
            type="password",
            key="login_password",
            placeholder="Введите пароль",
            autocomplete="new-password",
            value="",
        )

        st.markdown("<br>", unsafe_allow_html=True)  # Небольшой отступ

        # Кнопка "Войти" — на всю ширину, primary (красная/акцентная)
        submit_login = st.form_submit_button("🚀 Войти", type="primary", use_container_width=True)

        # Кнопка "Забыли пароль?" — на всю ширину, вторая по важности
        submit_reset = st.form_submit_button("❓ Забыли пароль?", use_container_width=True)

        if submit_login:
            if username and password:
                success, user = authenticate(username, password)
                if success and user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"✅ Добро пожаловать, {user['username']}!")
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.switch_page("project_visualization_app.py")
                else:
                    st.error("❌ Неверное имя пользователя или пароль")
            else:
                st.warning("⚠️ Заполните все поля")

        if submit_reset:
            st.session_state.reset_mode = True
            st.rerun()

    st.markdown("---")

    # Информация о демо-доступе
    with st.expander("ℹ️ Демо-доступ", expanded=False):
        st.markdown("""
        **Тестовые учетные данные:**
        - **Имя пользователя:** `admin`
        - **Пароль:** `admin123`
        - **Роль:** Суперадминистратор
        """)
