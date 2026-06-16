import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from pathlib import Path
import requests
import base64

st.set_page_config(page_title="Discovery Manager МТС Инвестиции", page_icon="🚀", layout="wide")

# ==========================================
#  АВТОРИЗАЦИЯ
# ==========================================
def check_authentication():
    """Проверка пароля для доступа к приложению"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Discovery Manager")
        st.markdown("### Введите пароль для доступа к системе")
        st.markdown("---")
        
        password_input = st.text_input("Пароль", type="password", key="password_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Войти", type="primary", use_container_width=True):
                correct_password = st.secrets.get("auth", {}).get("password", "")
                
                if password_input == correct_password and correct_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Неверный пароль")
        
        st.stop()

check_authentication()

# ==========================================
# КОНЕЦ БЛОКА АВТОРИЗАЦИИ
# ==========================================

# ================= КОНСТАНТЫ =================
BUSINESS_FIELDS = {
    "problem": "Проблема/Возможность",
    "audience": "Целевая аудитория",
    "business_goal": "Бизнес-цель",
    "metrics": "Метрики успеха",
    "impact": "Что будет если не сделать?",
    "use_cases": "Основной сценарий"
}

ANALYST_FIELDS = {
    "acceptance_criteria": "Критерии приемки (DoD)",
    "subtasks": "Декомпозиция на подзадачи",
    "technical_estimate": "Техническая оценка",
    "detailed_dependencies": "Детальные технические зависимости"
}

COMPLEXITY_INFO = {
    "S": {"days": "< 5 дней", "sprints": "< 0.5 спринта", "effort_score": 1},
    "M": {"days": "5-10 дней", "sprints": "0.5-1 спринт", "effort_score": 2},
    "L": {"days": "10-20 дней", "sprints": "1-2 спринта", "effort_score": 4},
    "XL": {"days": "20-40 дней", "sprints": "2-4 спринта", "effort_score": 8},
    "XXL": {"days": "40+ дней", "sprints": "4+ спринтов", "effort_score": 16}
}

BUSINESS_VALUE_HINTS = {
    "High": "🔴 Влияет на деньги (AUM, опердоход), регуляторные требования, удержание клиентов",
    "Medium": " Влияет на NPS, активность клиентов, конверсию (но не критично)",
    "Low": "🟢 Косметические улучшения, внутренние удобства"
}

URGENCY_HINTS = {
    "High": "🔴 Жесткий дедлайн, блокирует другие задачи, клиенты уже уходят",
    "Medium": "🟡 Желательно в этом квартале, накопительный эффект",
    "Low": "🟢 Нет дедлайна, можно отложить"
}

# ================= ФУНКЦИИ =================
def check_readiness(task):
    filled_business = [f for f in BUSINESS_FIELDS if task.get(f)]
    filled_analyst = [f for f in ANALYST_FIELDS if task.get(f)]
    business_progress = len(filled_business) / len(BUSINESS_FIELDS)
    analyst_progress = len(filled_analyst) / len(ANALYST_FIELDS)
    is_ready_for_analyst = business_progress >= 0.83
    return {
        "business_progress": business_progress,
        "analyst_progress": analyst_progress,
        "is_ready_for_analyst": is_ready_for_analyst,
        "missing_business": [f for f in BUSINESS_FIELDS if not task.get(f)],
        "missing_analyst": [f for f in ANALYST_FIELDS if not task.get(f)]
    }

def auto_update_status(task):
    """Автоматически обновляет статус задачи на основе заполненности полей"""
    current_status = task.get("status", "Idea")
    
    has_problem = bool(task.get("problem", "").strip())
    has_goal = bool(task.get("business_goal", "").strip())
    
    readiness = check_readiness(task)
    is_ready_for_analyst = readiness.get("is_ready_for_analyst", False)
    
    # 1. Idea → In Discovery: заполнены проблема и цель
    if current_status == "Idea" and has_problem and has_goal:
        task["status"] = "In Discovery"
        return True
    
    # 2. In Discovery → Ready for Analyst: все бизнес-поля заполнены
    if current_status == "In Discovery" and is_ready_for_analyst:
        task["status"] = "Ready for Analyst"
        if not task.get("analyst_deadline"):
            task["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        return True
    
    return False

def calculate_rice(reach, impact, confidence, effort):
    if effort == 0:
        return 0
    return (reach * impact * (confidence / 100)) / effort

def save_tasks_to_file(tasks):
    """Сохраняет задачи в локальный файл"""
    try:
        with open('tasks_data.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

def commit_to_github(file_path, message):
    """Автокоммит файла в GitHub через API"""
    try:
        token = st.secrets.get("github", {}).get("token", "")
        repo = st.secrets.get("github", {}).get("repo", "")
        owner = st.secrets.get("github", {}).get("owner", "")
        
        if not token or not repo or not owner:
            return False, "GitHub credentials не настроены"
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Получаем текущий SHA файла
        sha = None
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                sha = response.json()["sha"]
        except:
            pass
        
        # Читаем файл и кодируем в base64
        if not os.path.exists(file_path):
            return False, "Файл не найден"
        
        with open(file_path, 'rb') as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        data = {
            "message": message,
            "content": encoded_content
        }
        if sha:
            data["sha"] = sha
        
        response = requests.put(url, headers=headers, json=data, timeout=10)
        
        if response.status_code in [200, 201]:
            return True, "✅ Сохранено в Git"
        else:
            return False, f"Ошибка Git: {response.status_code}"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def save_and_commit(tasks, action="Изменение"):
    """Сохраняет файл и делает автокоммит"""
    save_tasks_to_file(tasks)
    timestamp = datetime.now().strftime("%H:%M")
    success, msg = commit_to_github(
        "tasks_data.json",
        f"{action} [{timestamp}]"
    )
    return success, msg

def load_tasks_from_file():
    try:
        if os.path.exists('tasks_data.json'):
            with open('tasks_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

def download_template():
    template_path = Path("Шаблон для задач в МТСИ.xlsx")
    if template_path.exists():
        with open(template_path, "rb") as f:
            return f.read()
    return None

def import_tasks_from_excel(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.write("📋 Найдены колонки:", list(df.columns))
        
        tasks = []
        
        for idx, row in df.iterrows():
            if idx == 0:
                continue
            
            title = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            
            if not title or title == "nan":
                continue
            
            def norm_choice(val):
                if pd.isna(val):
                    return None
                s = str(val).strip()
                if not s:
                    return None
                return s[0].upper() + s[1:].lower() if len(s) > 1 else s.upper()
            
            task = {
                "id": idx,
                "title": title,
                "owner": str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) and len(row) > 1 else "",
                "type": str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) and len(row) > 2 else "Бизнес-фича",
                "problem": str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) and len(row) > 3 else "",
                "audience": str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) and len(row) > 4 else "",
                "metrics": str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) and len(row) > 5 else "",
                "business_goal": str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) and len(row) > 6 else "",
                "impact": str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) and len(row) > 7 else "",
                "use_cases": str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) and len(row) > 8 else "",
                "urgency": norm_choice(row.iloc[9]) or "Medium",
                "business_value": norm_choice(row.iloc[10]) or "Medium",
                "complexity": str(row.iloc[11]).strip().upper() if pd.notna(row.iloc[11]) and len(row) > 11 else "M",
                "as_is": "",
                "to_be": "",
                "dependencies": "",
                "constraints": "",
                "risks": "",
                "acceptance_criteria": "",
                "subtasks": "",
                "technical_estimate": "",
                "detailed_dependencies": "",
                "analyst_deadline": "",
                "priority": "",
                "rice_score": 0,
                "reach": 0,
                "impact_rice": 0,
                "confidence": 0,
                "effort": 0,
                "executive_priority": False,
                "status": "Idea",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "prioritized_at": ""
            }
            tasks.append(task)
        return tasks
    except Exception as e:
        st.error(f"❌ Ошибка импорта: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return []

def generate_confluence_text(task):
    text = f"""h2. {task['title']}

