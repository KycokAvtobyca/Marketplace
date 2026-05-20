from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, PhoneBan, Shop, ShopModerationRequest, SMSCode


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "phone_number",
        "name",
        "is_active",
        "is_staff",
        "date_time_create",
    )

    search_fields = (
        "phone_number",
        "name",
        "email",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "date_time_create",
    )

    ordering = ("-date_time_create",)
    list_per_page = 25
    date_hierarchy = "date_time_create"
    actions = ("block_users", "unblock_users", "ban_phone_numbers")

    readonly_fields = ("date_time_create", "date_time_update", "last_login")

    @admin.action(description="Заблокировать выбранных пользователей")
    def block_users(self, request, queryset):
        queryset.exclude(is_superuser=True).update(is_active=False)

    @admin.action(description="Разблокировать выбранных пользователей")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Забанить выбранные номера телефонов")
    def ban_phone_numbers(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(
                request,
                "Бан по телефону доступен только суперпользователю.",
                level=messages.ERROR,
            )
            return
        created = 0
        for user in queryset.exclude(is_superuser=True):
            _, was_created = PhoneBan.objects.update_or_create(
                phone_number=user.phone_number,
                defaults={
                    "is_active": True,
                    "created_by": request.user,
                    "reason": "Заблокирован через список пользователей.",
                },
            )
            created += int(was_created)
        self.message_user(
            request,
            f"Активных блокировок телефонов: {queryset.count()}. Новых: {created}.",
        )

    def get_fieldsets(self, request, obj=None):
        """Убрать раздел пароля для не-суперпользователей."""
        fieldsets = super().get_fieldsets(request, obj)
        
        # Скрываем пароль если редактируем не-суперпользователя
        if obj is not None and not obj.is_superuser:
            fieldsets = [
                (name, opts) for name, opts in fieldsets
                if name != 'Password'
            ]
        
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Убрать поле пароля из формы для не-суперпользователей."""
        form = super().get_form(request, obj, **kwargs)
        
        # Убираем поле пароля если редактируем не-суперпользователя
        if obj is not None and not obj.is_superuser:
            # Удаляем из fields если есть
            if hasattr(form, 'fields') and 'password' in form.fields:
                del form.fields['password']
            # Также удаляем из base_fields для инстанце проверок
            if hasattr(form, 'base_fields') and 'password' in form.base_fields:
                form.base_fields = {k: v for k, v in form.base_fields.items() if k != 'password'}
        
        return form


@admin.register(PhoneBan)
class PhoneBanAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "is_active",
        "created_by",
        "date_time_create",
    )
    list_filter = ("is_active", "date_time_create")
    search_fields = ("phone_number", "reason")
    readonly_fields = ("created_by", "date_time_create", "date_time_update")

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Shop)
class ShopAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "owner",
        "is_active",
        "data_time_create",
    )

    search_fields = ("name", "owner__name", "owner__phone_number")

    list_filter = ("is_active", "data_time_create")

    readonly_fields = ("data_time_create",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "description")
        }),
        ("Владелец и статус", {
            "fields": ("owner", "is_active")
        }),
        ("Изображение", {
            "fields": ("image",)
        }),
        ("Дополнительно", {
            "fields": ("data_time_create",),
            "classes": ("collapse",)
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """
        Суперпользователь может указывать owner при создании магазина.
        Обычный пользователь видит только свой магазин.
        """
        fieldsets = super().get_fieldsets(request, obj)
        
        # Если не суперпользователь, скрываем поле owner
        if not request.user.is_superuser and obj is not None:
            fieldsets = [
                (name, opts) for name, opts in fieldsets
                if name != "Владелец и статус"
            ]
            # Добавляем измененный fieldset
            fieldsets = list(fieldsets) + [
                ("Статус", {
                    "fields": ("is_active",)
                })
            ]
        
        return fieldsets
    
    def get_queryset(self, request):
        """
        Фильтруем магазины:
        - Суперпользователь видит все магазины
        - Обычный пользователь видит только свои магазины
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(owner=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        """
        При создании магазина:
        - Суперпользователь может выбрать owner
        - Обычный пользователь автоматически становится owner
        """
        if not change:  # Если создаём новый магазин
            if not request.user.is_superuser:
                obj.owner = request.user  # Обычный пользователь - его магазин
            # Суперпользователь может выбрать owner в форме
        
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """
        Суперпользователь может удалять любой магазин.
        Обычный пользователь может удалять только свой магазин.
        """
        if request.user.is_superuser:
            return True
        if obj and obj.owner == request.user:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Суперпользователь может редактировать любой магазин.
        Обычный пользователь может редактировать только свой магазин.
        """
        if request.user.is_superuser:
            return True
        if obj and obj.owner == request.user:
            return True
        return False
    
    def has_add_permission(self, request):
        """
        Только суперпользователи и верифицированные пользователи могут создавать магазины.
        """
        # Все пользователи (включая обычных) могут создавать магазины
        return True


@admin.register(ShopModerationRequest)
class ShopModerationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "user", "shop", "name", "status", "date_time_create")
    list_filter = ("action", "status", "date_time_create")
    search_fields = ("name", "description", "user__phone_number", "shop__name")
    readonly_fields = ("user", "shop", "action", "name", "description", "image", "date_time_create", "date_time_update")

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = type(obj).objects.only("status").get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if old_status == obj.status or obj.status != ShopModerationRequest.Status.APPROVED:
            return

        if obj.action == ShopModerationRequest.Action.CREATE:
            shop = Shop.objects.create(
                owner=obj.user,
                name=obj.name,
                description=obj.description,
                image=obj.image,
                is_active=True,
            )
            obj.shop = shop
            obj.save(update_fields=["shop", "date_time_update"])
            if not obj.user.is_staff:
                obj.user.is_staff = True
                obj.user.save(update_fields=["is_staff", "date_time_update"])

        if obj.action == ShopModerationRequest.Action.DELETE and obj.shop_id:
            user = obj.user
            obj.shop.delete()
            if not Shop.objects.filter(owner=user).exists() and not user.is_superuser:
                user.is_staff = False
                user.save(update_fields=["is_staff", "date_time_update"])


@admin.register(SMSCode)
class SMSCodeAdmin(ImportExportModelAdmin):
    list_display = (
        "phone_number",
        "code",
        "date_time_create",
    )

    search_fields = ("phone_number",)

    list_filter = ("date_time_create",)

    readonly_fields = ("phone_number", "code", "date_time_create")
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
