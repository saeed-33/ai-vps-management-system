# المرحلة السابعة: Users & Roles Management Foundation

## الهدف

إنشاء أساس إدارة المستخدمين والأدوار بعد بناء Auth & RBAC foundation.

هذه المرحلة لا تبني إدارة مستخدمين كاملة مرتبطة بقاعدة البيانات بعد، لكنها تضع:

- contracts واضحة للمستخدمين والأدوار.
- endpoints محمية بالـ bearer token.
- صفحة Users أولية في لوحة الإدارة.
- ربط أولي بين الواجهة وBackend API.

## النطاق

داخل النطاق:

- إضافة schemas للمستخدمين والأدوار.
- إضافة service مبدئي للمستخدمين.
- إضافة routes:
  - `GET /api/v1/users`
  - `GET /api/v1/users/me`
  - `GET /api/v1/users/roles`
- حماية routes باستخدام `GET /auth/me` principal logic.
- إضافة صفحة `/users` في لوحة الإدارة.
- إضافة users API client في الواجهة.
- تحديث sidebar لربط صفحة المستخدمين.
- إضافة اختبارات Backend.
- تحديث التوثيق.

خارج النطاق حاليا:

- إنشاء مستخدمين فعليا في قاعدة البيانات.
- تعديل مستخدمين.
- حذف مستخدمين.
- دعوات المستخدمين.
- reset password.
- ربط المستخدمين بجدول `users`.
- واجهة RBAC كاملة.

## لماذا foundation قبل CRUD؟

لأن قاعدة البيانات لم يتم تشغيل migrations عليها بعد في البيئة المحلية، كما أن audit وrepository layers لم تكتمل. هذه المرحلة تثبت contract والواجهة العامة، ثم سنربطها بقاعدة البيانات عند بناء repositories.

## معايير الإنجاز

- Backend tests ناجحة.
- Admin lint وbuild ناجحان.
- `/users` تعمل في لوحة الإدارة.
- endpoints محمية وترفض الطلب دون token.
- يتم commit وpush وtag إلى GitHub.
