import PyPDF2
import pdfplumber
import json

def read_pdf(filepath):
    """قراءة ملف PDF بطريقتين لضمان الجودة"""
    text = ""
    
    # المحاولة 1: استخدام pdfplumber (الأفضل للنصوص العربية)
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # إذا نجحت وكان النص جيد، ارجع
        if text and len(text) > 100:
            return clean_arabic_text(text)
    except Exception as e:
        print(f"⚠️ pdfplumber فشل: {e}")
    
    # المحاولة 2: استخدام PyPDF2 كبديل
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return clean_arabic_text(text)
    except Exception as e:
        print(f"❌ خطأ في قراءة PDF {filepath}: {e}")
        return ""

def clean_arabic_text(text):
    """تنظيف النص العربي من المشاكل الشائعة"""
    if not text:
        return ""
    
    # إزالة الأحرف الغريبة والرموز
    replacements = {
        'ك': 'ك',
        'ي': 'ي',
        'ة': 'ة',
        'أ': 'أ',
        'إ': 'إ',
        'آ': 'آ',
        'ؿ': 'ل',
        'ف': 'ف',
        'ؾ': 'ك',
        'ط': 'ع',
        'حُّ': 'حب',
        'األ': 'الأ',
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    # إزالة الأسطر الفارغة المتكررة
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 3:  # تجاهل الأسطر القصيرة جداً
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # إزالة المسافات الزائدة
    text = ' '.join(text.split())
    
    return text

def read_json(filepath):
    """قراءة ملف JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"خطأ في قراءة الملف {filepath}: {e}")
        return {}

def merge_contents(*texts):
    """دمج عدة نصوص مع فواصل"""
    return "\n\n---\n\n".join(filter(None, texts))