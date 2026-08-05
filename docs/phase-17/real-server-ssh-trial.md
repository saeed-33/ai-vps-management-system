# تجربة المراقبة مع سيرفر حقيقي

## الخطوات

1. شغل PostgreSQL وطبق migration.
2. شغل Backend API.
3. شغل لوحة الإدارة.
4. سجل الدخول.
5. افتح:

```text
http://127.0.0.1:3000/servers
```

6. احفظ إعدادات SSH للسيرفر foundation:

```text
Host
Port
Username
Private key path أو Password
```

7. افتح:

```text
http://127.0.0.1:3000/periodic-monitoring
```

8. اضغط `تشغيل دورة`.

## ما يحدث

- API يقرأ إعدادات SSH المؤقتة.
- API يمررها إلى `PeriodicMonitoringAgent`.
- `HybridBaselineCollector` يختار `SshBaselineCollector`.
- الوكيل ينفذ أدوات baseline read-only عبر SSH.
- يتم إنتاج تقرير.
- إذا كانت قاعدة البيانات جاهزة، يتم حفظ التقرير والـ metrics.

## الأوامر المستخدمة

```text
uptime
free -m
df -P -T
systemctl --failed --no-pager
```

## قيود التجربة

- لا يوجد test connection منفصل بعد.
- لا يوجد تخزين دائم لإعدادات SSH.
- إذا أعدت تشغيل API تحتاج إعادة حفظ إعدادات SSH من صفحة السيرفرات.
