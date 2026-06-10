import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Discovery Manager", page_icon="", layout="wide")

# ================= ДЕМО-ДАННЫЕ (одна задача) =================
DEMO_TASKS = [
    {
        "id": 1,
        "title": "Пополнение в выходной день",
        "type": "Улучшение",
        "problem": "Клиенты не могут пополнить счет в выходные",
        "audience": "Активные клиенты",
        "business_goal": "Улучшить NPS",
        "metrics": "NPS, влияние на отложенное поручение",
        "impact": "Недовольство клиентов",
        "as_is": "Пополнение только в рабочие дни",
        "to_be": "Пополнение 24/7 без вывода день в день",
        "use_cases": "Клиент → Выходной день → Пополняет счет",
        "dependencies": "Нет",
        "constraints": "Без вывода день в день",
        "risks": "Не учитывается сумма пополнения в общей сумме инвестиций",
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
        "urgency": "High",
        "business_value": "Medium",
        "complexity": "S",
        "status": "In Discovery",
        "owner": "",
        "created_date": "2026-06-10",
        "prioritized_at": ""
    }
]

# ================= КОНСТАНТЫ =================
BUSINESS_FIELDS = {
    "problem": "Проблема/Возможность",
    "audience": "Целевая аудитория",
    "business_goal": "Бизнес-цель",
    "metrics": "Метрики успеха",
    "impact": "Что будет если не сделать",
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
    "Medium": "🟡 Влияет на NPS, активность клиентов, конверсию (но не критично)",
    "Low": "🟢 Косметические улучшения, внутренние удобства"
}

URGENCY_HINTS = {
    "High": "🔴 Жесткий дедлайн, блокирует другие задачи, клиенты уже уходят",
    "Medium": " Желательно в этом квартале, накопительный эффект",
    "Low": "🟢 Нет дедлайна, можно отложить"
}

