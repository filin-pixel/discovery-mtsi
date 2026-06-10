import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Discovery Manager", page_icon="🚀", layout="wide")

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
        "use_cases": "Клиент → Выходной день → Пополняет счет → Средства зачисляются в понедельник",
        "dependencies": "Нет",
        "constraints": "Без вывода день в день",
        "risks": "Не учитывается сумма пополнения в общей сумме инвестиций",
        "acceptance_criteria": "",
        "subtasks": "",
        "technical_estimate": "",
        "detailed_dependencies": "",
        "analyst_deadline": "",
        "urgency": "High",
        "business_value": "Medium",
        "complexity": "S",
        "status": "In Discovery",
        "owner": "",
        "created_date": "2026-06-10"
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
    "technical_estimate": "Техническая оценка (story points)",
    "detailed_dependencies": "Детальные технические зависимости"
}

OPTIONAL_FIELDS = {
    "as_is": "As Is (как сейчас)",
    "to_be": "To Be (как должно быть)",
    "dependencies": "Зависимости (высокоуровневые)",
    "constraints": "Ограничения",
    "risks": "Риски"
}

def check_readiness(task):
    """Проверяет готовность задачи к передаче аналитику"""
    filled_business = [f for f in BUSINESS_FIELDS if task.get(f)]
    filled_analyst = [f for f in ANALYST_FIELDS if task.get(f)]
    
    business_progress = len(filled_business) / len(BUSINESS_FIELDS)
    analyst_progress = len(filled_analyst) / len(ANALYST_FIELDS)
    
    is_ready_for_analyst = business_progress >= 0.83
    
    return {
        "business_progress": business_progress,
        "analyst_progress": analyst_progress,
        "is_ready_for_analyst": is_ready_for_analyst,
        "filled_business": filled_business,
        "missing_business": [f for f in BUSINESS_FIELDS if not task.get(f)],
        "filled_analyst": filled_analyst,
        "missing_analyst": [f for f in ANALYST_FIELDS if not task.get(f)]
    }

# ================= ИНИЦИАЛИЗАЦИЯ =================
if "tasks" not in st.session_state:
    st.session_state.tasks = DEMO_TASKS.copy()

if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

st.title("🚀 Discovery Manager")
st.markdown("Конвейер спринтов: Этап Discovery")

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача"])

# ================= ИНСТРУКЦИЯ =================
with st.expander("ℹ️ Как пользоваться Discovery Manager", expanded=False):
    st.markdown("""
    **🎯 Цель этапа Discovery:** Превратить сырую идею в задачу, готовую к передаче аналитику.
    
    **📝 Процесс:**
    1. **Инициатор** создает задачу и заполняет бизнес-поля (проблема, цель, метрики, сценарий)
    2. **Система** автоматически показывает прогресс заполнения
    3. Когда бизнес-поля заполнены на 80%+, появляется кнопка **"Передать аналитику"**
    4. **Аналитик/Чаттер-лид** уточняет требования, пишет Acceptance Criteria, оценивает сложность
    5. Задача переходит в статус **"Ready for Refinement"** и идет к команде
    
    **💡 Важно:**
    - Задачу можно создать с **любым количеством полей** - не нужно заполнять всё сразу
    - Система подскажет, какие поля нужно дополнить
    - Статусы меняются автоматически или вручную
    """)

# ================= ЛЕГЕНДА =================
st.markdown("### 📖 Легенда")

col_legend1, col_legend2, col_legend3 = st.columns(3)

with col_legend1:
    st.markdown("** Статусы задач:**")
    st.markdown("""
    - ⚪ **Idea** — сырая идея, не обсуждали
    - 🔵 **In Discovery** — бизнес заполняет шаблон
    - 🟠 **Ready for Analyst** — готово к передаче аналитику
    - 🟣 **Requirements Clarification** — аналитик уточняет требования
    - ✅ **Ready for Refinement** — готово к бэклог-рефайнменту
    """)

with col_legend2:
    st.markdown("** Приоритеты:**")
    st.markdown("""
    - 🔴 **High** — критично, высокий приоритет
    -  **Medium** — средне
    - 🟢 **Low** — низко, можно отложить
    """)

with col_legend3:
    st.markdown("**📏 Ёмкость (T-shirt sizing):**")
    st.markdown("""
    - **XS** — очень маленькая (< 1 дня)
    - **S** — маленькая (1-3 дня)
    - **M** — средняя (3-5 дней)
    - **L** — большая (1-2 недели)
    - **XL** — очень большая (2+ недели)
    """)

