# ADR-001: بنية لوحة الإدارة

## الحالة

مقبول.

## القرار

سنستخدم:

```text
Next.js App Router
+ TypeScript
+ Modular Feature-Based Frontend Architecture
+ Lightweight Layered Frontend Structure
```

الاسم المختصر:

```text
Modular Feature-Based Frontend Architecture
```

بالعربية:

```text
بنية واجهة معيارية قائمة على الميزات
```

## لماذا ليست MVC؟

MVC يقسم التطبيق إلى:

```text
Model
View
Controller
```

هذا النمط مناسب أكثر لتطبيقات server-rendered التقليدية أو بعض backend frameworks. في React وNext.js، حدود المسؤوليات مختلفة:

- الصفحات والمكونات تمثل presentation.
- hooks وquery functions تدير data fetching وstate.
- API client يتواصل مع backend.
- schemas تتحقق من المدخلات.
- features تجمع منطق كل مجال.

فرض MVC على لوحة React كبيرة سيجعل البنية أقل طبيعية وأكثر غموضا.

## لماذا ليست Clean Architecture كاملة؟

Clean Architecture الكاملة في الواجهة ستقترح طبقات مثل:

```text
domain
application
infrastructure
presentation
```

هذا مفيد في أنظمة frontend شديدة التعقيد، لكنه ثقيل مبكرا لنظامنا. لوحة الإدارة تحتاج تنظيما واضحا وسريعا، لكنها لا تحتاج عزل domain بنفس صرامة backend في البداية.

لذلك سنستخدم Clean Architecture كمبدأ خفيف فقط:

- عدم خلط API calls داخل كل component.
- فصل validation schemas.
- فصل types.
- فصل reusable components.
- إبقاء منطق كل feature داخل مجلدها.

## البنية المقترحة

```text
apps/admin-panel/
  src/
    app/
      layout.tsx
      page.tsx
      dashboard/
      users/
      servers/
      monitoring-profiles/
      specialist-agents/
      issues/
      reports/
      logs/
      allowed-tools/
      allowed-solutions/
      documents/
      chat/
      settings/

    features/
      users/
      servers/
      monitoring-profiles/
      specialist-agents/
      issues/
      reports/
      audit-logs/
      allowed-tools/
      allowed-solutions/
      documents/
      chat/

    components/
      layout/
      navigation/
      data-table/
      forms/
      charts/
      ui/

    lib/
      api-client.ts
      query-client.ts
      auth.ts
      routes.ts
      utils.ts

    schemas/
    types/
    hooks/
    styles/
```

## شكل كل feature

كل feature كبيرة يمكن أن تحتوي:

```text
features/servers/
  api.ts
  types.ts
  schemas.ts
  hooks.ts
  components/
  views/
```

## سبب الاختيار

لوحة الإدارة ستكون كبيرة وتشمل:

- المستخدمين.
- السيرفرات.
- ملفات المراقبة.
- الوكلاء المتخصصين.
- المشكلات.
- التقارير.
- السجلات.
- صلاحيات الوكيل.
- الأدوات والحلول المسموحة.
- الوثائق.
- المحادثة.

تقسيمها حسب الميزات يقلل التشابك ويجعل كل مجال قابلا للتطوير بشكل مستقل.

## النتائج الإيجابية

- سهولة إضافة صفحة أو feature جديدة.
- وضوح ملكية الملفات.
- تقليل الاعتماد المتبادل بين الصفحات.
- سهولة اختبار كل feature.
- توافق طبيعي مع Next.js App Router.
- مناسب لفريق صغير الآن وقابل للتوسع لاحقا.

## التنازلات

- قد يحدث تكرار بسيط بين features في البداية.
- يحتاج انضباطا حتى لا تتحول `components/` و`lib/` إلى مجلدات عشوائية.
- لا يوفر عزلا صارما مثل Clean Architecture الكاملة.

## قواعد العمل

- كل منطق feature يبقى داخل `features/<feature-name>`.
- المكونات العامة فقط توضع في `components/`.
- الاتصال بالـ API يتم عبر `lib/api-client.ts` أو ملفات `api.ts` داخل feature.
- validation يتم عبر schemas، وليس داخل components مباشرة.
- الصفحات في `app/` يجب أن تكون رفيعة وتستدعي views/components من feature.
