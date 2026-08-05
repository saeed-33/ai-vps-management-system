# سجل المراحل

هذا الملف يوثق العمل المطلوب وما تم إنجازه في كل مرحلة.

## المرحلة الثلاثون: تحليل التقارير عبر LLM حصرا

الحالة: مكتملة.

العمل المطلوب:

- جعل LLM هو المصدر الوحيد للتحليل النهائي.
- إبقاء قواعد العتبات كإشارات داخلية للـ prompt فقط.
- منع fallback إلى تحليل قاعدي نهائي عند فشل LLM.
- تسجيل `analysis_unavailable` أو `analysis_failed` عند عدم إنتاج LLM للتحليل.

ما تم إنجازه:

- تحديث `llm_analysis.py` ليصدر `MonitoringReportAnalysis` مباشرة.
- تحديث خدمة المراقبة الدورية لتخزين نتيجة LLM فقط.
- تحديث الاختبارات لتثبت عدم إصدار rule-based findings كتحليل نهائي عند فشل LLM.
- تحديث `apps/api/README.md`.
- إنشاء `docs/phase-30/phase-30-plan.md`.
- إنشاء `docs/phase-30/completion-report.md`.

التحقق:

- `uv run pytest` داخل `apps/api`: نجح، 52 اختبارا.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.

## المرحلة التاسعة والعشرون: تحسين عرض تقارير التحليل

الحالة: مكتملة.

العمل المطلوب:

- تحسين طريقة عرض تقارير التحليل.
- استبدال grid البطاقات بواجهة قراءة واضحة.
- فصل قائمة التقارير عن تفاصيل التقرير المحدد.
- عرض الخلاصة، LLM، النتائج، والخطوات التالية بشكل مرتب.

ما تم إنجازه:

- إضافة master-detail layout لتقارير التحليل.
- إضافة قائمة تقارير قابلة للاختيار.
- إضافة صفحة تفاصيل للتقرير المحدد.
- إضافة مؤشرات severity في القائمة.
- تحسين CSS responsive.
- إنشاء `docs/phase-29/phase-29-plan.md`.
- إنشاء `docs/phase-29/completion-report.md`.

التحقق:

- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.
- `uv run pytest` داخل `apps/api`: نجح، 52 اختبارا.
- صفحة `/periodic-monitoring`: ترجع 200 محليا.

## المرحلة الثامنة والعشرون: إثراء تحليل التقارير عبر LLM

الحالة: مكتملة.

العمل المطلوب:

- إضافة طبقة LLM اختيارية لتحليل التقارير قبل المحادثة.
- ملاحظة: تم تعديل هذا القرار في المرحلة الثلاثين ليصبح التحليل النهائي عبر LLM حصرا.
- دعم تعطيل LLM افتراضيا.
- دعم Ollama المحلي كمزود أولي.
- حفظ حالة LLM داخل تقرير التحليل.
- ضمان fallback عند فشل LLM.

ما تم إنجازه:

- إضافة إعدادات `LLM_ANALYSIS_*`.
- إضافة `MonitoringLlmEnrichment`.
- إضافة `llm_analysis.py`.
- ربط LLM enrichment بعد التحليل القاعدي.
- عرض حالة LLM في لوحة الإدارة.
- تحديث `.env.example` و`apps/api/README.md`.
- إضافة اختبارات لفشل LLM والـ fallback.
- إنشاء `docs/phase-28/phase-28-plan.md`.
- إنشاء `docs/phase-28/completion-report.md`.

التحقق:

- `uv lock`: نجح.
- `uv run pytest` داخل `apps/api`: نجح، 52 اختبارا.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.
- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.

## المرحلة السابعة والعشرون: تنظيم الواجهة وقواعد SOLID

الحالة: مكتملة.

العمل المطلوب:

- توحيد حالة عدم تسجيل الدخول بحيث تظهر واجهة تسجيل الدخول فقط.
- إزالة تكرار واجهات تسجيل الدخول من الصفحات الداخلية.
- فصل المواضيع المختلفة داخل الصفحات إلى tabs.
- تحسين الالتزام الأساسي بمبادئ SOLID.
- توثيق القاعدة قبل الانتقال إلى المحادثة.

ما تم إنجازه:

- إضافة auth gating مركزي داخل `AppShell`.
- تبسيط صفحة تسجيل الدخول.
- إضافة component عام `Tabs`.
- تحويل صفحة المراقبة الدورية إلى تبويبات.
- تحويل صفحة السيرفرات إلى تبويبات.
- نقل بناء تقارير التحليل المستقلة إلى `analysis_reports.py`.
- إنشاء `docs/phase-27/phase-27-plan.md`.
- إنشاء `docs/phase-27/completion-report.md`.

التحقق:

- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.
- `uv run pytest` داخل `apps/api`: نجح، 51 اختبارا.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.

## المرحلة السادسة والعشرون: تقارير تحليل دورية منفصلة

الحالة: مكتملة.

العمل المطلوب:

