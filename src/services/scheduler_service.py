"""定时任务服务

每日早上 8:00 自动收集昨日资讯
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from src.services.news_collector import news_collector

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = AsyncIOScheduler()


async def daily_news_collection():
    """每日资讯收集任务"""
    logger.info("⏰ 定时任务：开始收集昨日资讯")
    
    try:
        # 获取昨日日期
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 创建新的数据库会话
        from src.models.database import SessionLocal
        
        db = SessionLocal()
        try:
            stats = await news_collector.collect_all(db, yesterday)
            logger.info(f"✅ 资讯收集完成: {stats}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ 资讯收集失败: {e}")


def start_scheduler():
    """启动定时调度器"""
    if scheduler.running:
        logger.warning("Scheduler already running")
        return
    
    # 每日早上 8:00 执行
    scheduler.add_job(
        daily_news_collection,
        CronTrigger(hour=8, minute=0),
        id="daily_news_collection",
        name="每日资讯收集",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ 定时调度器已启动 (每日 08:00)")


def stop_scheduler():
    """停止定时调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏹️ 定时调度器已停止")


def get_scheduler_status():
    """获取调度器状态"""
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }
