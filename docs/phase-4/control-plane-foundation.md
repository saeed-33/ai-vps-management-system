# تصميم أساس Control Plane

## دور Control Plane

Control Plane هو طبقة القرار المركزية في النظام. لا يجب أن تكون لوحة الإدارة أو الوكيل هي صاحبة القرار النهائي في التنفيذ أو الصلاحيات.

مسؤولياته المستقبلية:

- تطبيق صلاحيات المستخدمين.
- تطبيق صلاحيات الوكيل.
- إدارة السيرفرات.
- إدارة ملفات المراقبة.
- إدارة الوكلاء المتخصصين.
- إدارة الأدوات والحلول المسموحة.
- تسجيل audit logs.
- استقبال نتائج المراقبة.
- إصدار طلبات MCP إلى الوكيل.
- حفظ التقارير والمشكلات.

## الهيكل الحالي

```text
apps/api/
  src/control_plane_api/
    api/
      routes/
    core/
    schemas/
    main.py
```

## طبقات الكود

### `main.py`

ينشئ تطبيق FastAPI من خلال application factory.

الهدف:

- تسهيل الاختبار.
- السماح بتغيير الإعدادات لاحقا.
- عزل initialization عن تعريف التطبيق.

### `core/config.py`

يحمل إعدادات الخدمة من environment variables.

أمثلة:

```text
APP_NAME
APP_ENV
DATABASE_URL
REDIS_URL
API_V1_PREFIX
```

### `core/database.py`

يجهز SQLAlchemy async engine وsession maker.

في المرحلة الحالية، لا يتم إجبار التطبيق على وجود قاعدة البيانات عند بدء التشغيل. بدلا من ذلك:

- `/health/live` يتحقق أن الخدمة تعمل.
- `/health/ready` يتحقق من قاعدة البيانات.

### `api/router.py`

يجمع routes الخاصة بـ API v1.

### `api/routes/health.py`

يوفر:

```text
/health/live
/health/ready
```

### `api/routes/meta.py`

يوفر:

```text
/api/v1/meta
```

هذا endpoint يعرض الوحدات المخطط لها وحالتها الحالية.

## لماذا لا نبني CRUD الآن؟

لأن CRUD يحتاج قرارات إضافية:

- شكل auth.
- سياسة RBAC.
- DTOs النهائية.
- كيفية تطبيق audit logs.
- هل سنستخدم SQLAlchemy ORM models أم SQLModel أم طبقة repository يدوية.

المرحلة الحالية تثبت التطبيق والاتصال والهيكل بدون قفل هذه القرارات مبكرا.
