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

- `FixtureBaselineCollector` ما زال الافتراضي.
- `SshBaselineCollector` موجود وجاهز للاستخدام البرمجي.
- لوحة الإدارة لا تمرر credentials بعد.
- لا يوجد تشغيل SSH فعلي من الواجهة حتى يتم بناء إدارة credentials.

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
