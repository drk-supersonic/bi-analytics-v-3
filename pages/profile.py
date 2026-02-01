"""
Страница настроек профиля пользователя
"""
import sys
import os
# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from auth import (
    require_auth,
    get_current_user,
    get_user_role_display,
    change_password,
    update_user_email,
    logout,
    is_streamlit_context,
    render_sidebar_menu
)
from logger import log_action

# Проверка, что мы в контексте Streamlit
if is_streamlit_context():
    # Настройка страницы
    st.set_page_config(
        page_title="Настройки профиля - BI Analytics",
        page_icon="👤",
        layout="wide",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Проверка авторизации
    require_auth()
    
    user = get_current_user()
    
    # Проверка, что пользователь получен
    if not user:
        st.error("⚠️ Ошибка получения данных пользователя")
        st.stop()
    
    # Боковая панель с меню навигации
    render_sidebar_menu(current_page="profile")
    
    # Заголовок
    st.title("👤 Настройки профиля")
    st.markdown("---")
    
    # Информация о пользователе
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Пользователь", user['username'])
    with col2:
        st.metric("Роль", get_user_role_display(user['role']))
    with col3:
        if st.button("🚪 Выйти"):
            log_action(user['username'], 'logout', 'Выход из системы')
            logout()
            st.success("Вы вышли из системы")
            st.rerun()
    
    st.markdown("---")
    
    # Вкладки настроек
    tab1, tab2 = st.tabs(["🔐 Изменить пароль", "📧 Изменить email"])
    
    # ==================== TAB 1: Изменить пароль ====================
    with tab1:
        st.subheader("🔐 Изменение пароля")
        st.info("Для изменения пароля необходимо ввести текущий пароль и новый пароль.")
        
        with st.form("change_password_form"):
            old_password = st.text_input("Текущий пароль", type="password", help="Введите ваш текущий пароль")
            new_password = st.text_input("Новый пароль", type="password", help="Введите новый пароль (минимум 6 символов)")
            confirm_password = st.text_input("Подтвердите новый пароль", type="password", help="Повторите новый пароль")
            
            submitted = st.form_submit_button("Изменить пароль", type="primary")
            
            if submitted:
                # Валидация
                if not old_password:
                    st.error("⚠️ Введите текущий пароль")
                elif not new_password:
                    st.error("⚠️ Введите новый пароль")
                elif len(new_password) < 6:
                    st.error("⚠️ Новый пароль должен содержать минимум 6 символов")
                elif new_password != confirm_password:
                    st.error("⚠️ Новый пароль и подтверждение не совпадают")
                else:
                    # Изменяем пароль
                    success, message = change_password(user['username'], old_password, new_password)
                    if success:
                        st.success(f"✅ {message}")
                        log_action(user['username'], 'change_password', 'Пароль успешно изменен')
                        # Очищаем поля формы
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # ==================== TAB 2: Изменить email ====================
    with tab2:
        st.subheader("📧 Изменение email")
        st.info("Вы можете изменить или добавить email адрес для вашего профиля.")
        
        # Показываем текущий email
        current_email = user.get('email', 'Не указан')
        st.write(f"**Текущий email:** {current_email if current_email else 'Не указан'}")
        
        with st.form("change_email_form"):
            new_email = st.text_input(
                "Новый email",
                value=current_email if current_email and current_email != 'Не указан' else "",
                help="Введите новый email адрес или оставьте пустым для удаления"
            )
            
            submitted = st.form_submit_button("Изменить email", type="primary")
            
            if submitted:
                # Валидация email (базовая)
                email_value = new_email.strip() if new_email else None
                
                if email_value and '@' not in email_value:
                    st.error("⚠️ Введите корректный email адрес")
                else:
                    # Обновляем email
                    success, message = update_user_email(user['username'], email_value)
                    if success:
                        st.success(f"✅ {message}")
                        log_action(user['username'], 'change_email', f'Email изменен на: {email_value or "удален"}')
                        # Обновляем данные пользователя в сессии
                        user['email'] = email_value
                        st.session_state['user'] = user
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    st.markdown("---")
    st.info("💡 Для возврата к отчетам используйте меню в боковой панели или нажмите кнопку 'Выйти' для выхода из системы.")

