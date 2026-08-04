# عقد MCP بين لوحة الإدارة والوكيل

## الهدف

MCP هو طبقة الربط المنظمة بين control plane والوكيل. لا يستخدم لتجاوز الصلاحيات، بل لتطبيقها وتسجيلها.

## أوامر أولية

```text
monitoring.start_cycle
monitoring.run_server_baseline
monitoring.run_specialist_agent
monitoring.submit_metrics
monitoring.submit_analysis
agent.chat
rag.query
report.generate
policy.evaluate
sandbox.test_solution
```

## طلب بدء دورة مراقبة

```json
{
  "request_id": "req_cycle_001",
  "cycle_id": "cycle_2026_08_04_001",
  "server_ids": ["srv_001", "srv_002"],
  "mode": "readonly",
  "requested_by": "scheduler"
}
```

## طلب مراقبة شاملة لسيرفر

```json
{
  "request_id": "req_srv_001",
  "cycle_id": "cycle_2026_08_04_001",
  "server_id": "srv_001",
  "mode": "readonly",
  "monitoring_profiles": [
    "linux-baseline",
    "service-health-baseline"
  ],
  "allowed_tools": ["df", "ps", "ss", "journalctl_readonly"]
}
```

## نتيجة المراقبة الشاملة

```json
{
  "request_id": "req_srv_001",
  "cycle_id": "cycle_2026_08_04_001",
  "server_id": "srv_001",
  "metrics_ref": "storage://monitoring/cycle_2026_08_04_001/srv_001/metrics.json",
  "initial_analysis": {
    "status": "suspected_issue",
    "signals": [],
    "required_specialists": ["nginx-health-specialist"]
  }
}
```

## طلب تشغيل وكيل متخصص

```json
{
  "request_id": "req_specialist_001",
  "cycle_id": "cycle_2026_08_04_001",
  "server_id": "srv_001",
  "specialist_agent_id": "nginx-health-specialist",
  "specialist_agent_version": 1,
  "trigger_reason": "expected_process_missing",
  "mode": "readonly",
  "allowed_tools": ["systemctl_status", "journalctl_readonly", "nginx_test_config", "ss"],
  "input_metrics_ref": "storage://monitoring/cycle_2026_08_04_001/srv_001/metrics.json"
}
```

## نتيجة وكيل متخصص

```json
{
  "request_id": "req_specialist_001",
  "cycle_id": "cycle_2026_08_04_001",
  "server_id": "srv_001",
  "specialist_agent_id": "nginx-health-specialist",
  "status": "confirmed_issue",
  "severity": "critical",
  "metrics_ref": "storage://monitoring/cycle_2026_08_04_001/srv_001/nginx-specialist-metrics.json",
  "analysis": {
    "issue_type": "service_down",
    "evidence": [],
    "recommended_solution": null
  }
}
```

## قيود

- كل request يجب أن يحتوي `request_id`.
- كل دورة مراقبة يجب أن تحتوي `cycle_id`.
- كل أداة يجب أن تكون ضمن `allowed_tools`.
- تشغيل أي وكيل متخصص يجب أن يستخدم نسخة محددة من تعريفه.
- كل نتيجة يجب أن تحفظ raw output أو metrics reference عند الإمكان.
- لا يقبل MCP طلب execution إلا عبر policy decision صالح.
