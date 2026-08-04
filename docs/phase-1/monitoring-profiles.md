# ملفات المراقبة

## التعريف

ملف المراقبة ليس ملف عتبات فقط. هو خطة مراقبة وتحليل سياقي لمجال معين، تحدد ما الذي يجب قياسه، كيف تسجل القيم، كيف تفسر القيم، ومتى يتم استدعاء وكيل متخصص.

العتبات مفيدة، لكنها لا تكفي وحدها. أحيانا تكون القيمة المنخفضة أو الغائبة مؤشرا على مشكلة:

- CPU منخفض جدا لأن الخدمة الأساسية متوقفة.
- Network traffic يساوي صفرا لخدمة يفترض أن تستقبل طلبات.
- عدد العمليات أقل من المتوقع.
- Disk I/O منخفض رغم وجود queue يفترض أنها تعمل.
- عدد الاتصالات منخفض بشكل غير طبيعي.

## أنواع القواعد داخل ملف المراقبة

```text
threshold_rules
absence_rules
trend_rules
baseline_rules
correlation_rules
service_expectation_rules
anomaly_rules
```

## صيغة أولية

```yaml
id: service-health-baseline
name: Service Health Baseline
category: services
version: 1
description: Monitor expected service availability and behavior

scope:
  applies_to:
    - linux

metrics:
  - id: process_count
    source_tool: ps
    parser: process_count_parser

  - id: listening_ports
    source_tool: ss
    parser: listening_ports_parser

  - id: request_rate
    source_tool: nginx_access_log
    parser: request_rate_parser

analysis_rules:
  - id: expected_process_missing
    type: absence_rule
    severity: critical
    condition:
      metric: process_count
      expected_min: 1
      service_name: nginx
    specialist_agents:
      - nginx-health-specialist
      - service-health-specialist

  - id: traffic_unexpectedly_zero
    type: baseline_rule
    severity: warning
    condition:
      metric: request_rate
      compare_to: historical_baseline
      behavior: unexpectedly_low
    specialist_agents:
      - nginx-health-specialist
      - network-health-specialist

execution_policy:
  mode: read_only
  allow_remediation: false
```

## دور ملف المراقبة في سير العمل

ملف المراقبة يستخدم في مرحلتين:

- أثناء المراقبة الشاملة لتحديد القيم التي يجب تسجيلها.
- أثناء التحليل الأولي لتحديد هل نحتاج تشغيل وكلاء متخصصين.

## قواعد مهمة

- كل ملف مراقبة يبدأ بوضع `read_only`.
- كل أداة داخله يجب أن تكون ضمن الأدوات المسموحة.
- كل metric يجب أن ينتج قيمة منظمة قابلة للحفظ.
- كل rule يجب أن يشرح سبب الاشتباه أو المشكلة.
- كل rule يمكن أن يقترح وكلاء متخصصين للتشغيل.
- كل تعديل على ملف مراقبة يحتاج version جديد.

## finding منظم

```json
{
  "profile_id": "service-health-baseline",
  "rule_id": "expected_process_missing",
  "status": "confirmed_issue",
  "severity": "critical",
  "domain": "services",
  "evidence": {
    "service_name": "nginx",
    "expected_min_processes": 1,
    "actual_processes": 0
  },
  "required_specialists": [
    "nginx-health-specialist",
    "service-health-specialist"
  ],
  "message": "Expected nginx process is missing"
}
```