RICE_HINTS = {
    "reach": "Сколько клиентов затронет?\n\n• 1-3 = небольшая группа\n• 4-6 = половина клиентов\n• 7-10 = все клиенты",
    "impact": "Насколько сильно повлияет?\n\n• 1 = слабое\n• 2 = среднее (NPS)\n• 3 = массовый эффект (AUM, выручка)",
    "confidence": "Насколько уверены в оценках?\n\n• 50% = догадки\n• 80% = экспертная оценка\n• 100% = есть данные",
    "effort": "Сколько времени займет?\n\nАвтоматически из поля 'Ёмкость'"
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

def calculate_rice(reach, impact, confidence, effort):
    if effort == 0:
        return 0
    return (reach * impact * (confidence / 100)) / effort

def save_tasks_to_file(tasks):
    try:
        with open('tasks_data.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

def load_tasks_from_file():
    try:
        if os.path.exists('tasks_data.json'):
            with open('tasks_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

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

def create_template():
    """Создает шаблон Excel для импорта задач"""
    df = pd.DataFrame(columns=[
        "Название", "Инициатор", "Тип задачи", "Проблема/Возможность",
        "Целевая аудитория", "Метрики успеха", "Бизнес цель",
        "Что будет если не сделать?", "Основной сценарий",
        "Срочность", "Бизнес-ценность", "Сложность/Ёмкость"
    ])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Шаблон', index=False)
    output.seek(0)
    return output

def import_tasks_from_excel(uploaded_file):
    """Импортирует задачи из Excel файла"""
    try:
        df = pd.read_excel(uploaded_file)
        tasks = []
        
        for idx, row in df.iterrows():
            if pd.notna(row.get("Название")) and str(row.get("Название")).strip():
                task = {
                    "id": idx + 1,
                    "title": str(row.get("Название", "")).strip(),
                    "owner": str(row.get("Инициатор", "")).strip(),
                    "type": str(row.get("Тип задачи", "Бизнес-фича")).strip(),
                    "problem": str(row.get("Проблема/Возможность", "")).strip(),
                    "audience": str(row.get("Целевая аудитория", "")).strip(),
                    "metrics": str(row.get("Метрики успеха", "")).strip(),
                    "business_goal": str(row.get("Бизнес цель", "")).strip(),
                    "impact": str(row.get("Что будет если не сделать?", "")).strip(),
                    "use_cases": str(row.get("Основной сценарий", "")).strip(),
                    "urgency": str(row.get("Срочность", "Medium")).strip(),
                    "business_value": str(row.get("Бизнес-ценность", "Medium")).strip(),
                    "complexity": str(row.get("Сложность/Ёмкость", "M")).strip(),
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
        st.error(f"Ошибка импорта: {e}")
        return []

# ================= ИНИЦИАЛИЗАЦИЯ =================
saved_tasks = load_tasks_from_file()

if "tasks" not in st.session_state:
    if saved_tasks:
        st.session_state.tasks = saved_tasks
    else:
        st.session_state.tasks = DEMO_TASKS.copy()

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

# ================= ИНСТРУКЦИЯ =================
with st.expander("ℹ️ Как пользоваться Discovery Manager", expanded=False):
    st.markdown("""
    **🎯 Цель этапа Discovery:** Превратить сырую идею в задачу, готовую к передаче аналитику.
    
    **📝 Процесс:**
    1. **Инициатор** создает задачу и заполняет бизнес-поля
    2. **Система** показывает прогресс заполнения
    3. Когда бизнес-поля заполнены на 80%+, появляется кнопка **"Передать аналитику"**
    4. **Аналитик** уточняет требования
    5. Задача проходит **Приоритезацию** (RICE)
    6. Задача переходит в статус **"Ready for Refinement"**
    """)

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == " Список задач":
    with st.expander("📖 Легенда", expanded=False):
        col_legend1, col_legend2, col_legend3 = st.columns(3)
        with col_legend1:
            st.markdown("**📌 Статусы задач:**")
            st.markdown("""
            - ⚪ **Idea** — сырая идея
            - 🔵 **In Discovery** — бизнес заполняет шаблон
            - 🟠 **Ready for Analyst** — готово к передаче аналитику
            - 🟣 **Requirements Clarification** — аналитик уточняет
            - ✅ **Ready for Refinement** — готово к команде
            """)
        with col_legend2:
            st.markdown("**⏰ Срочность:**")
            st.markdown("""
            - 🔴 **High** — критично
            - 🟡 **Medium** — средне
            - 🟢 **Low** — низко
            """)
        with col_legend3:
            st.markdown("**📏 мкость:**")
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
                
                st.subheader("🎯 Решение")
                as_is = st.text_area("As Is", value=task_to_edit.get("as_is", ""), height=80)
                to_be = st.text_area("To Be", value=task_to_edit.get("to_be", ""), height=80)
                
                st.subheader("️ Ограничения")
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
                    urgency = st.selectbox("Срочность", ["High", "Medium", "Low"])
                with col2:
                    business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"])
                with col3:
                    complexity = st.selectbox("Сложность", ["S", "M", "L", "XL", "XXL"])
                
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
                    save_tasks_to_file(st.session_state.tasks)
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
                st.metric(" Просрочено", overdue)
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.multiselect("Статус", ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"], default=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"])
            with col2:
                value_filter = st.multiselect("Бизнес-ценность", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
            with col3:
                priority_filter = st.multiselect("Приоритет", ["P1", "P2", "P3", "P4", "Без приоритета"], default=["P1", "P2", "P3", "P4", "Без приоритета"])
            
            filtered = []
            for t in tasks:
                if t["status"] not in status_filter:
                    continue
                if t["business_value"] not in value_filter:
                    continue
                p = t.get("priority", "") or "Без приоритета"
                if p not in priority_filter:
                    continue
                filtered.append(t)
            
            st.markdown(f"**Показано: {len(filtered)}**")
            st.markdown("---")
            
            for task in filtered:
                readiness = check_readiness(task)
                status_emoji = {"Idea": "", "In Discovery": "🔵", "Ready for Analyst": "🟠", "Requirements Clarification": "🟣", "Ready for Refinement": "✅"}[task["status"]]
                value_emoji = {"High": "🔴", "Medium": "🟡", "Low": ""}[task["business_value"]]
                exec_badge = " 👑" if task.get("executive_priority") else ""
                
                urgency_emoji = "🔴" if task.get("urgency") == "High" else "🟡" if task.get("urgency") == "Medium" else "🟢"
                priority = task.get('priority', '')
                priority_display = f"⭐ {priority}" if priority else "⚪ Без приоритета"

                
                # ===== Строка задачи до раскрытия =====
                priority = task.get("priority", "")
                priority_display = priority if priority else "—"

                col1, col2, col3, col4, col5, col6 = st.columns([4, 2, 1.3, 1.3, 1, 1])
                with col1:
                    st.markdown(f"**{task['title']}** {exec_badge}")
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

                
                with st.expander("Подробнее", expanded=False):
         
                    st.markdown("**📊 Прогресс:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.progress(readiness["business_progress"], text=f"Бизнес-поля: {int(readiness['business_progress']*100)}%")
                    
                    if readiness["is_ready_for_analyst"] and task["status"] == "In Discovery":
                        st.success("✅ Готово к передаче аналитику!")
                        if st.button(" Передать аналитику", key=f"ready_{task['id']}", type="primary"):
                            task["status"] = "Ready for Analyst"
                            task["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                            save_tasks_to_file(st.session_state.tasks)
                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown(f"**Проблема:** {task.get('problem', 'Не указана')}")
                    st.markdown(f"**Цель:** {task.get('business_goal', 'Не указана')}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✏️ Редактировать", key=f"edit_{task['id']}"):
                            st.session_state.editing_task_id = task["id"]
                            st.rerun()
                    with col2:
                        new_status = st.selectbox("Статус", ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"], index=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"].index(task["status"]), key=f"status_{task['id']}")
                        if new_status != task["status"]:
                            task["status"] = new_status
                            save_tasks_to_file(st.session_state.tasks)
                            st.rerun()
                    with col3:
                        confluence_text = generate_confluence_text(task)
                        st.download_button(label="📥 Confluence", data=confluence_text, file_name=f"{task['title']}.txt", mime="text/plain", key=f"confluence_{task['id']}")
                    with col4:
                        if st.button("🗑️ Удалить", key=f"delete_{task['id']}"):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                            save_tasks_to_file(st.session_state.tasks)
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
                urgency = st.selectbox("Срочность", ["High", "Medium", "Low"])
            with col2:
                business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"])
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
                    save_tasks_to_file(st.session_state.tasks)
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
            st.progress((st.session_state.prioritization_index) / len(unprioritized), text=f"Прогресс: {st.session_state.prioritization_index}/{len(unprioritized)}")
            
            with st.expander(f"📋 {current_task['title']}", expanded=True):
                st.markdown(f"**Проблема:** {current_task.get('problem', '')}")
                st.markdown(f"**Цель:** {current_task.get('business_goal', '')}")
            
            st.markdown("---")
            st.subheader("Оценка RICE")
            
            with st.form(f"rice_{current_task['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    with st.popover("ℹ️ Reach"):
                        st.markdown(RICE_HINTS["reach"])
                    reach = st.slider("Охват (1-10)", 1, 10, 5, key=f"r_{current_task['id']}")
                    
                    with st.popover("ℹ️ Impact"):
                        st.markdown(RICE_HINTS["impact"])
                    impact = st.slider("Влияние (1-3)", 1, 3, 2, key=f"i_{current_task['id']}")
                
                with col2:
                    with st.popover("ℹ️ Confidence"):
                        st.markdown(RICE_HINTS["confidence"])
                    confidence = st.slider("Уверенность (50-100%)", 50, 100, 80, key=f"c_{current_task['id']}")
                    
                    with st.popover("ℹ️ Effort"):
                        st.markdown(RICE_HINTS["effort"])
                    effort = st.selectbox("Ёмкость", ["S", "M", "L", "XL", "XXL"], index=["S", "M", "L", "XL", "XXL"].index(current_task.get("complexity", "M")), key=f"e_{current_task['id']}")
                
                exec_priority = st.checkbox("👑 Высший приоритет", key=f"exec_{current_task['id']}")
                
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
                    
                    save_tasks_to_file(st.session_state.tasks)
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
elif page == " Импорт задач":
    st.header(" Импорт задач из Excel")
    
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
        
        template_file = create_template()
        st.download_button(
            label="📥 Загрузить шаблон",
            data=template_file,
            file_name="Шаблон_задач_MTSI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.subheader("📤 Шаг 2: Импортировать задачи")
        st.markdown("Загрузите заполненный Excel файл")
        
        uploaded_file = st.file_uploader("Выберите файл Excel", type=['xlsx'], key="import_file")
        
        if uploaded_file:
            if st.button("📤 Импортировать задачи", type="primary", use_container_width=True):
                new_tasks = import_tasks_from_excel(uploaded_file)
                
                if new_tasks:
                    max_id = max([t["id"] for t in st.session_state.tasks], default=0)
                    for i, task in enumerate(new_tasks):
                        task["id"] = max_id + i + 1
                        st.session_state.tasks.append(task)
                    
                    save_tasks_to_file(st.session_state.tasks)
                    st.success(f"✅ Импортировано {len(new_tasks)} задач!")
                    st.info(" Перейдите в раздел '📋 Список задач' чтобы увидеть импортированные задачи")
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