h3. Базовая информация
*Тип:* {task.get('type', 'Не указан')}
*Владелец:* {task.get('owner', 'Не указан')}
*Статус:* {task.get('status', 'Не указан')}
*Создана:* {task.get('created_date', 'Не указана')}

h3. Бизнес-контекст
*Проблема:* {task.get('problem', 'Не указана')}
*Целевая аудитория:* {task.get('audience', 'Не указана')}
*Бизнес-цель:* {task.get('business_goal', 'Не указана')}
*Метрики:* {task.get('metrics', 'Не указаны')}

h3. Решение
*As Is:* {task.get('as_is', 'Не описано')}
*To Be:* {task.get('to_be', 'Не описано')}

h3. Ограничения
*Зависимости:* {task.get('dependencies', 'Не указаны')}
*Ограничения:* {task.get('constraints', 'Нет')}
*Риски:* {task.get('risks', 'Нет')}

h3. Приоритизация
*Срочность:* {task.get('urgency', 'Не указана')}
*Бизнес-ценность:* {task.get('business_value', 'Не указана')}
*Сложность:* {task.get('complexity', 'Не указана')}
*Приоритет:* {task.get('priority', 'Не заполнен')}
"""
    if task.get('rice_score'):
        text += f"*RICE Score:* {task['rice_score']:.2f}\n"
    if task.get('analyst_deadline'):
        text += f"*Срок анализа:* {task['analyst_deadline']}\n"
    return text

# ================= ИНИЦИАЛИЗАЦИЯ =================
saved_tasks = load_tasks_from_file()

if "tasks" not in st.session_state:
    if saved_tasks:
        st.session_state.tasks = saved_tasks
    else:
        st.session_state.tasks = []

if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

if "show_new_task_form" not in st.session_state:
    st.session_state.show_new_task_form = False

if "prioritization_index" not in st.session_state:
    st.session_state.prioritization_index = 0

if "prioritization_order" not in st.session_state:
    st.session_state.prioritization_order = []

if "show_prioritization_tasks" not in st.session_state:
    st.session_state.show_prioritization_tasks = False

st.title("🚀 Discovery Manager")
st.markdown("Конвейер спринтов: Этап Discovery")

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача", "📊 Приоритезация задач", "📥 Импорт задач"])

# Индикатор Git-синхронизации
git_token = st.secrets.get("github", {}).get("token", "")
if git_token:
    st.sidebar.success(" Git-синхронизация активна")
else:
    st.sidebar.warning(" Git-синхронизация не настроена")

# ================= ИНСТРУКЦИЯ =================
with st.expander("ℹ️ Как пользоваться Discovery Manager", expanded=False):
    st.markdown("""
    **🎯 Цель этапа Discovery:** Превратить сырую идею в задачу, готовую к передаче команде разработки.
    
    **📝 Процесс:**
    1. **Инициатор** создает задачу и заполняет базовые поля. В задаче показывается прогресс заполнения (idea)
    2. Когда бизнес-поля заполнены на 80%+, появляется кнопка **"Передать аналитику"** (in discovery)
    3. **Аналитик** уточняет требования и берёт задачу в анализ (Ready for Analyst)
    4. **Аналитик** пишет требования (In analysis)
    5. **Задача** должна пройти **Приоритезацию** (RICE)
    6. **Задача** переходит в статус **"Ready for Refinement"** (grooming)
    7. **Задача** готова к спринту (Ready for sprint)
    
    **💾 Автосохранение:** Все изменения автоматически сохраняются в Git-репозиторий.
    """)

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == "📋 Список задач":
    with st.expander("📖 Легенда", expanded=False):
        col_legend1, col_legend2, col_legend3 = st.columns(3)
        with col_legend1:
            st.markdown("**Статусы задач:**")
            st.markdown("""
            - ⚪ **Idea** — идея
            - 🔵 **In Discovery** — бизнес заполняет шаблон
            - **Ready for Analyst** — готово к передаче аналитику
            - 🟣 **Requirements Clarification** — аналитик уточняет
            - ✅ **Ready for Refinement** — готово к команде
            """)
        with col_legend2:
            st.markdown("**⏰ Срочность:**")
            st.markdown("""
            - 🔴 **High** — критично
            - 🟡 **Medium** — средне
            -  **Low** — низко
            """)
        with col_legend3:
            st.markdown("**📏 Ёмкость:**")
            st.markdown("""
            - **S** — < 5 дней
            - **M** — 5-10 дней
            - **L** — 10-20 дней
            - **XL** — 20-40 дней
            - **XXL** — 40+ дней
            """)
        st.markdown("---")

    if st.session_state.editing_task_id is not None:
        task_to_edit = next((t for t in st.session_state.tasks if t["id"] == st.session_state.editing_task_id), None)
        if task_to_edit:
            st.header(f"✏️ Редактирование: {task_to_edit['title']}")
            readiness = check_readiness(task_to_edit)
            if readiness["is_ready_for_analyst"] and task_to_edit["status"] == "In Discovery":
                st.success("✅ Задача полностью заполнена и готова к передаче аналитику!")
                if st.button(" Передать аналитику", key=f"ready_edit_{task_to_edit['id']}", type="primary", use_container_width=True):
                    task_to_edit["status"] = "Ready for Analyst"
                    task_to_edit["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    save_and_commit(st.session_state.tasks, "Передано аналитику")
                    st.rerun()
            st.markdown("---")
            
            st.markdown("**⚡ Быстрые действия:**")
            col_conf, col_del = st.columns([1.5, 1])
        
            with col_conf:
                try:
                    confluence_text = generate_confluence_text(task_to_edit)
                    safe_title = "".join(c for c in str(task_to_edit.get('title', 'task')) if c.isalnum() or c in (' ', '.', '_')).rstrip()
                    st.download_button(
                        label="📥 Скачать текст для Confluence", 
                        data=confluence_text, 
                        file_name=f"{safe_title}.txt", 
                        mime="text/plain", 
                        key=f"confluence_edit_{task_to_edit['id']}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Ошибка генерации текста: {e}")
            
            with col_del:
                if st.button("🗑️ Удалить задачу", key=f"delete_edit_{task_to_edit['id']}", type="secondary", use_container_width=True):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_to_edit["id"]]
                    save_and_commit(st.session_state.tasks, "Удалена задача")
                    st.session_state.editing_task_id = None
                    st.rerun()

            st.markdown("---")
            
            with st.form("edit_task_form"):
                st.subheader("📌 Базовая информация")
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Название *", value=task_to_edit.get("title", ""))
                    task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"])
                with col2:
                    owner = st.text_input("Инициатор/Владелец", value=task_to_edit.get("owner", ""))
                
                st.subheader("💼 Бизнес-контекст")
                problem = st.text_area("Проблема", value=task_to_edit.get("problem", ""), height=80)
                audience = st.text_area("Аудитория", value=task_to_edit.get("audience", ""), height=80)
                business_goal = st.text_area("Бизнес-цель", value=task_to_edit.get("business_goal", ""), height=80)
                metrics = st.text_area("Метрики", value=task_to_edit.get("metrics", ""), height=80)
                impact = st.text_area("Если не сделать", value=task_to_edit.get("impact", ""), height=80)
                use_cases = st.text_area("Сценарий", value=task_to_edit.get("use_cases", ""), height=80)
                
                st.subheader(" Решение")
                as_is = st.text_area("As Is", value=task_to_edit.get("as_is", ""), height=80)
                to_be = st.text_area("To Be", value=task_to_edit.get("to_be", ""), height=80)
                
                st.subheader("⚠️ Ограничения")
                dependencies = st.text_area("Зависимости", value=task_to_edit.get("dependencies", ""), height=80)
                constraints = st.text_area("Ограничения", value=task_to_edit.get("constraints", ""), height=80)
                risks = st.text_area("Риски", value=task_to_edit.get("risks", ""), height=80)
                
                st.subheader("🔧 Поля аналитика")
                acceptance_criteria = st.text_area("Критерии приемки", value=task_to_edit.get("acceptance_criteria", ""), height=80)
                subtasks = st.text_area("Декомпозиция", value=task_to_edit.get("subtasks", ""), height=80)
                technical_estimate = st.text_area("Техническая оценка", value=task_to_edit.get("technical_estimate", ""), height=80)
                detailed_dependencies = st.text_area("Детальные зависимости", value=task_to_edit.get("detailed_dependencies", ""), height=80)
                
                if task_to_edit["status"] in ["Ready for Analyst", "Requirements Clarification"]:
                    st.subheader("📅 Срок анализа")
                    default_date = datetime.strptime(task_to_edit.get("analyst_deadline", "2026-06-17"), "%Y-%m-%d").date() if task_to_edit.get("analyst_deadline") else datetime.now() + timedelta(days=7)
                    analyst_deadline = st.date_input("Срок анализа", value=default_date)
                else:
                    analyst_deadline = None

                st.subheader("📊 Приоритизация")
                col1, col2, col3 = st.columns(3)
                with col1:
                    urgency_options = ["High", "Medium", "Low", "Не определено"]
                    urgency_default = task_to_edit.get("urgency", "Не определено") or "Не определено"
                    urgency_index = urgency_options.index(urgency_default) if urgency_default in urgency_options else 3
                    urgency = st.selectbox("Срочность", urgency_options, index=urgency_index)
                with col2:
                    value_options = ["High", "Medium", "Low", "Не определено"]
                    value_default = task_to_edit.get("business_value", "Не определено") or "Не определено"
                    value_index = value_options.index(value_default) if value_default in value_options else 3
                    business_value = st.selectbox("Бизнес-ценность", value_options, index=value_index)
                with col3:
                    complexity_options = ["S", "M", "L", "XL", "XXL"]
                    complexity_default = task_to_edit.get("complexity", "S")
                    complexity_index = complexity_options.index(complexity_default) if complexity_default in complexity_options else 0
                    complexity = st.selectbox("Сложность", complexity_options, index=complexity_index)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Сохранить", type="primary")
                with col2:
                    cancelled = st.form_submit_button("❌ Отмена")
                
                if submitted:
                    task_to_edit.update({
                        "title": title, "type": task_type, "owner": owner,
                        "problem": problem, "audience": audience, "business_goal": business_goal,
                        "metrics": metrics, "impact": impact, "use_cases": use_cases,
                        "as_is": as_is, "to_be": to_be,
                        "dependencies": dependencies, "constraints": constraints, "risks": risks,
                        "acceptance_criteria": acceptance_criteria, "subtasks": subtasks,
                        "technical_estimate": technical_estimate, "detailed_dependencies": detailed_dependencies,
                        "urgency": urgency, "business_value": business_value, "complexity": complexity
                    })
                    if analyst_deadline:
                        task_to_edit["analyst_deadline"] = analyst_deadline.strftime("%Y-%m-%d")
                    
                    auto_update_status(task_to_edit)
                    save_and_commit(st.session_state.tasks, f"Редактирование: {title}")
                    st.session_state.editing_task_id = None
                    st.success("✅ Сохранено!")
                    st.rerun()
                if cancelled:
                    st.session_state.editing_task_id = None
                    st.rerun()
    else:
        st.header("Бэклог инициатив")
        
        if not st.session_state.tasks:
            st.info("ℹ️ Нет задач")
        else:
            tasks = st.session_state.tasks
            
            needs_business_fill = sum(1 for t in tasks if not check_readiness(t)["is_ready_for_analyst"])
            ready_for_analyst = sum(1 for t in tasks if check_readiness(t)["is_ready_for_analyst"] and t["status"] == "In Discovery")
            not_prioritized = sum(1 for t in tasks if not t.get("priority"))
            
            today = datetime.now().date()
            overdue = sum(1 for t in tasks if t.get("analyst_deadline") and t["status"] in ["Ready for Analyst", "Requirements Clarification"] and datetime.strptime(t["analyst_deadline"], "%Y-%m-%d").date() < today)
            
            st.markdown("### 📈 Дэшборд")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Всего задач", len(tasks))
            with col2:
                st.metric("⚠️ Требуют заполнения", needs_business_fill)
            with col3:
                st.metric("🟠 Готовы к аналитику", ready_for_analyst)
            with col4:
                st.metric("📊 Не приоритезировано", not_prioritized)
            with col5:
                st.metric("🚨 Просрочено", overdue)
            
            st.markdown("---")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                status_filter = st.multiselect("Статус", ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"], default=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"])
            with col2:
                value_filter = st.multiselect("Бизнес-ценность", ["High", "Medium", "Low", "Не определено"], default=["High", "Medium", "Low", "Не определено"])
            with col3:
                urgency_filter = st.multiselect("Срочность", ["High", "Medium", "Low", "Не определено"], default=["High", "Medium", "Low", "Не определено"])
            with col4:
                priority_filter = st.multiselect("Приоритет", ["P1", "P2", "P3", "P4", "Без приоритета"], default=["P1", "P2", "P3", "P4", "Без приоритета"])

            filtered = []
            for t in tasks:
                task_status = t.get("status", "") or ""
                status_ok = task_status in status_filter
                
                task_value = t.get("business_value", "") or "Не определено"
                value_ok = task_value in value_filter
                
                task_urgency = t.get("urgency", "") or "Не определено"
                urgency_ok = task_urgency in urgency_filter
                
                task_priority = t.get("priority", "") or "Без приоритета"
                priority_ok = task_priority in priority_filter
                
                if status_ok and value_ok and urgency_ok and priority_ok:
                    filtered.append(t)
            
            st.markdown(f"**Показано: {len(filtered)}**")
            st.markdown("---")

            # ЗАГОЛОВКИ ТАБЛИЦЫ (один раз)
            col_header1, col_header2, col_header3, col_header4, col_header5, col_header6 = st.columns([4, 2, 1.3, 1.3, 1, 1])
            
            with col_header1:
                st.markdown("**Задача**")
            with col_header2:
                st.markdown("**Статус**")
            with col_header3:
                st.markdown("**Срочность**")
            with col_header4:
                st.markdown("**Бизнес-ценность**")
            with col_header5:
                st.markdown("**Ёмкость**")
            with col_header6:
                st.markdown("**Приоритет**")
            
            st.markdown("---")
            
            # ТАБЛИЧНОЕ ОТОБРАЖЕНИЕ
            for task in filtered:
                readiness = check_readiness(task)
                status_emoji = {"Idea": "⚪", "In Discovery": "🔵", "Ready for Analyst": "🟠", "Requirements Clarification": "🟣", "Ready for Refinement": "✅"}.get(task["status"], "")
                value_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "Не определено": "⚪"}.get(task.get("business_value", "Не определено"), "⚪")
                urgency_emoji = {"High": "", "Medium": "🟡", "Low": "🟢", "Не определено": "⚪"}.get(task.get("urgency", "Не определено"), "⚪")
                exec_badge = " 👑" if task.get("executive_priority") else ""
                
                priority = task.get("priority", "")
                priority_display = priority if priority else "—"
                
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([4, 2, 1.3, 1.3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{task['title']}**{exec_badge}")
                        if st.button("📄 Подробнее", key=f"details_{task['id']}"):
                            st.session_state.editing_task_id = task["id"]
                            st.rerun()
                    with col2:
                        st.markdown(f"{status_emoji} {task['status']}")
                    with col3:
                        st.markdown(f"{urgency_emoji} {task.get('urgency', 'Medium')}")
                    with col4:
                        st.markdown(f"{value_emoji} {task.get('business_value', 'Medium')}")
                    with col5:
                        st.markdown(f"⏱ {task.get('complexity', 'M')}")
                    with col6:
                        st.markdown(f"⭐ {priority_display}")
                    
                    st.markdown("---")
                    
                    if st.session_state.editing_task_id == task["id"]:
                        with st.expander("📋 Детали задачи", expanded=True):
                            st.markdown("**📊 Прогресс:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.progress(readiness["business_progress"]) 
                                st.write(f"Бизнес-поля: {int(readiness['business_progress']*100)}%")
                            
                            if readiness["is_ready_for_analyst"] and task["status"] == "In Discovery":
                                st.success("✅ Готово к передаче аналитику!")
                                if st.button("🚀 Передать аналитику", key=f"ready_{task['id']}", type="primary"):
                                    task["status"] = "Ready for Analyst"
                                    task["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                                    save_and_commit(st.session_state.tasks, "Передано аналитику")
                                    st.rerun()
                            
                            st.markdown("---")
                            st.markdown(f"**Проблема:** {task.get('problem', 'Не указана')}")
                            st.markdown(f"**Цель:** {task.get('business_goal', 'Не указана')}")
                            
                            col1, col2, col3, col4 = st.columns([1, 2.5, 1, 1])
                            
                            with col1:
                                if st.button("✏️ Ред.", key=f"edit_{task.get('id', 'unknown')}"):
                                    st.session_state.editing_task_id = task["id"]
                                    st.rerun()
                            
                            with col2:
                                status_options = ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"]
                                current_status = task.get("status", "Idea")
                                safe_index = status_options.index(current_status) if current_status in status_options else 0
                                
                                new_status = st.selectbox(
                                    "Статус", 
                                    status_options, 
                                    index=safe_index, 
                                    key=f"status_{task.get('id', 'unknown')}",
                                    label_visibility="collapsed"
                                )
                                if new_status != current_status:
                                    task["status"] = new_status
                                    save_and_commit(st.session_state.tasks, f"Статус → {new_status}")
                                    st.rerun()
                            
                            with col3:
                                try:
                                    confluence_text = generate_confluence_text(task)
                                    safe_title = "".join(c for c in task.get('title', 'task') if c.isalnum() or c in (' ', '.', '_')).rstrip()
                                    st.download_button(
                                        label=" Confluence", 
                                        data=confluence_text, 
                                        file_name=f"{safe_title}.txt", 
                                        mime="text/plain", 
                                        key=f"confluence_{task.get('id', 'unknown')}",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error("Ошибка генерации текста")
                                    st.write(f"Детали: {e}")
                            
                            with col4:
                                if st.button("🗑️ Удалить", key=f"delete_{task.get('id', 'unknown')}", type="secondary", use_container_width=True):
                                    st.session_state.tasks = [t for t in st.session_state.tasks if t.get("id") != task.get("id")]
                                    save_and_commit(st.session_state.tasks, "Удалена задача")
                                    st.rerun()
       
                        st.markdown("---")

# ================= ЭКРАН 2: НОВАЯ ЗАДАЧА =================
elif page == "➕ Новая задача":
    if not st.session_state.show_new_task_form:
        st.header("Создание новой инициативы")
        st.markdown("""
        💡 **Как это работает:**
        1. Нажми кнопку ниже
        2. Заполни основную информацию
        3. Система создаст задачу со статусом **Idea**
        4. Дополни детали через редактирование в списке задач
        """)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Создать задачу", type="primary", use_container_width=True):
                st.session_state.show_new_task_form = True
                st.rerun()
    else:
        st.header("Создание инициативы")
        if st.button("← Назад"):
            st.session_state.show_new_task_form = False
            st.rerun()
        
        with st.form("new_task"):
            title = st.text_input("Название *")
            problem = st.text_area("Проблема", placeholder="Что не так?", height=80)
            audience = st.text_area("Аудитория", placeholder="Для кого?", height=80)
            business_goal = st.text_area("Бизнес-цель", placeholder="Зачем?", height=80)
            metrics = st.text_area("Метрики", placeholder="Как измерим?", height=80)
            impact = st.text_area("Если не сделать", placeholder="Влияние", height=80)
            use_cases = st.text_area("Сценарий", placeholder="Кто → Что → Результат", height=80)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                urgency = st.selectbox("Срочность", ["High", "Medium", "Low"], help=URGENCY_HINTS.get("High"))
            with col2:
                business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"], help=BUSINESS_VALUE_HINTS.get("Medium"))
            with col3:
                complexity = st.selectbox("Сложность", ["S", "M", "L", "XL", "XXL"])
            
            submitted = st.form_submit_button("✅ Создать", type="primary")
            if submitted:
                if title:
                    new_task = {
                        "id": len(st.session_state.tasks) + 1,
                        "title": title, "problem": problem, "audience": audience,
                        "business_goal": business_goal, "metrics": metrics, "impact": impact,
                        "use_cases": use_cases, "as_is": "", "to_be": "",
                        "dependencies": "", "constraints": "", "risks": "",
                        "acceptance_criteria": "", "subtasks": "", "technical_estimate": "",
                        "detailed_dependencies": "", "analyst_deadline": "",
                        "priority": "", "rice_score": 0, "reach": 0, "impact_rice": 0,
                        "confidence": 0, "effort": 0, "executive_priority": False,
                        "urgency": urgency, "business_value": business_value, "complexity": complexity,
                        "status": "Idea", "created_date": datetime.now().strftime("%Y-%m-%d"),
                        "prioritized_at": ""
                    }
                    st.session_state.tasks.append(new_task)
                    save_and_commit(st.session_state.tasks, f"Создана задача: {title}")
                    st.session_state.show_new_task_form = False
                    st.success(f"✅ Задача '{title}' создана!")
                    st.rerun()

# ================= ЭКРАН 3: ПРИОРИТЕЗАЦИЯ =================
elif page == "📊 Приоритезация задач":
    st.header("📊 Приоритезация (RICE)")
    tasks = st.session_state.tasks
    unprioritized = [t for t in tasks if not t.get("priority")]
    prioritized = [t for t in tasks if t.get("priority")]

    st.markdown("###  Дэшборд")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего", len(tasks))
    with col2:
        st.metric("⏳ Не приоритезировано", len(unprioritized))
    with col3:
        st.metric("✅ Приоритезировано", len(prioritized))

    st.markdown("---")

    if len(tasks) == 0:
        st.info("ℹ️ Нет задач")
    elif len(unprioritized) == 0:
        st.success("✅ Все приоритезированы!")
    else:
        st.markdown(f"⚠️ **{len(unprioritized)} задач** ждут приоритезации")
        st.markdown("---")
        
        if st.button("🚀 Начать приоритезацию", type="primary"):
            st.session_state.prioritization_index = 0
            st.session_state.show_prioritization_tasks = True
            st.rerun()
        
        if st.session_state.get("show_prioritization_tasks", False) and st.session_state.prioritization_index < len(unprioritized):
            st.markdown("---")
            current_task = unprioritized[st.session_state.prioritization_index]
            
            st.markdown(f"### Задача **{st.session_state.prioritization_index + 1}** из **{len(unprioritized)}**")
            st.progress((st.session_state.prioritization_index) / len(unprioritized))
            st.write(f"Прогресс: {st.session_state.prioritization_index}/{len(unprioritized)}")
            
            with st.expander(f"📋 {current_task['title']}", expanded=True):
                st.markdown(f"**Проблема:** {current_task.get('problem', '')}")
                st.markdown(f"**Цель:** {current_task.get('business_goal', '')}")
            
            st.markdown("---")
            st.subheader("Оценка RICE")
            
            with st.form(f"rice_{current_task['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    reach = st.slider("Охват (1-10)", 1, 10, 5, key=f"r_{current_task['id']}", help="Сколько клиентов затронет?\n\n• 1-3 = небольшая группа\n• 4-6 = половина клиентов\n• 7-10 = все клиенты")
                    impact = st.slider("Влияние (1-3)", 1, 3, 2, key=f"i_{current_task['id']}", help="Насколько сильно повлияет?\n\n• 1 = слабое\n• 2 = среднее (NPS)\n• 3 = массовый эффект (AUM, выручка)")
                
                with col2:
                    confidence = st.slider("Уверенность (50-100%)", 50, 100, 80, key=f"c_{current_task['id']}", help="Насколько уверены в оценках?\n\n• 50% = догадки\n• 80% = экспертная оценка\n• 100% = есть данные")
                    effort = st.selectbox("Ёмкость", ["S", "M", "L", "XL", "XXL"], index=["S", "M", "L", "XL", "XXL"].index(current_task.get("complexity", "M")), key=f"e_{current_task['id']}", help="Сколько времени займет?\n\nАвтоматически из поля 'Ёмкость'")
                
                exec_priority = st.checkbox(" Высший приоритет", key=f"exec_{current_task['id']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    submitted = st.form_submit_button("✅ Сохранить", type="primary")
                with col2:
                    skipped = st.form_submit_button("⏭️ Пропустить")
                with col3:
                    cancelled = st.form_submit_button("❌ Отмена")
                
                if submitted:
                    effort_score = COMPLEXITY_INFO[effort]["effort_score"]
                    rice_score = calculate_rice(reach, impact, confidence, effort_score)
                    
                    priority = "P1" if rice_score >= 5 else "P2" if rice_score >= 2 else "P3" if rice_score >= 1 else "P4"
                    
                    current_task.update({
                        "reach": reach, "impact_rice": impact, "confidence": confidence,
                        "effort": effort_score, "rice_score": rice_score, "priority": priority,
                        "executive_priority": exec_priority,
                        "prioritized_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    if current_task["id"] not in st.session_state.prioritization_order:
                        st.session_state.prioritization_order.append(current_task["id"])
                    
                    save_and_commit(st.session_state.tasks, f"Приоритезация: {current_task['title']} → {priority}")
                    st.success(f"✅ RICE: {rice_score:.2f} → {priority}")
                    
                    if st.session_state.prioritization_index < len(unprioritized) - 1:
                        st.session_state.prioritization_index += 1
                    st.rerun()
            
            if skipped or cancelled:
                st.rerun()

    if st.session_state.prioritization_order:
        st.markdown("---")
        st.markdown("### 📜 История (последняя сверху)")
        for idx, task_id in enumerate(reversed(st.session_state.prioritization_order)):
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                badge = "👑 " if task.get("executive_priority") else ""
                st.markdown(f"**{idx + 1}.** {badge}**{task['title']}** — {task.get('priority')} | RICE: {task.get('rice_score', 0):.2f}")

# ================= ЭКРАН 4: ИМПОРТ ЗАДАЧ =================
elif page == "📥 Импорт задач":
    st.header("📥 Импорт задач из Excel")
    st.markdown("""
    ### Инструкция:
    1. **Загрузите шаблон** — скачайте Excel-шаблон для заполнения задач
    2. **Заполните и сохраните шаблон** — внесите данные о задачах
    3. **Импортируйте заполненный шаблон** — загрузите файл обратно в систему
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Шаг 1: Загрузить шаблон")
        st.markdown("Скачайте шаблон Excel для заполнения задач")
        
        template_bytes = download_template()
        if template_bytes:
            st.download_button(
                label="📥 Скачать шаблон Excel",
                data=template_bytes,
                file_name="Шаблон_для_задач_в_МТСИ.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Шаблон не найден в репозитории. Убедитесь, что файл 'Шаблон для задач в МТСИ.xlsx' загружен в Git.")

    with col2:
        st.subheader(" Шаг 2: Импортировать задачи")
        st.markdown("Загрузите заполненный Excel файл")
        
        uploaded_file = st.file_uploader("Выберите файл Excel", type=['xlsx'], key="import_file")
        
        if uploaded_file:
            if st.button("📤 Импортировать задачи", type="primary", use_container_width=True):
                new_tasks = import_tasks_from_excel(uploaded_file)
                
                if new_tasks:
                    if len(st.session_state.tasks) == 1 and st.session_state.tasks[0].get('title') == 'Пополнение в выходной день':
                        st.session_state.tasks = []

                    existing_titles = {t["title"].lower().strip() for t in st.session_state.tasks}
                    tasks_to_add = []
                    skipped_count = 0
                    
                    for task in new_tasks:
                        title_lower = task["title"].lower().strip()
                        if title_lower not in existing_titles:
                            tasks_to_add.append(task)
                            existing_titles.add(title_lower)
                        else:
                            skipped_count += 1
                    
                    if tasks_to_add:
                        max_id = max([t["id"] for t in st.session_state.tasks], default=0)
                        for i, task in enumerate(tasks_to_add):
                            task["id"] = max_id + i + 1
                            st.session_state.tasks.append(task)
                        
                        save_and_commit(st.session_state.tasks, f"Импорт {len(tasks_to_add)} задач")
                        
                        msg = f"✅ Импортировано {len(tasks_to_add)} задач!"
                        if skipped_count > 0:
                            msg += f" (Пропущено {skipped_count} дубликатов)"
                        st.success(msg)
                        st.info("💡 Перейдите в раздел ' Список задач' чтобы увидеть импортированные задачи")
                    else:
                        st.warning("️ Все задачи уже существуют в системе (дубликаты пропущены).")
                else:
                    st.warning("⚠️ Не удалось импортировать задачи. Проверьте формат файла.")

    st.markdown("---")
    st.markdown("### 📋 Шаблон содержит следующие поля:")
    st.markdown("""
    - **Название** — название инициативы
    - **Инициатор** — ФИО ответственного
    - **Тип задачи** — Бизнес-фича / Улучшение / Регуляторка / Техдолг
    - **Проблема/Возможность** — что сейчас не так
    - **Целевая аудитория** — для кого делаем
    - **Метрики успеха** — как измерим успех
    - **Бизнес цель** — KPI/КПЭ
    - **Что будет если не сделать?** — влияние на бизнес
    - **Основной сценарий** — Кто → Что делает → Результат
    - **Срочность** — High / Medium / Low
    - **Бизнес-ценность** — High / Medium / Low
    - **Сложность/Ёмкость** — S / M / L / XL / XXL
    """)