st.markdown("---")

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == "📋 Список задач":
    if st.session_state.editing_task_id is not None:
        task_to_edit = next((t for t in st.session_state.tasks if t["id"] == st.session_state.editing_task_id), None)
        
        if task_to_edit:
            st.header(f"️ Редактирование: {task_to_edit['title']}")
            
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
                    technical_estimate = st.text_area("Техническая оценка (story points)", value=task_to_edit.get("technical_estimate", ""), height=80)
                
                if task_to_edit["status"] in ["Ready for Analyst", "Requirements Clarification"]:
                    st.subheader("📅 Срок анализа")
                    analyst_deadline = st.date_input("Срок, до которого аналитик должен завершить анализ", 
                                                    value=datetime.strptime(task_to_edit.get("analyst_deadline", "2026-06-17"), "%Y-%m-%d").date() if task_to_edit.get("analyst_deadline") else datetime.now() + timedelta(days=7))
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
                    complexity = st.selectbox("Сложность", ["XS", "S", "M", "L", "XL"],
                                             index=["XS", "S", "M", "L", "XL"].index(task_to_edit.get("complexity", "M")))
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button(" Сохранить изменения", type="primary")
                with col2:
                    cancelled = st.form_submit_button("❌ Отмена")
                
                if submitted:
                    task_to_edit["title"] = title
                    task_to_edit["type"] = task_type
                    task_to_edit["owner"] = owner
                    task_to_edit["problem"] = problem
                    task_to_edit["audience"] = audience
                    task_to_edit["business_goal"] = business_goal
                    task_to_edit["metrics"] = metrics
                    task_to_edit["impact"] = impact
                    task_to_edit["as_is"] = as_is
                    task_to_edit["to_be"] = to_be
                    task_to_edit["use_cases"] = use_cases
                    task_to_edit["dependencies"] = dependencies
                    task_to_edit["constraints"] = constraints
                    task_to_edit["risks"] = risks
                    task_to_edit["acceptance_criteria"] = acceptance_criteria
                    task_to_edit["subtasks"] = subtasks
                    task_to_edit["technical_estimate"] = technical_estimate
                    task_to_edit["detailed_dependencies"] = detailed_dependencies
                    task_to_edit["urgency"] = urgency
                    task_to_edit["business_value"] = business_value
                    task_to_edit["complexity"] = complexity
                    
                    if analyst_deadline:
                        task_to_edit["analyst_deadline"] = analyst_deadline.strftime("%Y-%m-%d")
                    
                    st.session_state.editing_task_id = None
                    st.success("✅ Изменения сохранены!")
                    st.rerun()
                
                if cancelled:
                    st.session_state.editing_task_id = None
                    st.rerun()
    else:
        st.header("Бэклог инициатив")
        
        if not st.session_state.tasks:
            st.info("Нет задач. Добавь первую!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect(
                    "Статус",
                    ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                    default=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"]
                )
            with col2:
                value_filter = st.multiselect(
                    "Бизнес-ценность",
                    ["High", "Medium", "Low"],
                    default=["High", "Medium", "Low"]
                )
            
            filtered = [t for t in st.session_state.tasks if t["status"] in status_filter and t["business_value"] in value_filter]
            filtered.sort(key=lambda x: {"High": 0, "Medium": 1, "Low": 2}.get(x["business_value"], 3))
            
            st.markdown(f"**Всего задач: {len(filtered)}**")
            st.markdown("---")
            
            for task in filtered:
                readiness = check_readiness(task)
                
                status_emoji = {
                    "Idea": "⚪",
                    "In Discovery": "🔵",
                    "Ready for Analyst": "🟠",
                    "Requirements Clarification": "🟣",
                    "Ready for Refinement": "✅"
                }[task["status"]]
                
                value_emoji = {"High": "🔴", "Medium": "", "Low": "🟢"}[task["business_value"]]
                
                with st.expander(f"{value_emoji} **{task['title']}** {status_emoji} `{task['status']}`"):
                    st.markdown("**📊 Прогресс заполнения:**")
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
                            st.warning(f"⏰ Срок анализа истекает через {days_left} дн. (дедлайн: {task['analyst_deadline']})")
                        else:
                            st.info(f"📅 Срок анализа: {task['analyst_deadline']} (осталось {days_left} дн.)")
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Тип:** {task.get('type', 'Не указан')}")
                        st.markdown(f"**Владелец:** {task.get('owner', '') or 'Не указан'}")
                    with col2:
                        st.markdown(f"**Срочность:** {task.get('urgency', 'Medium')}")
                        st.markdown(f"**Сложность:** {task.get('complexity', 'M')}")
                    with col3:
                        st.markdown(f"**Бизнес-ценность:** {task.get('business_value', 'Medium')}")
                        st.markdown(f"**Создана:** {task.get('created_date', 'Не указана')}")
                    
                    st.markdown("---")
                    
                    st.markdown("**💼 Бизнес-контекст** *(заполняет инициатор)*")
                    st.markdown(f"**Проблема:** {task.get('problem', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Целевая аудитория:** {task.get('audience', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Бизнес-цель:** {task.get('business_goal', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Метрики успеха:** {task.get('metrics', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Что будет если не сделать:** {task.get('impact', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Основной сценарий:** {task.get('use_cases', '') or '️ Не заполнено'}")
                    
                    st.markdown("---")
                    
                    st.markdown("** Решение** *(опционально, заполняет инициатор)*")
                    st.markdown(f"**As Is:** {task.get('as_is', '') or 'Не описано'}")
                    st.markdown(f"**To Be:** {task.get('to_be', '') or 'Не описано'}")
                    
                    st.markdown("---")
                    
                    st.markdown("**️ Ограничения и зависимости** *(опционально, заполняет инициатор)*")
                    st.markdown(f"**Зависимости:** {task.get('dependencies', '') or 'Не указаны'}")
                    st.markdown(f"**Ограничения:** {task.get('constraints', '') or 'Нет'}")
                    st.markdown(f"**Риски:** {task.get('risks', '') or 'Нет'}")
                    
                    st.markdown("---")
                    
                    st.markdown("**🔧 Поля аналитика** *(заполняет аналитик/чаттер-лид)*")
                    st.markdown(f"**Критерии приемки (DoD):** {task.get('acceptance_criteria', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Декомпозиция на подзадачи:** {task.get('subtasks', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Техническая оценка:** {task.get('technical_estimate', '') or '⚠️ Не заполнено'}")
                    st.markdown(f"**Детальные зависимости:** {task.get('detailed_dependencies', '') or '⚠️ Не заполнено'}")
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_status = st.selectbox(
                            "Изменить статус",
                            ["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"],
                            index=["Idea", "In Discovery", "Ready for Analyst", "Requirements Clarification", "Ready for Refinement"].index(task["status"]),
                            key=f"status_{task['id']}"
                        )
                        if new_status != task["status"]:
                            task["status"] = new_status
                            st.rerun()
                    
                    with col2:
                        if st.button("✏️ Редактировать", key=f"edit_{task['id']}"):
                            st.session_state.editing_task_id = task["id"]
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️ Удалить", key=f"delete_{task['id']}"):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                            st.rerun()

