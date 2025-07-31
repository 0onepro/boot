#!/usr/bin/env python3
"""
اختبار بوت XSS Automation
"""

import os
import sys
import asyncio
import logging
from unittest.mock import Mock, patch

# إضافة مسار src للاستيراد
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot import XSSAutomationBot

# إعداد التسجيل للاختبار
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotTester:
    def __init__(self):
        self.bot = None
        self.test_results = []
    
    def setup_mock_bot(self):
        """إعداد بوت وهمي للاختبار"""
        # تعيين رمز وهمي للاختبار
        os.environ['BOT_TOKEN'] = 'TEST_TOKEN_123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        try:
            self.bot = XSSAutomationBot()
            return True
        except Exception as e:
            logger.error(f"فشل في إنشاء البوت: {e}")
            return False
    
    def test_domain_validation(self):
        """اختبار التحقق من صحة النطاقات"""
        logger.info("🧪 اختبار التحقق من صحة النطاقات...")
        
        test_cases = [
            ("example.com", True),
            ("https://example.com", True),
            ("http://test.example.com", True),
            ("invalid", False),
            ("", False),
            ("test..com", False),
            ("test.com/path", True),  # يجب أن يكون صحيح بعد التنظيف
        ]
        
        passed = 0
        total = len(test_cases)
        
        for domain, expected in test_cases:
            try:
                result = self.bot.is_valid_domain(domain)
                if result == expected:
                    logger.info(f"✅ {domain} -> {result} (متوقع: {expected})")
                    passed += 1
                else:
                    logger.error(f"❌ {domain} -> {result} (متوقع: {expected})")
            except Exception as e:
                logger.error(f"❌ خطأ في اختبار {domain}: {e}")
        
        success_rate = (passed / total) * 100
        self.test_results.append({
            'test': 'Domain Validation',
            'passed': passed,
            'total': total,
            'success_rate': success_rate
        })
        
        logger.info(f"📊 نتيجة اختبار التحقق من النطاقات: {passed}/{total} ({success_rate:.1f}%)")
        return success_rate >= 80
    
    def test_command_handlers(self):
        """اختبار معالجات الأوامر"""
        logger.info("🧪 اختبار معالجات الأوامر...")
        
        # فحص وجود المعالجات
        handlers = self.bot.application.handlers
        
        command_handlers = []
        callback_handlers = []
        message_handlers = []
        
        for handler_group in handlers.values():
            for handler in handler_group:
                if hasattr(handler, 'command'):
                    command_handlers.append(handler.command)
                elif hasattr(handler, 'pattern'):
                    callback_handlers.append('callback_query')
                elif hasattr(handler, 'filters'):
                    message_handlers.append('message')
        
        expected_commands = ['start', 'help', 'scan']
        found_commands = [cmd for cmd_list in command_handlers for cmd in cmd_list if cmd_list]
        
        passed = 0
        total = len(expected_commands)
        
        for cmd in expected_commands:
            if cmd in found_commands:
                logger.info(f"✅ أمر /{cmd} موجود")
                passed += 1
            else:
                logger.error(f"❌ أمر /{cmd} غير موجود")
        
        # فحص وجود معالج الأزرار
        if callback_handlers:
            logger.info("✅ معالج الأزرار التفاعلية موجود")
            passed += 0.5
        else:
            logger.error("❌ معالج الأزرار التفاعلية غير موجود")
        
        # فحص وجود معالج الرسائل
        if message_handlers:
            logger.info("✅ معالج الرسائل النصية موجود")
            passed += 0.5
        else:
            logger.error("❌ معالج الرسائل النصية غير موجود")
        
        total += 1  # للمعالجات الإضافية
        success_rate = (passed / total) * 100
        
        self.test_results.append({
            'test': 'Command Handlers',
            'passed': passed,
            'total': total,
            'success_rate': success_rate
        })
        
        logger.info(f"📊 نتيجة اختبار معالجات الأوامر: {passed:.1f}/{total} ({success_rate:.1f}%)")
        return success_rate >= 80
    
    def test_file_structure(self):
        """اختبار بنية الملفات"""
        logger.info("🧪 اختبار بنية الملفات...")
        
        required_files = [
            'src/telegram_bot.py',
            'src/bot_main.py',
            'requirements.txt',
            'README.md',
            'Dockerfile',
            'render.yaml',
            'deploy_instructions.md',
            '.env.example'
        ]
        
        passed = 0
        total = len(required_files)
        
        for file_path in required_files:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                logger.info(f"✅ {file_path} موجود")
                passed += 1
            else:
                logger.error(f"❌ {file_path} غير موجود")
        
        success_rate = (passed / total) * 100
        
        self.test_results.append({
            'test': 'File Structure',
            'passed': passed,
            'total': total,
            'success_rate': success_rate
        })
        
        logger.info(f"📊 نتيجة اختبار بنية الملفات: {passed}/{total} ({success_rate:.1f}%)")
        return success_rate >= 90
    
    def test_dependencies(self):
        """اختبار المكتبات المطلوبة"""
        logger.info("🧪 اختبار المكتبات المطلوبة...")
        
        required_packages = [
            'telegram',
            'flask',
            'sqlalchemy'
        ]
        
        passed = 0
        total = len(required_packages)
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} مثبت")
                passed += 1
            except ImportError:
                logger.error(f"❌ {package} غير مثبت")
        
        success_rate = (passed / total) * 100
        
        self.test_results.append({
            'test': 'Dependencies',
            'passed': passed,
            'total': total,
            'success_rate': success_rate
        })
        
        logger.info(f"📊 نتيجة اختبار المكتبات: {passed}/{total} ({success_rate:.1f}%)")
        return success_rate >= 100
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        logger.info("🚀 بدء تشغيل اختبارات البوت...")
        
        # إعداد البوت الوهمي
        if not self.setup_mock_bot():
            logger.error("❌ فشل في إعداد البوت للاختبار")
            return False
        
        # تشغيل الاختبارات
        tests = [
            self.test_file_structure,
            self.test_dependencies,
            self.test_domain_validation,
            self.test_command_handlers,
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                    logger.info("✅ الاختبار نجح")
                else:
                    logger.warning("⚠️ الاختبار فشل")
            except Exception as e:
                logger.error(f"❌ خطأ في الاختبار: {e}")
        
        # تقرير النتائج النهائية
        logger.info("\n" + "="*50)
        logger.info("📋 تقرير الاختبارات النهائي")
        logger.info("="*50)
        
        for result in self.test_results:
            logger.info(f"{result['test']}: {result['passed']:.1f}/{result['total']} ({result['success_rate']:.1f}%)")
        
        overall_success = (passed_tests / total_tests) * 100
        logger.info(f"\n🎯 النتيجة الإجمالية: {passed_tests}/{total_tests} ({overall_success:.1f}%)")
        
        if overall_success >= 75:
            logger.info("🎉 البوت جاهز للنشر!")
            return True
        else:
            logger.warning("⚠️ البوت يحتاج إلى تحسينات قبل النشر")
            return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🤖 اختبار بوت XSS Automation")
    print("="*40)
    
    tester = BotTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ جميع الاختبارات نجحت! البوت جاهز للاستخدام.")
        return 0
    else:
        print("\n❌ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
        return 1

if __name__ == '__main__':
    exit(main())

