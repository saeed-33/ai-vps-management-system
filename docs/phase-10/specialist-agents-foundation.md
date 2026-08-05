# أساس الوكلاء المتخصصين

## القرار

تم تعريف الوكلاء المتخصصين كعقود قابلة للإدارة، وليس كتنفيذ فعلي بعد. هذا يفصل بين تعريف الوكيل وسياسة تشغيله من جهة، وبين orchestration والتنفيذ من جهة أخرى.

## البنية

```text
apps/api/src/control_plane_api/
  schemas/specialist_agents.py
  modules/specialist_agents/service.py
  api/routes/specialist_agents.py

apps/admin-panel/src/
  app/specialist-agents/page.tsx
  features/specialist-agents/components/specialist-agents-view.tsx
  lib/specialist-agents-client.ts
```

## نموذج الوكيل

كل وكيل متخصص يحتوي:

- `id`
- `name`
- `domain`
- `version`
- `status`
- `execution_mode`
- `trigger_profiles`
- `triggers`
- `allowed_tools`
- `analysis_contract`
- `output_contract`

## لماذا صلاحية قراءة مستقلة؟

تمت إضافة `specialist_agents.read` لأن عرض تعريفات الوكلاء لا يجب أن يتطلب صلاحية تعديلهم. هذا مهم لاحقا عند وجود أدوار تشغيلية تستطيع قراءة مسار التحليل بدون القدرة على تغيير تعريفات الوكلاء.

## القيود

- البيانات fixture مؤقتة.
- لا يوجد CRUD.
- لا يوجد تشغيل فعلي للوكلاء.
- لا يوجد تنفيذ أوامر.
- لا يوجد sandbox integration.
