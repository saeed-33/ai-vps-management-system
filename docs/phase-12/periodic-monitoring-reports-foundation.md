# أساس تقارير المراقبة الدورية

## القرار

تم تنفيذ المراقبة الدورية كقدرة collection/reporting فقط. هذا يفصل جمع البيانات عن التحليل، لأن التحليل وتشغيل الوكلاء المتخصصين يجب أن يبنيا فوق تقارير مستقرة وواضحة.

## سير العمل الحالي

```text
1. المستخدم أو النظام يستدعي POST /periodic-monitoring/cycles.
2. الخدمة تحدد السيرفرات النشطة من fixture السيرفرات الحالي.
3. لكل سيرفر يتم إنشاء Server Sub-Agent منطقي.
4. الوكيل الفرعي يجمع baseline metrics من fixture read-only.
5. يتم إنتاج ServerSubAgentReport.
6. يتم تجميع التقارير داخل PeriodicMonitoringCycleReport.
7. تحفظ آخر الدورات مؤقتا في ذاكرة عملية API.
```

## البنية

```text
apps/api/src/control_plane_api/
  schemas/periodic_monitoring.py
  modules/periodic_monitoring/service.py
  api/routes/periodic_monitoring.py

apps/admin-panel/src/
  app/periodic-monitoring/page.tsx
  features/periodic-monitoring/components/periodic-monitoring-view.tsx
  lib/periodic-monitoring-client.ts
```

## التقرير الناتج

كل تقرير سيرفر يحتوي:

- `sub_agent_id`
- `server_id`
- `server_name`
- `status`
- `started_at`
- `completed_at`
- `monitoring_profiles`
- `metrics`
- `raw_snapshot`
- `collection_summary`

## القيود

- الحفظ مؤقت في memory وليس PostgreSQL.
- البيانات fixture وليست قياسات حقيقية.
- لا يوجد scheduler دائم.
- لا يوجد تحليل مشكلات.
- لا يوجد تشغيل وكلاء متخصصين.
- لا يوجد تنفيذ حلول.
