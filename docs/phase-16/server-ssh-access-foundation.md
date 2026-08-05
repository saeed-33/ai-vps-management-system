# أساس إعدادات SSH للسيرفرات

## القرار

تمت إضافة إعداد SSH access كجزء من إدارة السيرفرات، لكن بشكل مؤقت داخل الذاكرة. الهدف هو إكمال مسار التجربة بين:

```text
Admin Panel -> API -> PeriodicMonitoringAgent -> SSH Collector
```

## نموذج الاستجابة

الـ API يعيد نسخة masked فقط:

```json
{
  "enabled": true,
  "host": "10.0.0.10",
  "port": 22,
  "username": "ubuntu",
  "auth_method": "private_key",
  "has_password": false,
  "private_key_path": "C:/keys/id_rsa"
}
```

لا يتم إرجاع `password`.

## العلاقة مع المراقبة الدورية

عند تشغيل دورة مراقبة:

- إذا كان للسيرفر SSH access مفعّل، يمرره الـ API إلى الوكيل.
- `HybridBaselineCollector` يستخدم `SshBaselineCollector`.
- إذا لم تكن إعدادات SSH مفعلة، يرجع الوكيل إلى fixture collector.

## القيود

- التخزين داخل memory فقط.
- إعدادات SSH تضيع عند إعادة تشغيل API.
- لا يوجد encryption layer بعد.
- لا يوجد SSH connection test endpoint بعد.
