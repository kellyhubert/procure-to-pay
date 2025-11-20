from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PurchaseRequest, Approval


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'department')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'department')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'department')}),
    )


class ApprovalInline(admin.TabularInline):
    model = Approval
    extra = 0
    readonly_fields = ('approved_at',)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ApprovalInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'amount', 'status', 'created_by')
        }),
        ('Documents', {
            'fields': ('proforma', 'proforma_data', 'purchase_order', 'purchase_order_data',
                      'receipt', 'receipt_data', 'receipt_validation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'approver', 'approved', 'approved_at')
    list_filter = ('approved', 'approved_at', 'approver__role')
    search_fields = ('purchase_request__title', 'approver__username')
    readonly_fields = ('approved_at',)
