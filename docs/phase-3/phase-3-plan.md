# المرحلة الثالثة: قاعدة البيانات والنماذج الأساسية

## الهدف

إنشاء الأساس البياني الذي سيعتمد عليه النظام بالكامل قبل بناء API أو لوحة الإدارة أو الوكيل.

هذه المرحلة تركز على:

- مخطط قاعدة البيانات.
- العلاقات الأساسية.
- سجل التدقيق.
- كيانات المراقبة الدورية.
- كيانات الوكلاء المتخصصين.
- كيانات الأدوات والحلول المسموحة.
- كيانات RAG والوثائق.
- إعداد بيئة تطوير محلية لـ PostgreSQL وRedis.

## النطاق

داخل النطاق:

- PostgreSQL schema أولي.
- تفعيل `pgcrypto` لاستخدام UUID.
- تفعيل `pgvector` لاستخدامه لاحقا في RAG.
- Docker Compose للتطوير المحلي.
- توثيق الجداول والمبادئ.

خارج النطاق حاليا:

- بناء API.
- بناء لوحة الإدارة.
- بناء الوكيل.
- ORM نهائي.
- seed data.
- migrations tool نهائي.

## الجداول الأساسية

```text
users
roles
permissions
role_permissions
user_roles

servers
server_groups
server_group_members
server_credentials

monitoring_profiles
monitoring_profile_versions
monitoring_profile_assignments

specialist_agents
specialist_agent_versions
specialist_agent_runs

monitoring_cycles
periodic_monitoring_reports
monitoring_metrics

issues
issue_events
issue_comments

reports
report_items

allowed_tools
allowed_tool_versions
allowed_solutions
solution_versions

execution_requests
execution_results

documents
document_chunks
links

chat_sessions
chat_messages

telegram_chats
telegram_events

agent_permissions
audit_logs
```

## مبادئ التصميم

- استخدام UUID لكل الكيانات الأساسية.
- حفظ التعريفات القابلة للتغيير بنظام versions.
- استخدام JSONB للبيانات التي ستتغير صيغتها كثيرا في البداية.
- عدم حفظ أسرار السيرفرات كنص صريح.
- كل عملية حساسة يجب أن تسجل في `audit_logs`.
- التنفيذ ممنوع افتراضيا، لكن schema يجهز مسار الموافقات والتنفيذ لاحقا.

## معايير الإنجاز

- وجود migration أولي قابل للمراجعة.
- وجود Docker Compose لـ PostgreSQL + Redis.
- وجود توثيق واضح للمخطط.
- تحديث سجل المراحل.
- commit وpush إلى GitHub.
