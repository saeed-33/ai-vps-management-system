# تقرير إنجاز المرحلة العاشرة: أساس إدارة الوكلاء المتخصصين

## الحالة

مكتملة.

## ما تم تنفيذه

- إضافة نماذج API للوكلاء المتخصصين.
- إضافة خدمة foundation بثلاثة وكلاء:
  - `CPU and Memory Specialist`
  - `Storage Specialist`
  - `Nginx Health Specialist`
- إضافة صلاحية `specialist_agents.read`.
- إضافة endpoints القراءة والملخص والتفاصيل.
- حماية endpoints بصلاحية القراءة.
- إضافة صفحة `/specialist-agents` في لوحة الإدارة.
- تحديث رابط sidebar للوكلاء المتخصصين.
- توثيق المرحلة.

## الملفات الرئيسية

- `apps/api/src/control_plane_api/schemas/specialist_agents.py`
- `apps/api/src/control_plane_api/modules/specialist_agents/service.py`
- `apps/api/src/control_plane_api/api/routes/specialist_agents.py`
- `apps/api/tests/test_specialist_agents.py`
- `apps/admin-panel/src/app/specialist-agents/page.tsx`
- `apps/admin-panel/src/features/specialist-agents/components/specialist-agents-view.tsx`
- `apps/admin-panel/src/lib/specialist-agents-client.ts`

## endpoints

```text
GET /api/v1/specialist-agents
GET /api/v1/specialist-agents/summary
GET /api/v1/specialist-agents/{agent_id}
```

## ملاحظات

- هذه المرحلة تعرف عقود الوكلاء فقط.
- لا يوجد تشغيل فعلي أو ربط مع دورة المراقبة.
- لا يوجد CRUD أو ربط قاعدة بيانات.

## التحقق

- `uv run pytest`: نجح، `29 passed`.
- `uv run python -m compileall src scripts`: نجح.
- `npm run lint`: نجح.
- `npm run build`: نجح.
