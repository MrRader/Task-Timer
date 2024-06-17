"""
MIT License

Copyright (c) 2024 Marvin Rader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import csv
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
    QDateEdit,
    QScrollArea
)
from PyQt6.QtCore import QDate, Qt, pyqtSlot

# Define a global variable for button and field width
GLOBAL_WIDTH = 215

class TaskTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Tracker")
        self.current_task = None
        self.tasks = self.load_tasks()  # Call load_tasks in init
        self.task_name_input = QLineEdit()
        self.task_name_input.setFixedWidth(GLOBAL_WIDTH)
        self.task_name_input.textChanged.connect(self.update_add_button_state)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.setFixedWidth(GLOBAL_WIDTH)
        self.add_task_button.clicked.connect(self.add_task)
        self.add_task_button.setEnabled(False)

        self.stop_task_button = QPushButton("Stop Task")
        self.stop_task_button.setFixedWidth(GLOBAL_WIDTH)
        self.stop_task_button.clicked.connect(self.stop_task)
        self.stop_task_button.setEnabled(False)  # Initially disable the Stop Task button

        self.create_report_button = QPushButton("Create Report")
        self.create_report_button.setFixedWidth(GLOBAL_WIDTH)
        self.create_report_button.clicked.connect(self.create_report)

        self.report_date_picker = QDateEdit(QDate.currentDate())
        self.report_date_picker.setFixedWidth(GLOBAL_WIDTH)
        self.report_date_picker.setCalendarPopup(True)

        self.status_label = QLabel("")  # Label to show status messages

        self.task_buttons_layout = QVBoxLayout()

        # Create a QWidget to contain the task buttons layout
        task_buttons_widget = QWidget()
        task_buttons_widget.setLayout(self.task_buttons_layout)

        # Create a QScrollArea to contain the task buttons widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(task_buttons_widget)
        self.scroll_area.setMinimumWidth(GLOBAL_WIDTH + 30)  # Adjust to avoid covering buttons

        layout = QVBoxLayout()
        layout.addWidget(QLabel("New Task:"))
        layout.addWidget(self.task_name_input)
        layout.addWidget(self.add_task_button)
        layout.addWidget(self.stop_task_button)  # Add the stop task button to the layout
        layout.addWidget(QLabel("Report Date:"))
        layout.addWidget(self.report_date_picker)  # Add the date picker to the layout
        layout.addWidget(self.create_report_button)  # Add the create report button to the layout
        layout.addWidget(self.status_label)  # Add the status label to the layout
        layout.addWidget(self.scroll_area)  # Add the scroll area to the layout

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.create_task_buttons()
        self.create_tsv_if_not_exists()

    def create_task_buttons(self):
        for task in self.tasks:
            button = QPushButton(task)
            button.setFixedWidth(GLOBAL_WIDTH)
            button.clicked.connect(self.on_task_click)
            self.task_buttons_layout.addWidget(button)

    def add_task(self):
        task_name = self.task_name_input.text().strip()
        if task_name:
            self.tasks.append(task_name)
            self.save_tasks()
            button = QPushButton(task_name)
            button.setFixedWidth(GLOBAL_WIDTH)
            button.clicked.connect(self.on_task_click)
            self.task_buttons_layout.addWidget(button)
            self.task_name_input.clear()

    def on_task_click(self):
        clicked_task = self.sender().text()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write the stop event for the previous task if there is one
        if self.current_task:
            self.write_task_data(self.current_task, "Stopped Task", current_time)
            self.status_label.setText(f"Stopping task: {self.current_task}")
            print(f"Stopping task: {self.current_task}")

        # Write the start event for the clicked task
        self.write_task_data(clicked_task, "Started Task", current_time)
        self.status_label.setText(f"Starting task: {clicked_task}")
        print(f"Starting task: {clicked_task}")

        self.current_task = clicked_task
        self.stop_task_button.setEnabled(True)  # Enable the Stop Task button when a task is started

    def stop_task(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.current_task:
            self.write_task_data(self.current_task, "Stopped Task", current_time)
            self.status_label.setText(f"Stopping task: {self.current_task}")
            print(f"Stopping task: {self.current_task}")
            self.current_task = None
            self.stop_task_button.setEnabled(False)  # Disable the Stop Task button when no task is active

    def create_tsv_if_not_exists(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.filename = f"{self.current_date}.tsv"
        
        if not os.path.isfile(self.filename):
            try:
                with open(self.filename, 'w', newline='') as tsvfile:
                    tsvwriter = csv.writer(tsvfile, delimiter='\t')
                    tsvwriter.writerow(["Timestamp", "Task", "Status"])
                print(f"Created new TSV file: {self.filename}")
            except Exception as e:
                print(f"Error creating TSV file: {e}")
                self.status_label.setText(f"Error creating TSV file: {e}")
        else:
            print(f"TSV file already exists: {self.filename}")

    def create_report(self):
        report_date = self.report_date_picker.date().toString("yyyy-MM-dd")
        tsv_filename = f"{report_date}.tsv"
        base_report_filename = f"{report_date}_Report.csv"
        report_filename = base_report_filename
        counter = 1

        while os.path.isfile(report_filename):
            report_filename = f"{report_date}_Report_{counter}.csv"
            counter += 1

        tasks = {}

        try:
            # Check if the TSV file exists
            if not os.path.isfile(tsv_filename):
                raise FileNotFoundError(f"TSV file for {report_date} does not exist")

            # Read the TSV file for the selected date
            with open(tsv_filename, 'r') as tsvfile:
                tsvreader = csv.reader(tsvfile, delimiter='\t')
                next(tsvreader)  # Skip header row
                for row in tsvreader:
                    timestamp, task, status = row
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                    if task not in tasks:
                        tasks[task] = {"start_times": [], "total_duration": timedelta()}

                    if status == "Started Task":
                        tasks[task]["start_times"].append(timestamp)
                    elif status == "Stopped Task" and tasks[task]["start_times"]:
                        start_time = tasks[task]["start_times"].pop(0)
                        duration = timestamp - start_time
                        tasks[task]["total_duration"] += duration

            # Write the report CSV file
            with open(report_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Task", "Total Time Spent"])
                for task, data in tasks.items():
                    total_seconds = data["total_duration"].total_seconds()
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    total_time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
                    csvwriter.writerow([task, total_time_str])

            self.status_label.setText(f"Report created: {report_filename}")
            print(f"Report created: {report_filename}")
        except FileNotFoundError as fnf_error:
            print(fnf_error)
            self.status_label.setText(str(fnf_error))
        except Exception as e:
            print(f"Error creating report: {e}")
            self.status_label.setText(f"Error creating report: {e}")

    def load_tasks(self):
        tasks = []
        try:
            with open("tasks.txt", "r") as file:
                tasks = [line.strip() for line in file]
        except FileNotFoundError:
            pass
        return tasks

    def save_tasks(self):
        try:
            with open("tasks.txt", "w") as file:
                for task in self.tasks:
                    file.write(task + "\n")
        except Exception as e:
            print(f"Error saving tasks: {e}")
            self.status_label.setText(f"Error saving tasks: {e}")

    def update_add_button_state(self):
        # Enable button only if text is entered in the input field
        self.add_task_button.setEnabled(bool(self.task_name_input.text()))

    def write_task_data(self, task, status, timestamp):
        try:
            with open(self.filename, 'a', newline='') as tsvfile:
                tsvwriter = csv.writer(tsvfile, delimiter='\t')
                tsvwriter.writerow([timestamp, task, status])
            print(f"Written to TSV: {timestamp}, {task}, {status}")
        except Exception as e:
            print(f"Error writing to TSV: {e}")
            self.status_label.setText(f"Error writing to TSV: {e}")

    @pyqtSlot()
    def closeEvent(self, event):
        # Handle the window close event to stop the current task
        self.stop_task()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = TaskTracker()
    window.show()
    app.exec()