- التأكد أن تحليل التقارير الدورية يصدر كتقارير تحليل منفصلة.
- إضافة endpoint مستقل لتقارير التحليل.
- ربط تقرير التحليل بالدورة وتقرير السيرفر الأصلي.
- عرض تقارير التحليل في لوحة الإدارة.
- إضافة اختبار يثبت إصدار تقرير تحليل منفصل بعد تشغيل دورة مراقبة.

ما تم إنجازه:

- إضافة `PeriodicMonitoringAnalysisReport`.
- إضافة `PeriodicMonitoringAnalysisReportsListResponse`.
- إضافة `GET /api/v1/periodic-monitoring/analysis-reports`.
- إضافة projection من دورات المراقبة المحفوظة إلى تقارير تحليل مستقلة.
- تحديث client لوحة الإدارة.
- إضافة قسم `تقارير التحليل` في صفحة المراقبة الدورية.
- تحديث اختبارات API.
- إنشاء `docs/phase-26/phase-26-plan.md`.
- إنشاء `docs/phase-26/completion-report.md`.

التحقق:

- `uv run pytest` داخل `apps/api`: نجح، 51 اختبارا.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.

## المرحلة الخامسة والعشرون: تحليل تقارير مرتبط بملفات المراقبة

الحالة: مكتملة.

العمل المطلوب:

- استخدام تعريفات ملفات المراقبة كمصدر لقواعد التحليل.
- تسجيل ملف المراقبة وملاحظة التفسير داخل كل finding.
- تسجيل فجوات التغطية عندما يتوقع الملف مقاييس غير موجودة في التقرير.
- اقتراح الوكلاء المتخصصين كبيانات تحليل فقط دون تشغيلهم.
- عرض metadata التحليل في لوحة الإدارة.

ما تم إنجازه:

- تحويل التحليل من عتبات ثابتة فقط إلى تحليل يعتمد على `MonitoringProfileDetail`.
- إضافة `profile_id` و`interpretation_note` و`suggested_specialist_agents` إلى findings.
- إضافة `profiles_evaluated` و`suggested_specialist_agents` و`next_actions` إلى analysis.
- إضافة coverage gap informational finding.
- تحديث صفحة المراقبة الدورية لعرض الملفات المقيمة والوكلاء المقترحين والخطوات التالية.
- تحديث اختبارات API.
- إنشاء `docs/phase-25/phase-25-plan.md`.
- إنشاء `docs/phase-25/completion-report.md`.

التحقق:

- `uv run pytest` داخل `apps/api`: نجح، 50 اختبارا.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.

## المرحلة الرابعة والعشرون: تحليل تقارير المراقبة الدورية

الحالة: مكتملة.

العمل المطلوب:

- إضافة تحليل أولي لكل تقرير مراقبة دورية.
- تخزين التحليل مع تقارير المراقبة في قاعدة البيانات.
- عرض نتيجة التحليل في لوحة الإدارة.
- إزالة ملاحظات التطوير الظاهرة من لوحة الإدارة.
- تحديث الاختبارات والتوثيق.

ما تم إنجازه:

- إضافة schemas للتحليل والنتائج.
- إضافة محلل deterministic داخل Control Plane.
- ربط التحليل بدورة المراقبة بعد جمع القيم.
- حفظ `initial_analysis` و`final_analysis` في PostgreSQL.
- عرض status وseverity وsummary وfindings في صفحة المراقبة الدورية.
- تنظيف نصوص `foundation` و`مؤقت` من واجهات الإدارة الظاهرة للمستخدم.
- تحديث اختبارات API والوكيل.
- إنشاء `docs/phase-24/phase-24-plan.md`.
- إنشاء `docs/phase-24/completion-report.md`.

التحقق:

- `uv run pytest` داخل `apps/api`: نجح، 49 اختبارا.
- `uv run --extra dev pytest` داخل `apps/agent`: نجح، 8 اختبارات.
- `uv run python -m compileall src scripts` داخل `apps/api`: نجح.
- `npm run lint` داخل `apps/admin-panel`: نجح.
- `npm run build` داخل `apps/admin-panel`: نجح.

## المرحلة الأولى: تثبيت النطاق والبنية

الحالة: مكتملة توثيقيا.

العمل المطلوب:

- تحديد بنية النظام.
- تحديد قرار المودل.
- تحديد نموذج الصلاحيات.
- تحديد مفهوم ملفات المراقبة.
- تحديد الوكلاء المتخصصين.
- تحديد سير عمل الوكيل.
- تحديد عقد MCP الأولي.
- تحديد خطة النشر الأولية.

ما تم إنجازه:

- إنشاء وثائق المرحلة الأولى داخل `docs/phase-1`.
- تثبيت قرار عدم استخدام RLHF حاليا.
- تثبيت قرار عدم استخدام مودل متخصص في البداية.
- تعديل سير العمل بحيث يبدأ بمراقبة دورية شاملة لكل السيرفرات.
- تثبيت مفهوم إنشاء `Server Sub-Agent` لكل سيرفر في كل دورة مراقبة.
- تثبيت مفهوم تعريف `Specialist Agents` من لوحة الإدارة.

## المرحلة الثانية: تأسيس المشروع والمستودع

الحالة: مكتملة.

العمل المطلوب:

