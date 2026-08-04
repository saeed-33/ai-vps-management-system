# شرح ملفات Docker

## الهدف

ملفات Docker الحالية لا تشغل النظام كاملا بعد. هي مخصصة لتجهيز خدمات التطوير الأساسية التي ستحتاجها المراحل القادمة:

- PostgreSQL مع pgvector.
- Redis.

## الملفات الحالية

```text
infra/compose/docker-compose.dev.yml
infra/compose/README.md
.env.example
```

## `infra/compose/docker-compose.dev.yml`

هذا الملف يعرف خدمات التطوير المحلية.

### `name`

```yaml
name: ai-vps-management
```

يثبت اسم مشروع Docker Compose. بدون هذا السطر سيستخدم Docker اسم المجلد أو `compose`، وقد تتغير أسماء الشبكات والـ volumes حسب مكان التشغيل.

النتيجة المتوقعة:

```text
ai-vps-management_default
ai-vps-management_postgres_data
ai-vps-management_redis_data
```

### خدمة `postgres`

```yaml
postgres:
  image: pgvector/pgvector:pg16
```

تستخدم صورة PostgreSQL 16 مضافا إليها pgvector.

سبب اختيارها:

- نحتاج PostgreSQL كقاعدة البيانات الأساسية.
- نحتاج pgvector لاحقا لنظام RAG.
- هذا يمنع الحاجة لبناء image مخصصة في البداية.

### `container_name`

```yaml
container_name: ai-vps-postgres-dev
```

اسم ثابت للحاوية، يسهل تنفيذ أوامر مثل:

```bash
docker exec -i ai-vps-postgres-dev psql -U postgres -d ai_vps_management
```

### متغيرات PostgreSQL

```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB:-ai_vps_management}
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change_me}
```

تقرأ القيم من البيئة أو تستخدم قيما افتراضية للتطوير.

المصدر المقترح للقيم هو `.env` المبني من `.env.example`.

### المنافذ

```yaml
ports:
  - "${POSTGRES_PORT:-5432}:5432"
```

يفتح PostgreSQL على جهازك المحلي.

إذا كان المنفذ `5432` مستخدما، يمكن تغييره في `.env`:

```text
POSTGRES_PORT=5433
```

### التخزين

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

يحفظ بيانات PostgreSQL داخل Docker volume حتى لا تضيع عند إيقاف الحاوية.

لحذف البيانات بالكامل:

```bash
docker compose -f infra/compose/docker-compose.dev.yml down -v
```

### Healthcheck

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-ai_vps_management}"]
```

يتحقق أن PostgreSQL جاهز لاستقبال الاتصالات.

هذا مهم لاحقا عندما نضيف API أو worker يعتمدان على قاعدة البيانات.

## خدمة `redis`

```yaml
redis:
  image: redis:7-alpine
```

Redis سيستخدم لاحقا لـ:

- queues.
- المهام الدورية.
- job state.
- rate limiting أو cache عند الحاجة.

### `container_name`

```yaml
container_name: ai-vps-redis-dev
```

اسم ثابت لحاوية Redis.

### المنافذ

```yaml
ports:
  - "${REDIS_PORT:-6379}:6379"
```

يفتح Redis محليا على `6379` افتراضيا.

### التخزين

```yaml
volumes:
  - redis_data:/data
```

يحفظ بيانات Redis إذا استخدمنا persistence.

### Healthcheck

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
```

يتحقق أن Redis يرد بـ `PONG`.

## `.env.example`

هذا الملف نموذج للقيم المطلوبة محليا.

الأجزاء المهمة:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_vps_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql://postgres:change_me@localhost:5432/ai_vps_management

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379
```

في التطوير، يمكن نسخ الملف إلى `.env`.

لا يجب رفع `.env` إلى Git.

## تشغيل الخدمات

```bash
docker compose -f infra/compose/docker-compose.dev.yml up -d
```

## إيقاف الخدمات

```bash
docker compose -f infra/compose/docker-compose.dev.yml down
```

## حذف الخدمات مع البيانات

```bash
docker compose -f infra/compose/docker-compose.dev.yml down -v
```

## تطبيق migration

بعد تشغيل Docker Desktop والخدمات:

```bash
Get-Content packages/database/migrations/0001_initial_schema.sql | docker exec -i ai-vps-postgres-dev psql -U postgres -d ai_vps_management
```

## التحقق من الجداول

```bash
docker exec -it ai-vps-postgres-dev psql -U postgres -d ai_vps_management -c "\dt"
```

## سبب عدم إضافة Dockerfiles الآن

لم نضف Dockerfiles للتطبيقات بعد لأننا لم نبدأ بناء الخدمات التالية:

- `apps/api`
- `apps/admin-panel`
- `apps/agent`
- `apps/worker`

عند اختيار وتنفيذ stack كل خدمة، سنضيف Dockerfile مناسب لها.

المرحلة الحالية تحتاج خدمات خارجية فقط، لذلك Docker Compose كاف.
