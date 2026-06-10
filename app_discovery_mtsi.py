import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Discovery Manager", page_icon="🚀", layout="wide")

# ================= ДЕМО-ДАННЫЕ =================
DEMO_TASKS = [
    {
        "id": 1,
        "title": "Инвесткопилка",
        "type": "Бизнес-фича",
        "problem": "Нет автоматического инвестирования небольших сумм",
        "audience": "Клиенты МТС Инвестиций",
        "business_goal": "Увеличить AUM и количество активных клиентов",
        "metrics": "AUM, фондированные и активные клиенты",
        "impact": "Потеря клиентов, которые хотят инвестировать по чуть-чуть",
        "as_is": "Клим + Саша Стояновский делают прототип и исследование",
        "to_be": "Автоматическое инвестирование округленных сумм",
        "use_cases": "Клиент → Подключает инвесткопилку → Система автоматически инвестирует округления",
        "dependencies": "Зависит от механики (iOS, web ЛК, комиссия, МТСИ)",
        "constraints": "Желательно не создавать новые договоры/счета",
        "risks": "Сложность с выходными днями и расчетами",
        "urgency": "High",
        "business_value": "High",
        "complexity": "XL",
        "status": "In Discovery",
        "owner": "Клим + Саша Стояновский",
        "created_date": "2026-06-10"
    },
    {
        "id": 2,
        "title": "СБП по ценным бумагам",
        "type": "Регуляторика",
        "problem": "Регуляторное требование с 01.09",
        "audience": "Все клиенты",
        "business_goal": "Соответствие регуляторным требованиям",
        "metrics": "Регуляторка + потенциально AUM",
        "impact": "Штрафы от регулятора",
        "as_is": "Нужно посмотреть макеты и направить в Депозитарий",
        "to_be": "Интеграция с СБП для операций с ценными бумагами",
        "use_cases": "Клиент → Выбирает СБП → Совершает операцию с ЦБ",
        "dependencies": "Общебанк, Депозитарий",
        "constraints": "Срок до 01.09",
        "risks": "Задержка от Депозитария",
        "urgency": "High",
        "business_value": "High",
        "complexity": "XL",
        "status": "Ready for Analyst",
        "owner": "",
        "created_date": "2026-06-10"
    },
    {
        "id": 3,
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
        "urgency": "High",
        "business_value": "Medium",
        "complexity": "S",
        "status": "In Discovery",
        "owner": "",
        "created_date": "2026-06-10"
    }
]

# ================= ПРАВИЛА ЗАПОЛНЕНИЯ =================
BUSINESS_FIELDS = ["problem", "audience", "business_goal", "metrics", "impact", "use_cases"]
TECHNICAL_FIELDS = ["dependencies", "constraints", "risks", "as_is", "to_be"]

def check_readiness(task):
    """Проверяет готовность задачи к передаче аналитику"""
    filled_business = [f for f in BUSINESS_FIELDS if task.get(f)]
    filled_technical = [f for f in TECHNICAL_FIELDS if task.get(f)]
    
    business_progress = len(filled_business) / len(BUSINESS_FIELDS)
    technical_progress = len(filled_technical) / len(TECHNICAL_FIELDS)
    
    is_ready_for_analyst = business_progress >= 0.8  # 80% бизнес-полей заполнено
    
    return {
        "business_progress": business_progress,
        "technical_progress": technical_progress,
        "is_ready_for_analyst": is_ready_for_analyst,
        "missing_business": [f for f in BUSINESS_FIELDS if not task.get(f)],
        "missing_technical": [f for f in TECHNICAL_FIELDS if not task.get(f)]
    }

# ================= ИНИЦИАЛИЗАЦИЯ =================
if "tasks" not in st.session_state:
    st.session_state.tasks = DEMO_TASKS.copy()

st.title(" Discovery Manager")
st.markdown("Конвейер спринтов: Этап Discovery")

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача"])