- إنشاء مجلد مشروع جديد مستقل.
- إنشاء هيكل monorepo أولي.
- نقل وثائق المرحلة الأولى إلى المشروع الجديد.
- إنشاء وثيقة خطة المرحلة الثانية.
- تهيئة Git.
- إنشاء أول commit يوثق بداية المشروع.
- محاولة ربط المشروع مع GitHub.

ما تم إنجازه:

- إنشاء مجلد المشروع `ai-vps-management-system`.
- إنشاء هيكل monorepo أولي.
- نقل وثائق المرحلة الأولى إلى `docs/phase-1`.
- إنشاء وثائق المرحلة الثانية داخل `docs/phase-2`.
- إنشاء `README.md`.
- إنشاء `.gitignore`.
- إنشاء `.gitattributes`.
- إنشاء `.env.example`.
- إنشاء قالب Pull Request أولي.
- تهيئة Git على الفرع `main`.
- إنشاء commit أول:
  - `88e1488 chore: initialize project structure and phase docs`

حالة GitHub:

- GitHub CLI غير مثبت على الجهاز.
- تم تثبيت GitHub plugin داخل Codex.
- تم العثور على المستودع `saeed-33/ai-vps-management-system`.
- أظهر GitHub plugin صلاحيات `admin` و`push` على المستودع.
- تم ربط المستودع المحلي بـ `origin`.
- تم دفع الفرع `main` إلى GitHub.

الرابط:

```text
https://github.com/saeed-33/ai-vps-management-system
```

## المرحلة الثالثة: قاعدة البيانات والنماذج الأساسية

الحالة: مكتملة كملفات تنفيذ وتصميم. تحقق تطبيق migration على قاعدة فعلية مؤجل حتى تشغيل Docker daemon أو تثبيت `psql`.

العمل المطلوب:

- إنشاء مخطط قاعدة البيانات الأساسي.
- تعريف جداول المستخدمين والصلاحيات.
- تعريف جداول السيرفرات.
- تعريف جداول ملفات المراقبة.
- تعريف جداول الوكلاء المتخصصين.
- تعريف جداول المراقبة الدورية وقيمها.
- تعريف جداول المشكلات والتقارير.
- تعريف جداول الأدوات والحلول المسموحة.
- تعريف جداول التنفيذ ونتائجه.
- تعريف جداول RAG والوثائق.
- تعريف جداول المحادثة وتيليغرام.
- تعريف سجل التدقيق.
- إضافة بيئة PostgreSQL وRedis للتطوير.

ما تم إنجازه:

- إنشاء `docs/phase-3/phase-3-plan.md`.
- إنشاء `docs/phase-3/data-model.md`.
- إنشاء `docs/phase-3/database-schema-guide.md`.
- إنشاء `docs/phase-3/docker-guide.md`.
- إنشاء `docs/phase-3/completion-report.md`.
- إنشاء `packages/database/migrations/0001_initial_schema.sql`.
- إنشاء `packages/database/README.md`.
- إنشاء `infra/compose/docker-compose.dev.yml`.
- إنشاء `infra/compose/README.md`.
- تحديث `.env.example`.

التحقق:

- تم التحقق من وجود Docker CLI.
- تم التحقق من صحة صيغة Docker Compose.
- لم يتم تطبيق migration لأن Docker daemon غير شغال و`psql` غير مثبت محليا.

## المرحلة الرابعة: Backend API / Control Plane Foundation

الحالة: مكتملة.

العمل المطلوب:

- إنشاء أساس خدمة API.
- اختيار بنية backend مناسبة.
- إعداد settings مركزي.
- إعداد router structure.
- إضافة health checks.
- تجهيز database readiness.
- إضافة اختبارات smoke.
- توثيق التشغيل المحلي.

ما تم إنجازه:

- إنشاء مشروع FastAPI داخل `apps/api`.
- إنشاء `apps/api/pyproject.toml`.
- إنشاء application factory.
- إضافة `GET /health/live`.
- إضافة `GET /health/ready`.
- إضافة `GET /api/v1/meta`.
- إضافة طبقة database readiness باستخدام SQLAlchemy async.
- إضافة اختبارات smoke.
- إنشاء `docs/phase-4/phase-4-plan.md`.
- إنشاء `docs/phase-4/control-plane-foundation.md`.
- إنشاء `docs/phase-4/completion-report.md`.

التحقق:

- تم تنفيذ `uv sync --extra dev`.
- تم تنفيذ `uv run pytest`.
- النتيجة: `3 passed`.

قرارات معمارية مرتبطة:

- توثيق بنية لوحة الإدارة في `docs/architecture-decisions/adr-001-admin-panel-architecture.md`.
- توثيق بنية Backend / Control Plane في `docs/architecture-decisions/adr-002-backend-architecture.md`.

## المرحلة الخامسة: Admin Panel Foundation

الحالة: مكتملة.

العمل المطلوب:

