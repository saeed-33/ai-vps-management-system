# نموذج الصلاحيات

## أنواع الصلاحيات

يوجد ثلاث دوائر صلاحيات منفصلة:

- صلاحيات المستخدمين.
- صلاحيات الوكيل.
- صلاحيات الأدوات والحلول.

لا يكفي أن يكون المستخدم مسموحا له بطلب إجراء. يجب أيضا أن يكون الوكيل مسموحا له، والأداة مسموحة، والحل مسموح، والسيرفر ضمن النطاق.

## أدوار المستخدمين المقترحة

```text
owner
admin
operator
viewer
auditor
```

## صلاحيات الوكيل

```text
agent.read_metrics
agent.read_logs
agent.create_issue
agent.create_report
agent.suggest_solution
agent.run_sandbox
agent.request_approval
agent.execute_approved_solution
```

في MVP تعطى الصلاحيات التالية فقط:

```text
agent.read_metrics
agent.read_logs
agent.create_issue
agent.create_report
agent.suggest_solution
```

## قرار التنفيذ

```text
can_execute =
  user_has_permission &&
  agent_has_permission &&
  server_in_scope &&
  tool_is_allowed &&
  solution_is_allowed &&
  approval_is_valid
```

## حالات القرار

```text
deny
allow_readonly
allow_sandbox
requires_approval
allow_execution
```

## Audit Log

كل عملية حساسة يجب أن تسجل:

- المستخدم.
- الوكيل أو الخدمة.
- نوع العملية.
- المورد.
- الحالة قبل وبعد.
- نتيجة policy engine.
- وقت العملية.
- عنوان IP أو مصدر الطلب.
