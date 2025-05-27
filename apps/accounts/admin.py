from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models
from .forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ("email", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_staff", "created_at")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "last_login")

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    full_name.short_description = "Name"


class DoctorProfileInline(admin.StackedInline):
    model = models.DoctorProfile
    extra = 0
    readonly_fields = ("created_at", "updated_at")


class PatientProfileInline(admin.StackedInline):
    model = models.PatientProfile
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "specialization",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user",)
    list_per_page = 25

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "specialization",
                    "license_number",
                    "years_of_experience",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(models.PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "age", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at", "age")
    list_select_related = ("user",)
    list_per_page = 25
    date_hierarchy = "date_of_birth"

    fieldsets = (
        (None, {"fields": ("user", "date_of_birth", "gender", "address", "age")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def age(self, obj):
        if obj.date_of_birth:
            from datetime import date

            today = date.today()
            return (
                today.year
                - obj.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (obj.date_of_birth.month, obj.date_of_birth.day)
                )
            )
        return None

    age.short_description = "Age"
