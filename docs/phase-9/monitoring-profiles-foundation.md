# أساس ملفات المراقبة

## القرار

تم بناء ملفات المراقبة ككيان مستقل عن دورة المراقبة نفسها. هذا يسمح للوحة الإدارة بعرض التعريفات، العتبات، الأدوات، وملاحظات التحليل قبل تنفيذ أي مراقبة فعلية.

## البنية

```text
apps/api/src/control_plane_api/
  schemas/monitoring_profiles.py
  modules/monitoring_profiles/service.py
  api/routes/monitoring_profiles.py

apps/admin-panel/src/
  app/monitoring-profiles/page.tsx
  features/monitoring-profiles/components/monitoring-profiles-view.tsx
  lib/monitoring-profiles-client.ts
```

## نموذج البيانات في هذه المرحلة

كل ملف مراقبة يحتوي:

- `id`
- `name`
- `domain`
- `version`
- `status`
- `assigned_servers`
- `thresholds`
- `tools`
- `specialist_agents`
- `analysis_guidelines`

## سبب إبقاء البيانات fixture

هذه المرحلة هدفها تثبيت واجهة العقد بين لوحة الإدارة والـ API. الربط مع PostgreSQL سيأتي في مرحلة لاحقة بعد تثبيت مسارات القراءة والشكل النهائي للبيانات.

## العلاقة مع سير عمل الوكيل

في دورة المراقبة القادمة، سيستخدم الوكيل هذه الملفات لتحديد:

- ما الذي يجب قياسه.
- ما الأدوات المسموحة للقراءة.
- ما العتبات التي تعد إشارات.
- متى يمكن تشغيل وكيل متخصص.

## القيود

- لا يوجد تنفيذ مراقبة.
- لا يوجد تعديل على الملفات.
- لا يوجد sandbox execution.
- لا يوجد ربط مع الوكلاء المتخصصين فعليا بعد.
