# TaskTrackr

A command-line task management application with reminders, built in Python.

## Features

- Add, view, update, and delete tasks
- Set task priorities (low, medium, high)
- Add due dates to tasks
- Set reminders for tasks
- Color-coded task display
- Persistent storage of tasks
- Automatic reminder notifications

## Installation

1. Make sure you have Python 3.7+ installed on your system.

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python tasktrackr.py
```

### Menu Options

1. **Add Task**: Create a new task with title, description, due date, priority, and optional reminder.
2. **View Tasks**: Display all tasks with their details and status.
3. **Mark Task as Complete/Incomplete**: Toggle the completion status of a task.
4. **Delete Task**: Remove a task from the list.
5. **Exit**: Close the application.

### Task Properties

- **Title**: Required, the name of the task
- **Description**: Optional, additional details about the task
- **Due Date**: Optional, when the task should be completed (format: YYYY-MM-DD HH:MM)
- **Priority**: Low, medium, or high (default: medium)
- **Reminder**: Optional, set a reminder time for the task

### Reminders

The application runs a background thread that checks for due reminders every minute. When a reminder is due, it will display a notification in the console.

## Data Storage

Tasks are automatically saved to a `tasks.json` file in the same directory as the application. This ensures your tasks persist between sessions.

## Color Coding

- ✓ Green: Completed tasks
- ✗ Red: Pending tasks
- Blue: Low priority tasks
- Yellow: Medium priority tasks
- Red: High priority tasks 