- إنشاء أساس لوحة الإدارة.
- تطبيق البنية القائمة على الميزات.
- إنشاء layout إداري.
- إنشاء sidebar.
- إنشاء dashboard أولي.
- إنشاء صفحة حالة API.
- إضافة API client.
- تشغيل lint وbuild.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء تطبيق Next.js داخل `apps/admin-panel`.
- إنشاء `apps/admin-panel/package.json`.
- إنشاء `apps/admin-panel/package-lock.json`.
- إنشاء layout وsidebar.
- إنشاء dashboard أولي.
- إنشاء صفحة `api-status`.
- إنشاء `src/lib/api-client.ts`.
- إنشاء `docs/phase-5/phase-5-plan.md`.
- إنشاء `docs/phase-5/admin-panel-foundation.md`.
- إنشاء `docs/phase-5/completion-report.md`.

التحقق:

- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة الرابعة عشرة: Periodic Monitoring Agent Runtime

الحالة: مكتملة.

العمل المطلوب:

- إنشاء حزمة وكيل فعلية داخل `apps/agent`.
- نقل مسؤولية جمع تقارير المراقبة الدورية إلى الوكيل.
- إنشاء `PeriodicMonitoringAgent`.
- إنشاء `ServerSubAgent`.
- إنشاء collector read-only foundation.
- ربط Backend API بحزمة الوكيل.
- إضافة اختبار مباشر للوكيل.
- توثيق التصحيح.

ما تم إنجازه:

- إنشاء `apps/agent/pyproject.toml`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/models.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/collectors.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/server_sub_agent.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/orchestrator.py`.
- إنشاء `apps/agent/tests/test_periodic_monitoring_agent.py`.
- تحديث `apps/api/pyproject.toml`.
- تحديث `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- إنشاء `docs/phase-14/phase-14-plan.md`.
- إنشاء `docs/phase-14/periodic-monitoring-agent-runtime.md`.
- إنشاء `docs/phase-14/completion-report.md`.

التحقق:

- تم تنفيذ `uv run --extra dev pytest` داخل `apps/agent`.
- النتيجة: `1 passed`.
- تم تنفيذ `uv run pytest` داخل `apps/api`.
- النتيجة: `39 passed`.
- تم تنفيذ compileall للوكيل والـ API.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: build passed.

## المرحلة السابعة عشرة: Real Server Monitoring & Report Persistence Foundation

الحالة: مكتملة كأساس أولي.

العمل المطلوب:

- استخدام إعدادات SSH للسيرفرات الحقيقية عند تشغيل دورة المراقبة.
- حفظ دورات المراقبة والتقارير والـ metrics في PostgreSQL.
- إبقاء fallback إلى الذاكرة عند غياب قاعدة البيانات.
- توثيق طريقة التجربة.
- إضافة اختبار للـ UUID mapping.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/modules/periodic_monitoring/persistence.py`.
- تحديث `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- تحديث `apps/api/src/control_plane_api/api/routes/periodic_monitoring.py`.
- تحديث `apps/api/tests/test_periodic_monitoring.py`.
- إنشاء `docs/phase-17/phase-17-plan.md`.
- إنشاء `docs/phase-17/database-report-persistence.md`.
- إنشاء `docs/phase-17/real-server-ssh-trial.md`.
- إنشاء `docs/phase-17/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest` داخل `apps/api`.
- النتيجة: `43 passed`.
- تم تنفيذ `uv run --extra dev pytest` داخل `apps/agent`.
- النتيجة: `7 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: build passed.

ملاحظة البيئة المحلية:

- تم التحقق من توفر Docker Desktop.
- محاولة تشغيل `docker compose -f infra/compose/docker-compose.dev.yml up -d` لم تكتمل ضمن المهلة.
- لم يتم تطبيق migration فعليا في هذه الجلسة.

## المرحلة السادسة عشرة: Server SSH Access Foundation

الحالة: مكتملة كأساس مؤقت.

العمل المطلوب:

- إضافة إعدادات SSH إلى إدارة السيرفرات.
- إضافة endpoint لتحديث SSH access.
- إخفاء كلمة المرور من الاستجابات.
- ربط periodic monitoring بإعدادات SSH المحفوظة.
- إضافة نموذج SSH في لوحة الإدارة.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- تحديث `apps/api/src/control_plane_api/schemas/servers.py`.
- تحديث `apps/api/src/control_plane_api/modules/servers/service.py`.
- تحديث `apps/api/src/control_plane_api/api/routes/servers.py`.
- تحديث `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- تحديث `apps/api/tests/test_servers.py`.
- تحديث `apps/admin-panel/src/features/servers/components/servers-view.tsx`.
- تحديث `apps/admin-panel/src/lib/servers-client.ts`.
- إنشاء `docs/phase-16/phase-16-plan.md`.
- إنشاء `docs/phase-16/server-ssh-access-foundation.md`.
- إنشاء `docs/phase-16/completion-report.md`.

التحقق:

- تم تنفيذ `uv run --extra dev pytest` داخل `apps/agent`.
- النتيجة: `7 passed`.
- تم تنفيذ `uv run pytest` داخل `apps/api`.
- النتيجة: `42 passed`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: build passed.

## المرحلة الخامسة عشرة: SSH Monitoring Foundation

الحالة: مكتملة كأساس داخلي للوكيل.

العمل المطلوب:

