# ADR-002: بنية Backend / Control Plane

## الحالة

مقبول.

## القرار

سنستخدم:

```text
FastAPI
+ Modular Monolith في البداية
+ Modular Layered Architecture
+ Lightweight Clean Architecture
```

الاسم المختصر:

```text
Modular Layered Backend Architecture
```

بالعربية:

```text
بنية خلفية معيارية متعددة الطبقات
```

## لماذا Modular Monolith في البداية؟

النظام يحتوي مجالات كثيرة:

- المستخدمون والصلاحيات.
- السيرفرات.
- المراقبة.
- الوكلاء المتخصصون.
- التقارير.
- المشكلات.
- الأدوات والحلول.
- الوثائق وRAG.
- المحادثة.
- MCP.
- Policy Engine.

رغم ذلك، تقسيمها إلى microservices مبكرا سيضيف تعقيدا غير ضروري:

- نشر أكثر تعقيدا.
- مراقبة أكثر تعقيدا.
- network boundaries قبل ثبات النطاق.
- صعوبة في migrations والمعاملات.

لذلك نبدأ كـ modular monolith: خدمة backend واحدة، لكن مقسمة داخليا إلى modules واضحة. إذا احتجنا لاحقا، يمكن فصل worker أو agent أو MCP إلى خدمات مستقلة.

## لماذا ليست MVC؟

MVC في backend قد يكون مناسبا لتطبيقات CRUD بسيطة، لكنه لا يكفي هنا لأن النظام يحتوي:

- Policy decisions.
- Workflows.
- Audit logs.
- Agent orchestration.
- Execution requests.
- Versioned operational definitions.

نحتاج فصل أوضح من Controller/Model/View.

## لماذا ليست Clean Architecture صارمة؟

Clean Architecture الكاملة تعطي عزلا قويا، لكنها تزيد عدد الملفات والطبقات مبكرا. في المرحلة الحالية نحتاج سرعة تنفيذ مع حدود جيدة.

لذلك سنطبق نسخة خفيفة:

- `api` للـ HTTP routes.
- `schemas` للـ DTOs.
- `services` لمنطق التطبيق.
- `repositories` للوصول للبيانات.
- `models` أو `db` لاحقا لتمثيل قاعدة البيانات.
- `core` للإعدادات والبنية المشتركة.

## الطبقات

```text
API Layer
  FastAPI routers, request/response handling

Schema Layer
  Pydantic DTOs and validation

Service Layer
  business/application logic

Repository Layer
  database access

Core Layer
  config, database, logging, security, shared infrastructure
```

## البنية المقترحة داخل `apps/api`

```text
apps/api/
  src/control_plane_api/
    main.py

    core/
      config.py
      database.py
      logging.py
      security.py

    api/
      router.py
      dependencies.py
      routes/
        health.py
        meta.py
        users.py
        servers.py
        monitoring_profiles.py
        specialist_agents.py
        issues.py
        reports.py
        allowed_tools.py
        allowed_solutions.py
        documents.py
        chat.py
        mcp.py

    modules/
      users/
        schemas.py
        service.py
        repository.py
      servers/
        schemas.py
        service.py
        repository.py
      monitoring/
        schemas.py
        service.py
        repository.py
      specialist_agents/
        schemas.py
        service.py
        repository.py
      policy/
        schemas.py
        service.py
        rules.py
      audit/
        schemas.py
        service.py
        repository.py

    schemas/
      health.py
      meta.py
      common.py
```

## شكل الطلب داخل backend

مثال مستقبلي لإدارة السيرفرات:

```text
HTTP request
  -> api/routes/servers.py
  -> modules/servers/service.py
  -> modules/servers/repository.py
  -> database
```

ومع audit:

```text
HTTP request
  -> service
  -> policy/audit checks
  -> repository
  -> audit log
  -> response
```

## علاقة Policy Engine بالبنية

Policy Engine يجب ألا يكون مجرد if statements داخل routes.

سيكون module مستقل:

```text
modules/policy/
  service.py
  rules.py
  schemas.py
```

أي عملية حساسة تمر عليه قبل التنفيذ أو الموافقة.

## علاقة Audit بالبنية

Audit يجب أن يكون module مبكر:

```text
modules/audit/
```

كل عملية حساسة تسجل:

- actor.
- action.
- resource.
- before_state.
- after_state.
- policy_decision.

## علاقة MCP بالبنية

MCP يبدأ كـ module داخل backend:

```text
api/routes/mcp.py
modules/mcp/
```

لاحقا إذا زاد التعقيد، يمكن فصله إلى service مستقلة.

## النتائج الإيجابية

- مناسب للبدء السريع.
- يحافظ على حدود واضحة بين المجالات.
- يسمح بتطبيق audit وpolicy بشكل منظم.
- لا يقفلنا داخل microservices مبكرا.
- يمكن فصل بعض modules لاحقا إذا ظهر احتياج حقيقي.

## التنازلات

- modular monolith يحتاج انضباطا حتى لا تتحول الخدمة إلى كتلة واحدة.
- الفصل بين modules سيكون بالاتفاق والبنية، وليس بعزل network.
- قد نحتاج refactor لاحقا إذا تضخم MCP أو RAG أو worker.

## قواعد العمل

- routes لا تحتوي business logic ثقيل.
- service layer هي مكان منطق التطبيق.
- repository layer هي مكان SQL/database access.
- كل عملية حساسة تستدعي audit.
- كل تنفيذ أو موافقة تستدعي policy.
- لا اتصال مباشر من route إلى قاعدة البيانات إلا في endpoints صحية أو تقنية بسيطة.
