# تشغيل المشروع محليا

هذا الدليل يشرح تشغيل المشروع في حالته الحالية بعد المرحلة العاشرة.

## الحالة الحالية

المشروع يعمل حاليا كـ foundation محلي:

- Backend API مبني بـ FastAPI.
- Admin Panel مبنية بـ Next.js.
- المصادقة تعمل عبر Bootstrap Super Admin من متغيرات البيئة.
- صفحات المستخدمين، السيرفرات، ملفات المراقبة، والوكلاء المتخصصين تعتمد على بيانات fixture مؤقتة.
- لا يوجد CRUD متصل بقاعدة البيانات بعد.
- لا يوجد تشغيل فعلي للوكيل أو مراقبة فعلية للسيرفرات بعد.

## المتطلبات

- Python مع `uv`.
- Node.js وnpm.
- Git.
- Docker اختياري حاليا، لأن قاعدة البيانات ليست مستخدمة فعليا في endpoints الحالية.

## إعداد Backend API

ادخل إلى مجلد الـ API:

```powershell
cd E:\AI_VPS_Mamgment\ai-vps-management-system\apps\api
```

ثبت الاعتماديات:

```powershell
uv sync --extra dev
```

أنشئ ملف البيئة:

```powershell
Copy-Item ..\..\.env.example .env
```

إذا لم يعمل الأمر السابق بسبب المسار، انسخ محتوى الملف التالي يدويا:

```text
E:\AI_VPS_Mamgment\ai-vps-management-system\.env.example
```

إلى:

```text
E:\AI_VPS_Mamgment\ai-vps-management-system\apps\api\.env
```

## إعداد السوبر آدمن

في الحالة الحالية، السوبر آدمن هو Bootstrap Admin وليس مستخدما محفوظا في قاعدة البيانات.

الـ API يحتاج هذه القيم داخل:

```text
apps/api/.env
```

```env
AUTH_SECRET_KEY=change_me_to_a_long_random_value
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD_HASH=
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

ولد hash لكلمة المرور:

```powershell
uv run python scripts/hash_password.py
```

سيطلب السكربت كلمة المرور مرتين، ثم يطبع hash. ضع الناتج في:

```env
BOOTSTRAP_ADMIN_PASSWORD_HASH=ضع_الهاش_هنا
```

غيّر `AUTH_SECRET_KEY` إلى قيمة طويلة وعشوائية. لا تستخدم القيمة الافتراضية في أي بيئة حقيقية.

بيانات الدخول ستكون:

```text
Email: قيمة BOOTSTRAP_ADMIN_EMAIL
Password: كلمة المرور التي استخدمتها عند توليد hash
Role: owner
```

## تشغيل Backend API

من داخل:

```text
apps/api
```

شغل الخدمة:

```powershell
uv run uvicorn control_plane_api.main:app --reload --host 127.0.0.1 --port 8000
```

روابط التحقق:

```text
http://127.0.0.1:8000/health/live
http://127.0.0.1:8000/health/ready
http://127.0.0.1:8000/api/v1/meta
```

ملاحظة: `health/ready` قد يرجع أن قاعدة البيانات غير جاهزة إذا لم تكن PostgreSQL تعمل. هذا متوقع حاليا لأن معظم endpoints foundation لا تعتمد على قاعدة البيانات بعد.

## إعداد لوحة الإدارة

ادخل إلى مجلد لوحة الإدارة:

```powershell
cd E:\AI_VPS_Mamgment\ai-vps-management-system\apps\admin-panel
```

ثبت الاعتماديات:

```powershell
npm install --no-audit --no-fund --ignore-scripts
```

أنشئ ملف البيئة:

```powershell
New-Item -ItemType File -Force .env.local
```

ضع داخله:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## تشغيل لوحة الإدارة

من داخل:

```text
apps/admin-panel
```

شغل الواجهة:

```powershell
npm run dev
```

افتح:

```text
http://127.0.0.1:3000
```

صفحة تسجيل الدخول:

```text
http://127.0.0.1:3000/login
```

## تسجيل الدخول

1. افتح `/login`.
2. أدخل البريد الموجود في `BOOTSTRAP_ADMIN_EMAIL`.
3. أدخل كلمة المرور الأصلية التي استخدمتها عند توليد `BOOTSTRAP_ADMIN_PASSWORD_HASH`.
4. بعد نجاح الدخول، تحفظ الواجهة `access_token` محليا في المتصفح.

بعد الدخول يمكن فتح:

```text
http://127.0.0.1:3000/users
http://127.0.0.1:3000/periodic-monitoring
http://127.0.0.1:3000/servers
http://127.0.0.1:3000/monitoring-profiles
http://127.0.0.1:3000/specialist-agents
http://127.0.0.1:3000/allowed-tools
```

## تشغيل المراقبة الدورية

من صفحة:

```text
http://127.0.0.1:3000/periodic-monitoring
```

يمكنك:

- تشغيل دورة مراقبة يدوية.
- تشغيل scheduler بفاصل زمني بالثواني.
- إيقاف scheduler.
- رؤية آخر تقرير baseline.

الـ scheduler الحالي يعمل داخل عملية API فقط. عند إعادة تشغيل API تضيع حالة الجدولة والتقارير المؤقتة.

## اختبار المشروع

اختبار Backend API:

```powershell
cd E:\AI_VPS_Mamgment\ai-vps-management-system\apps\api
uv run pytest
```

فحص بناء لوحة الإدارة:

```powershell
cd E:\AI_VPS_Mamgment\ai-vps-management-system\apps\admin-panel
npm run lint
npm run build
```

## تشغيل خدمات التطوير الاختيارية

ملف Docker Compose موجود هنا:

```text
infra/compose/docker-compose.dev.yml
```

تشغيل PostgreSQL وRedis:

```powershell
cd E:\AI_VPS_Mamgment\ai-vps-management-system
docker compose -f infra/compose/docker-compose.dev.yml up -d
```

هذا اختياري في المرحلة الحالية. الربط الفعلي مع قاعدة البيانات سيصبح ضروريا عند الانتقال إلى CRUD وrepositories.

## مشاكل شائعة

إذا فشل تسجيل الدخول:

- تأكد أن `apps/api/.env` يحتوي `AUTH_SECRET_KEY`.
- تأكد أن `BOOTSTRAP_ADMIN_EMAIL` يطابق البريد في صفحة login.
- تأكد أنك أدخلت كلمة المرور الأصلية، وليس hash.
- أعد تشغيل API بعد تعديل `.env`.

إذا ظهرت أخطاء CORS:

- تأكد أن `CORS_ORIGINS` يحتوي:

```env
CORS_ORIGINS=["http://127.0.0.1:3000"]
```

إذا كانت الواجهة لا تصل إلى API:

- تأكد أن API يعمل على `http://127.0.0.1:8000`.
- تأكد أن `apps/admin-panel/.env.local` يحتوي:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

إذا ظهر تحذير Next.js عن `@next/swc-win32-x64-msvc` أثناء `npm run build` لكن البناء اكتمل بنجاح، فهو تحذير من حزمة SWC على Windows ولا يمنع تشغيل المشروع في الحالة الحالية.
