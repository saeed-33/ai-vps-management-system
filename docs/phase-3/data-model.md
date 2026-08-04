# نموذج البيانات

## الفكرة العامة

قاعدة البيانات تقسم إلى مجموعات منطقية:

- الهوية والصلاحيات.
- السيرفرات والاعتمادات.
- المراقبة الدورية.
- ملفات المراقبة.
- الوكلاء المتخصصون.
- المشكلات والتقارير.
- الأدوات والحلول والتنفيذ.
- RAG والوثائق.
- المحادثة وتيليغرام.
- سجل التدقيق.

## المراقبة الدورية

كل دورة مراقبة تمثلها `monitoring_cycles`.

داخل كل دورة:

- يتم إنشاء تقرير لكل سيرفر في `periodic_monitoring_reports`.
- يتم تسجيل القيم في `monitoring_metrics`.
- إذا احتاج السيرفر تحليلا متخصصا، يتم تسجيل تشغيل الوكيل في `specialist_agent_runs`.
- عند وجود مشكلة، يتم إنشاء سجل في `issues`.

## ملفات المراقبة

`monitoring_profiles` تمثل الهوية العامة للملف.

`monitoring_profile_versions` تحفظ النسخ الفعلية للملف، لأن تعريف ملف المراقبة سيتغير بمرور الوقت.

`monitoring_profile_assignments` تربط ملفات المراقبة بالسيرفرات أو مجموعات السيرفرات.

## الوكلاء المتخصصون

`specialist_agents` تمثل الوكيل المتخصص ككيان قابل للإدارة من لوحة الإدارة.

`specialist_agent_versions` تحفظ تعريف كل نسخة:

- الأدوات المسموحة.
- triggers.
- input metrics.
- output schema.
- صلاحيات sandbox.

`specialist_agent_runs` تحفظ كل تشغيل فعلي للوكيل ضمن دورة مراقبة.

## الأدوات والحلول

الأدوات والحلول لها نسخ مستقلة:

- `allowed_tools`
- `allowed_tool_versions`
- `allowed_solutions`
- `solution_versions`

هذا يسمح بمراجعة وتدقيق أي تغيير قبل السماح به.

## التنفيذ

`execution_requests` لا تعني أن التنفيذ تم. هي طلب تنفيذ أو اختبار أو محاكاة.

`execution_results` تحفظ النتيجة.

في MVP، الطلبات العملية ستكون غالبا:

```text
dry_run
sandbox
```

وليس:

```text
production_execution
```

## RAG

`documents` و`links` تحفظ مصادر المعرفة.

`document_chunks` تحفظ المقاطع المفهرسة، وفيها عمود `embedding` باستخدام pgvector.

الـ embedding dimension مضبوط مبدئيا على `1536`، ويمكن تغييره في migration لاحق حسب نموذج embeddings المختار.
