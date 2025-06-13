import os
import json
from datetime import datetime
import schedule
import time
from colorama import init, Fore, Style
import threading
import sys
import signal

# Initialize colorama
init()

class Task:
    def __init__(self, title, description="", due_date=None, priority="medium", reminder=False, reminder_time=None):
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        self.title = title.strip()
        self.description = description.strip()
        self.due_date = due_date
        self.priority = priority.lower() if priority else "medium"
        if self.priority not in ["low", "medium", "high"]:
            self.priority = "medium"
        self.reminder = bool(reminder)
        self.reminder_time = reminder_time
        self.completed = False
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "reminder": self.reminder,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        try:
            task = cls(
                title=data["title"],
                description=data.get("description", ""),
                priority=data.get("priority", "medium"),
                reminder=data.get("reminder", False)
            )
            if data.get("due_date"):
                task.due_date = datetime.fromisoformat(data["due_date"])
            if data.get("reminder_time"):
                task.reminder_time = datetime.fromisoformat(data["reminder_time"])
            task.completed = data.get("completed", False)
            task.created_at = datetime.fromisoformat(data["created_at"])
            return task
        except (KeyError, ValueError) as e:
            print(f"{Fore.RED}Error loading task: {e}{Style.RESET_ALL}")
            return None

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.data_file = "tasks.json"
        self.load_tasks()
        self._running = True

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = []
                    for task_data in data:
                        task = Task.from_dict(task_data)
                        if task:
                            self.tasks.append(task)
            except json.JSONDecodeError:
                print(f"{Fore.RED}Error: Invalid JSON in tasks file. Creating new file.{Style.RESET_ALL}")
                self.save_tasks()
            except Exception as e:
                print(f"{Fore.RED}Error loading tasks: {e}{Style.RESET_ALL}")
                self.tasks = []

    def save_tasks(self):
        try:
            with open(self.data_file, "w", encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.RED}Error saving tasks: {e}{Style.RESET_ALL}")

    def add_task(self, task):
        try:
            self.tasks.append(task)
            self.save_tasks()
            return True
        except Exception as e:
            print(f"{Fore.RED}Error adding task: {e}{Style.RESET_ALL}")
            return False

    def remove_task(self, index):
        try:
            if 0 <= index < len(self.tasks):
                del self.tasks[index]
                self.save_tasks()
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}Error removing task: {e}{Style.RESET_ALL}")
            return False

    def toggle_task_completion(self, index):
        try:
            if 0 <= index < len(self.tasks):
                self.tasks[index].completed = not self.tasks[index].completed
                self.save_tasks()
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}Error updating task: {e}{Style.RESET_ALL}")
            return False

    def get_tasks(self, show_completed=True):
        try:
            if show_completed:
                return self.tasks
            return [task for task in self.tasks if not task.completed]
        except Exception as e:
            print(f"{Fore.RED}Error getting tasks: {e}{Style.RESET_ALL}")
            return []

    def check_reminders(self):
        if not self._running:
            return
            
        try:
            now = datetime.now()
            for task in self.tasks:
                if (task.reminder and task.reminder_time and 
                    not task.completed and 
                    task.reminder_time <= now):
                    print(f"\n{Fore.YELLOW}REMINDER: {task.title}{Style.RESET_ALL}")
                    print(f"Description: {task.description}")
                    if task.due_date:
                        print(f"Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
                    print(f"Priority: {task.priority}\n")
        except Exception as e:
            print(f"{Fore.RED}Error checking reminders: {e}{Style.RESET_ALL}")

    def stop(self):
        self._running = False
        self.save_tasks()

def print_menu():
    print(f"\n{Fore.CYAN}=== TaskTrackr ==={Style.RESET_ALL}")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task as Complete/Incomplete")
    print("4. Delete Task")
    print("5. Exit")
    print(f"{Fore.CYAN}=================={Style.RESET_ALL}")

def get_task_input():
    while True:
        title = input("Enter task title: ").strip()
        if title:
            break
        print(f"{Fore.RED}Title cannot be empty. Please try again.{Style.RESET_ALL}")

    description = input("Enter task description (optional): ").strip()
    
    due_date = None
    while True:
        due_date_str = input("Enter due date (YYYY-MM-DD HH:MM) or press Enter to skip: ").strip()
        if not due_date_str:
            break
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
            if due_date < datetime.now():
                print(f"{Fore.YELLOW}Warning: Due date is in the past.{Style.RESET_ALL}")
            break
        except ValueError:
            print(f"{Fore.RED}Invalid date format. Please use YYYY-MM-DD HH:MM{Style.RESET_ALL}")

    while True:
        priority = input("Enter priority (low/medium/high) [default: medium]: ").lower().strip()
        if not priority or priority in ["low", "medium", "high"]:
            priority = priority or "medium"
            break
        print(f"{Fore.RED}Invalid priority. Please choose from: low, medium, high{Style.RESET_ALL}")

    reminder = input("Set reminder? (y/n) [default: n]: ").lower().strip() == "y"
    reminder_time = None
    if reminder:
        while True:
            reminder_str = input("Enter reminder time (YYYY-MM-DD HH:MM): ").strip()
            try:
                reminder_time = datetime.strptime(reminder_str, "%Y-%m-%d %H:%M")
                if reminder_time < datetime.now():
                    print(f"{Fore.YELLOW}Warning: Reminder time is in the past.{Style.RESET_ALL}")
                if due_date and reminder_time > due_date:
                    print(f"{Fore.YELLOW}Warning: Reminder time is after due date.{Style.RESET_ALL}")
                break
            except ValueError:
                print(f"{Fore.RED}Invalid date format. Please use YYYY-MM-DD HH:MM{Style.RESET_ALL}")

    return Task(title, description, due_date, priority, reminder, reminder_time)

def handle_exit(signum, frame):
    print(f"\n{Fore.YELLOW}Shutting down TaskTrackr...{Style.RESET_ALL}")
    if 'task_manager' in globals():
        task_manager.stop()
    sys.exit(0)

def main():
    global task_manager
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    task_manager = TaskManager()
    
    def run_reminder_checker():
        while task_manager._running:
            task_manager.check_reminders()
            time.sleep(60)  # Check every minute

    reminder_thread = threading.Thread(target=run_reminder_checker, daemon=True)
    reminder_thread.start()

    while True:
        try:
            print_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                try:
                    task = get_task_input()
                    if task_manager.add_task(task):
                        print(f"{Fore.GREEN}Task added successfully!{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error adding task: {e}{Style.RESET_ALL}")

            elif choice == "2":
                tasks = task_manager.get_tasks()
                if not tasks:
                    print("No tasks found.")
                else:
                    print(f"\n{Fore.CYAN}Your Tasks:{Style.RESET_ALL}")
                    for i, task in enumerate(tasks):
                        status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if task.completed else f"{Fore.RED}✗{Style.RESET_ALL}"
                        priority_color = {
                            "low": Fore.BLUE,
                            "medium": Fore.YELLOW,
                            "high": Fore.RED
                        }.get(task.priority, Fore.WHITE)
                        
                        print(f"\n{status} {i+1}. {task.title}")
                        if task.description:
                            print(f"   Description: {task.description}")
                        if task.due_date:
                            print(f"   Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
                        print(f"   Priority: {priority_color}{task.priority}{Style.RESET_ALL}")
                        if task.reminder and task.reminder_time:
                            print(f"   Reminder: {task.reminder_time.strftime('%Y-%m-%d %H:%M')}")

            elif choice == "3":
                tasks = task_manager.get_tasks()
                if not tasks:
                    print("No tasks to update.")
                else:
                    try:
                        index = int(input("Enter task number to toggle completion: ")) - 1
                        if task_manager.toggle_task_completion(index):
                            print(f"{Fore.GREEN}Task status updated!{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}Invalid task number.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

            elif choice == "4":
                tasks = task_manager.get_tasks()
                if not tasks:
                    print("No tasks to delete.")
                else:
                    try:
                        index = int(input("Enter task number to delete: ")) - 1
                        if task_manager.remove_task(index):
                            print(f"{Fore.GREEN}Task deleted successfully!{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}Invalid task number.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

            elif choice == "5":
                print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                task_manager.stop()
                break

            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
            print("Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down TaskTrackr...{Style.RESET_ALL}")
        if 'task_manager' in globals():
            task_manager.stop()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1) 