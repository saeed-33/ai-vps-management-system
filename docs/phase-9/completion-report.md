# تقرير إنجاز المرحلة التاسعة: أساس إدارة ملفات المراقبة

## الحالة

مكتملة.

## ما تم تنفيذه

- إضافة نماذج API لملفات المراقبة.
- إضافة خدمة foundation بملفي مراقبة:
  - `Linux Baseline`
  - `Nginx Health`
- إضافة عتبات تفصيلية وملاحظات تفسيرية لكل عتبة.
- إضافة أدوات قراءة مسموحة لكل ملف.
- إضافة endpoints القراءة والملخص والتفاصيل.
- حماية endpoints بصلاحية `monitoring.read`.
- إضافة صفحة `/monitoring-profiles` في لوحة الإدارة.
- تحديث رابط sidebar لملفات المراقبة.
- توثيق المرحلة.

## الملفات الرئيسية

- `apps/api/src/control_plane_api/schemas/monitoring_profiles.py`
- `apps/api/src/control_plane_api/modules/monitoring_profiles/service.py`
- `apps/api/src/control_plane_api/api/routes/monitoring_profiles.py`
- `apps/api/tests/test_monitoring_profiles.py`
- `apps/admin-panel/src/app/monitoring-profiles/page.tsx`
- `apps/admin-panel/src/features/monitoring-profiles/components/monitoring-profiles-view.tsx`
- `apps/admin-panel/src/lib/monitoring-profiles-client.ts`

## endpoints

```text
GET /api/v1/monitoring-profiles
GET /api/v1/monitoring-profiles/summary
GET /api/v1/monitoring-profiles/{profile_id}
```

## ملاحظات

- العتبات لا تستخدم كقرار نهائي، بل كإشارات ضمن تحليل أوسع.
- لا يوجد CRUD في هذه المرحلة.
- لا يوجد تشغيل مراقبة فعلي في هذه المرحلة.

## التحقق

- `uv run pytest`: نجح، `24 passed`.
- `uv run python -m compileall src scripts`: نجح.
- `npm run lint`: نجح.
- `npm run build`: نجح.
