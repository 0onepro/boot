#!/usr/bin/env python3
"""
XSS Automation Telegram Bot
بوت تيليجرام لأتمتة اكتشاف ثغرات XSS
"""

import os
import sys
import logging
from telegram_bot import XSSAutomationBot

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    
    # إعداد التسجيل
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # التحقق من وجود رمز البوت
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
        logger.error("❌ لم يتم تعيين BOT_TOKEN في متغيرات البيئة")
        logger.error("يرجى الحصول على رمز البوت من @BotFather وتعيينه كمتغير بيئة:")
        logger.error("export BOT_TOKEN='your_bot_token_here'")
        sys.exit(1)
    
    # التحقق من وجود سكربت XSS Automation
    script_path = "/home/ubuntu/XSS-Automation/xss_automation.sh"
    if not os.path.exists(script_path):
        logger.error(f"❌ سكربت XSS Automation غير موجود في: {script_path}")
        logger.error("يرجى التأكد من وجود السكربت في المسار الصحيح")
        sys.exit(1)
    
    try:
        logger.info("🚀 بدء تشغيل بوت XSS Automation...")
        bot = XSSAutomationBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

