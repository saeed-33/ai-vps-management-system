# خطة المرحلة الخامسة عشرة: أساس SSH للمراقبة الدورية

## الهدف

إضافة أساس اتصال SSH داخل الوكيل حتى يصبح الانتقال من fixture collector إلى قياسات حقيقية ممكنا، مع الحفاظ على نطاق تقارير المراقبة الدورية فقط.

## النطاق

- إضافة `asyncssh` إلى حزمة الوكيل.
- إضافة نماذج SSH access.
- إضافة SSH command client.
- إضافة command policy يمنع الأدوات غير المعرفة والأوامر mutating.
- إضافة registry لأدوات baseline read-only.
- إضافة parsers لمخرجات `uptime` و`free -m` و`df -P -T` و`systemctl --failed --no-pager`.
- إضافة `SshBaselineCollector`.
- إضافة اختبارات policy/parsers/models.

## خارج النطاق

- ربط credentials من لوحة الإدارة.
- تشغيل SSH فعلي من الواجهة.
- حفظ credentials في قاعدة البيانات.
- تحليل مشكلات.
- تشغيل وكلاء متخصصين.
- حلول أو sandbox execution.

## الأدوات المسموحة في هذه المرحلة

```text
uptime
free -m
df -P -T
systemctl --failed --no-pager
```

## معيار الأمان

- لا يتم قبول أمر حر.
- كل أمر يجب أن يأتي من registry.
- كل أداة baseline read-only.
- يتم رفض أوامر مثل restart/stop/start/rm/reboot.
- يوجد timeout وmax output size في SSH access model.
