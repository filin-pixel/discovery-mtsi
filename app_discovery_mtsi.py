import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="Discovery Manager", page_icon="🚀", layout="wide")

# ================= ДЕМО-ДАННЫЕ =================
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
        "priority": "P2",
        "rice_score": 2.0,
        "reach": 5,
        "impact_rice": 2,
        "confidence": 80,
        "effort": 1,
        "executive_priority": False,
        "urgency": "High",
        "business_value": "Medium",
        "complexity": "S",
        "status": "In Discovery",
        "owner": "",
        "created_date": "2026-06-10",
        "prioritized_at": "2026-06-10 12:00"
    }
]

# ================= ПРАВИЛА ЗАПОЛНЕНИЯ =================
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
    "Medium": "🟡 Желательно в этом квартале, накопительный эффект",
    "Low": "🟢 Нет дедлайна, можно отложить"
}

RICE_HINTS = {
    "reach": "Сколько клиентов/пользователей затронет задача?\n\n• 1-3 = небольшая группа\n• 4-6 = половина клиентской базы\n• 7-10 = все или почти все клиенты",
    "impact": "Насколько сильно задача повлияет на каждого клиента?\n\n• 1 = слабое влияние\n• 2 = среднее влияние (NPS)\n• 3 = массовый эффект (AUM, выручка)",
    "confidence": "Насколько вы уверены в своих оценках?\n\n• 50% = догадки\n• 80% = экспертная оценка\n• 100% = есть данные",
    "effort": "Сколько времени займет реализация?\n\nАвтоматически из поля 'Ёмкость'"
}

def check_readiness(task):
    filled_business = [f for f in BUSINESS_FIELDS if task.get(f)]
    business_progress = len(filled_business) / len(BUSINESS_FIELDS)
    return {
        "business_progress": business_progress,
        "is_ready_for_analyst": business_progress >= 0.83,
        "missing_business": [f for f in BUSINESS_FIELDS if not task.get(f)]
    }

def calculate_rice(reach, impact, confidence, effort):
    if effort == 0:
        return 0
    return (reach * impact * (confidence / 100)) / effort

def priority_sort_key(task):
    p = task.get("priority", "")
    order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
    return order.get(p, 4)

