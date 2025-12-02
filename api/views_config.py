"""Tenant configuration API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from api.tenants import get_tenant_config


class TenantConfigView(APIView):
    """
    API endpoint for tenant configuration.

    Returns product choices and display options for the active tenant.
    """
    permission_classes = [permissions.AllowAny]  # Config is public

    def get(self, request):
        try:
            config = get_tenant_config()

            return Response({
                'tenant_id': config.tenant_id,
                'display_name': config.display_name,
                'choices': {
                    'mesh': config.get_mesh_choices(),
                    'frame_color': config.get_frame_color_choices(),
                    'mesh_color': config.get_mesh_color_choices(),
                    'opacity': config.get_opacity_choices(),
                },
                'pipeline_steps': config.get_pipeline_steps(),
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to load tenant config: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