- إضافة أساس SSH داخل حزمة الوكيل.
- إضافة policy تمنع الأوامر غير المسموحة أو mutating.
- إضافة registry لأدوات baseline read-only.
- إضافة parsers لمخرجات الأدوات.
- إضافة `SshBaselineCollector`.
- إضافة اختبارات.
- توثيق الحدود.

ما تم إنجازه:

- إنشاء `apps/agent/src/ai_vps_agent/server_access/models.py`.
- إنشاء `apps/agent/src/ai_vps_agent/server_access/command_policy.py`.
- إنشاء `apps/agent/src/ai_vps_agent/server_access/ssh_client.py`.
- إنشاء `apps/agent/src/ai_vps_agent/tools/registry.py`.
- إنشاء `apps/agent/src/ai_vps_agent/tools/parsers.py`.
- تحديث `apps/agent/src/ai_vps_agent/periodic_monitoring/collectors.py`.
- تحديث `apps/api/src/control_plane_api/core/config.py`.
- تحديث `.env.example`.
- إنشاء `apps/agent/tests/test_command_policy.py`.
- إنشاء `apps/agent/tests/test_baseline_parsers.py`.
- إنشاء `apps/agent/tests/test_ssh_models.py`.
- إنشاء `docs/phase-15/phase-15-plan.md`.
- إنشاء `docs/phase-15/ssh-monitoring-foundation.md`.
- إنشاء `docs/phase-15/completion-report.md`.

التحقق:

- تم تنفيذ `uv run --extra dev pytest` داخل `apps/agent`.
- النتيجة: `7 passed`.
- تم تنفيذ `uv run pytest` داخل `apps/api`.
- النتيجة: `39 passed`.
- تم تنفيذ compileall للوكيل والـ API.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: build passed.

## المرحلة الثالثة عشرة: Periodic Monitoring Scheduler Readiness

الحالة: مكتملة.

العمل المطلوب:

- إضافة قدرة جدولة دورات المراقبة الدورية.
- إضافة حزمة وكيل فعلية داخل `apps/agent` للمراقبة الدورية.
- إضافة endpoints تشغيل وإيقاف وحالة scheduler.
- تشغيل دورة أولى مباشرة عند تفعيل scheduler.
- تحديث صفحة المراقبة الدورية للتحكم بالجدولة.
- إضافة اختبارات.
- توثيق حدود النطاق.

ما تم إنجازه:

