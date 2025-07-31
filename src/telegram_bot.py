import os
import logging
import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# رمز البوت - يجب الحصول عليه من BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

class XSSAutomationBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """إعداد معالجات الأوامر والرسائل"""
        # معالج أمر البداية
        self.application.add_handler(CommandHandler("start", self.start))
        
        # معالج أمر المساعدة
        self.application.add_handler(CommandHandler("help", self.help))
        
        # معالج أمر فحص XSS
        self.application.add_handler(CommandHandler("scan", self.scan_xss))
        
        # معالج الأزرار التفاعلية
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # معالج الرسائل النصية (للنطاقات)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_domain))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر البداية"""
        welcome_message = """
🔒 مرحباً بك في بوت XSS Automation!

هذا البوت يساعدك في اكتشاف ثغرات XSS (Cross-Site Scripting) في المواقع الإلكترونية بشكل آلي.

📋 الأوامر المتاحة:
/start - بدء المحادثة
/help - عرض المساعدة
/scan - فحص موقع للبحث عن ثغرات XSS

⚠️ تنبيه: استخدم هذا البوت فقط على المواقع التي تملكها أو لديك إذن صريح لاختبارها.

للبدء، أرسل /scan متبوعاً بالنطاق المراد فحصه
مثال: /scan example.com
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 بدء فحص جديد", callback_data='new_scan')],
            [InlineKeyboardButton("❓ المساعدة", callback_data='help')],
            [InlineKeyboardButton("ℹ️ حول البوت", callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر المساعدة"""
        help_message = """
📖 دليل استخدام بوت XSS Automation

🔍 كيفية الاستخدام:
1. أرسل الأمر /scan متبوعاً بالنطاق
   مثال: /scan testphp.vulnweb.com

2. أو أرسل النطاق مباشرة بدون أمر
   مثال: example.com

🛠️ ما يقوم به البوت:
• جمع عناوين URL من Wayback Machine
• البحث عن النطاقات الفرعية
• فحص الروابط النشطة
• اختبار ثغرات XSS باستخدام أدوات متقدمة

⏱️ وقت الفحص:
قد يستغرق الفحص من 5-15 دقيقة حسب حجم الموقع

⚠️ تحذيرات مهمة:
• استخدم البوت فقط على المواقع التي تملكها
• لا تستخدمه لأغراض ضارة أو غير قانونية
• البوت للأغراض التعليمية والاختبار الأمني المشروع فقط

📞 للدعم: تواصل مع مطور البوت
        """
        await update.message.reply_text(help_message)
    
    async def scan_xss(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر فحص XSS"""
        if not context.args:
            await update.message.reply_text(
                "❌ يرجى تحديد النطاق المراد فحصه\n"
                "مثال: /scan example.com"
            )
            return
        
        domain = context.args[0].strip()
        await self.perform_scan(update, domain)
    
    async def handle_domain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية (النطاقات)"""
        domain = update.message.text.strip()
        
        # التحقق من صحة النطاق
        if not self.is_valid_domain(domain):
            await update.message.reply_text(
                "❌ النطاق غير صحيح. يرجى إدخال نطاق صحيح\n"
                "مثال: example.com أو https://example.com"
            )
            return
        
        await self.perform_scan(update, domain)
    
    def is_valid_domain(self, domain):
        """التحقق من صحة النطاق"""
        # إزالة البروتوكول إذا كان موجوداً
        domain = domain.replace('https://', '').replace('http://', '')
        domain = domain.split('/')[0]  # إزالة المسار إذا كان موجوداً
        
        # فحص بسيط للنطاق
        if '.' not in domain or len(domain) < 3:
            return False
        
        # فحص الأحرف المسموحة
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
        return all(c in allowed_chars for c in domain)
    
    async def perform_scan(self, update: Update, domain: str):
        """تنفيذ عملية الفحص"""
        # تنظيف النطاق
        clean_domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        # رسالة البداية
        status_message = await update.message.reply_text(
            f"🔍 بدء فحص النطاق: {clean_domain}\n"
            "⏳ جاري التحضير... يرجى الانتظار"
        )
        
        try:
            # تحديث الحالة
            await status_message.edit_text(
                f"🔍 فحص النطاق: {clean_domain}\n"
                "📡 جاري جمع المعلومات من Wayback Machine..."
            )
            
            # تنفيذ سكربت XSS Automation
            result = await self.run_xss_automation(clean_domain, status_message)
            
            if result['success']:
                # إرسال النتائج
                await self.send_results(update, clean_domain, result['data'])
            else:
                await status_message.edit_text(
                    f"❌ فشل في فحص النطاق: {clean_domain}\n"
                    f"الخطأ: {result['error']}"
                )
        
        except Exception as e:
            logger.error(f"خطأ في فحص النطاق {clean_domain}: {str(e)}")
            await status_message.edit_text(
                f"❌ حدث خطأ أثناء فحص النطاق: {clean_domain}\n"
                "يرجى المحاولة مرة أخرى لاحقاً"
            )
    
    async def run_xss_automation(self, domain: str, status_message):
        """تشغيل سكربت XSS Automation"""
        try:
            # مسار سكربت XSS Automation
            script_path = "/home/ubuntu/XSS-Automation/xss_automation.sh"
            
            # التأكد من وجود السكربت
            if not os.path.exists(script_path):
                return {
                    'success': False,
                    'error': 'سكربت XSS Automation غير موجود'
                }
            
            # إعداد متغيرات البيئة
            env = os.environ.copy()
            env['PATH'] = env.get('PATH', '') + ':/usr/local/go/bin'
            env['GOPATH'] = '/home/ubuntu/go'
            
            # تشغيل السكربت
            process = await asyncio.create_subprocess_exec(
                'bash', script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd='/home/ubuntu/XSS-Automation'
            )
            
            # إرسال المدخلات للسكربت
            input_data = f"{domain}\nn\n"  # النطاق + عدم استخدام حمولات مخصصة
            
            # تحديث الحالة بشكل دوري
            await status_message.edit_text(
                f"🔍 فحص النطاق: {domain}\n"
                "🔧 جاري تثبيت الأدوات المطلوبة..."
            )
            
            # انتظار انتهاء العملية مع تحديث الحالة
            stdout, stderr = await process.communicate(input_data.encode())
            
            if process.returncode == 0:
                # قراءة النتائج
                results_dir = f"/home/ubuntu/XSS-Automation/results/{domain}"
                return await self.parse_results(results_dir, domain)
            else:
                return {
                    'success': False,
                    'error': f'فشل السكربت: {stderr.decode()[:200]}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تشغيل السكربت: {str(e)}'
            }
    
    async def parse_results(self, results_dir: str, domain: str):
        """تحليل نتائج الفحص"""
        try:
            if not os.path.exists(results_dir):
                return {
                    'success': False,
                    'error': 'مجلد النتائج غير موجود'
                }
            
            results = {
                'domain': domain,
                'wayback_urls': 0,
                'subdomains': 0,
                'live_urls': 0,
                'xss_ready_urls': 0,
                'vulnerable_urls': 0,
                'files': {}
            }
            
            # قراءة الملفات المختلفة
            files_to_check = [
                'wayback.txt',
                'subdomains.txt', 
                'live_uro1.txt',
                'xss_ready.txt',
                'Vulnerable_XSS.txt'
            ]
            
            for filename in files_to_check:
                filepath = os.path.join(results_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                        results['files'][filename] = lines
                        
                        # حساب الإحصائيات
                        if filename == 'wayback.txt':
                            results['wayback_urls'] = len(lines)
                        elif filename == 'subdomains.txt':
                            results['subdomains'] = len(lines)
                        elif filename == 'live_uro1.txt':
                            results['live_urls'] = len(lines)
                        elif filename == 'xss_ready.txt':
                            results['xss_ready_urls'] = len(lines)
                        elif filename == 'Vulnerable_XSS.txt':
                            results['vulnerable_urls'] = len(lines)
            
            return {
                'success': True,
                'data': results
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في تحليل النتائج: {str(e)}'
            }
    
    async def send_results(self, update: Update, domain: str, results: dict):
        """إرسال نتائج الفحص"""
        # رسالة الملخص
        summary = f"""
🎯 نتائج فحص النطاق: {domain}

📊 الإحصائيات:
• عناوين URL من Wayback: {results['wayback_urls']}
• النطاقات الفرعية: {results['subdomains']}
• الروابط النشطة: {results['live_urls']}
• روابط قابلة لاختبار XSS: {results['xss_ready_urls']}
• ثغرات XSS مكتشفة: {results['vulnerable_urls']}

{'🚨 تم اكتشاف ثغرات XSS!' if results['vulnerable_urls'] > 0 else '✅ لم يتم اكتشاف ثغرات XSS'}
        """
        
        keyboard = []
        
        # إضافة أزرار لعرض التفاصيل
        if results['vulnerable_urls'] > 0:
            keyboard.append([InlineKeyboardButton("🚨 عرض الثغرات المكتشفة", callback_data=f'show_vulns_{domain}')])
        
        if results['xss_ready_urls'] > 0:
            keyboard.append([InlineKeyboardButton("🔍 عرض الروابط المختبرة", callback_data=f'show_tested_{domain}')])
        
        keyboard.append([InlineKeyboardButton("📊 عرض الإحصائيات التفصيلية", callback_data=f'show_stats_{domain}')])
        keyboard.append([InlineKeyboardButton("🔍 فحص نطاق جديد", callback_data='new_scan')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, reply_markup=reply_markup)
        
        # حفظ النتائج في السياق للاستخدام لاحقاً
        if 'scan_results' not in update.effective_user.id.__dict__:
            update.effective_user.scan_results = {}
        update.effective_user.scan_results = {domain: results}
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'new_scan':
            await query.edit_message_text(
                "🔍 أرسل النطاق الذي تريد فحصه\n"
                "مثال: example.com أو https://example.com"
            )
        elif query.data == 'help':
            await self.help(update, context)
        elif query.data == 'about':
            about_message = """
ℹ️ حول بوت XSS Automation

🤖 هذا البوت تم تطويره لأتمتة عملية اكتشاف ثغرات XSS في المواقع الإلكترونية.

🛠️ الأدوات المستخدمة:
• Waybackurls - جمع الروابط من أرشيف الإنترنت
• GAU - جمع الروابط من مصادر متعددة
• Subfinder - اكتشاف النطاقات الفرعية
• Httpx - فحص الروابط النشطة
• Dalfox - اختبار ثغرات XSS

⚖️ إخلاء المسؤولية:
هذا البوت للأغراض التعليمية والاختبار الأمني المشروع فقط.
المطور غير مسؤول عن أي استخدام غير قانوني.

👨‍💻 تطوير: Manus AI
            """
            await query.edit_message_text(about_message)
    
    def run(self):
        """تشغيل البوت"""
        logger.info("بدء تشغيل بوت XSS Automation...")
        self.application.run_polling()

if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ يرجى تعيين BOT_TOKEN في متغيرات البيئة")
        exit(1)
    
    bot = XSSAutomationBot()
    bot.run()