# ================= ЭКРАН 1: СПИСОК ЗАДАЧ =================
if page == "📋 Список задач":
    st.header("Бэклог инициатив")
    
    if not st.session_state.tasks:
        st.info("Нет задач. Добавь первую!")
    else:
        # Фильтры
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
        
        # Фильтрация
        filtered = [t for t in st.session_state.tasks if t["status"] in status_filter and t["business_value"] in value_filter]
        filtered.sort(key=lambda x: {"High": 0, "Medium": 1, "Low": 2}.get(x["business_value"], 3))
        
        st.markdown(f"**Всего задач: {len(filtered)}**")
        st.markdown("---")
        
        # Легенда статусов
        with st.expander("📖 Легенда статусов"):
            st.markdown("""
            **Статусы:**
            -  **Idea** - сырая идея
            - 🔵 **In Discovery** - бизнес заполняет шаблон
            - 🟠 **Ready for Analyst** - готово к передаче аналитику
            - 🟣 **Requirements Clarification** - аналитик уточняет требования
            - ✅ **Ready for Refinement** - готово к команде
            
            **Приоритеты:**
            - 🔴 **High** - критично
            - 🟡 **Medium** - средне
            - 🟢 **Low** - низко
            """)
        
        for task in filtered:
            readiness = check_readiness(task)
            
            # Определяем эмодзи статуса
            status_emoji = {
                "Idea": "⚪",
                "In Discovery": "🔵",
                "Ready for Analyst": "🟠",
                "Requirements Clarification": "🟣",
                "Ready for Refinement": "✅"
            }[task["status"]]
            
            value_emoji = {"High": "🔴", "Medium": "🟡", "Low": ""}[task["business_value"]]
            
            with st.expander(f"{value_emoji} **{task['title']}** {status_emoji} `{task['status']}`"):
                # Прогресс-бар заполнения
                st.markdown("**📊 Прогресс заполнения:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.progress(readiness["business_progress"], text=f"Бизнес-поля: {int(readiness['business_progress']*100)}%")
                with col2:
                    st.progress(readiness["technical_progress"], text=f"Технические поля: {int(readiness['technical_progress']*100)}%")
                
                if readiness["is_ready_for_analyst"] and task["status"] == "In Discovery":
                    st.success("✅ Задача готова к передаче аналитику!")
                    if st.button("🚀 Передать аналитику", key=f"ready_{task['id']}"):
                        task["status"] = "Ready for Analyst"
                        st.rerun()
                elif not readiness["is_ready_for_analyst"]:
                    missing = readiness["missing_business"]
                    if missing:
                        st.warning(f"⚠️ Не заполнены бизнес-поля: {', '.join(missing)}")
                
                st.markdown("---")
                
                # Основная информация
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Тип:** {task.get('type', 'Не указан')}")
                    st.markdown(f"**Владелец:** {task.get('owner', 'Не указан')}")
                with col2:
                    st.markdown(f"**Срочность:** {task.get('urgency', 'Medium')}")
                    st.markdown(f"**Сложность:** {task.get('complexity', 'M')}")
                with col3:
                    st.markdown(f"**Бизнес-ценность:** {task.get('business_value', 'Medium')}")
                    st.markdown(f"**Создана:** {task.get('created_date', 'Не указана')}")
                
                st.markdown("---")
                
                # Бизнес-контекст
                st.markdown("**💼 Бизнес-контекст**")
                st.markdown(f"**Проблема:** {task.get('problem', '⚠️ Не заполнено')}")
                st.markdown(f"**Целевая аудитория:** {task.get('audience', '⚠️ Не заполнено')}")
                st.markdown(f"**Бизнес-цель:** {task.get('business_goal', '⚠️ Не заполнено')}")
                st.markdown(f"**Метрики успеха:** {task.get('metrics', '️ Не заполнено')}")
                st.markdown(f"**Что будет если не сделать:** {task.get('impact', '⚠️ Не заполнено')}")
                
                st.markdown("---")
                
                # Решение
                st.markdown("**🎯 Решение**")
                st.markdown(f"**As Is:** {task.get('as_is', '⚠️ Не заполнено')}")
                st.markdown(f"**To Be:** {task.get('to_be', '️ Не заполнено')}")
                st.markdown(f"**Сценарий:** {task.get('use_cases', '⚠️ Не заполнено')}")
                
                st.markdown("---")
                
                # Ограничения
                st.markdown("**⚠️ Ограничения и риски**")
                st.markdown(f"**Зависимости:** {task.get('dependencies', '⚠️ Не заполнено')}")
                st.markdown(f"**Ограничения:** {task.get('constraints', '⚠️ Не заполнено')}")
                st.markdown(f"**Риски:** {task.get('risks', '️ Не заполнено')}")
                
                st.markdown("---")
                
                # Управление статусом
                col1, col2 = st.columns(2)
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
                    if st.button("🗑️ Удалить задачу", key=f"delete_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                        st.rerun()

# ================= ЭКРАН 2: НОВАЯ ЗАДАЧА =================
elif page == "➕ Новая задача":
    st.header("Создание инициативы")
    st.markdown("💡 **Совет:** Задачу можно создать с любым количеством полей. Система покажет, что нужно дополнить.")
    
    with st.form("new_task"):
        # Базовая информация
        st.subheader("📌 Базовая информация")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Название *", placeholder="Краткое название")
            task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"])
        with col2:
            owner = st.text_input("Инициатор/Владелец", placeholder="ФИО")
        
        # Бизнес-контекст
        st.subheader("💼 Бизнес-контекст (заполняет инициатор)")
        problem = st.text_area("Проблема/Возможность *", placeholder="Что не так сейчас?", height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            audience = st.text_area("Целевая аудитория *", placeholder="Для кого делаем?", height=80)
            business_goal = st.text_area("Бизнес-цель *", placeholder="Зачем это нужно?", height=80)
        with col2:
            metrics = st.text_area("Метрики успеха *", placeholder="Как поймем успех?", height=80)
            impact = st.text_area("Что будет если не сделать", placeholder="Влияние на бизнес", height=80)
        
        # Решение
        st.subheader("🎯 Решение и сценарии")
        col1, col2 = st.columns(2)
        with col1:
            as_is = st.text_area("As Is (как сейчас)", placeholder="Текущее состояние", height=80)
            to_be = st.text_area("To Be (как должно быть)", placeholder="Желаемое состояние", height=80)
        with col2:
            use_cases = st.text_area("Основной сценарий", placeholder="Кто → Что делает → Результат", height=80)
        
        # Ограничения
        st.subheader("⚠️ Ограничения и зависимости")
        col1, col2, col3 = st.columns(3)
        with col1:
            dependencies = st.text_area("Зависимости", placeholder="От каких систем/команд", height=80)
        with col2:
            constraints = st.text_area("Ограничения", placeholder="Технические, регуляторные", height=80)
        with col3:
            risks = st.text_area("Риски", placeholder="Что может пойти не так", height=80)
        
        # Приоритизация
        st.subheader("📊 Приоритизация")
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
                    "as_is": as_is,
                    "to_be": to_be,
                    "use_cases": use_cases,
                    "dependencies": dependencies,
                    "constraints": constraints,
                    "risks": risks,
                    "urgency": urgency,
                    "business_value": business_value,
                    "complexity": complexity,
                    "status": "Idea",
                    "owner": owner,
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.tasks.append(new_task)
                st.success(f"✅ Задача '{title}' создана!")
                st.info("Перейди в 'Список задач' чтобы увидеть прогресс заполнения")
                st.rerun()
            else:
                st.error("❌ Укажи название задачи")