- تحديث `apps/api/src/control_plane_api/schemas/periodic_monitoring.py`.
- تحديث `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- تحديث `apps/api/src/control_plane_api/api/routes/periodic_monitoring.py`.
- تحديث `apps/api/tests/test_periodic_monitoring.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/orchestrator.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/server_sub_agent.py`.
- إنشاء `apps/agent/src/ai_vps_agent/periodic_monitoring/collectors.py`.
- إنشاء `apps/agent/tests/test_periodic_monitoring_agent.py`.
- تحديث `apps/admin-panel/src/features/periodic-monitoring/components/periodic-monitoring-view.tsx`.
- تحديث `apps/admin-panel/src/lib/periodic-monitoring-client.ts`.
- إنشاء `docs/phase-13/phase-13-plan.md`.
- إنشاء `docs/phase-13/periodic-monitoring-scheduler-readiness.md`.
- إنشاء `docs/phase-13/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `39 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة الثانية عشرة: Periodic Monitoring Reports Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة قدرة تشغيل دورة مراقبة دورية.
- إنشاء Server Sub-Agent منطقي لكل سيرفر نشط.
- إنتاج تقرير مراقبة دوري لكل سيرفر.
- إضافة endpoints لتشغيل وعرض الدورات والتقارير.
- إضافة صفحة المراقبة الدورية في لوحة الإدارة.
- ضمان أن المرحلة تنتج تقارير فقط بدون تحليل أو حلول.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/periodic_monitoring.py`.
- إنشاء `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/periodic_monitoring.py`.
- إنشاء `apps/api/tests/test_periodic_monitoring.py`.
- إنشاء `apps/admin-panel/src/app/periodic-monitoring/page.tsx`.
- إنشاء `apps/admin-panel/src/features/periodic-monitoring/components/periodic-monitoring-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/periodic-monitoring-client.ts`.
- إنشاء `docs/phase-12/phase-12-plan.md`.
- إنشاء `docs/phase-12/periodic-monitoring-reports-foundation.md`.
- إنشاء `docs/phase-12/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `38 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة الحادية عشرة: Allowed Tools Management Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة أساس API لإدارة الأدوات المسموحة.
- إضافة endpoints لقائمة الأدوات وملخصها وتفاصيل أداة واحدة.
- إضافة صلاحية قراءة مستقلة `tools.read`.
- حماية endpoints بصلاحية القراءة.
- إضافة صفحة الأدوات المسموحة في لوحة الإدارة.
- ربط صفحة الأدوات المسموحة بعميل API.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/allowed_tools.py`.
- إنشاء `apps/api/src/control_plane_api/modules/allowed_tools/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/allowed_tools.py`.
- إنشاء `apps/api/tests/test_allowed_tools.py`.
- إنشاء `apps/admin-panel/src/app/allowed-tools/page.tsx`.
- إنشاء `apps/admin-panel/src/features/allowed-tools/components/allowed-tools-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/allowed-tools-client.ts`.
- إنشاء `docs/phase-11/phase-11-plan.md`.
- إنشاء `docs/phase-11/allowed-tools-foundation.md`.
- إنشاء `docs/phase-11/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `34 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة العاشرة: Specialist Agents Management Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة أساس API لإدارة الوكلاء المتخصصين.
- إضافة endpoints لقائمة الوكلاء وملخصهم وتفاصيل وكيل واحد.
- إضافة صلاحية قراءة مستقلة `specialist_agents.read`.
- حماية endpoints بصلاحية القراءة.
- إضافة صفحة الوكلاء المتخصصين في لوحة الإدارة.
- ربط صفحة الوكلاء المتخصصين بعميل API.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/specialist_agents.py`.
- إنشاء `apps/api/src/control_plane_api/modules/specialist_agents/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/specialist_agents.py`.
- إنشاء `apps/api/tests/test_specialist_agents.py`.
- إنشاء `apps/admin-panel/src/app/specialist-agents/page.tsx`.
- إنشاء `apps/admin-panel/src/features/specialist-agents/components/specialist-agents-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/specialist-agents-client.ts`.
- إنشاء `docs/phase-10/phase-10-plan.md`.
- إنشاء `docs/phase-10/specialist-agents-foundation.md`.
- إنشاء `docs/phase-10/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `29 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة التاسعة: Monitoring Profiles Management Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة أساس API لإدارة ملفات المراقبة.
- إضافة endpoints لقائمة ملفات المراقبة وملخصها وتفاصيل ملف واحد.
- حماية endpoints بصلاحية `monitoring.read`.
- إضافة صفحة ملفات المراقبة في لوحة الإدارة.
- ربط صفحة ملفات المراقبة بعميل API.
- إضافة عتبات وملاحظات تحليلية ضمن fixture مفصل.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/monitoring_profiles.py`.
- إنشاء `apps/api/src/control_plane_api/modules/monitoring_profiles/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/monitoring_profiles.py`.
- إنشاء `apps/api/tests/test_monitoring_profiles.py`.
- إنشاء `apps/admin-panel/src/app/monitoring-profiles/page.tsx`.
- إنشاء `apps/admin-panel/src/features/monitoring-profiles/components/monitoring-profiles-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/monitoring-profiles-client.ts`.
- إنشاء `docs/phase-9/phase-9-plan.md`.
- إنشاء `docs/phase-9/monitoring-profiles-foundation.md`.
- إنشاء `docs/phase-9/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `24 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة السابعة: Users & Roles Management Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة Users API foundation.
- إضافة Roles summary endpoint.
- حماية endpoints بالـ bearer token.
- إضافة صفحة المستخدمين في لوحة الإدارة.
- إضافة users client.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/users.py`.
- إنشاء `apps/api/src/control_plane_api/modules/users/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/users.py`.
- إنشاء `apps/api/tests/test_users.py`.
- إنشاء `apps/admin-panel/src/app/users/page.tsx`.
- إنشاء `apps/admin-panel/src/features/users/components/users-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/users-client.ts`.
- إنشاء `docs/phase-7/phase-7-plan.md`.
- إنشاء `docs/phase-7/users-roles-foundation.md`.
- إنشاء `docs/phase-7/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `14 passed`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة السادسة: Auth & RBAC Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة أساس مصادقة في Backend API.
- إضافة hashing لكلمات المرور.
- إضافة JWT access tokens.
- إضافة bootstrap admin login.
- إضافة RBAC catalog أولي.
- إضافة routes للمصادقة.
- إضافة اختبارات.
- إضافة صفحة login أولية في لوحة الإدارة.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/core/security.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/auth.py`.
- إنشاء `apps/api/src/control_plane_api/schemas/auth.py`.
- إنشاء `apps/api/src/control_plane_api/modules/auth/rbac.py`.
- إنشاء `apps/api/scripts/hash_password.py`.
- إنشاء `apps/api/tests/test_auth.py`.
- إنشاء `apps/admin-panel/src/app/login/page.tsx`.
- إنشاء `apps/admin-panel/src/features/auth/components/login-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/auth-client.ts`.
- إنشاء `docs/phase-6/phase-6-plan.md`.
- إنشاء `docs/phase-6/auth-rbac-foundation.md`.
- إنشاء `docs/phase-6/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `10 passed`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.

## المرحلة الثامنة: Servers Management Foundation

الحالة: مكتملة.

العمل المطلوب:

- إضافة أساس API لإدارة السيرفرات.
- إضافة endpoints لقائمة السيرفرات وملخصها وتفاصيل سيرفر واحد.
- حماية endpoints السيرفرات بالمصادقة وصلاحية `servers.read`.
- إضافة صفحة السيرفرات في لوحة الإدارة.
- ربط صفحة السيرفرات بعميل API.
- تحديث لوحة المعلومات لتعكس fixture السيرفرات الحالية.
- إضافة اختبارات.
- توثيق المرحلة.

ما تم إنجازه:

- إنشاء `apps/api/src/control_plane_api/schemas/servers.py`.
- إنشاء `apps/api/src/control_plane_api/modules/servers/service.py`.
- إنشاء `apps/api/src/control_plane_api/api/routes/servers.py`.
- إنشاء `apps/api/tests/test_servers.py`.
- إنشاء `apps/admin-panel/src/app/servers/page.tsx`.
- إنشاء `apps/admin-panel/src/features/servers/components/servers-view.tsx`.
- إنشاء `apps/admin-panel/src/lib/servers-client.ts`.
- إنشاء `docs/phase-8/phase-8-plan.md`.
- إنشاء `docs/phase-8/servers-foundation.md`.
- إنشاء `docs/phase-8/completion-report.md`.

التحقق:

- تم تنفيذ `uv run pytest`.
- النتيجة: `19 passed`.
- تم تنفيذ `uv run python -m compileall src scripts`.
- تم تنفيذ `npm run lint`.
- تم تنفيذ `npm run build`.
- النتيجة: lint passed وbuild passed.
## Phase 23: Periodic Monitoring UX Improvement

Status: completed.

Required work:

- Improve cycle selection.
- Improve scheduler status and controls.
- Display reports as server cards.
- Display metrics as compact metric cards.
- Highlight failed reports.

Completed work:

- Rebuilt `apps/admin-panel/src/features/periodic-monitoring/components/periodic-monitoring-view.tsx`.
- Updated `apps/admin-panel/src/app/globals.css`.
- Created `docs/phase-23`.

Verification:

- `npm run lint`: passed.
- `npm run build`: passed.

## Phase 22: Periodic Monitoring Server UUID Persistence Fix

Status: completed.

Required work:

- Fix duplicate server insertion when persisting monitoring reports for database-backed servers.
- Preserve real UUID server ids.
- Keep stable UUID mapping for text fixture ids.

Completed work:

- Updated `apps/api/src/control_plane_api/modules/periodic_monitoring/persistence.py`.
- Updated `apps/api/tests/test_periodic_monitoring.py`.
- Created `docs/phase-22`.

Verification:

- `uv run pytest` in `apps/api`: `48 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `GET /health/ready`: ready.

