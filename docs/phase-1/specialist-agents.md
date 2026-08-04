# الوكلاء المتخصصون

## التعريف

الوكيل المتخصص هو وحدة مراقبة وتحليل لمجال محدد. لا يعمل دائما في كل دورة مراقبة، بل يتم استدعاؤه عند الحاجة بناء على نتائج التحليل الأولي أو قواعد ملفات المراقبة.

أمثلة:

- `disk-health-specialist`
- `memory-health-specialist`
- `network-health-specialist`
- `service-health-specialist`
- `nginx-health-specialist`
- `docker-health-specialist`
- `postgres-health-specialist`
- `security-baseline-specialist`

## إدارة الوكلاء من لوحة الإدارة

يجب أن تسمح لوحة الإدارة بتعريف وكلاء متخصصين جدد بدون تعديل مباشر على كود النظام في كل مرة.

الحد الأدنى لتعريف وكيل متخصص:

```yaml
id: nginx-health-specialist
name: Nginx Health Specialist
domain: nginx
version: 1
status: active

description: Analyze Nginx availability, configuration, logs, ports, and traffic behavior.

allowed_tools:
  - systemctl_status
  - journalctl
  - nginx_test_config
  - ss
  - tail_readonly

input_metrics:
  - process_count
  - listening_ports
  - nginx_error_rate
  - request_rate

triggers:
  - expected_process_missing
  - traffic_unexpectedly_zero
  - nginx_error_rate_high

output_schema:
  status:
    enum:
      - no_issue
      - suspected_issue
      - confirmed_issue
      - needs_human_review
  severity:
    enum:
      - info
      - warning
      - critical
  required_evidence: true

execution_policy:
  mode: read_only
  allow_sandbox: true
  allow_production_execution: false
```

## ما يمكن تعديله من لوحة الإدارة

- اسم الوكيل ووصفه.
- المجال.
- الأدوات المسموحة له.
- قواعد التشغيل triggers.
- أنواع القيم التي يستقبلها.
- شكل المخرجات المتوقع.
- صلاحياته.
- هل يسمح له باستخدام sandbox.
- هل يسمح له باقتراح حلول.
- حالة الوكيل: draft, active, disabled.

## قيود مهمة

- تعريف وكيل جديد لا يعني منحه صلاحيات تنفيذ.
- كل أداة يستخدمها يجب أن تكون موجودة في `allowed-tools`.
- كل تشغيل لوكيل متخصص يجب أن يسجل في audit logs.
- كل نسخة من الوكيل يجب أن تكون versioned.
- تعطيل وكيل يجب ألا يحذف تاريخه أو تقاريره السابقة.

## علاقة الوكيل المتخصص بملفات المراقبة

ملفات المراقبة تحدد متى نحتاج وكيلا متخصصا. الوكيل المتخصص يحدد كيف سيتم التعمق في المجال.

```text
Monitoring Profile Rule
        |
        | triggers
        v
Specialist Agent
        |
        | produces
        v
Specialist Analysis Result
```
