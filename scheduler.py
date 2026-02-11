"""
Scheduler Module
Schedule automatic video creation and upload
"""

import schedule
import time
from datetime import datetime
import yaml
from main import AutomationPipeline


class AutomationScheduler:
    """Schedule automated video creation"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize scheduler"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.automation_config = self.config['automation']
        self.pipeline = AutomationPipeline(config_path)
        
        self.videos_today = 0
        self.last_run_date = None
    
    def run_automation(self):
        """Run the automation pipeline"""
        current_date = datetime.now().date()
        
        # Reset daily counter
        if self.last_run_date != current_date:
            self.videos_today = 0
            self.last_run_date = current_date
        
        # Check daily limit
        max_per_day = self.automation_config.get('max_videos_per_day', 3)
        if self.videos_today >= max_per_day:
            print(f"⏸️  Daily limit reached ({max_per_day} videos)")
            return
        
        print(f"\n{'='*60}")
        print(f"🤖 SCHEDULED RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            result = self.pipeline.create_video()
            
            if result['success']:
                self.videos_today += 1
                print(f"\n✅ Video {self.videos_today}/{max_per_day} created today")
            
        except Exception as e:
            print(f"\n❌ Scheduled run failed: {str(e)}")
            # TODO: Send notification if configured
    
    def start(self):
        """Start the scheduler"""
        if not self.automation_config.get('enabled', False):
            print("❌ Automation is disabled in config.yaml")
            print("   Set automation.enabled to true to use scheduler")
            return
        
        frequency = self.automation_config['schedule']['frequency']
        run_time = self.automation_config['schedule']['time']
        
        print(f"🤖 Starting automation scheduler...")
        print(f"   Frequency: {frequency}")
        print(f"   Time: {run_time}")
        print(f"   Max videos/day: {self.automation_config['max_videos_per_day']}")
        print(f"\n⏰ Waiting for scheduled time...\n")
        
        # Schedule based on frequency
        if frequency == 'daily':
            schedule.every().day.at(run_time).do(self.run_automation)
        elif frequency == 'weekly':
            # Run weekly on Sunday
            schedule.every().sunday.at(run_time).do(self.run_automation)
        else:
            print(f"❌ Unknown frequency: {frequency}")
            return
        
        # Run scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped by user")


def main():
    """Main entry point for scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Schedule automated Islamic story videos'
    )
    
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run automation immediately (ignore schedule)'
    )
    
    args = parser.parse_args()
    
    scheduler = AutomationScheduler()
    
    if args.run_now:
        print("▶️  Running automation immediately...\n")
        scheduler.run_automation()
    else:
        scheduler.start()


if __name__ == "__main__":
    main()
