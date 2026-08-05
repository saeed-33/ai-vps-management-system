# جاهزية Scheduler المراقبة الدورية

## القرار

تم وضع scheduler داخل عملية Backend API مؤقتا. هذا مناسب للمرحلة الحالية لأنه يثبت العقد وسلوك التكرار بدون إدخال worker مستقل أو queue قبل أوانها.

## السلوك

```text
1. المستخدم يستدعي start scheduler.
2. API يشغل دورة مراقبة مباشرة.
3. API يحفظ تقرير الدورة في الذاكرة.
4. scheduler ينتظر interval_seconds.
5. scheduler يشغل دورة جديدة.
6. المستخدم يستطيع قراءة status أو إيقاف scheduler.
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

- scheduler يعمل داخل نفس process الخاص بالـ API.
- عند إعادة تشغيل API تضيع حالة scheduler والتقارير المؤقتة.
- هذا ليس بديلا نهائيا عن worker مستقل.
- مناسب الآن لأن الهدف إنتاج التقارير فقط قبل التحليل والتخزين الدائم.

## الترقية اللاحقة

عند ربط PostgreSQL والـ worker، ينتقل scheduler إلى:

```text
apps/worker أو apps/agent
```

وتصبح التقارير محفوظة في:

```text
monitoring_cycles
periodic_monitoring_reports
monitoring_metrics
```