# ================= ЭКРАН 2: НОВАЯ ЗАДАЧА (только поля инициатора) =================
elif page == "➕ Новая задача":
    st.header("Создание инициативы")
    st.markdown("💡 **Совет:** Задачу можно создать с любым количеством полей. Система покажет, что нужно дополнить.")
    
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
        
        st.subheader(" Основной сценарий")
        use_cases = st.text_area("Кто → Что делает → Результат", placeholder="Клиент → Открывает приложение → Видит портфель", height=80)
        
        st.subheader(" Приоритизация")
        col1, col2, col3 = st.columns(3)
        with col1:
            urgency = st.selectbox("Срочность", ["High", "Medium", "Low"])
        with col2:
            business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"])
        with col3:
            complexity = st.selectbox("Сложность", ["XS", "S", "M", "L", "XL"])
        
        submitted = st.form_submit_button("✅ Создать задачу", type="primary")
        
        if submitted:
            if title:
                new_task = {
                    "id": len(st.session_state.tasks) + 1,
                    "title": title,
                    "type": task_type,
                    "problem": problem,
                    "audience": audience,
                    "business_goal": business_goal,
                    "metrics": metrics,
                    "impact": impact,
                    "as_is": "",
                    "to_be": "",
                    "use_cases": use_cases,
                    "dependencies": "",
                    "constraints": "",
                    "risks": "",
                    "acceptance_criteria": "",
                    "subtasks": "",
                    "technical_estimate": "",
                    "detailed_dependencies": "",
                    "analyst_deadline": "",
                    "urgency": urgency,
                    "business_value": business_value,
                    "complexity": complexity,
                    "status": "Idea",
                    "owner": owner,
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.tasks.append(new_task)
                st.success(f"✅ Задача '{title}' создана!")
                st.rerun()
            else:
                st.error("❌ Укажи название задачи")
