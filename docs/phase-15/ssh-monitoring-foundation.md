# أساس SSH للمراقبة الدورية

## القرار

تم بناء طبقة SSH داخل `apps/agent` وليس داخل `apps/api`. السبب أن الوكيل هو المسؤول عن الوصول للسيرفر وجمع القيم، بينما يبقى الـ API مسؤولا عن التحكم والجدولة وعرض النتائج.

## البنية

```text
apps/agent/src/ai_vps_agent/
  server_access/
    models.py
    command_policy.py
    ssh_client.py
  tools/
    registry.py
    parsers.py
  periodic_monitoring/
    collectors.py
```

## التدفق المستهدف

```text
PeriodicMonitoringAgent
  -> ServerSubAgent
  -> SshBaselineCollector
  -> SshCommandClient
  -> CommandPolicy
  -> asyncssh
  -> parsers
  -> AgentMonitoringMetricSample[]
```

## الوضع الحالي

- `HybridBaselineCollector` هو collector المستخدم من الـ API.
- إذا لم يكن للسيرفر إعدادات SSH، يستخدم `FixtureBaselineCollector`.
- إذا كان للسيرفر إعدادات SSH، يستخدم `SshBaselineCollector`.
- `SshBaselineCollector` موجود وجاهز للاستخدام البرمجي.
- إعدادات SSH للـ foundation server تقرأ مؤقتا من متغيرات البيئة.
- لوحة الإدارة لا تدير credentials بعد.

## أدوات baseline

- `uptime`: load averages.
- `free -m`: memory usage.
- `df -P -T`: root disk usage.
- `systemctl --failed --no-pager`: failed systemd units.

## القيود

- لا يوجد known_hosts management نهائي بعد.
- لا يوجد secrets manager.
- لا يوجد SSH integration test بسيرفر حقيقي.
- لا يوجد تنفيذ أوامر mutating.

## إعدادات التطوير المؤقتة

```env
FOUNDATION_SERVER_SSH_ENABLED=false
FOUNDATION_SERVER_SSH_HOST=
FOUNDATION_SERVER_SSH_PORT=22
FOUNDATION_SERVER_SSH_USERNAME=
FOUNDATION_SERVER_SSH_PRIVATE_KEY_PATH=
FOUNDATION_SERVER_SSH_PASSWORD=
```
