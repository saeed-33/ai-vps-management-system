# المرحلة الثامنة: Servers Management Foundation

## الهدف

إنشاء أساس إدارة السيرفرات لأن السيرفر هو محور المراقبة الدورية والوكلاء الفرعيين.

هذه المرحلة لا تربط السيرفرات بقاعدة البيانات بعد، لكنها تثبت:

- عقود API الخاصة بالسيرفرات.
- endpoints محمية بالـ bearer token.
- صفحة إدارة السيرفرات في لوحة الإدارة.
- ربط أولي بين الواجهة وBackend API.

## النطاق

داخل النطاق:

- إضافة schemas للسيرفرات.
- إضافة service مبدئي للسيرفرات.
- إضافة routes:
  - `GET /api/v1/servers`
  - `GET /api/v1/servers/summary`
  - `GET /api/v1/servers/{server_id}`
- حماية routes باستخدام صلاحية `servers.read`.
- إضافة صفحة `/servers` في لوحة الإدارة.
- إضافة servers API client في الواجهة.
- تحديث dashboard/sidebar.
- إضافة اختبارات Backend.
- تحديث التوثيق.

خارج النطاق حاليا:

- إنشاء سيرفرات فعليا.
- تعديل سيرفرات.
- حذف سيرفرات.
- حفظ credentials.
- اختبار اتصال SSH.
- ربط PostgreSQL repository.
- تشغيل مراقبة فعلية على السيرفرات.

## معايير الإنجاز

- Backend tests ناجحة.
- Admin lint وbuild ناجحان.
- `/servers` تعمل في لوحة الإدارة.
- endpoints محمية وترفض الطلب دون token.
- يتم commit وpush وtag إلى GitHub.
