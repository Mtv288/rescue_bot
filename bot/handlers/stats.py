from sqlalchemy.orm import Session
from bot.database.models import Task, Group, User
from aiogram import Router

router = Router()

def get_tasks_completed_count(session: Session, group_id: int) -> int:
    return session.query(Task).filter_by(group_id=group_id, completed=True).count()

def get_user_task_report(session: Session, user_id: int):
    tasks = session.query(Task).join(Group).join(User).filter(User.id == user_id).all()
    return tasks

def get_group_statistics(session: Session, group_id: int):
    total_tasks = session.query(Task).filter_by(group_id=group_id).count()
    completed_tasks = session.query(Task).filter_by(group_id=group_id, completed=True).count()
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / total_tasks) if total_tasks > 0 else 0,
    }
