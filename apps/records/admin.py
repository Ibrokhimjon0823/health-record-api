from django.contrib import admin

from . import models


class HealthRecordFileInline(admin.TabularInline):
    model = models.HealthRecordFile
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("file", "created_at")


class DoctorAnnotationInline(admin.StackedInline):
    model = models.DoctorAnnotation
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    fields = ("note", "created_at", "updated_at")


@admin.register(models.HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "record_type", "created_at")
    list_filter = ("record_type", "created_at")
    search_fields = ("patient__email", "patient__first_name", "patient__last_name", 
                     "doctor__email", "doctor__first_name", "doctor__last_name", "description")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("patient", "doctor")
    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("patient", "doctor", "record_type")}),
        ("Details", {"fields": ("description",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    
    inlines = [HealthRecordFileInline, DoctorAnnotationInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, "role"):
            if request.user.role == "doctor":
                qs = qs.filter(doctor=request.user)
            elif request.user.role == "patient":
                qs = qs.filter(patient=request.user)
        return qs


@admin.register(models.HealthRecordFile)
class HealthRecordFileAdmin(admin.ModelAdmin):
    list_display = ("id", "record", "file_name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("record__patient__email", "record__description", "file")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("record", "record__patient", "record__doctor")
    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("record", "file")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    
    def file_name(self, obj):
        return obj.file.name.split("/")[-1] if obj.file else "No file"
    file_name.short_description = "File Name"


@admin.register(models.DoctorAnnotation)
class DoctorAnnotationAdmin(admin.ModelAdmin):
    list_display = ("id", "record", "doctor_name", "truncated_note", "created_at")
    list_filter = ("created_at",)
    search_fields = ("record__patient__email", "record__doctor__email", "note")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("record", "record__doctor")
    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("record",)}),
        ("Content", {"fields": ("note",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    
    def doctor_name(self, obj):
        return obj.record.doctor.get_full_name() or obj.record.doctor.email
    doctor_name.short_description = "Doctor"
    
    def truncated_note(self, obj):
        return obj.note[:100] + "..." if len(obj.note) > 100 else obj.note
    truncated_note.short_description = "Note"