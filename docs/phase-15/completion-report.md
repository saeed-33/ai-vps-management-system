# تقرير إنجاز المرحلة الخامسة عشرة: أساس SSH للمراقبة الدورية

## الحالة

مكتملة كأساس داخلي للوكيل.

## ما تم تنفيذه

- إضافة `asyncssh` إلى `apps/agent`.
- إضافة `SshServerAccess`.
- إضافة `SshCommandClient`.
- إضافة `CommandPolicy`.
- إضافة baseline tool registry.
- إضافة parsers لمخرجات أدوات baseline.
- إضافة `SshBaselineCollector`.
- إضافة `HybridBaselineCollector` لاختيار SSH عند توفر الإعدادات والرجوع إلى fixture عند غيابها.
- إضافة إعدادات SSH مؤقتة للـ foundation server عبر `.env`.
- إضافة اختبارات للأمان والـ parsers ونموذج SSH.

## الملفات الرئيسية

- `apps/agent/src/ai_vps_agent/server_access/models.py`
- `apps/agent/src/ai_vps_agent/server_access/command_policy.py`
- `apps/agent/src/ai_vps_agent/server_access/ssh_client.py`
- `apps/agent/src/ai_vps_agent/tools/registry.py`
- `apps/agent/src/ai_vps_agent/tools/parsers.py`
- `apps/agent/src/ai_vps_agent/periodic_monitoring/collectors.py`
- `apps/agent/tests/test_command_policy.py`
- `apps/agent/tests/test_baseline_parsers.py`
- `apps/agent/tests/test_ssh_models.py`

## ملاحظات

- لا تزال الواجهة تستخدم fixture collector افتراضيا.
- يمكن تفعيل SSH مؤقتا عبر `.env` للـ foundation server.
- إدارة credentials من لوحة الإدارة ما زالت مرحلة لاحقة.
- لا يوجد تحليل أو حلول أو تشغيل وكلاء متخصصين.

## التحقق

- `uv run --extra dev pytest` داخل `apps/agent`: نجح، `7 passed`.
- `uv run pytest` داخل `apps/api`: نجح، `39 passed`.
- `uv run python -m compileall src` داخل `apps/agent`: نجح.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint`: نجح.
- `npm run build`: نجح.
