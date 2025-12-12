"""
Export tenant configuration from database to YAML.

Usage:
    python manage.py export_tenant_config boss
    python manage.py export_tenant_config pools
    python manage.py export_tenant_config --all
"""
import os
import yaml
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.models import TenantConfig


class Command(BaseCommand):
    help = 'Export tenant configuration from database to YAML file'

    def add_arguments(self, parser):
        parser.add_argument(
            'tenant_id',
            nargs='?',
            type=str,
            help='Tenant ID to export (e.g., boss, pools)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Export all tenant configs from database'
        )
        parser.add_argument(
            '--stdout',
            action='store_true',
            help='Output to stdout instead of file'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.export_all_tenants(options['stdout'])
        elif options['tenant_id']:
            self.export_tenant(options['tenant_id'], options['stdout'])
        else:
            raise CommandError('Please specify a tenant_id or use --all')

    def export_all_tenants(self, to_stdout: bool):
        """Export all tenant configs from database."""
        configs = TenantConfig.objects.all()
        
        if not configs.exists():
            self.stdout.write(
                self.style.WARNING('No tenant configs found in database')
            )
            return
        
        for config in configs:
            self._export_tenant_internal(config, to_stdout)

    def export_tenant(self, tenant_id: str, to_stdout: bool = False):
        """Export a single tenant's config from DB to YAML."""
        try:
            config = TenantConfig.objects.get(tenant_id=tenant_id)
        except TenantConfig.DoesNotExist:
            raise CommandError(f'No config found for tenant: {tenant_id}')
        
        self._export_tenant_internal(config, to_stdout)

    def _export_tenant_internal(self, config: TenantConfig, to_stdout: bool = False):
        
        # Build YAML structure
        config_data = {
            'tenant_id': config.tenant_id,
            'display_name': config.display_name,
            'product_categories': config.product_categories,
            'pipeline_steps': config.pipeline_steps,
        }
        
        if config.step_configs:
            config_data['step_configs'] = config.step_configs
        
        if config.branding:
            config_data['branding'] = config.branding
        
        # Convert to YAML
        yaml_content = yaml.dump(
            config_data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        
        if to_stdout:
            self.stdout.write(f"\n# {config.tenant_id} config (v{config.config_version})")
            self.stdout.write(yaml_content)
        else:
            # Write to file
            config_path = os.path.join(
                settings.BASE_DIR, 'api', 'tenants', config.tenant_id, 'config.yaml'
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(yaml_content)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Exported {config.tenant_id} config (v{config.config_version}) to {config_path}"
                )
            )
