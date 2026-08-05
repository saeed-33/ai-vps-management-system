# جاهزية Scheduler المراقبة الدورية

## القرار

تم وضع scheduler داخل عملية Backend API مؤقتا، بينما جمع التقرير نفسه يتم عبر `PeriodicMonitoringAgent` داخل `apps/agent`. هذا مناسب للمرحلة الحالية لأنه يثبت العقد وسلوك التكرار بدون إدخال worker مستقل أو queue قبل أوانها.

## السلوك

```text
1. المستخدم يستدعي start scheduler.
2. API يشغل دورة مراقبة مباشرة عبر `PeriodicMonitoringAgent`.
3. الوكيل ينشئ Server Sub-Agent لكل سيرفر وينتج التقارير.
4. API يحفظ تقرير الدورة في الذاكرة.
5. scheduler ينتظر interval_seconds.
6. scheduler يشغل دورة جديدة.
7. المستخدم يستطيع قراءة status أو إيقاف scheduler.
```

## حالة Scheduler

الـ status يحتوي:

- `enabled`
- `interval_seconds`
- `started_at`
- `last_run_at`
- `next_run_at`
- `runs_count`
- `last_error`

## حدود التصميم الحالي

- scheduler يعمل داخل نفس process الخاص بالـ API، لكنه يستدعي حزمة الوكيل.
- عند إعادة تشغيل API تضيع حالة scheduler والتقارير المؤقتة.
- هذا ليس بديلا نهائيا عن worker مستقل.
- مناسب الآن لأن الهدف إنتاج التقارير فقط قبل التحليل والتخزين الدائم.

## الترقية اللاحقة

عند ربط PostgreSQL والـ worker، ينتقل scheduler إلى:

```text
apps/worker
```

وتصبح التقارير محفوظة في:

```text
monitoring_cycles
periodic_monitoring_reports
monitoring_metrics
```
