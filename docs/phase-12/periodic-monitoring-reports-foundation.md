# أساس تقارير المراقبة الدورية

## القرار

تم تنفيذ المراقبة الدورية كقدرة collection/reporting فقط داخل حزمة الوكيل `apps/agent`. هذا يفصل جمع البيانات عن التحليل، لأن التحليل وتشغيل الوكلاء المتخصصين يجب أن يبنيا فوق تقارير مستقرة وواضحة.

## سير العمل الحالي

```text
1. المستخدم أو النظام يستدعي POST /periodic-monitoring/cycles.
2. الخدمة تحدد السيرفرات النشطة من fixture السيرفرات الحالي.
3. Control Plane يستدعي `PeriodicMonitoringAgent` من `apps/agent`.
4. الوكيل ينشئ Server Sub-Agent منطقي لكل سيرفر نشط.
5. الوكيل الفرعي يجمع baseline metrics من fixture read-only.
6. يتم إنتاج ServerSubAgentReport.
7. يتم تجميع التقارير داخل PeriodicMonitoringCycleReport.
8. تحفظ آخر الدورات مؤقتا في ذاكرة عملية API.
```

## البنية

```text
apps/api/src/control_plane_api/
  schemas/periodic_monitoring.py
  modules/periodic_monitoring/service.py
  api/routes/periodic_monitoring.py

apps/agent/src/ai_vps_agent/
  periodic_monitoring/models.py
  periodic_monitoring/collectors.py
  periodic_monitoring/server_sub_agent.py
  periodic_monitoring/orchestrator.py

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
- collector الحالي fixture وليس SSH أو قياسات حقيقية.
- لا يوجد scheduler دائم.
- لا يوجد تحليل مشكلات.
- لا يوجد تشغيل وكلاء متخصصين.
- لا يوجد تنفيذ حلول.
