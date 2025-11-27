from django.contrib import admin
from .models import UserProfile, ScreenType, VisualizationRequest, GeneratedImage

# Basic registration
admin.site.register(UserProfile)
admin.site.register(ScreenType)
admin.site.register(VisualizationRequest)
admin.site.register(GeneratedImage)

# You can customize the admin interface later if needed
# Example:
# class VisualizationRequestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'screen_type', 'status', 'created_at')
#     list_filter = ('status', 'screen_type', 'user')
#     search_fields = ('user__username',)
# admin.site.register(VisualizationRequest, VisualizationRequestAdmin)
