import os
import sys
import json
import urllib.request
from playwright.sync_api import sync_playwright

APP_URL = os.getenv("STREAMLIT_APP_URL", "https://yesgoo.streamlit.app/")
TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_msg(message: str):
    """通过 Telegram API 发送通知"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("未检测到 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳过推送通知。")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print("Telegram 通知发送成功！")
            else:
                print(f"Telegram 推送失败，状态码: {response.status}")
    except Exception as e:
        print(f"发送 Telegram 通知时发生异常: {e}")

def run():
    print(f"正在启动无头浏览器，访问目标地址: {APP_URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(APP_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            
            # 定位复活按钮
            wake_button = page.locator('button:has-text("Yes, get this app back up!"), button:has-text("Wake app")')
            
            if wake_button.is_visible(timeout=5000):
                print("检测到应用处于休眠状态，正在点击唤醒...")
                wake_button.click()
                page.wait_for_timeout(15000)
                
                msg = f"🚀 *Streamlit 休眠唤醒成功*\n\n应用先前处于休眠状态，已被脚本成功复活！\n🔗 *链接*: {APP_URL}"
                print(msg)
                send_telegram_msg(msg)
            else:
                msg = f"✅ *Stream 巡检正常*\n\n应用当前正常在线运行中，无需唤醒。\n🔗 *链接*: {APP_URL}"
                print(msg)
                send_telegram_msg(msg)

        except Exception as e:
            err_msg = f"❌ *Streamlit 保活运行报错*\n\n保活脚本执行失败，请检查工作流日志。\n⚠️ *报错原因*: `{e}`\n🔗 *链接*: {APP_URL}"
            print(f"脚本运行错误: {e}", file=sys.stderr)
            send_telegram_msg(err_msg)
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
