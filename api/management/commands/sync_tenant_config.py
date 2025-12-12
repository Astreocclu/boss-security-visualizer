"""
Sync tenant configuration from YAML to database.

Usage:
    python manage.py sync_tenant_config boss
    python manage.py sync_tenant_config pools
    python manage.py sync_tenant_config --all
"""
import os
import yaml
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.models import TenantConfig


class Command(BaseCommand):
    help = 'Sync tenant configuration from YAML file to database'

    def add_arguments(self, parser):
        parser.add_argument(
            'tenant_id',
            nargs='?',
            type=str,
            help='Tenant ID to sync (e.g., boss, pools)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all tenant configs found in api/tenants/'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.sync_all_tenants()
        elif options['tenant_id']:
            self.sync_tenant(options['tenant_id'])
        else:
            raise CommandError('Please specify a tenant_id or use --all')

    def sync_all_tenants(self):
        """Find and sync all tenant configs."""
        tenants_dir = os.path.join(settings.BASE_DIR, 'api', 'tenants')
        
        synced = 0
        for item in os.listdir(tenants_dir):
            item_path = os.path.join(tenants_dir, item)
            config_path = os.path.join(item_path, 'config.yaml')
            
            if os.path.isdir(item_path) and os.path.exists(config_path):
                self.sync_tenant(item)
                synced += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Synced {synced} tenant config(s)')
        )

    def sync_tenant(self, tenant_id: str):
        """Sync a single tenant's config from YAML to DB."""
        config_path = os.path.join(
            settings.BASE_DIR, 'api', 'tenants', tenant_id, 'config.yaml'
        )
        
        if not os.path.exists(config_path):
            raise CommandError(f'Config file not found: {config_path}')
        
        # Load YAML
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['tenant_id', 'display_name', 'product_categories', 'pipeline_steps']
        for field in required_fields:
            if field not in config_data:
                raise CommandError(f"Missing required field '{field}' in {config_path}")
        
        if config_data['tenant_id'] != tenant_id:
            raise CommandError(
                f"tenant_id in YAML ({config_data['tenant_id']}) "
                f"doesn't match directory ({tenant_id})"
            )
        
        # Upsert to database
        tenant_config, created = TenantConfig.objects.get_or_create(
            tenant_id=tenant_id,
            defaults={
                'display_name': config_data['display_name'],
                'product_categories': config_data['product_categories'],
                'pipeline_steps': config_data['pipeline_steps'],
                'step_configs': config_data.get('step_configs', {}),
                'branding': config_data.get('branding', {}),
            }
        )
        
        if not created:
            # Update existing
            tenant_config.display_name = config_data['display_name']
            tenant_config.product_categories = config_data['product_categories']
            tenant_config.pipeline_steps = config_data['pipeline_steps']
            tenant_config.step_configs = config_data.get('step_configs', {})
            tenant_config.branding = config_data.get('branding', {})
            tenant_config.config_version += 1
            tenant_config.save()
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {tenant_id} config (v{tenant_config.config_version})"
            )
        )
