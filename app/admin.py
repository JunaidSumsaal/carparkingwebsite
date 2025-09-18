from django.contrib import admin
from .models import DetectionResult, Registration, ContactMessage, FAQ, UserFeedback

admin.site.register(DetectionResult)
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "password")

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submitted_at')   # columns to show in list view
    list_filter = ('submitted_at',)                   # filter by date
    search_fields = ('name', 'email', 'message')      # search box
    readonly_fields = ('submitted_at',)               # submitted_at not editable
    ordering = ('-submitted_at',)                     # newest first


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'created_at')        # columns in list view
    search_fields = ('question', 'answer')           # search by question or answer
    readonly_fields = ('created_at',)                # created_at not editable
    ordering = ('-created_at',)                      # newest first


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')   # columns in list view
    search_fields = ('name', 'email', 'message')     # search box
    list_filter = ('created_at',)                    # filter by date
    readonly_fields = ('created_at',)                # created_at not editable
    ordering = ('-created_at',)     