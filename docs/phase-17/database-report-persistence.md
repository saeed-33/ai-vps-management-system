# حفظ تقارير المراقبة في قاعدة البيانات

## الجداول المستخدمة

```text
monitoring_cycles
periodic_monitoring_reports
monitoring_metrics
servers
```

## آلية الحفظ

بعد إنتاج `PeriodicMonitoringCycleReport`:

1. يتم إنشاء UUID مستقر من `cycle_id`.
2. يتم حفظ سجل في `monitoring_cycles`.
3. لكل تقرير سيرفر:
   - يتم إنشاء UUID مستقر من `server_id`.
   - يتم upsert للسيرفر في جدول `servers`.
   - يتم حفظ تقرير في `periodic_monitoring_reports`.
   - يتم حفظ كل metric في `monitoring_metrics`.

## لماذا UUID مستقر؟

الـ foundation الحالي يستخدم IDs نصية مثل:

```text
srv-foundation-001
cycle-...
```

بينما مخطط PostgreSQL يستخدم UUID. لذلك نستخدم UUID v5 مستقر حتى يمكن إعادة توليد نفس UUID من نفس المفتاح النصي.

## fallback

إذا كانت `DATABASE_URL` غير مضبوطة أو قاعدة البيانات غير متاحة، لا تفشل دورة المراقبة. يتم حفظ التقرير في ذاكرة API وتسجيل سبب فشل persistence داخل حالة scheduler عند الحاجة.

## القيود

- لا يتم قراءة التقارير من قاعدة البيانات بعد.
- لا توجد pagination.
- لا يوجد retention policy.
- لا يوجد تشفير credentials.