## Phase 21: Server Management UX Improvement

Status: completed.

Required work:

- Improve the add-server form.
- Show database vs memory persistence source.
- Make selected server state clear.
- Improve SSH setup and test feedback.
- Surface backend API error details in the UI.

Completed work:

- Rebuilt `apps/admin-panel/src/features/servers/components/servers-view.tsx`.
- Updated `apps/admin-panel/src/lib/servers-client.ts`.
- Updated `apps/admin-panel/src/app/globals.css`.
- Created `docs/phase-21`.

Verification:

- `npm run lint`: passed.
- `npm run build`: passed.

## Phase 20: Database Persistence Enforcement

Status: completed.

Required work:

- Diagnose why added servers disappeared after backend restart.
- Run the project PostgreSQL database and apply migration.
- Point the API to the project database.
- Prevent silent memory fallback when `DATABASE_URL` is configured.
- Show persistence source in the admin panel.

Completed work:

- Started `ai-vps-postgres-dev` on host port `55432`.
- Applied `packages/database/migrations/0001_initial_schema.sql`.
- Updated local API database URL to `localhost:55432`.
- Updated server routes to return `503` if configured DB persistence fails.
- Updated routes to use app-scoped settings.
- Updated `/servers` to show `source`.
- Created `docs/phase-20`.

Verification:

- `uv run pytest` in `apps/api`: `47 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint`: passed.
- `GET /health/ready`: ready.

## Phase 19: Periodic Monitoring Report Visibility Completion

Status: completed.

Required work:

- Show all periodic monitoring cycles in the admin panel.
- Show all server reports for each cycle.
- Show all metrics for each server report.
- Preserve failed server reports when collection fails.
- Keep the scope before report analysis.

Completed work:

- Updated `apps/admin-panel/src/features/periodic-monitoring/components/periodic-monitoring-view.tsx`.
- Updated `apps/admin-panel/src/lib/periodic-monitoring-client.ts`.
- Updated `apps/agent/src/ai_vps_agent/periodic_monitoring/server_sub_agent.py`.
- Updated `apps/agent/tests/test_periodic_monitoring_agent.py`.
- Created `docs/phase-19`.

Verification:

- `uv run --extra dev pytest` in `apps/agent`: `8 passed`.
- `uv run pytest` in `apps/api`: `47 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint`: passed.
- `npm run build`: passed.

## Phase 18: Periodic Monitoring Readiness Completion

Status: completed as a practical foundation.

Required work:

- Make server management database-aware.
- Keep memory fallback when PostgreSQL is unavailable.
- Add create/update server API.
- Persist SSH access through `server_credentials` when PostgreSQL is available.
- Add SSH connection test endpoint.
- Make periodic monitoring read active servers from the server service.
- Load periodic monitoring reports from PostgreSQL when available.
- Update the admin panel server screen.
- Add tests and documentation.

Completed work:

