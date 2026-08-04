# الأدوات والحلول المسموحة

## القاعدة العامة

```text
Default: deny all execution
```

الأدوات والحلول غير مسموحة افتراضيا. يضيف المطور لاحقا ما يسمح به صراحة.

## أنواع الأدوات

```text
readonly
sandbox
execution
notification
```

## مثال أداة read-only

```yaml
id: df
name: Disk Free
type: readonly
command_template: df {{flags}}
allowed_flags:
  - -h
  - -P
requires_approval: false
```

## مثال حل مسموح مستقبلا

```yaml
id: cleanup-old-logs
name: Cleanup old logs
status: draft
risk_level: medium
allowed_servers:
  - group: staging
required_tools:
  - find
  - rm
requires_approval: true
requires_sandbox: true
pre_checks:
  - check_disk_usage
commands:
  - find /var/log -type f -name "*.log.*" -mtime +30 -delete
post_checks:
  - check_disk_usage
rollback:
  available: false
  reason: deleted files cannot be restored unless backups exist
```

## MVP

في النسخة الأولى:

- يسمح بأدوات read-only فقط.
- تسجل الحلول المقترحة.
- لا ينفذ أي حل على السيرفر الحقيقي.
- يمكن تجهيز schema للحلول المسموحة بدون تفعيل التنفيذ.
