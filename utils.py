"""
Утилиты для работы с приложением
"""
import streamlit as st
import streamlit.components.v1 as components
import os


def load_css(css_file_path: str = "static/css/style.css"):
    """
    Загружает CSS файл и применяет стили к приложению
    
    Args:
        css_file_path: Путь к CSS файлу относительно корня проекта
    """
    try:
        # Получаем путь к корню проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, css_file_path)
        
        # Проверяем существование файла
        if not os.path.exists(css_path):
            st.warning(f"CSS файл не найден: {css_path}")
            return
        
        # Читаем CSS файл
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Применяем стили
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка при загрузке CSS: {e}")


def load_fonts(font_css_path: str = "static/css/font_style.css"):
    """
    Загружает CSS файл со шрифтами и исправляет пути к файлам шрифтов
    Использует base64 для встраивания шрифтов прямо в CSS
    
    Args:
        font_css_path: Путь к CSS файлу со шрифтами относительно корня проекта
    """
    try:
        import base64
        import re
        
        # Получаем путь к корню проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, font_css_path)
        
        # Проверяем существование файла
        if not os.path.exists(font_path):
            # Не показываем предупреждение, если файл не найден (шрифты опциональны)
            return
        
        # Читаем CSS файл
        with open(font_path, 'r', encoding='utf-8') as f:
            font_content = f.read()
        
        # Находим все пути к шрифтам и заменяем их на base64
        def replace_font_path(match):
            font_file = match.group(1)
            font_full_path = os.path.join(current_dir, "static", "fonts", font_file)
            
            if os.path.exists(font_full_path):
                try:
                    with open(font_full_path, 'rb') as f:
                        font_data = f.read()
                        font_base64 = base64.b64encode(font_data).decode('utf-8')
                        # Определяем формат по расширению и правильный MIME type
                        if font_file.endswith('.woff2'):
                            mime_type = 'font/woff2'
                        elif font_file.endswith('.woff'):
                            mime_type = 'font/woff'
                        elif font_file.endswith('.ttf'):
                            mime_type = 'font/ttf'
                        elif font_file.endswith('.otf'):
                            mime_type = 'font/otf'
                        else:
                            mime_type = 'font/woff2'
                        
                        return f"url('data:{mime_type};base64,{font_base64}')"
                except Exception:
                    # Если не удалось загрузить, возвращаем оригинальный путь
                    return match.group(0)
            else:
                # Если файл не найден, возвращаем оригинальный путь
                return match.group(0)
        
        # Заменяем все пути к шрифтам на base64
        # Поддерживаем разные форматы: url('../fonts/...'), url("../fonts/..."), url(../fonts/...)
        patterns = [
            r"url\('\.\./fonts/([^']+)'\)",  # url('../fonts/...')
            r'url\("\.\./fonts/([^"]+)"\)',   # url("../fonts/...")
            r'url\(\.\./fonts/([^)]+)\)',     # url(../fonts/...)
        ]
        
        for pattern in patterns:
            font_content = re.sub(pattern, replace_font_path, font_content)
        
        # Применяем стили
        st.markdown(f"<style>{font_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        # Не показываем ошибку пользователю (шрифты опциональны)
        # Ошибки можно увидеть в логах сервера
        pass


def load_all_styles():
    """
    Загружает все CSS файлы: сначала шрифты, затем основные стили
    """
    # Загружаем Material Icons ПЕРВЫМ, чтобы они были доступны
    st.markdown("""
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    load_fonts()
    load_css()
    
    # Стили для Material Icons
    st.markdown("""
        <style>
        span.material-icons {
            font-family: 'Material Icons' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
            text-rendering: optimizeLegibility !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # JavaScript для скрытия текстовых артефактов Material Icons
    components.html("""
        <script>
        (function() {
            function hideIconText() {
                try {
                    var allSpans = document.querySelectorAll('span');
                    var materialIconNames = [
                        'keyboard_arrow_right', 'keyboard_arrow_left', 'keyboard_arrow_up', 'keyboard_arrow_down',
                        'arrow_right', 'arrow_left', 'arrow_up', 'arrow_down', 'arrow_forward', 'arrow_back'
                    ];
                    
                    for (var i = 0; i < allSpans.length; i++) {
                        var span = allSpans[i];
                        var text = (span.textContent || span.innerText || '').trim();
                        
                        // Если текст является именем Material Icon, скрываем элемент
                        var isIcon = false;
                        for (var j = 0; j < materialIconNames.length; j++) {
                            if (text === materialIconNames[j]) {
                                isIcon = true;
                                break;
                            }
                        }
                        
                        if (isIcon || 
                            (text.indexOf('keyboard_arrow') !== -1 && text.length < 25) ||
                            (text.indexOf('arrow_') === 0 && text.length < 20)) {
                            // Скрываем элемент полностью
                            span.style.display = 'none';
                            span.style.visibility = 'hidden';
                            span.style.width = '0';
                            span.style.height = '0';
                            span.style.fontSize = '0';
                            span.style.lineHeight = '0';
                            span.style.opacity = '0';
                            span.style.position = 'absolute';
                            span.style.left = '-9999px';
                        }
                    }
                } catch(e) {
                    console.error('Error hiding icon text:', e);
                }
            }
            
            function runHideIcons() {
                hideIconText();
                setTimeout(hideIconText, 50);
                setTimeout(hideIconText, 100);
                setTimeout(hideIconText, 200);
                setTimeout(hideIconText, 500);
                setTimeout(hideIconText, 1000);
            }
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', runHideIcons);
            } else {
                runHideIcons();
            }
            
            if (typeof MutationObserver !== 'undefined') {
                var observer = new MutationObserver(hideIconText);
                if (document.body) {
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        characterData: true
                    });
                }
            }
            
            // Применение цвета фона только к фону графиков Plotly (не трогаем другие свойства)
            function applyGraphBackground() {
                try {
                    var graphBgColor = getComputedStyle(document.documentElement).getPropertyValue('--graphBackgroundColor').trim();
                    if (graphBgColor) {
                        var svgElements = document.querySelectorAll('svg.main-svg');
                        for (var i = 0; i < svgElements.length; i++) {
                            // Меняем только background-color, не трогая другие стили
                            svgElements[i].style.setProperty('background-color', graphBgColor, 'important');
                        }
                    }
                } catch(e) {
                    console.error('Error applying graph background:', e);
                }
            }
            
            // Применяем сразу и при изменениях DOM
            applyGraphBackground();
            setTimeout(applyGraphBackground, 100);
            setTimeout(applyGraphBackground, 500);
            setTimeout(applyGraphBackground, 1000);
            
            if (typeof MutationObserver !== 'undefined') {
                var graphObserver = new MutationObserver(function(mutations) {
                    var hasNewSvg = false;
                    for (var i = 0; i < mutations.length; i++) {
                        if (mutations[i].addedNodes.length > 0) {
                            for (var j = 0; j < mutations[i].addedNodes.length; j++) {
                                var node = mutations[i].addedNodes[j];
                                if (node.nodeType === 1 && (node.tagName === 'svg' || node.querySelector('svg.main-svg'))) {
                                    hasNewSvg = true;
                                    break;
                                }
                            }
                        }
                    }
                    if (hasNewSvg) {
                        setTimeout(applyGraphBackground, 100);
                    }
                });
                if (document.body) {
                    graphObserver.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                }
            }
        })();
        </script>
    """, height=0)


def load_css_custom(css_content: str):
    """
    Применяет кастомные CSS стили
    
    Args:
        css_content: Строка с CSS стилями
    """
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

