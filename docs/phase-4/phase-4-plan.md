# المرحلة الرابعة: Backend API / Control Plane Foundation

## الهدف

إنشاء أساس خدمة Backend API التي ستكون مركز التحكم في النظام.

هذه المرحلة لا تبني كل وظائف لوحة الإدارة، لكنها تضع البنية التي ستستقبل لاحقا:

- المستخدمين والصلاحيات.
- السيرفرات.
- ملفات المراقبة.
- الوكلاء المتخصصين.
- التقارير والمشكلات.
- الأدوات والحلول المسموحة.
- RAG والوثائق.
- المحادثة.
- MCP والوكيل.
- Policy Engine.

## النطاق

داخل النطاق:

- إنشاء مشروع FastAPI داخل `apps/api`.
- إعداد config مركزي.
- إنشاء application factory.
- إنشاء routes أساسية.
- إنشاء health check وreadiness check.
- تجهيز database session layer.
- تجهيز router structure لـ API v1.
- إضافة اختبارات smoke.
- توثيق التشغيل المحلي.

خارج النطاق حاليا:

- تسجيل دخول فعلي.
- JWT وRBAC.
- CRUD كامل للجداول.
- ربط مباشر مع الوكيل.
- MCP server فعلي.
- تشغيل migrations تلقائيا.
- Dockerfile الإنتاجي.

## القرارات التقنية

```text
Framework: FastAPI
Runtime: Python
Database access: SQLAlchemy async
PostgreSQL driver: asyncpg
Config: pydantic-settings
Tests: pytest + FastAPI TestClient
Package manager: uv
```

## سبب البداية بـ FastAPI

- مناسب لبناء API واضح وسريع.
- يدعم typing وOpenAPI تلقائيا.
- مناسب للتكامل مع Python Agent لاحقا.
- يقلل الفجوة بين API والوكيل وRAG.

## معايير الإنجاز

- يمكن تشغيل API محليا.
- `/health/live` يعمل بدون قاعدة بيانات.
- `/health/ready` يفحص الاتصال بقاعدة البيانات عند توفرها.
- `/api/v1/meta` يعرض معلومات النظام والوحدات المجهزة.
- توجد اختبارات smoke ناجحة.
- يتم تحديث سجل المراحل.
- يتم commit وpush إلى GitHub.
