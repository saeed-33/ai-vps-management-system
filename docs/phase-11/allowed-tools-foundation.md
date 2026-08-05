# أساس الأدوات المسموحة

## القرار

تم تعريف الأدوات المسموحة كعقود قراءة وتحليل، وليس كأوامر تنفيذ مباشرة. هذا يثبت حدود ما يمكن للوكيل طلبه لاحقا بدون فتح باب التنفيذ على السيرفرات.

## البنية

```text
apps/api/src/control_plane_api/
  schemas/allowed_tools.py
  modules/allowed_tools/service.py
  api/routes/allowed_tools.py

apps/admin-panel/src/
  app/allowed-tools/page.tsx
  features/allowed-tools/components/allowed-tools-view.tsx
  lib/allowed-tools-client.ts
```

## نموذج الأداة

كل أداة تحتوي:

- `id`
- `code`
- `name`
- `category`
- `version`
- `status`
- `execution_scope`
- `read_only`
- `used_by`
- `command_shape`
- `guardrails`
- `output_contract`

## سبب إضافة `tools.read`

إدارة الأدوات الحساسة لا يجب أن تختلط مع عرضها. لذلك تم فصل:

- `tools.read`: مشاهدة الأدوات المسموحة.
- `tools.manage`: إدارة الأدوات لاحقا.

## القيود

- البيانات fixture مؤقتة.
- لا يوجد CRUD.
- لا يوجد تنفيذ أوامر.
- لا يوجد ربط مع sandbox.
- لا يوجد اعتماد حلول.
