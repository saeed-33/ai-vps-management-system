# وكيل المراقبة الدورية

## القرار

تم فصل منطق المراقبة الدورية إلى حزمة `ai-vps-agent` داخل:

```text
apps/agent
```

بهذا يصبح Backend API هو Control Plane، بينما حزمة الوكيل مسؤولة عن إنشاء دورة المراقبة وتقارير السيرفرات.

## البنية

```text
apps/agent/src/ai_vps_agent/
  periodic_monitoring/
    models.py
    collectors.py
    server_sub_agent.py
    orchestrator.py
```

## المكونات

- `PeriodicMonitoringAgent`: منسق دورة المراقبة الدورية.
- `ServerSubAgent`: وكيل فرعي منطقي لكل سيرفر نشط.
- `FixtureBaselineCollector`: collector read-only مؤقت للتطوير.
- `AgentPeriodicMonitoringCycleReport`: تقرير دورة المراقبة.
- `AgentServerSubAgentReport`: تقرير سيرفر واحد.

## العلاقة مع API

`apps/api` يعتمد على الحزمة المحلية:

```toml
ai-vps-agent = { path = "../agent", editable = true }
```

وعند تشغيل دورة مراقبة، يستدعي:

```text
PeriodicMonitoringAgent.run_cycle(...)
```

ثم يحول مخرجات الوكيل إلى schemas الخاصة بالـ API.

## القيود

- collector الحالي fixture.
- لا يوجد SSH.
- لا يوجد تنفيذ أوامر حقيقية.
- لا يوجد تحليل.
- لا يوجد حفظ دائم.
