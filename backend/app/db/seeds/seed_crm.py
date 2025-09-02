# backend/app/db/seeds/seed_crm.py
"""
CRM module seeder - contains ONLY CRM-specific data and business logic.
Uses factory infrastructure but keeps all CRM concerns isolated in this file.

This file owns:
- CRM permissions definitions
- CRM roles and their permission mappings  
- CRM-specific validation and business rules
- Any CRM-specific seeding logic beyond permissions/roles
"""
from typing import List, Dict
from app.db.seeds.seed_factory import (
    BaseSeeder, SeederMode, SeederStats, 
    GenericPermissionSeeder, GenericRoleSeeder,
    seeder_registry
)

from app.models.permission import Permission
from app.models.role import Role

import logging
import time

logger = logging.getLogger(__name__)

class CRMSeeder(BaseSeeder):
    """
    CRM module seeder implementation.
    Inherits enterprise-grade infrastructure from BaseSeeder.
    Contains only CRM-specific business logic and data.
    """
    
    def get_module_name(self) -> str:
        return "crm"
    
    def should_run_in_mode(self, mode: SeederMode) -> bool:
        """CRM should run in all environments - it's a core module."""
        return True
    
    def get_crm_permissions(self) -> List[Dict[str, str]]:
        """
        Define all CRM permissions.
        This is the single source of truth for CRM permissions across the application.
        """
        # Core CRM permissions (available in all environments)
        core_permissions = [
            {"name": "view_crm", "description": "View customer profiles and sales data"},
            {"name": "edit_crm", "description": "Edit customer records and pipelines"},
            {"name": "create_lead", "description": "Create new leads"},
            {"name": "assign_lead", "description": "Assign leads to team members"},
            {"name": "convert_lead", "description": "Convert leads into customers"},
            {"name": "export_crm_data", "description": "Export CRM data to various formats"},
            {"name": "view_crm_reports", "description": "View CRM analytics and reports"},
        ]
        
        # Development-specific permissions
        if self.mode == SeederMode.DEVELOPMENT:
            core_permissions.extend([
                {"name": "delete_lead", "description": "Delete leads (development only)"},
                {"name": "bulk_import_crm", "description": "Bulk import CRM data (development only)"},
                {"name": "reset_crm_data", "description": "Reset CRM module data (development only)"},
                {"name": "debug_crm", "description": "Access CRM debug features (development only)"},
            ])
        
        # Test-specific permissions
        elif self.mode == SeederMode.TEST:
            core_permissions.extend([
                {"name": "create_test_data", "description": "Create test CRM data (testing only)"},
                {"name": "cleanup_test_data", "description": "Cleanup test CRM data (testing only)"},
            ])
        
        return core_permissions
    
    def get_crm_roles(self) -> Dict[str, List[str]]:
        """
        Define all CRM roles and their permission mappings.
        This encapsulates CRM business logic about who can do what.
        """
        # Core roles for all environments
        core_roles = {
            "crm_manager": [
                "view_crm", "edit_crm", "assign_lead", "convert_lead", 
                "export_crm_data", "view_crm_reports"
            ],
            "crm_agent": [
                "view_crm", "create_lead", "edit_crm"
            ],
            "crm_viewer": [
                "view_crm", "view_crm_reports"
            ],
            "sales_rep": [
                "view_crm", "create_lead", "edit_crm", "assign_lead"
            ],
        }
        
        # Environment-specific roles
        if self.mode == SeederMode.DEVELOPMENT:
            core_roles.update({
                "crm_admin": [
                    "view_crm", "edit_crm", "create_lead", "assign_lead", "convert_lead",
                    "export_crm_data", "view_crm_reports", "delete_lead", 
                    "bulk_import_crm", "reset_crm_data", "debug_crm"
                ],
                "crm_developer": [
                    "view_crm", "create_lead", "delete_lead", "debug_crm", "create_test_data"
                ],
            })
        
        elif self.mode == SeederMode.TEST:
            core_roles.update({
                "test_user": [
                    "view_crm", "create_lead", "create_test_data", "cleanup_test_data"
                ],
            })
        
        return core_roles
    
    def validate_dependencies(self) -> bool:
        """
        Validate CRM-specific dependencies.
        Override the base class to add CRM business rules.
        """
        # Example: CRM requires at least one organization to exist
        from app.models.organization import Organization
        
        org_count = self.db.query(Organization).count()
        if org_count == 0:
            self.log_progress("No organizations found - CRM requires organizations", "warning")
            
            # In development, auto-create default organization
            if self.mode == SeederMode.DEVELOPMENT:
                return self._create_default_organization()
            else:
                self.log_progress("Cannot seed CRM without organizations in production mode", "error")
                return False
        
        self.log_progress(f"Dependencies validated - found {org_count} organizations", "debug")
        return True
    
    def _create_default_organization(self) -> bool:
        """Create default organization for CRM in development mode."""
        try:
            from app.models.organization import Organization
            
            with self.safe_transaction("create_default_org"):
                default_org = Organization(
                    name="Development Organization",
                    description="Auto-created for CRM development and testing"
                )
                self.db.add(default_org)
            
            self.log_progress("Created default organization for CRM development", "info")
            return True
            
        except Exception as e:
            self.log_progress(f"Failed to create default organization: {e}", "error")
            return False
    
    def pre_seed_hook(self):
        """CRM-specific pre-seeding logic."""
        self.log_progress("Starting CRM module seeding", "info")
        
        # Example: Could validate CRM configuration, check external dependencies, etc.
        if self.mode == SeederMode.DEVELOPMENT:
            self.log_progress("Development mode: including test permissions and roles", "debug")
    
    def post_seed_hook(self, stats: SeederStats):
        """CRM-specific post-seeding logic."""
        self.log_progress(f"CRM seeding completed successfully: {stats}", "info")
        
        # Example: Could trigger cache warming, send notifications, etc.
        if stats.errors == 0:
            self.log_progress("CRM module is ready for use", "info")
        else:
            self.log_progress(f"CRM seeding completed with {stats.errors} errors - review logs", "warning")
    
    def seed(self) -> SeederStats:
        """
        Execute CRM seeding using the factory infrastructure.
        This method orchestrates CRM-specific seeding while leveraging shared utilities.
        """
        start_time = time.time()
        
        try:
            self.log_progress(f"Executing CRM seeding in {self.mode.value} mode", "info")
            
            # Seed CRM permissions using generic infrastructure
            with self.safe_transaction("crm_permissions"):
                perm_seeder = GenericPermissionSeeder(self.db, Permission, "crm")
                perm_stats = perm_seeder.upsert_permissions(self.get_crm_permissions())
                self.log_progress(f"Permissions processed: {perm_stats}", "debug")
            
            # Seed CRM roles using generic infrastructure  
            with self.safe_transaction("crm_roles"):
                role_seeder = GenericRoleSeeder(self.db, Role, Permission, "crm")
                role_stats = role_seeder.upsert_roles(self.get_crm_roles())
                self.log_progress(f"Roles processed: {role_stats}", "debug")
            
            # Any additional CRM-specific seeding logic
            self._seed_crm_specific_data()
            
            # Aggregate final statistics
            self.stats.created = perm_stats.created + role_stats.created
            self.stats.updated = perm_stats.updated + role_stats.updated
            self.stats.skipped = perm_stats.skipped + role_stats.skipped
            self.stats.errors = perm_stats.errors + role_stats.errors
            self.stats.duration_ms = int((time.time() - start_time) * 1000)
            
            self.log_progress(f"CRM seeding completed: {self.stats}", "info")
            return self.stats
            
        except Exception as e:
            self.stats.errors += 1
            self.stats.duration_ms = int((time.time() - start_time) * 1000)
            self.log_progress(f"CRM seeding failed after {self.stats.duration_ms}ms: {e}", "error")
            raise
    
    def _seed_crm_specific_data(self):
        """
        Seed CRM-specific data beyond permissions and roles.
        Examples: default pipeline stages, lead sources, customer types, etc.
        """
        try:
            # Example: Create default lead statuses
            self._create_default_lead_statuses()
            
            # Example: Create default pipeline stages
            self._create_default_pipeline_stages()
            
            self.log_progress("CRM-specific data seeded successfully", "debug")
            
        except Exception as e:
            self.log_progress(f"Failed to seed CRM-specific data: {e}", "error")
            raise
    
    def _create_default_lead_statuses(self):
        """Create default lead statuses for CRM."""
        # Example implementation - you'd replace with your actual Lead Status model
        default_statuses = ["new", "contacted", "qualified", "proposal", "closed_won", "closed_lost"]
        
        # This is just an example - implement based on your actual models
        self.log_progress(f"Would create {len(default_statuses)} default lead statuses", "debug")
    
    def _create_default_pipeline_stages(self):
        """Create default sales pipeline stages."""
        # Example implementation
        default_stages = [
            {"name": "Prospecting", "order": 1},
            {"name": "Qualification", "order": 2}, 
            {"name": "Proposal", "order": 3},
            {"name": "Negotiation", "order": 4},
            {"name": "Closing", "order": 5}
        ]
        
        self.log_progress(f"Would create {len(default_stages)} pipeline stages", "debug")

# Register this seeder in the global registry
seeder_registry.register(CRMSeeder)

# Legacy compatibility function for backward compatibility
def seed_crm(db):
    """
    Legacy entry point for CRM seeding.
    Maintains compatibility with existing code while using new factory pattern.
    """
    crm_seeder = CRMSeeder(db, SeederMode.DEVELOPMENT)
    return crm_seeder.seed()