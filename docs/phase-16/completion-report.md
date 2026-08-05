# تقرير إنجاز المرحلة السادسة عشرة: ربط إعدادات SSH بإدارة السيرفرات

## الحالة

مكتملة كأساس مؤقت.

## ما تم تنفيذه

- إضافة `ServerSshAccessPublic`.
- إضافة `ServerSshAccessUpdate`.
- إضافة endpoint لتحديث SSH access.
- حفظ إعدادات SSH مؤقتا داخل API memory.
- منع رجوع كلمة المرور في الاستجابة.
- ربط periodic monitoring بإعدادات SSH المحفوظة.
- إضافة نموذج SSH في صفحة السيرفرات.
- إضافة اختبارات API.

## الملفات الرئيسية

- `apps/api/src/control_plane_api/schemas/servers.py`
- `apps/api/src/control_plane_api/modules/servers/service.py`
- `apps/api/src/control_plane_api/api/routes/servers.py`
- `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`
- `apps/api/tests/test_servers.py`
- `apps/admin-panel/src/features/servers/components/servers-view.tsx`
- `apps/admin-panel/src/lib/servers-client.ts`

## endpoint

```text
PUT /api/v1/servers/{server_id}/ssh-access
```

## ملاحظات

- الحفظ مؤقت للتطوير.
- لا تزال الأسرار بحاجة إلى تخزين مشفر لاحقا.
- لا يوجد test connection من الواجهة بعد.

## التحقق

- `uv run --extra dev pytest` داخل `apps/agent`: نجح، `7 passed`.
- `uv run pytest` داخل `apps/api`: نجح، `42 passed`.
- `npm run lint`: نجح.
- `npm run build`: نجح.
