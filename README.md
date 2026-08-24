# ✦ VORTEX CLI - Next-Gen Media Engine & Stream Grabber ✦

أداة سطر أوامر تفاعلية حديثة واحترافية متقدمة (CLI) لتحميل الفيديوهات والمقاطع الصوتية بأعلى سرعة وجودة، بالروابط المباشرة أو بمجرد البحث بالاسم، بتصميم سايبربانك داكن وأنيق.

---

## ⚡ التشغيل المباشر من أي مكان (Global Command)
الأداة مثبتة الآن على جهازك عالمياً! يمكنك كتابة الأمر التالي من أي تيرمينال أو مجلد:
```bash
vortex
```
أو تشغيل ملف:
```
start_cli.bat
```

---

## ✨ المميزات الرئيسية
- 🎨 **واجهة تفاعلية إبداعية (Cyberpunk / Dark Theme)**: تحكم كامل بالأسهم ولوحة المفاتيح مع شريط تقدم مباشر يُظهر السرعة، الحجم المنقول، والوقت المتبقي بدقة.
- ⚙️ **إعدادات ومسار حفظ مخصص (Settings & Preferences)**:
  - التحميل الافتراضي يتم داخل مجلد الأداة `downloads/`.
  - يمكنك من خلال خيار `⚙️ Settings & Customization` في القائمة تغيير مجلد الحفظ إلى سطح المكتب (Desktop)، مجلد التنزيلات (Downloads)، أو أي مسار مخصص تريده، مع حفظ الإعداد تلقائياً وبشكل دائم في `config.json`.
- 🔍 **البحث الذكي بالاسم**: لا تحتاج لنسخ الرابط! فقط اكتب اسم الفيديو/الأنشودة/الأغنية وستظهر لك قائمة بأفضل النتائج لاختيار ما تريد تحميله.
- 🔗 **دعم الروابط المباشرة**: يدعم أكثر من 1000 منصة (YouTube, TikTok, Twitter/X, Instagram, Facebook, SoundCloud, Pinterest، وروابط MP4/MP3 المباشرة).
- 🎬 **جودات وصيغ متعددة**:
  - **فيديو (MP4)**:
    - 🌟 **Ultra / High**: دقة 4K / 1080p 60fps (أعلى جودة متوفرة).
    - ⚡ **Medium / Standard**: دقة 720p / 480p (متوازنة وسريعة).
    - 💾 **Low / Saver**: دقة 360p / 240p (حجم خفيف وتوفير للمساحة).
  - **صوت (MP3)**:
    - 🌟 **High Fidelity**: جودة استوديو 320 kbps MP3.
    - ⚡ **Standard**: جودة 192 kbps MP3.
    - 💾 **Low / Fast**: جودة 128 kbps MP3.
- 📁 **تحميل دُفعي (Batch Download)**: إمكانية تحميل عدة روابط دفعة واحدة من ملف نصي أو بلصق روابط متعددة.
- ⚡ **تكامل تلقائي لـ FFmpeg**: دمج الصوت والصورة وتحويل التنسيقات وتضمين الغلاف والبيانات تلقائياً.

---

## 🚀 أوامر سريعة (CLI Commands)
```bash
# فتح الواجهة التفاعلية
vortex

# تحميل فيديو عبر الرابط مباشرة
vortex "https://www.youtube.com/watch?v=..." --type video --quality high

# تحميل صوت MP3 بالبحث بالاسم مباشرة
vortex -s "سورة الكهف بصوت خاشع" --type audio --quality high

# تحميل قائمة روابط من ملف نصي
vortex --batch urls.txt --type video --quality medium
```

---

## 📂 بنية المشروع
- [`downloader_cli.py`](file:///c:/Users/Drafter-5/Desktop/Download%20all%20by%20one/downloader_cli.py): واجهة المستخدم والأوامر.
- [`downloader_engine.py`](file:///c:/Users/Drafter-5/Desktop/Download%20all%20by%20one/downloader_engine.py): محرك التحميل والمعالجة.
- [`config.py`](file:///c:/Users/Drafter-5/Desktop/Download%20all%20by%20one/config.py): إدارة الإعدادات ومسارات الحفظ المستمرة.
- [`config.json`](file:///c:/Users/Drafter-5/Desktop/Download%20all%20by%20one/config.json): ملف تخزين الإعدادات المخصصة للمستخدم.
- [`start_cli.bat`](file:///c:/Users/Drafter-5/Desktop/Download%20all%20by%20one/start_cli.bat): مشغل سريع 1-Click.
- `downloads/`: المجلد الافتراضي للتحميلات.
