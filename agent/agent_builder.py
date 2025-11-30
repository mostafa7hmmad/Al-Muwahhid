import os
import google.generativeai as genai
from .utils import read_pdf, read_json, merge_contents
from .resources import search_site
from dotenv import load_dotenv

class Da3iAgentStreaming:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.load_configuration()
        self.documents = self.load_books()
        self.resources = read_json(os.path.join(data_dir, "resources.json"))
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ لم يتم العثور على GOOGLE_API_KEY في ملف .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=self.system_instruction
        )
    
    def load_configuration(self):
        """تحميل جميع ملفات التكوين"""
        system_path = os.path.join(self.data_dir, "system_instructions.json")
        system_data = read_json(system_path)
        base_instruction = system_data.get("system_instruction", "")
        
        behaviour_path = os.path.join(self.data_dir, "behaviour_rules.json")
        behaviour_data = read_json(behaviour_path)
        behaviour_rules = behaviour_data.get("rules", [])
        behaviour_text = "\n".join([f"- {rule}" for rule in behaviour_rules])
        
        persona_path = os.path.join(self.data_dir, "persona.json")
        persona_data = read_json(persona_path)
        persona_name = persona_data.get("name", "المُوَحِّد")
        persona_description = persona_data.get("description", "")
        persona_traits = persona_data.get("traits", [])
        persona_text = f"{persona_description}\nالصفات: {', '.join(persona_traits)}"
        
        requirements_path = os.path.join(self.data_dir, "base_requirements.txt")
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                base_requirements = f.read()
        except:
            base_requirements = ""
        
        viewshot_path = os.path.join(self.data_dir, "viewshot_examples.json")
        viewshot_data = read_json(viewshot_path)
        examples = viewshot_data.get("examples", [])
        examples_text = ""
        for ex in examples[:3]:
            examples_text += f"\nمثال:\nالسؤال: {ex.get('question', '')}\nالإجابة: {ex.get('answer', '')}\n"
        
        self.system_instruction = f"""اسمك: {persona_name}

{persona_text}

{base_instruction}

متطلبات أساسية:
{base_requirements}

قواعد السلوك:
{behaviour_text}

أمثلة على الإجابات المتوقعة:
{examples_text}

⚠️ مهم جداً:
- اكتب بلغة عربية فصيحة وواضحة
- لا تنسخ النصوص من المراجع حرفياً إذا كانت مشوهة
- أعد صياغة المعلومات بأسلوبك الخاص
- إذا وجدت نصاً مشوهاً في المرجع، لا تستخدمه
"""
        
        print("✅ تم تحميل التكوينات بنجاح")

    def load_books(self):
        """تحميل الكتب مع فحص جودة النص"""
        books_dir = os.path.join(self.data_dir, "books")
        books_data = []
        
        if not os.path.exists(books_dir):
            print(f"⚠️ مجلد الكتب غير موجود")
            return books_data
        
        pdf_files = [f for f in os.listdir(books_dir) if f.endswith(".pdf")]
        print(f"📚 جاري تحميل {len(pdf_files)} كتاب...")
        
        for book_file in pdf_files:
            book_path = os.path.join(books_dir, book_file)
            text = read_pdf(book_path)
            
            # فحص جودة النص
            if text and len(text) > 500:
                # حساب نسبة الأحرف العربية الصحيحة
                arabic_chars = sum(1 for c in text[:1000] if '\u0600' <= c <= '\u06FF')
                quality_ratio = arabic_chars / min(1000, len(text))
                
                if quality_ratio > 0.3:  # على الأقل 30% أحرف عربية
                    books_data.append({
                        "name": book_file.replace(".pdf", ""),
                        "content": text[:15000],
                        "quality": "جيد" if quality_ratio > 0.7 else "متوسط"
                    })
                    print(f"  ✓ {book_file} (جودة: {quality_ratio*100:.0f}%)")
                else:
                    print(f"  ⚠️ {book_file} (جودة منخفضة، تم التجاهل)")
            else:
                print(f"  ❌ {book_file} (فارغ أو قصير جداً)")
        
        print(f"✅ تم تحميل {len(books_data)} كتاب بنجاح")
        return books_data

    def generate_stream(self, prompt):
        """توليد إجابة streaming"""
        try:
            response = self.model.generate_content(
                prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    top_p=0.9,
                    max_output_tokens=2000,
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"❌ خطأ في API: {str(e)}"

    def ask(self, question, chat_history=[]):
        """الإجابة على السؤال"""
        
        # جمع المراجع من الكتب الجيدة فقط
        books_context = ""
        good_books = [b for b in self.documents if b.get("quality") == "جيد"]
        
        if good_books:
            print(f"📖 استخدام {len(good_books)} كتاب كمرجع")
            for book in good_books[:3]:  # أول كتابين فقط
                books_context += f"\n### معلومات من: {book['name']}\n{book['content'][:10000]}\n"
        
        # البحث في المواقع
        web_context = ""
        try:
            urls = self.resources.get("urls", [])
            for url in urls[:3]:  # موقع واحد فقط
                snippet = search_site(question, url)
                if snippet and len(snippet) > 50:
                    web_context += f"\n### من موقع {url}:\n{snippet}\n"
        except:
            pass
        
        all_context = books_context + web_context
        
        # بناء التاريخ
        history_text = ""
        for msg in chat_history[-3:]:
            if msg["role"] == "user":
                history_text += f"س: {msg['message']}\n"
            elif msg["role"] == "assistant":
                history_text += f"ج: {msg['message'][:200]}...\n\n"
        
        # بناء Prompt
        if all_context.strip():
            prompt = f"""لديك المراجع التالية (قد تحتوي على أخطاء طباعية):

{all_context[:10000]}

المحادثة السابقة:
{history_text}

السؤال: {question}

⚠️ تعليمات مهمة:
1. اقرأ المراجع وافهم المعنى العام
2. أعد صياغة الإجابة بأسلوبك الخاص بلغة عربية فصيحة وواضحة
3. لا تنسخ النصوص المشوهة، بل اكتب بأسلوب جديد
4. استشهد بالآيات والأحاديث بشكل صحيح
5. اذكر المصدر بشكل بسيط (اسم الكتاب أو الموقع)
"""
        else:
            prompt = f"""السياق السابق:
{history_text}

السؤال: {question}

أجب بلغة عربية فصيحة وواضحة، بناءً على معرفتك بالعقيدة الإسلامية.
"""
        
        return self.generate_stream(prompt)