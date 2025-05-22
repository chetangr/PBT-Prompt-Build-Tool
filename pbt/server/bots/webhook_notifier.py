import os
import requests
import json
from datetime import datetime

class WebhookNotifier:
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    
    def send_slack_notification(self, message: str, channel: str = "#prompt-updates"):
        """Send notification to Slack"""
        if not self.slack_webhook:
            return {"error": "Slack webhook not configured"}
        
        payload = {
            "channel": channel,
            "username": "PBT Bot",
            "text": message,
            "icon_emoji": ":robot_face:"
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload)
            return {"success": response.status_code == 200}
        except Exception as e:
            return {"error": str(e)}
    
    def send_discord_notification(self, message: str):
        """Send notification to Discord"""
        if not self.discord_webhook:
            return {"error": "Discord webhook not configured"}
        
        payload = {
            "content": message,
            "username": "PBT Bot",
            "avatar_url": "https://example.com/bot-avatar.png"
        }
        
        try:
            response = requests.post(self.discord_webhook, json=payload)
            return {"success": response.status_code == 204}
        except Exception as e:
            return {"error": str(e)}
    
    def notify_prompt_published(self, prompt_name: str, author: str, version: str):
        """Notify when a new prompt pack is published"""
        message = f"📦 New PromptPack published!\n" \
                 f"**{prompt_name}** v{version} by {author}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        results = {}
        results["slack"] = self.send_slack_notification(message)
        results["discord"] = self.send_discord_notification(message)
        
        return results
    
    def notify_evaluation_complete(self, prompt_name: str, score: float, pass_rate: float):
        """Notify when prompt evaluation is complete"""
        status_emoji = "✅" if score >= 8 else "⚠️" if score >= 6 else "❌"
        
        message = f"{status_emoji} Evaluation Complete!\n" \
                 f"**{prompt_name}**\n" \
                 f"Score: {score}/10\n" \
                 f"Pass Rate: {pass_rate*100:.1f}%\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        results = {}
        results["slack"] = self.send_slack_notification(message)
        results["discord"] = self.send_discord_notification(message)
        
        return results
    
    def notify_weekly_digest(self, stats: dict):
        """Send weekly digest notification"""
        message = f"📊 Weekly PBT Digest\n" \
                 f"New Prompts: {stats.get('new_prompts', 0)}\n" \
                 f"Total Evaluations: {stats.get('total_evaluations', 0)}\n" \
                 f"Avg Score: {stats.get('avg_score', 0):.1f}/10\n" \
                 f"Top Prompt: {stats.get('top_prompt', 'N/A')}\n" \
                 f"Week ending: {datetime.now().strftime('%Y-%m-%d')}"
        
        results = {}
        results["slack"] = self.send_slack_notification(message, "#weekly-digest")
        results["discord"] = self.send_discord_notification(message)
        
        return results

notifier = WebhookNotifier()

# Legacy functions for backwards compatibility
def send_discord(message):
    notifier.send_discord_notification(message)

def send_slack(message):
    notifier.send_slack_notification(message)

if __name__ == "__main__":
    msg = "🔥 A new PromptPack was published!"
    send_discord(msg)
    send_slack(msg)