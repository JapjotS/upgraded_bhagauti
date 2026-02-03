from celery.schedules import crontab
from app.core.celery_app import celery_app
from app.core.config import Config


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Configure periodic tasks for automated data collection"""
    
    # Fetch market data every minute for all symbols
    sender.add_periodic_task(
        60.0,  # Every 60 seconds
        fetch_all_data.s(),
        name='fetch_all_market_data_periodic'
    )
    
    # Analyze signals every 2 minutes
    sender.add_periodic_task(
        120.0,  # Every 2 minutes
        analyze_all_signals.s(),
        name='analyze_all_signals_periodic'
    )


@celery_app.task(name='app.tasks.periodic.fetch_all_data')
def fetch_all_data():
    """Periodic task to fetch all market data"""
    from app.tasks.market_data import fetch_all_market_data
    return fetch_all_market_data.delay(Config.DEFAULT_SYMBOLS)


@celery_app.task(name='app.tasks.periodic.analyze_all_signals')
def analyze_all_signals():
    """Periodic task to analyze signals for all symbols"""
    from app.tasks.trading import analyze_signal
    
    results = {}
    for symbol in Config.DEFAULT_SYMBOLS:
        analyze_signal.delay(symbol)
        results[symbol] = 'queued'
    
    return results
