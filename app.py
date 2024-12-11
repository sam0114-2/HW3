from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import uuid

app = Flask(__name__)
TASK_FILE = "task.xlsx"

# 初始化 task.xlsx
if not os.path.exists(TASK_FILE):
    df = pd.DataFrame(columns=["Date", "Task", "Location", "Priority", "Subtask 1", "Subtask 2", "Subtask 3", "ID"])
    df.to_excel(TASK_FILE, index=False)
else:
    df = pd.read_excel(TASK_FILE)
    if "ID" not in df.columns:
        df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
        df.to_excel(TASK_FILE, index=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/task", methods=["GET", "POST"])
def task():
    if request.method == "POST":
        date = request.form["date"]
        task = request.form["task"]
        location = request.form["location"]
        priority = request.form["priorty"]
        detail_1 = request.form["detail_1"]
        detail_2 = request.form["detail_2"]
        detail_3 = request.form["detail_3"]

        # 生成唯一 ID
        unique_id = str(uuid.uuid4())

        # 新增事件到 DataFrame
        new_event = pd.DataFrame([{
            "ID": unique_id,  # 新增 ID
            "Date": date,
            "Task": task,
            "Location": location,
            "Priority": int(priority),
            "Subtask 1": str(detail_1),
            "Subtask 2": str(detail_2),
            "Subtask 3": str(detail_3),
        }])

        # 使用 pd.concat 合併新事件
        df = pd.read_excel(TASK_FILE)
        updated_df = pd.concat([df, new_event], ignore_index=True)
        updated_df.to_excel(TASK_FILE, index=False)

        return redirect(url_for("index"))
    return render_template("task.html")


@app.route("/tasks_on_date")
def tasks_on_date():
    selected_date = request.args.get("date", "")  # 獲取 URL 中的日期參數
    
    tasks_for_date = []
    if selected_date:
        df = pd.read_excel(TASK_FILE)  # 讀取最新的任務文件
        
        # 確保日期欄位格式一致
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        tasks_for_date = df[df["Date"] == selected_date].copy()

        # 計算進度百分比
        def calculate_progress(row):
            subtasks = [row.get("Subtask 1"), row.get("Subtask 2"), row.get("Subtask 3")]
            total = sum(1 for task in subtasks if pd.notna(task))
            completed = sum(1 for task in subtasks if pd.notna(task) and task.endswith("(完成)"))
            return int((completed / total) * 100) if total > 0 else 0

        tasks_for_date["progress"] = tasks_for_date.apply(calculate_progress, axis=1)
        tasks_for_date = tasks_for_date[["ID", "Task", "Priority", "progress"]].to_dict(orient="records")
        tasks_for_date = sorted(tasks_for_date, key=lambda x: x["Priority"], reverse=True)
        
    return render_template("tasks_on_date.html", tasks=tasks_for_date, selected_date=selected_date)



if __name__ == "__main__":
    app.run(debug=True)
