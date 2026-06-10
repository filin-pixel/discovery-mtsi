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
    },
    {
        "id": 2,
        "title": "Инвесткопилка",
        "type": "Бизнес-фича",
        "problem": "Нет автоматического инвестирования небольших сумм",
        "audience": "Клиенты МТС Инвестиций",
        "business_goal": "Увеличить AUM и количество активных клиентов",
        "metrics": "AUM, фондированные и активные клиенты",
        "impact": "Потеря клиентов, которые хотят инвестировать по чуть-чуть",
        "as_is": "Клим + Саша Стояновский делают прототип",
        "to_be": "Автоматическое инвестирование округленных сумм",
        "use_cases": "Клиент → Подключает инвесткопилку → Система инвестирует округления",
        "dependencies": "Зависит от механики (iOS, web ЛК, комиссия, МТСИ)",
        "constraints": "Желательно не создавать новые договоры/счета",
        "risks": "Сложность с выходными днями и расчетами",
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
        "business_value": "High",
        "complexity": "XL",
        "status": "In Discovery",
        "owner": "Клим + Саша Стояновский",
        "created_date": "2026-06-10",
        "prioritized_at": ""
    },
    {
        "id": 3,
        "title": "СБП по ценным бумагам",
        "type": "Регуляторика",
        "problem": "Регуляторное требование с 01.09",
        "audience": "Все клиенты",
        "business_goal": "Соответствие регуляторным требованиям",
        "metrics": "Регуляторка + потенциально AUM",
        "impact": "Штрафы от регулятора",
        "as_is": "Нужно посмотреть макеты и направить в Депозитарий",
        "to_be": "Интеграция с СБП для операций с ЦБ",
        "use_cases": "Клиент → Выбирает СБП → Совершает операцию с ЦБ",
        "dependencies": "Общебанк, Депозитарий",
        "constraints": "Срок до 01.09",
        "risks": "Задержка от Депозитария",
        "acceptance_criteria": "",
        "subtasks": "",
        "technical_estimate": "",
        "detailed_dependencies": "",
        "analyst_deadline": "2026-06-17",
        "priority": "",
        "rice_score": 0,
        "reach": 0,
        "impact_rice": 0,
        "confidence": 0,
        "effort": 0,
        "executive_priority": True,
        "urgency": "High",
        "business_value": "High",
        "complexity": "XL",
        "status": "Ready for Analyst",
        "owner": "",
        "created_date": "2026-06-10",
        "prioritized_at": ""
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
    "High": " Жесткий дедлайн, блокирует другие задачи, клиенты уже уходят",
    "Medium": "🟡 Желательно в этом квартале, накопительный эффект",
    "Low": "🟢 Нет дедлайна, можно отложить"
}

