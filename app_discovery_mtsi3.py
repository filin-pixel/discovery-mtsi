import streamlit as st
from datetime import datetime, timedelta
import json
import os
import uuid
from copy import deepcopy

# ================= CONFIG =================
st.set_page_config(page_title="Discovery Manager", page_icon="🚀", layout="wide")

DATA_FILE = "tasks_data.json"

# ================= CONSTANTS =================
BUSINESS_FIELDS = {
    "problem": "Проблема/Возможность",
    "audience": "Целевая аудитория",
    "business_goal": "Бизнес-цель",
    "metrics": "Метрики успеха",
    "impact": "Что будет если не сделать",
    "use_cases": "Основной сценарий"
}

ANALYST_FIELDS = {
    "acceptance_criteria": "Критерии приемки",
    "subtasks": "Декомпозиция",
    "technical_estimate": "Оценка",
    "detailed_dependencies": "Зависимости"
}

COMPLEXITY = {
    "S": 1,
    "M": 2,
    "L": 4,
    "XL": 8,
    "XXL": 16
}

RICE_LEVELS = {
    (5, float("inf")): "P1",
    (2, 5): "P2",
    (1, 2): "P3",
    (0, 1): "P4",
}

# ================= STORAGE =================
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Load error: {e}")
        return []

def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Save error: {e}")

# ================= TASK HELPERS =================
def new_task(title, task_type, owner, urgency, value, complexity):
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "type": task_type,
        "owner": owner,
        "status": "Idea",
        "urgency": urgency,
        "business_value": value,
        "complexity": complexity,
        "created_date": datetime.now().strftime("%Y-%m-%d"),

        # business
        "problem": "",
        "audience": "",
        "business_goal": "",
        "metrics": "",
        "impact": "",
        "use_cases": "",

        # analyst
        "acceptance_criteria": "",
        "subtasks": "",
        "technical_estimate": "",
        "detailed_dependencies": "",

        # rice
        "reach": 0,
        "impact_rice": 0,
        "confidence": 0,
        "effort": 0,
        "rice_score": 0,
        "priority": "",
        "executive_priority": False,
    }

def readiness(task):
    filled_b = sum(1 for k in BUSINESS_FIELDS if task.get(k))
    filled_a = sum(1 for k in ANALYST_FIELDS if task.get(k))

    return {
        "business": filled_b / len(BUSINESS_FIELDS),
        "analyst": filled_a / len(ANALYST_FIELDS),
        "ready": filled_b >= 5
    }

def calc_rice(reach, impact, confidence, effort):
    if effort == 0:
        return 0
    return (reach * impact * (confidence / 100)) / effort

def rice_to_priority(score):
    for (low, high), p in RICE_LEVELS.items():
        if low <= score < high:
            return p
    return "P4"

# ================= INIT =================
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

if "editing" not in st.session_state:
    st.session_state.editing = None

# ================= UI =================
st.title("🚀 Discovery Manager (Refactored v2)")

page = st.sidebar.radio("Навигация", ["📋 Tasks", "➕ New", "📊 RICE"])

# ================= LIST =================
if page == "📋 Tasks":

    tasks = st.session_state.tasks

    st.metric("Tasks", len(tasks))

    for t in tasks:
        r = readiness(t)

        st.markdown(f"## {t['title']}")
        st.caption(f"{t['status']} | {t['priority'] or 'no priority'}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("Business readiness", round(r["business"] * 100))

        with col2:
            st.write("Analyst readiness", round(r["analyst"] * 100))

        with col3:
            st.write("Complexity", t["complexity"])

        if r["ready"] and t["status"] == "Idea":
            if st.button("→ Send to Analyst", key=t["id"]):
                t["status"] = "Ready for Analyst"
                save_tasks(tasks)
                st.rerun()

        with st.expander("Edit"):
            t["title"] = st.text_input("Title", t["title"], key=f"title_{t['id']}")
            t["problem"] = st.text_area("Problem", t["problem"], key=f"p_{t['id']}")

            if st.button("Save", key=f"s_{t['id']}"):
                save_tasks(tasks)
                st.success("Saved")
                st.rerun()

# ================= CREATE =================
elif page == "➕ New":

    with st.form("new"):
        title = st.text_input("Title")
        owner = st.text_input("Owner")

        urgency = st.selectbox("Urgency", ["High", "Medium", "Low"])
        value = st.selectbox("Value", ["High", "Medium", "Low"])
        complexity = st.selectbox("Complexity", ["S", "M", "L", "XL", "XXL"])

        ok = st.form_submit_button("Create")

        if ok and title:
            task = new_task(title, "Idea", owner, urgency, value, complexity)
            st.session_state.tasks.append(task)
            save_tasks(st.session_state.tasks)
            st.success("Created")
            st.rerun()

# ================= RICE =================
elif page == "📊 RICE":

    tasks = st.session_state.tasks
    todo = [t for t in tasks if not t.get("priority")]

    st.metric("Unprioritized", len(todo))

    for t in todo:

        st.markdown(f"### {t['title']}")

        with st.form(f"rice_{t['id']}"):
            reach = st.slider("Reach", 1, 10, 5)
            impact = st.slider("Impact", 1, 3, 2)
            confidence = st.slider("Confidence", 50, 100, 80)
            effort = COMPLEXITY[t["complexity"]]

            exec_flag = st.checkbox("Executive priority")

            if st.form_submit_button("Calculate"):
                score = calc_rice(reach, impact, confidence, effort)

                t["reach"] = reach
                t["impact_rice"] = impact
                t["confidence"] = confidence
                t["effort"] = effort
                t["rice_score"] = score
                t["priority"] = rice_to_priority(score)
                t["executive_priority"] = exec_flag

                save_tasks(tasks)

                st.success(f"RICE={score:.2f} → {t['priority']}")
                st.rerun()