def save_tasks_to_file(tasks):
    """Сохраняет задачи в JSON файл (для постоянного хранения)"""
    try:
        with open('tasks_data.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

def load_tasks_from_file():
    """Загружает задачи из JSON файла"""
    try:
        if os.path.exists('tasks_data.json'):
            with open('tasks_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

# ================= ИНИЦИАЛИЗАЦИЯ =================
# Сначала пробуем загрузить из файла
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

st.title("🚀 Discovery Manager")
st.markdown("Конвейер спринтов: Этап Discovery")

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача", "📊 Приоритезация задач"])

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
    """)

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == "📋 Список задач":
    # ЛЕГЕНДА — теперь только здесь!
    with st.expander("📖 Легенда", expanded=False):
        col_legend1, col_legend2, col_legend3 = st.columns(3)
        with col_legend1:
            st.markdown("**📌 Статусы задач:**")
            st.markdown("""
            - ⚪ **Idea** — сырая идея
            - 🔵 **In Discovery** — бизнес заполняет шаблон
            - 🟠 **Ready for Analyst** — готово к передаче аналитику
            - 🟣 **Requirements Clarification** — аналитик уточняет требования
            - ✅ **Ready for Refinement** — готово к бэклог-рефайнменту
            """)
        with col_legend2:
            st.markdown("**⏰ Срочность:**")
            st.markdown("""
            - 🔴 **High** — критично, жесткий дедлайн
            - 🟡 **Medium** — средне, желательно в квартале
            - 🟢 **Low** — низко, можно отложить
            """)
        with col_legend3:
            st.markdown("**📏 Ёмкость (T-shirt sizing):**")
            st.markdown("""
            - **S** — < 5 дней (< 0.5 спринта)
            - **M** — 5-10 дней (0.5-1 спринт)
            - **L** — 10-20 дней (1-2 спринта)
            - **XL** — 20-40 дней (2-4 спринта)
            - **XXL** — 40+ дней (4+ спринтов)
            
            *Спринт = 10 дней*
            """)
        st.markdown("---")
    
    # Остальной код списка задач...
    if st.session_state.editing_task_id is not None:
        task_to_edit = next((t for t in st.session_state.tasks if t["id"] == st.session_state.editing_task_id), None)
        if task_to_edit:
            st.header(f"✏️ Редактирование: {task_to_edit['title']}")
            with st.form("edit_task_form"):
                st.subheader("📌 Базовая информация")
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Название *", value=task_to_edit.get("title", ""))
                    task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"],
                                           index=["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"].index(task_to_edit.get("type", "Бизнес-фича")))
                with col2:
                    owner = st.text_input("Инициатор/Владелец", value=task_to_edit.get("owner", ""))
                
                st.subheader("💼 Бизнес-контекст")
                problem = st.text_area("Проблема/Возможность", value=task_to_edit.get("problem", ""), height=80)
                col1, col2 = st.columns(2)
                with col1:
                    audience = st.text_area("Целевая аудитория", value=task_to_edit.get("audience", ""), height=80)
                    business_goal = st.text_area("Бизнес-цель", value=task_to_edit.get("business_goal", ""), height=80)
                with col2:
                    metrics = st.text_area("Метрики успеха", value=task_to_edit.get("metrics", ""), height=80)
                    impact = st.text_area("Что будет если не сделать", value=task_to_edit.get("impact", ""), height=80)
                
                st.subheader("🎯 Решение и сценарии")
                col1, col2 = st.columns(2)
                with col1:
                    as_is = st.text_area("As Is", value=task_to_edit.get("as_is", ""), height=80)
                    to_be = st.text_area("To Be", value=task_to_edit.get("to_be", ""), height=80)
                with col2:
                    use_cases = st.text_area("Основной сценарий", value=task_to_edit.get("use_cases", ""), height=80)
                
                st.subheader("⚠️ Ограничения")
                col1, col2, col3 = st.columns(3)
                with col1:
                    dependencies = st.text_area("Зависимости", value=task_to_edit.get("dependencies", ""), height=80)
                with col2:
                    constraints = st.text_area("Ограничения", value=task_to_edit.get("constraints", ""), height=80)
                with col3:
                    risks = st.text_area("Риски", value=task_to_edit.get("risks", ""), height=80)
                
                st.subheader("🔧 Поля аналитика")
                col1, col2 = st.columns(2)
                with col1:
                    acceptance_criteria = st.text_area("Критерии приемки", value=task_to_edit.get("acceptance_criteria", ""), height=80)
                    detailed_dependencies = st.text_area("Детальные зависимости", value=task_to_edit.get("detailed_dependencies", ""), height=80)
                with col2:
                    subtasks = st.text_area("Декомпозиция", value=task_to_edit.get("subtasks", ""), height=80)
                    technical_estimate = st.text_area("Техническая оценка", value=task_to_edit.get("technical_estimate", ""), height=80)
                
                if task_to_edit["status"] in ["Ready for Analyst", "Requirements Clarification"]:
                    st.subheader("📅 Срок анализа")
                    default_date = datetime.strptime(task_to_edit.get("analyst_deadline", "2026-06-17"), "%Y-%m-%d").date() if task_to_edit.get("analyst_deadline") else datetime.now() + timedelta(days=7)
                    analyst_deadline = st.date_input("Срок анализа", value=default_date)
                else:
                    analyst_deadline = None
                
                st.subheader("📊 Приоритизация")
                col1, col2, col3 = st.columns(3)
                with col1:
                    urgency = st.selectbox("Срочность", ["High", "Medium", "Low"],
                                          index=["High", "Medium", "Low"].index(task_to_edit.get("urgency", "Medium")))
                with col2:
                    business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"],
                                                 index=["High", "Medium", "Low"].index(task_to_edit.get("business_value", "Medium")))
                with col3:
                    complexity = st.selectbox("Сложность", ["S", "M", "L", "XL", "XXL"],
                                             index=["S", "M", "L", "XL", "XXL"].index(task_to_edit.get("complexity", "M")))
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Сохранить", type="primary")
                with col2:
                    cancelled = st.form_submit_button("❌ Отмена")
                
                if submitted:
                    task_to_edit.update({
                        "title": title, "type": task_type, "owner": owner,
                        "problem": problem, "audience": audience, "business_goal": business_goal,
                        "metrics": metrics, "impact": impact, "as_is": as_is, "to_be": to_be,
                        "use_cases": use_cases, "dependencies": dependencies,
                        "constraints": constraints, "risks": risks,
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
            st.info("ℹ️ Нет задач. Создай первую!")
        else:
            tasks = st.session_state.tasks
            
            # ДЭШБОРД
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
            
            # ФИЛЬТРЫ
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.multiselect("Статус",
                    ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                    default=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"])
            with col2:
                value_filter = st.multiselect("Бизнес-ценность", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
            with col3:
                priority_filter = st.multiselect("Приоритет",
                    ["P1", "P2", "P3", "P4", "Без приоритета"],
                    default=["P1", "P2", "P3", "P4", "Без приоритета"])
            
            filtered = []
            for t in tasks:
                if t["status"] not in status_filter or t["business_value"] not in value_filter:
                    continue
                p = t.get("priority", "") or "Без приоритета"
                if p not in priority_filter:
                    continue
                filtered.append(t)
            
            filtered.sort(key=lambda x: (priority_sort_key(x), {"High": 0, "Medium": 1, "Low": 2}.get(x["business_value"], 3)))
            
            st.markdown(f"**Показано: {len(filtered)} из {len(tasks)}**")
            st.markdown("---")
            
            for task in filtered:
                readiness = check_readiness(task)
                status_emoji = {"Idea": "⚪", "In Discovery": "🔵", "Ready for Analyst": "🟠", "Requirements Clarification": "🟣", "Ready for Refinement": "✅"}[task["status"]]
                value_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[task["business_value"]]
                
                priority_badge = f" | ⭐ **{task['priority']}**" if task.get("priority") else ""
                if task.get("executive_priority"):
                    priority_badge += " 👑"
                
                with st.expander(f"{value_emoji} **{task['title']}** {status_emoji} `{task['status']}`{priority_badge}"):
                    st.markdown("**📊 Прогресс:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.progress(readiness["business_progress"], text=f"Бизнес-поля: {int(readiness['business_progress']*100)}%")
                    with col2:
                        st.caption(f"RICE: {task.get('rice_score', 0):.2f}" if task.get("rice_score") else "RICE: не рассчитан")
                    
                    if readiness["is_ready_for_analyst"] and task["status"] == "In Discovery":
                        st.success("✅ Готово к передаче аналитику!")
                        if st.button("🚀 Передать аналитику", key=f"ready_{task['id']}", type="primary"):
                            task["status"] = "Ready for Analyst"
                            task["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                            save_tasks_to_file(st.session_state.tasks)
                            st.rerun()
                    elif not readiness["is_ready_for_analyst"]:
                        missing = [BUSINESS_FIELDS[f] for f in readiness["missing_business"]]
                        if missing:
                            st.warning(f"⚠️ Не заполнено: {', '.join(missing)}")
                    
                    st.markdown("---")
                    st.markdown(f"**Проблема:** {task.get('problem', 'Не указано')}")
                    st.markdown(f"**Цель:** {task.get('business_goal', 'Не указана')}")
                    st.markdown(f"**Метрики:** {task.get('metrics', 'Не указаны')}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Редактировать", key=f"edit_{task['id']}"):
                            st.session_state.editing_task_id = task["id"]
                            st.rerun()
                    with col2:
                        new_status = st.selectbox("Статус",
                            ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                            index=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"].index(task["status"]),
                            key=f"status_{task['id']}")
                        if new_status != task["status"]:
                            task["status"] = new_status
                            save_tasks_to_file(st.session_state.tasks)
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Удалить", key=f"delete_{task['id']}"):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                            save_tasks_to_file(st.session_state.tasks)
                            st.rerun()

# ================= ЭКРАН 2: НОВАЯ ЗАДАЧА =================
elif page == "➕ Новая задача":
    # Здесь НЕТ легенды!
    if not st.session_state.show_new_task_form:
        st.header("Создание новой инициативы")
        st.markdown("""
        💡 **Как это работает:**
        1. Нажми кнопку ниже
        2. Заполни основную информацию
        3. Система создаст задачу со статусом **Idea**
        4. Дополни детали через редактирование
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
            st.subheader("📌 Базовая информация")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Название *", placeholder="Краткое название")
                task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"])
            with col2:
                owner = st.text_input("Инициатор/Владелец", placeholder="ФИО")
            
            st.subheader("💼 Бизнес-контекст")
            problem = st.text_area("Проблема/Возможность", placeholder="Что не так?", height=80)
            col1, col2 = st.columns(2)
            with col1:
                audience = st.text_area("Целевая аудитория", placeholder="Для кого?", height=80)
                business_goal = st.text_area("Бизнес-цель", placeholder="Зачем?", height=80)
            with col2:
                metrics = st.text_area("Метрики успеха", placeholder="Как измерим?", height=80)
                impact = st.text_area("Если не сделать", placeholder="Влияние", height=80)
            
            st.subheader("🎯 Сценарий")
            use_cases = st.text_area("Кто → Что → Результат", placeholder="Клиент → Действие → Результат", height=80)
            
            st.subheader("📊 Приоритизация")
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
                        "title": title, "type": task_type, "owner": owner,
                        "problem": problem, "audience": audience, "business_goal": business_goal,
                        "metrics": metrics, "impact": impact, "use_cases": use_cases,
                        "as_is": "", "to_be": "", "dependencies": "", "constraints": "", "risks": "",
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
                else:
                    st.error("❌ Укажи название")

# ================= ЭКРАН 3: ПРИОРИТЕЗАЦИЯ =================
elif page == "📊 Приоритезация задач":
    st.header("📊 Приоритезация (RICE)")
    
    tasks = st.session_state.tasks
    unprioritized = [t for t in tasks if not t.get("priority")]
    prioritized = [t for t in tasks if t.get("priority")]
    
    st.markdown("### 📈 Дэшборд")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего", len(tasks))
    with col2:
        st.metric(" Не приоритезировано", len(unprioritized))
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
        
        if st.button("🚀 Начать", type="primary"):
            st.session_state.prioritization_index = 0
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.prioritization_index < len(unprioritized):
            current_task = unprioritized[st.session_state.prioritization_index]
            
            st.markdown(f"### Задача {st.session_state.prioritization_index + 1} из {len(unprioritized)}")
            
            with st.expander(f"📋 {current_task['title']}", expanded=True):
                st.markdown(f"**Проблема:** {current_task.get('problem', '')}")
                st.markdown(f"**Цель:** {current_task.get('business_goal', '')}")
                st.markdown(f"**Срочность:** {current_task.get('urgency')} | **Ценность:** {current_task.get('business_value')}")
            
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
                    effort = st.selectbox("Ёмкость", ["S", "M", "L", "XL", "XXL"], 
                                         index=["S", "M", "L", "XL", "XXL"].index(current_task.get("complexity", "M")),
                                         key=f"e_{current_task['id']}")
                
                exec_priority = st.checkbox("👑 Высший приоритет (от руководства)", key=f"exec_{current_task['id']}")
                
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
                    
                    save_tasks_to_file(st.session_state.tasks)
                    st.success(f"✅ RICE: {rice_score:.2f} → {priority}")
                    
                    if st.session_state.prioritization_index < len(unprioritized) - 1:
                        st.session_state.prioritization_index += 1
                    st.rerun()
                
                if skipped:
                    if st.session_state.prioritization_index < len(unprioritized) - 1:
                        st.session_state.prioritization_index += 1
                    st.rerun()
                
                if cancelled:
                    st.rerun()
    
    if st.session_state.prioritization_order:
        st.markdown("---")
        st.markdown("### 📜 История (последняя сверху)")
        for idx, task_id in enumerate(reversed(st.session_state.prioritization_order)):
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                badge = "👑 " if task.get("executive_priority") else ""
                st.markdown(f"**{idx + 1}.** {badge}**{task['title']}** — {task.get('priority')} | RICE: {task.get('rice_score', 0):.2f}")
