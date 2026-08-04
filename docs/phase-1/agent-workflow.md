# سير عمل الوكيل

## الفكرة الأساسية

المراقبة الدورية لا تبدأ بتشغيل كل الوكلاء المتخصصين مباشرة. تبدأ بمراقبة شاملة لكل السيرفرات، مع إنشاء وكيل فرعي مؤقت أو منطقي لكل سيرفر ضمن دورة المراقبة. بعد تسجيل القيم وتحليلها أوليا، يتم تشغيل الوكلاء المتخصصين فقط عند وجود مؤشرات تستدعي التعمق في مجال معين.

## سير المراقبة الدورية الصحيح

```text
1. Worker / Scheduler يبدأ دورة مراقبة دورية.
2. Control Plane يحدد السيرفرات المشمولة بالدورة.
3. Agent Orchestrator ينشئ Server Sub-Agent لكل سيرفر.
4. كل Server Sub-Agent ينفذ مراقبة شاملة read-only للسيرفر.
5. يتم تسجيل القيم الخام والمنظمة ضمن Periodic Monitoring Report.
6. يتم تنفيذ تحليل أولي للقيم المسجلة.
7. إذا ظهرت مؤشرات مشكلة أو سلوك غير طبيعي، يحدد الوكيل المجالات المتأثرة.
8. يتم تشغيل Specialist Agents حسب الحاجة فقط.
9. كل Specialist Agent يجمع قيما تفصيلية إضافية في مجاله.
10. يتم تسجيل نتائج المراقبة المتخصصة.
11. Agent Orchestrator يدمج نتائج المراقبة الشاملة والمتخصصة.
12. يتم إنتاج التحليل النهائي.
13. يتم تحديد النتيجة: مشكلة مؤكدة، تحذير، اشتباه، أو لا توجد مشكلة.
14. عند وجود مشكلة، يبحث الوكيل عن حل إن أمكن.
15. يتم اختبار أو محاكاة الحل في Sandbox عند الإمكان.
16. يتم عرض المشكلة والتحليل والحل ونتيجة sandbox على المستخدم.
```

## مخرجات دورة المراقبة

```json
{
  "cycle_id": "cycle_2026_08_04_001",
  "status": "completed",
  "servers_checked": 12,
  "servers_with_findings": 2,
  "periodic_reports": [],
  "issues_created": [],
  "specialist_runs": [],
  "final_summary": "Two servers require review"
}
```

## تقرير مراقبة سيرفر واحد

```json
{
  "cycle_id": "cycle_2026_08_04_001",
  "server_id": "srv_001",
  "baseline_metrics": {
    "cpu": {},
    "memory": {},
    "disk": {},
    "network": {},
    "services": {},
    "security": {}
  },
  "initial_analysis": {
    "status": "suspected_issue",
    "signals": [
      {
        "domain": "services",
        "reason": "Expected service has no active process"
      }
    ],
    "required_specialists": ["service-health-specialist"]
  },
  "specialist_results": [],
  "final_analysis": {
    "status": "confirmed_issue",
    "severity": "critical",
    "issue_type": "service_down",
    "evidence": [],
    "recommended_solution": null,
    "sandbox_result": null,
    "present_to_user": true
  }
}
```

## الحالات النهائية

```text
no_issue
suspected_issue
warning
confirmed_issue
critical_issue
needs_human_review
```

## حدود الوكيل في MVP

- لا تنفيذ فعلي على السيرفر الحقيقي.
- لا تعديل ملفات.
- لا restart للخدمات.
- لا حذف ملفات.
- لا أوامر Telegram تنفيذية.
- لا تجاوز لقائمة الأدوات.
- الحلول تعرض على المستخدم بعد تحليلها وتجربتها في sandbox عند الإمكان.
