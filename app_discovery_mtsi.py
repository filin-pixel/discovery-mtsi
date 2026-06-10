import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Discovery Manager", page_icon="🚀", layout="wide")

# Демо-данные из твоего Excel
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
        "status": "In Discovery",
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

# Инициализация
if "tasks" not in st.session_state:
    st.session_state.tasks = DEMO_TASKS.copy()

st.title("🚀 Discovery Manager")
st.markdown("Конвейер спринтов: Этап Discovery")

page = st.sidebar.radio("Навигация", ["📋 Список задач", "➕ Новая задача"])

# ================= СПИСОК ЗАДАЧ =================
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
                ["Idea", "In Discovery", "Requirements Clarification", "Ready for Refinement"],
                default=["Idea", "In Discovery", "Requirements Clarification", "Ready for Refinement"]
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
        
        for task in filtered:
            emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[task["business_value"]]
            with st.expander(f"{emoji} **{task['title']}** - `{task['status']} `"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Тип:** {task.get('type', '')}")
                    st.markdown(f"**Владелец:** {task.get('owner', '')}")
                with col2:
                    st.markdown(f"**Срочность:** {task.get('urgency', '')}")
                    st.markdown(f"**Сложность:** {task.get('complexity', '')}")
                with col3:
                    st.markdown(f"**Бизнес-ценность:** {task.get('business_value', '')}")
                
                st.markdown("---")
                st.markdown(f"**Проблема:** {task.get('problem', '')}")
                st.markdown(f"**Цель:** {task.get('business_goal', '')}")
                st.markdown(f"**Метрики:** {task.get('metrics', '')}")
                
                # Смена статуса
                new_status = st.selectbox(
                    "Статус",
                    ["Idea", "In Discovery", "Requirements Clarification", "Ready for Refinement"],
                    index=["Idea", "In Discovery", "Requirements Clarification", "Ready for Refinement"].index(task["status"]),
                    key=f"status_{task['id']}"
                )
                if new_status != task["status"]:
                    task["status"] = new_status
                    st.rerun()

# ================= НОВАЯ ЗАДАЧА =================
elif page == "➕ Новая задача":
    st.header("Создание инициативы")
    
    with st.form("new_task"):
        title = st.text_input("Название *")
        task_type = st.selectbox("Тип", ["Бизнес-фича", "Улучшение", "Техдолг", "Регуляторика"])
        owner = st.text_input("Владелец")
        
        problem = st.text_area("Проблема/Возможность *")
        audience = st.text_area("Целевая аудитория *")
        business_goal = st.text_area("Бизнес-цель *")
        metrics = st.text_area("Метрики успеха *")
        impact = st.text_area("Что будет если не сделать")
        
        as_is = st.text_area("As Is (как сейчас)")
        to_be = st.text_area("To Be (как должно быть)")
        use_cases = st.text_area("Основной сценарий")
        
        dependencies = st.text_area("Зависимости")
        constraints = st.text_area("Ограничения")
        risks = st.text_area("Риски")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            urgency = st.selectbox("Срочность", ["High", "Medium", "Low"])
        with col2:
            business_value = st.selectbox("Бизнес-ценность", ["High", "Medium", "Low"])
        with col3:
            complexity = st.selectbox("Сложность", ["XS", "S", "M", "L", "XL"])
        
        submitted = st.form_submit_button("✅ Создать")
        
        if submitted:
            if title and problem and audience and business_goal and metrics:
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
                st.success("✅ Задача создана!")
                st.rerun()
            else:
                st.error("Заполни обязательные поля (*)")
