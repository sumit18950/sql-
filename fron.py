
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Dummy Data


# Database setup
DB_PATH = "feedback.db"
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_email TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )''')
    # Insert default courses if not present
    default_courses = [
        "Python Basics", "Data Structures", "Web Development", "Machine Learning",
        "Database Systems", "Cloud Computing", "Cybersecurity", "AI Fundamentals"
    ]
    for course in default_courses:
        c.execute("INSERT OR IGNORE INTO courses (name) VALUES (?)", (course,))
    conn.commit()
    conn.close()

def get_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM courses ORDER BY name")
    courses = c.fetchall()
    conn.close()
    return courses

def add_feedback(course_id, student_name, student_email, rating, comment):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO feedback (course_id, student_name, student_email, rating, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (course_id, student_name, student_email, rating, comment, datetime.now()))
    conn.commit()
    conn.close()

def get_feedback():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT feedback.id, courses.name, feedback.student_name, feedback.student_email, feedback.rating, feedback.comment, feedback.timestamp
                 FROM feedback JOIN courses ON feedback.course_id = courses.id''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_feedback_by_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT rating FROM feedback WHERE course_id = ?''', (course_id,))
    ratings = [row[0] for row in c.fetchall()]
    conn.close()
    return ratings

init_db()



st.markdown("""
<h1 style='text-align: center; color: #4F8BF9;'>Student Feedback System</h1>
<hr style='border: 1px solid #4F8BF9;'>
""", unsafe_allow_html=True)



courses = get_courses()
course_names = [c[1] for c in courses]
course_ids = [c[0] for c in courses]

with st.form("feedback_form", clear_on_submit=True):
    course_idx = st.selectbox("Select Course", range(len(course_names)), format_func=lambda i: course_names[i])
    student_name = st.text_input("Your Name")
    student_email = st.text_input("Your Email")
    rating = st.slider("Rate (1-5)", 1, 5)
    comment = st.text_area("Your Feedback")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not student_name or not student_email:
            st.error("Please enter your name and email.")
        else:
            add_feedback(course_ids[course_idx], student_name, student_email, rating, comment)
            st.success("Feedback submitted!")




feedback_rows = get_feedback()
if feedback_rows:
    df = pd.DataFrame(feedback_rows, columns=["ID", "Course", "Student Name", "Student Email", "Rating", "Comment", "Timestamp"])
    st.markdown("<h3 style='color: #4F8BF9;'>Feedback Summary</h3>", unsafe_allow_html=True)
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

    selected_course_idx = st.selectbox("View feedback for course:", range(len(course_names)), format_func=lambda i: course_names[i], key="summary_course")
    selected_course_id = course_ids[selected_course_idx]
    ratings = get_feedback_by_course(selected_course_id)
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        st.metric("Average Rating", round(avg_rating, 2))

        import matplotlib.pyplot as plt
        import numpy as np
        import collections

        st.markdown("#### Ratings Distribution (Bar Chart)")
        rating_counts = collections.Counter(ratings)
        bar_data = pd.Series([rating_counts.get(i, 0) for i in range(1, 6)], index=range(1, 6))
        st.bar_chart(bar_data)

        st.markdown("#### Ratings Distribution (Pie Chart)")
        fig, ax = plt.subplots()
        ax.pie(bar_data, labels=bar_data.index, autopct='%1.1f%%', colors=plt.cm.Blues(np.linspace(0.5, 1, 5)))
        ax.set_ylabel('')
        ax.set_title('')
        st.pyplot(fig)
    else:
        st.info("No feedback for this course yet.")
