# المرحلة السادسة: Auth & RBAC Foundation

## الهدف

إنشاء أساس المصادقة والصلاحيات قبل بناء صفحات الإدارة الفعلية.

هذه المرحلة لا تبني نظام مستخدمين كاملا من قاعدة البيانات، لكنها تثبت:

- hashing لكلمات المرور.
- JWT access tokens.
- Bootstrap admin login عبر environment variables.
- endpoint لمعرفة المستخدم الحالي.
- تعريف أولي للأدوار والصلاحيات.
- صفحة login أولية في لوحة الإدارة.

## النطاق

داخل النطاق:

- إضافة أدوات security في Backend API.
- إضافة إعدادات auth.
- إضافة routes:
  - `POST /api/v1/auth/token`
  - `GET /api/v1/auth/me`
  - `GET /api/v1/auth/rbac`
- إضافة static RBAC catalog مبدئي.
- إضافة اختبارات auth.
- إضافة صفحة login أولية في لوحة الإدارة.
- إضافة auth client بسيط في الواجهة.

خارج النطاق حاليا:

- تسجيل مستخدمين من قاعدة البيانات.
- refresh tokens.
- sessions server-side.
- password reset.
- OAuth.
- إدارة المستخدمين من لوحة الإدارة.
- تطبيق RBAC فعلي على كل routes.

## لماذا Bootstrap Auth؟

لأن قاعدة المستخدمين وواجهات إدارة المستخدمين لم تبن بعد. نحتاج طريقة دخول أولية آمنة نسبيا لتطوير لوحة الإدارة بدون فتح login وهمي.

الدخول يعمل فقط إذا تم ضبط:

```text
BOOTSTRAP_ADMIN_EMAIL
BOOTSTRAP_ADMIN_PASSWORD_HASH
AUTH_SECRET_KEY
```

## معايير الإنجاز

- اختبارات Backend auth ناجحة.
- يمكن إصدار token عند صحة بيانات bootstrap admin.
- `/auth/me` يرفض الطلب بدون bearer token.
- `/auth/me` يعيد principal عند token صحيح.
- صفحة login موجودة في لوحة الإدارة.
- `npm run build` للوحة الإدارة ينجح.
- توثيق المرحلة محدث.
- commit وpush وtag إلى GitHub.