- Updated `apps/api/src/control_plane_api/modules/servers/service.py`.
- Updated `apps/api/src/control_plane_api/api/routes/servers.py`.
- Updated `apps/api/src/control_plane_api/schemas/servers.py`.
- Updated `apps/api/src/control_plane_api/modules/periodic_monitoring/service.py`.
- Updated `apps/api/src/control_plane_api/modules/periodic_monitoring/persistence.py`.
- Updated `apps/agent/src/ai_vps_agent/server_access/ssh_client.py`.
- Updated `apps/admin-panel/src/lib/servers-client.ts`.
- Rebuilt `apps/admin-panel/src/features/servers/components/servers-view.tsx`.
- Updated `apps/api/tests/test_servers.py`.
- Created `docs/phase-18`.

Verification:

- `uv run pytest` in `apps/api`: `47 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `uv run --extra dev pytest` in `apps/agent`: `7 passed`.
- `npm run lint`: passed.
- `npm run build`: passed.
## Phase 31: Claude Project Evidence Alignment

Status: completed.

Required work:

- Inspect `E:\AI_VPS_Mamgment\claude_project`.
- Compare the old MCP monitoring/report flow with the current periodic monitoring implementation.
- Preserve raw command evidence inside periodic monitoring reports.
- Feed raw evidence to the LLM-only final analysis.
- Persist raw snapshots in PostgreSQL.
- Improve report review in the admin panel.

Completed work:

- Added structured collection output in the agent.
- Stored SSH command results in `raw_snapshot.command_results`.
- Included raw monitoring evidence in the LLM prompt.
- Added `raw_snapshot` to `periodic_monitoring_reports`.
- Added and applied migration `0002_periodic_report_raw_snapshot.sql`.
- Displayed raw monitoring evidence in the admin panel report cards.
- Created `docs/phase-31`.

Verification:

- `uv run --extra dev pytest` in `apps/agent`: passed, 8 tests.
- `uv run pytest` in `apps/api`: passed, 52 tests.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint` in `apps/admin-panel`: passed.
- `npm run build` in `apps/admin-panel`: passed.
## Phase 32: Instruction-Driven Monitoring Profiles

Status: completed.

Required work:

- Remove threshold-based monitoring profile design from active code.
- Make monitoring profiles define read-only execution instructions.
- Let the user define periodic monitoring instructions from the admin panel.
- Use an agent orchestration library instead of a hand-written orchestration loop.
- Keep final report analysis LLM-only.

Completed work:

- Replaced `thresholds` with `monitoring_instructions`.
- Replaced `thresholds_count` with `instructions_count`.
- Added `POST /api/v1/monitoring-profiles`.
- Persisted custom profile definitions in `monitoring_profile_versions.definition`.
- Passed assigned profile instructions into the periodic monitoring agent.
- Built SSH command policy from profile instructions.
- Added LangGraph and used it in `PeriodicMonitoringAgent`.
- Added a tabbed admin page for profile list and instruction definition.
- Created `docs/phase-32`.

Verification:

- `uv run --extra dev pytest` in `apps/agent`: passed, 8 tests.
- `uv run pytest` in `apps/api`: passed, 53 tests.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint` in `apps/admin-panel`: passed.
- `npm run build` in `apps/admin-panel`: passed.
## Phase 33: Ollama LLM Runtime Configuration

Status: completed.

Required work:

- Enable local LLM report analysis through Ollama.
- Configure the API `.env` with a locally available model.
- Keep LLM final analysis enabled for local development.
- Document the required Ollama settings.

Completed work:

- Verified Ollama is installed and serving locally.
- Detected `gemma4:latest` as an available model.
- Set `LLM_ANALYSIS_ENABLED=true`.
- Set `LLM_ANALYSIS_PROVIDER=ollama`.
- Set `LLM_ANALYSIS_MODEL=gemma4:latest`.
- Set `LLM_ANALYSIS_TIMEOUT_SECONDS=60`.
- Updated `.env.example`, `apps/api/README.md`, and `docs/phase-33`.

Verification:

- Ollama `/api/tags`: reachable.
- Ollama `/api/generate` with `gemma4:latest` and JSON format: returned valid JSON.
- `uv run pytest tests/test_periodic_monitoring.py` in `apps/api`: passed, 11 tests.
- Backend `/health/ready`: ready after restart.
- Admin panel `/periodic-monitoring`: HTTP 200 after restart.
## Phase 34: Robust Ollama Analysis Payload Parsing

Status: completed.

Required work:

- Fix Ollama analysis failures caused by valid JSON with unexpected list item shapes.
- Keep LLM final analysis enabled without failing the whole report on minor response-shape drift.
- Make prompt schema clearer for string-only list fields.

Completed work:

- Normalized string-list fields returned by the LLM.
- Converted object items in `next_actions`, limitations, hypotheses, questions, and specialist-agent lists into safe JSON strings.
- Updated prompt constraints.
- Removed outdated rule-signal wording from failure limitations.
- Added a regression test for object-shaped `next_actions`.

Verification:

- `uv run pytest tests/test_periodic_monitoring.py` in `apps/api`: passed, 12 tests.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- Backend restarted and listens on port `8000`.
