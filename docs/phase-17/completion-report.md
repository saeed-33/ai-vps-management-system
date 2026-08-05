# تقرير إنجاز المرحلة السابعة عشرة: ربط السيرفرات الحقيقية وحفظ التقارير

## الحالة

مكتملة كأساس أولي.

## ما تم تنفيذه

- ربط دورة المراقبة بإعدادات SSH المحفوظة مؤقتا للسيرفر.
- إضافة persistence اختياري إلى PostgreSQL.
- حفظ `monitoring_cycles`.
- حفظ `periodic_monitoring_reports`.
- حفظ `monitoring_metrics`.
- Upsert للسيرفرات داخل جدول `servers`.
- إضافة UUID mapping مستقر للـ IDs النصية.
- إبقاء fallback إلى memory إذا لم تكن قاعدة البيانات جاهزة.
- إضافة اختبار لـ UUID mapping.

## الملفات الرئيسية

- `apps/api/src/control_plane_api/modules/periodic_monitoring/persistence.py`
- `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`
- `apps/api/src/control_plane_api/api/routes/periodic_monitoring.py`
- `apps/api/tests/test_periodic_monitoring.py`

## ملاحظات

- الحفظ في PostgreSQL يتطلب تشغيل migration وقاعدة بيانات جاهزة.
- إعدادات SSH نفسها لا تزال مؤقتة داخل ذاكرة API.
- قراءة التقارير من PostgreSQL ستأتي لاحقا.

## التحقق

- `uv run pytest` داخل `apps/api`: نجح، `43 passed`.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، `7 passed`.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint`: نجح.
- `npm run build`: نجح.

## تحقق البيئة المحلية

- تم التحقق من أن Docker Desktop متاح.
- محاولة تشغيل `docker compose -f infra/compose/docker-compose.dev.yml up -d` لم تكتمل ضمن المهلة بسبب بطء/تعليق تشغيل الحاويات.
- لم يتم تطبيق migration فعليا في هذه الجلسة.
- كود الحفظ في PostgreSQL جاهز، ويحتاج قاعدة بيانات مطبقة عليها `packages/database/migrations/0001_initial_schema.sql`.