RICE_HINTS = {
    "reach": "Сколько клиентов/пользователей затронет задача?\n\n• 1-3 = небольшая группа\n• 4-6 = половина клиентской базы\n• 7-10 = все или почти все клиенты",
    "impact": "Насколько сильно задача повлияет на каждого клиента?\n\n• 1 = слабое влияние\n• 2 = среднее влияние (NPS)\n• 3 = массовый эффект (AUM, выручка)",
    "confidence": "Насколько вы уверены в своих оценках?\n\n• 50% = догадки\n• 80% = экспертная оценка\n• 100% = есть данные",
    "effort": "Сколько времени займет реализация?\n\nАвтоматически из поля 'Ёмкость'"
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

def priority_sort_key(task):
    p = task.get("priority", "")
    order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
    return order.get(p, 4)

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
*Метрики успеха:* {task.get('metrics', 'Не указаны')}
*Что будет если не сделать:* {task.get('impact', 'Не указано')}
*Основной сценарий:* {task.get('use_cases', 'Не описан')}

h3. Решение
*As Is:* {task.get('as_is', 'Не описано')}
*To Be:* {task.get('to_be', 'Не описано')}

h3. Ограничения и зависимости
*Зависимости:* {task.get('dependencies', 'Не указаны')}
*Ограничения:* {task.get('constraints', 'Нет')}
*Риски:* {task.get('risks', 'Нет')}

h3. Поля аналитика
*Критерии приемки:* {task.get('acceptance_criteria', 'Не заполнено')}
*Декомпозиция:* {task.get('subtasks', 'Не заполнено')}
*Техническая оценка:* {task.get('technical_estimate', 'Не заполнено')}
*Детальные зависимости:* {task.get('detailed_dependencies', 'Не заполнено')}

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

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача", "📊 Приоритезация задач"])

# ================= ИНСТРУКЦИЯ =================
with st.expander("ℹ️ Как пользоваться Discovery Manager", expanded=False):
    st.markdown("""
    ** Цель этапа Discovery:** Превратить сырую идею в задачу, готовую к передаче аналитику.
    
    **📝 Процесс:**
    1. **Инициатор** создает задачу и заполняет бизнес-поля
    2. **Система** показывает прогресс заполнения
    3. Когда бизнес-поля заполнены на 80%+, появляется кнопка **"Передать аналитику"**
    4. **Аналитик** уточняет требования, пишет Acceptance Criteria
    5. Задача проходит **Приоритезацию** (RICE)
    6. Задача переходит в статус **"Ready for Refinement"**
    """)

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == "📋 Список задач":
    with st.expander(" Легенда", expanded=False):
        col_legend1, col_legend2, col_legend3 = st.columns(3)
        with col_legend1:
            st.markdown("**📌 Статусы задач:**")
            st.markdown("""
            -  **Idea** — сырая идея
            - 🔵 **In Discovery** — бизнес заполняет шаблон
            - 🟠 **Ready for Analyst** — готово к передаче аналитику
            - 🟣 **Requirements Clarification** — аналитик уточняет требования
            - ✅ **Ready for Refinement** — готово к бэклог-рефайнменту
            """)
        with col_legend2:
            st.markdown("** Срочность:**")
            st.markdown("""
            - 🔴 **High** — критично, жесткий дедлайн
            -  **Medium** — средне, желательно в квартале
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
                
                st.subheader("💼 Бизнес-контекст (заполняет инициатор)")
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
                    as_is = st.text_area("As Is (как сейчас)", value=task_to_edit.get("as_is", ""), height=80)
                    to_be = st.text_area("To Be (как должно быть)", value=task_to_edit.get("to_be", ""), height=80)
                with col2:
                    use_cases = st.text_area("Основной сценарий", value=task_to_edit.get("use_cases", ""), height=80)
                
                st.subheader("⚠️ Ограничения и зависимости")
                col1, col2, col3 = st.columns(3)
                with col1:
                    dependencies = st.text_area("Зависимости", value=task_to_edit.get("dependencies", ""), height=80)
                with col2:
                    constraints = st.text_area("Ограничения", value=task_to_edit.get("constraints", ""), height=80)
                with col3:
                    risks = st.text_area("Риски", value=task_to_edit.get("risks", ""), height=80)
                
                st.subheader("🔧 Поля аналитика (заполняет аналитик/чаттер-лид)")
                col1, col2 = st.columns(2)
                with col1:
                    acceptance_criteria = st.text_area("Критерии приемки (DoD)", value=task_to_edit.get("acceptance_criteria", ""), height=80)
                    detailed_dependencies = st.text_area("Детальные технические зависимости", value=task_to_edit.get("detailed_dependencies", ""), height=80)
                with col2:
                    subtasks = st.text_area("Декомпозиция на подзадачи", value=task_to_edit.get("subtasks", ""), height=80)
                    technical_estimate = st.text_area("Техническая оценка", value=task_to_edit.get("technical_estimate", ""), height=80)
                
                if task_to_edit["status"] in ["Ready for Analyst", "Requirements Clarification"]:
                    st.subheader("📅 Срок анализа")
                    default_date = datetime.strptime(task_to_edit.get("analyst_deadline", "2026-06-17"), "%Y-%m-%d").date() if task_to_edit.get("analyst_deadline") else datetime.now() + timedelta(days=7)
                    analyst_deadline = st.date_input("Срок, до которого аналитик должен завершить анализ", value=default_date)
                else:
                    analyst_deadline = None
                
                st.subheader(" Приоритизация")
                col1, col2, col3 = st.columns(3)
                with col1:
                    urgency = st.selectbox("Срочность", ["High", "Medium", "Low"],
                                          index=["High", "Medium", "Low"].index(task_to_edit.get("urgency", "Medium")))
                    st.caption(URGENCY_HINTS[urgency])
                with col2:
                    business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"],
                                                 index=["High", "Medium", "Low"].index(task_to_edit.get("business_value", "Medium")))
                    st.caption(BUSINESS_VALUE_HINTS[business_value])
                with col3:
                    complexity = st.selectbox("Сложность (ёмкость)", ["S", "M", "L", "XL", "XXL"],
                                             index=["S", "M", "L", "XL", "XXL"].index(task_to_edit.get("complexity", "M")))
                    if complexity in COMPLEXITY_INFO:
                        info = COMPLEXITY_INFO[complexity]
                        st.caption(f"{info['days']} | {info['sprints']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Сохранить изменения", type="primary")
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
                    st.success("✅ Изменения сохранены!")
                    st.rerun()
                if cancelled:
                    st.session_state.editing_task_id = None
                    st.rerun()
    else:
        st.header("Бэклог инициатив")
        
        if not st.session_state.tasks:
            st.info("️ Нет задач. Добавь первую!")
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
                st.metric("⚠️ Требуют заполнения", needs_business_fill, help="Бизнес-поля заполнены менее чем на 80%")
            with col3:
                st.metric("🟠 Готовы к аналитику", ready_for_analyst, help="Бизнес-поля заполнены, но статус не изменен")
            with col4:
                st.metric("📊 Не приоритезировано", not_prioritized)
            with col5:
                st.metric("🚨 Просрочено", overdue, help="Срок анализа истек")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.multiselect("Статус",
                    ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                    default=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"])
            with col2:
                value_filter = st.multiselect("Бизнес-ценность", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
            with col3:
                priority_filter = st.multiselect("Приоритет (RICE)",
                    ["P1", "P2", "P3", "P4", "Без приоритета"],
                    default=["P1", "P2", "P3", "P4", "Без приоритета"])
            
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
            
            priority_groups = {
                "P1": [t for t in filtered if t.get("priority") == "P1"],
                "P2": [t for t in filtered if t.get("priority") == "P2"],
                "P3": [t for t in filtered if t.get("priority") == "P3"],
                "P4": [t for t in filtered if t.get("priority") == "P4"],
                "Без приоритета": [t for t in filtered if not t.get("priority")]
            }
            
            for key in priority_groups:
                priority_groups[key].sort(key=lambda x: (
                    {"High": 0, "Medium": 1, "Low": 2}.get(x["business_value"], 3),
                    {"High": 0, "Medium": 1, "Low": 2}.get(x["urgency"], 3)
                ))
            
            st.markdown(f"**Показано: {len(filtered)} из {len(tasks)}**")
            st.markdown("---")
            
            group_headers = {
                "P1": ("🔴", "P1 — Критичный приоритет"),
                "P2": ("🟠", "P2 — Высокий приоритет"),
                "P3": ("🟡", "P3 — Средний приоритет"),
                "P4": ("🟢", "P4 — Низкий приоритет"),
                "Без приоритета": ("⚪", "Без приоритета")
            }
            
            for priority_level, tasks_in_group in priority_groups.items():
                if not tasks_in_group:
                    continue
                
                emoji, header = group_headers[priority_level]
                st.markdown(f"### {emoji} {header}")
                st.markdown(f"*{len(tasks_in_group)} задач*")
                # Заголовок списка
                h1, h2, h3, h4, h5, h6 = st.columns([4, 2, 1.3, 1.3, 1, 1])

                with h1:
                    st.markdown("**Задача**")
                    
                with h2:
                    st.markdown("**Статус**")
                    
                with h3:
                    st.markdown("**Срочность**")
                    
                with h4:
                    st.markdown("**Критичность**")
                    
                with h5:
                    st.markdown("**Ёмкость**")
                    
                with h6:
                    st.markdown("**Приоритет**")
               
                st.markdown("---")

                for task in tasks_in_group:
                    readiness = check_readiness(task)
                    status_emoji = {"Idea": "⚪", "In Discovery": "🔵", "Ready for Analyst": "🟠", "Requirements Clarification": "🟣", "Ready for Refinement": "✅"}[task["status"]]
                    value_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task["business_value"], "⚪")
                    urgency_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.get("urgency"), "⚪")
                    exec_badge = " 👑" if task.get("executive_priority") else ""
                    priority_display = task.get("priority", "")
                    or "—"
                    c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 1.3, 1.3, 1, 1])
                    with c1:
                        st.markdown(f"**{task['title']}**{exec_badge}")
                    with c2:
                        st.markdown(f"{status_emoji} {task['status']}")
                    with c3:
                        st.markdown(f"{urgency_emoji} {task.get('urgency', 'Medium')}")
                    with c4:
                        st.markdown(f"{value_emoji} {task.get('business_value', 'Medium')}")
                    with c5:
                        st.markdown(task.get("complexity", "M"))
                    with c6:
                        st.markdown(priority_display)
                    with st.expander("Подробнее"):

                        
                        col_info1, col_info2, col_info3, col_info4 = st.columns([2.5, 2, 1.5, 1.5])
                        with col_info1:
                            st.markdown(f"{value_emoji} **{task['title']}**")
                        with col_info2:
                            st.markdown(f"{status_emoji} `{task['status']}`")
                        with col_info3:
                            st.markdown(f"💎 {task.get('business_value', '')}")
                        with col_info4:
                            st.markdown(f"⏱ {task.get('complexity', '')}")
                        
                        st.markdown("---")
                        
                        st.markdown("** Прогресс заполнения:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.progress(readiness["business_progress"], text=f"Бизнес-поля (инициатор): {int(readiness['business_progress']*100)}%")
                        with col2:
                            st.progress(readiness["analyst_progress"], text=f"Поля аналитика: {int(readiness['analyst_progress']*100)}%")
                        
                        if readiness["is_ready_for_analyst"] and task["status"] == "In Discovery":
                            st.success("✅ Задача готова к передаче аналитику!")
                            if st.button("🚀 Передать аналитику", key=f"ready_{task['id']}", type="primary"):
                                task["status"] = "Ready for Analyst"
                                task["analyst_deadline"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                                save_tasks_to_file(st.session_state.tasks)
                                st.rerun()
                        elif not readiness["is_ready_for_analyst"]:
                            missing = readiness["missing_business"]
                            if missing:
                                missing_names = [BUSINESS_FIELDS[f] for f in missing]
                                st.warning(f"⚠️ Не заполнены бизнес-поля: {', '.join(missing_names)}")
                        
                        if task.get("analyst_deadline") and task["status"] in ["Ready for Analyst", "Requirements Clarification"]:
                            deadline_date = datetime.strptime(task["analyst_deadline"], "%Y-%m-%d").date()
                            days_left = (deadline_date - datetime.now().date()).days
                            if days_left < 0:
                                st.error(f"🚨 Срок анализа истек! Дедлайн был {task['analyst_deadline']}")
                            elif days_left <= 2:
                                st.warning(f"⏰ Срок анализа истекает через {days_left} дн.")
                            else:
                                st.info(f"📅 Срок анализа: {task['analyst_deadline']} (осталось {days_left} дн.)")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 📌 Основная информация")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(f"**Тип:** {task.get('type', 'Не указан')}")
                        with col2:
                            st.markdown(f"**Владелец:** {task.get('owner', '') or 'Не указан'}")
                        with col3:
                            st.markdown(f"**Создана:** {task.get('created_date', 'Не указана')}")
                        with col4:
                            rice_display = f"RICE: {task['rice_score']:.2f}" if task.get("rice_score") else "RICE: не рассчитан"
                            st.markdown(f"**RICE:** {rice_display}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 📊 Приоритизация")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(f"**Срочность:** {task.get('urgency', 'Medium')}")
                        with col2:
                            st.markdown(f"**Бизнес-ценность:** {task.get('business_value', 'Medium')}")
                        with col3:
                            st.markdown(f"**Сложность:** {task.get('complexity', 'M')}")
                            if task.get("complexity") in COMPLEXITY_INFO:
                                info = COMPLEXITY_INFO[task["complexity"]]
                                st.caption(f"{info['days']} | {info['sprints']}")
                        with col4:
                            priority = task.get('priority', '') or 'Не заполнен'
                            st.markdown(f"**Приоритет:** {priority}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 💼 Бизнес-контекст *(заполняет инициатор)*")
                        st.markdown(f"**Проблема:** {task.get('problem', '') or '⚠️ Не заполнено'}")
                        st.markdown(f"**Целевая аудитория:** {task.get('audience', '') or '⚠️ Не заполнено'}")
                        st.markdown(f"**Бизнес-цель:** {task.get('business_goal', '') or '⚠️ Не заполнено'}")
                        st.markdown(f"**Метрики успеха:** {task.get('metrics', '') or '⚠️ Не заполнено'}")
                        st.markdown(f"**Что будет если не сделать:** {task.get('impact', '') or '⚠️ Не заполнено'}")
                        st.markdown(f"**Основной сценарий:** {task.get('use_cases', '') or '⚠️ Не заполнено'}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 🎯 Решение *(опционально)*")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**As Is:** {task.get('as_is', '') or 'Не описано'}")
                        with col2:
                            st.markdown(f"**To Be:** {task.get('to_be', '') or 'Не описано'}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### ⚠️ Ограничения и зависимости *(опционально)*")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**Зависимости:** {task.get('dependencies', '') or 'Не указаны'}")
                        with col2:
                            st.markdown(f"**Ограничения:** {task.get('constraints', '') or 'Нет'}")
                        with col3:
                            st.markdown(f"**Риски:** {task.get('risks', '') or 'Нет'}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 🔧 Поля аналитика *(заполняет аналитик/чаттер-лид)*")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Критерии приемки:** {task.get('acceptance_criteria', '') or '⚠️ Не заполнено'}")
                            st.markdown(f"**Декомпозиция:** {task.get('subtasks', '') or '️ Не заполнено'}")
                        with col2:
                            st.markdown(f"**Техническая оценка:** {task.get('technical_estimate', '') or '⚠️ Не заполнено'}")
                            st.markdown(f"**Детальные зависимости:** {task.get('detailed_dependencies', '') or '⚠️ Не заполнено'}")
                        
                        st.markdown("---")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            new_status = st.selectbox("Изменить статус",
                                ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                                index=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"].index(task["status"]),
                                key=f"status_{task['id']}")
                            if new_status != task["status"]:
                                task["status"] = new_status
                                save_tasks_to_file(st.session_state.tasks)
                                st.rerun()
                        with col2:
                            if st.button("✏️ Редактировать", key=f"edit_{task['id']}"):
                                st.session_state.editing_task_id = task["id"]
                                st.rerun()
                        with col3:
                            confluence_text = generate_confluence_text(task)
                            st.download_button(
                                label=" Confluence",
                                data=confluence_text,
                                file_name=f"{task['title']}_confluence.txt",
                                mime="text/plain",
                                key=f"confluence_{task['id']}"
                            )
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
        2. Заполни основную информацию о задаче
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
            st.subheader("📌 Базовая информация")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Название *", placeholder="Краткое название")
                task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"])
            with col2:
                owner = st.text_input("Инициатор/Владелец", placeholder="ФИО")
            
            st.subheader("💼 Бизнес-контекст")
            problem = st.text_area("Проблема/Возможность", placeholder="Что не так сейчас?", height=80)
            col1, col2 = st.columns(2)
            with col1:
                audience = st.text_area("Целевая аудитория", placeholder="Для кого делаем?", height=80)
                business_goal = st.text_area("Бизнес-цель", placeholder="Зачем это нужно?", height=80)
            with col2:
                metrics = st.text_area("Метрики успеха", placeholder="Как поймем успех?", height=80)
                impact = st.text_area("Что будет если не сделать", placeholder="Влияние на бизнес", height=80)
            
            st.subheader("🎯 Основной сценарий")
            use_cases = st.text_area("Кто → Что делает → Результат", placeholder="Клиент → Открывает приложение → Видит портфель", height=80)
            
            st.subheader("📊 Приоритизация (предварительная)")
            col1, col2, col3 = st.columns(3)
            with col1:
                urgency = st.selectbox("Срочность", ["High", "Medium", "Low"])
                st.caption(URGENCY_HINTS[urgency])
            with col2:
                business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"])
                st.caption(BUSINESS_VALUE_HINTS[business_value])
            with col3:
                complexity = st.selectbox("Сложность (ёмкость)", ["S", "M", "L", "XL", "XXL"])
                if complexity in COMPLEXITY_INFO:
                    info = COMPLEXITY_INFO[complexity]
                    st.caption(f"{info['days']} | {info['sprints']}")
            
            submitted = st.form_submit_button("✅ Создать задачу", type="primary")
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
                    st.error("❌ Укажи название задачи")

# ================= ЭКРАН 3: ПРИОРИТЕЗАЦИЯ ЗАДАЧ =================
elif page == "📊 Приоритезация задач":
    st.header("📊 Приоритезация задач (RICE)")
    
    tasks = st.session_state.tasks
    unprioritized = [t for t in tasks if not t.get("priority")]
    prioritized = [t for t in tasks if t.get("priority")]
    
    st.markdown("### 📈 Дэшборд")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего задач", len(tasks))
    with col2:
        st.metric("⏳ Не приоритезировано", len(unprioritized))
    with col3:
        st.metric("✅ Приоритезировано", len(prioritized))
    
    st.markdown("---")
    
    if len(tasks) == 0:
        st.info("ℹ️ Нет задач для приоритезации. Создай первую задачу в разделе 'Новая задача'.")
    elif len(unprioritized) == 0:
        st.success("✅ Все задачи приоритезированы!")
    else:
        st.markdown(f"️ **{len(unprioritized)} задач** ожидают приоритезации")
        st.markdown("---")
        
        if st.button("🚀 Начать приоритезацию", type="primary"):
            st.session_state.prioritization_index = 0
            st.session_state.show_prioritization_tasks = True
            st.rerun()
        
        if st.session_state.get("show_prioritization_tasks", False) and st.session_state.prioritization_index < len(unprioritized):
            st.markdown("---")
            current_task = unprioritized[st.session_state.prioritization_index]
            
            st.markdown(f"### 📝 Задача **{st.session_state.prioritization_index + 1}** из **{len(unprioritized)}**")
            st.progress((st.session_state.prioritization_index) / len(unprioritized), text=f"Прогресс: {st.session_state.prioritization_index}/{len(unprioritized)}")
            
            with st.expander(f"📋 {current_task['title']}", expanded=True):
                st.markdown(f"**Проблема:** {current_task.get('problem', 'Не указана')}")
                st.markdown(f"**Бизнес-цель:** {current_task.get('business_goal', 'Не указана')}")
                st.markdown(f"**Метрики:** {current_task.get('metrics', 'Не указаны')}")
                st.markdown(f"**Срочность:** {current_task.get('urgency', 'Medium')} | **Бизнес-ценность:** {current_task.get('business_value', 'Medium')} | **Ёмкость:** {current_task.get('complexity', 'M')}")
            
            st.markdown("---")
            st.subheader("Оценка RICE")
            st.markdown("**Формула:** `RICE = (Reach × Impact × Confidence%) / Effort`")
            st.markdown("Чем выше RICE — тем выше приоритет задачи.")
            
            with st.form(f"rice_form_{current_task['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Reach (Охват)**")
                    with st.popover("️ Что такое Reach?"):
                        st.markdown(RICE_HINTS["reach"])
                    reach = st.slider("Сколько клиентов затронет? (1-10)", 1, 10, 5, key=f"reach_{current_task['id']}")
                    
                    st.markdown("**Impact (Влияние)**")
                    with st.popover("ℹ️ Что такое Impact?"):
                        st.markdown(RICE_HINTS["impact"])
                    impact = st.slider("Насколько сильно повлияет? (1-3)", 1, 3, 2, key=f"impact_{current_task['id']}")
                
                with col2:
                    st.markdown("**Confidence (Уверенность)**")
                    with st.popover("ℹ️ Что такое Confidence?"):
                        st.markdown(RICE_HINTS["confidence"])
                    confidence = st.slider("Насколько уверены в оценках? (50-100%)", 50, 100, 80, key=f"confidence_{current_task['id']}")
                    
                    st.markdown("**Effort (Усилия)**")
                    with st.popover("ℹ️ Что такое Effort?"):
                        st.markdown(RICE_HINTS["effort"])
                    effort_options = ["S", "M", "L", "XL", "XXL"]
                    effort_labels = ["S (< 5 дней)", "M (5-10 дней)", "L (10-20 дней)", "XL (20-40 дней)", "XXL (40+ дней)"]
                    effort_index = effort_options.index(current_task.get("complexity", "M")) if current_task.get("complexity") in effort_options else 1
                    effort = st.selectbox("Ёмкость задачи", effort_labels, index=effort_index, key=f"effort_{current_task['id']}")
                
                executive_priority = st.checkbox("👑 Высший приоритет (задача от руководства)", key=f"exec_{current_task['id']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    submitted = st.form_submit_button("✅ Сохранить и продолжить", type="primary")
                with col2:
                    skipped = st.form_submit_button("⏭️ Пропустить")
                with col3:
                    cancelled = st.form_submit_button("❌ Отмена")
                
                if submitted:
                    effort_score = COMPLEXITY_INFO[effort.split(" ")[0]]["effort_score"]
                    rice_score = calculate_rice(reach, impact, confidence, effort_score)
                    
                    if rice_score >= 5:
                        priority = "P1"
                    elif rice_score >= 2:
                        priority = "P2"
                    elif rice_score >= 1:
                        priority = "P3"
                    else:
                        priority = "P4"
                    
                    current_task.update({
                        "reach": reach, "impact_rice": impact,
                        "confidence": confidence, "effort": effort_score,
                        "rice_score": rice_score, "priority": priority,
                        "executive_priority": executive_priority,
                        "prioritized_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    if current_task["id"] not in st.session_state.prioritization_order:
                        st.session_state.prioritization_order.append(current_task["id"])
                    
                    save_tasks_to_file(st.session_state.tasks)
                    st.success(f"✅ RICE: {rice_score:.2f} → Приоритет: {priority}")
                    
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
        st.markdown("### 📜 История приоритезации (последняя сверху)")
        st.caption("Задачи отображаются в порядке прохождения приоритезации. Последняя приоритезированная — вверху.")
        
        for idx, task_id in enumerate(reversed(st.session_state.prioritization_order)):
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                badge = " " if task.get("executive_priority") else ""
                st.markdown(f"**{idx + 1}.** {badge}**{task['title']}** — ⭐ {task.get('priority', '-')} | RICE: {task.get('rice_score', 0):.2f} | {task.get('prioritized_at', '')}")
