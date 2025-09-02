# backend/app/db/seeds/seed_factory.py
"""
Seeder factory infrastructure - contains ONLY base classes and orchestration logic.
No module-specific data or business logic should be in this file.

This file provides the enterprise-grade foundation that all module seeders inherit from.
It handles transaction safety, performance monitoring, error recovery, and environment management.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Optional
from sqlalchemy.orm import Session
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)

class SeederMode(Enum):
    """Defines seeding behavior modes for different environments."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

@dataclass
class SeederStats:
    """Standardized seeding statistics for monitoring and reporting."""
    module_name: str
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    duration_ms: int = 0
    
    @property
    def total_processed(self) -> int:
        return self.created + self.updated + self.skipped
    
    @property
    def success_rate(self) -> float:
        total = self.total_processed + self.errors
        return (self.total_processed / total * 100) if total > 0 else 100.0
    
    def __str__(self) -> str:
        return (f"{self.module_name}: {self.created} created, {self.updated} updated, "
                f"{self.skipped} skipped, {self.errors} errors ({self.duration_ms}ms)")

class BaseSeeder(ABC):
    """
    Abstract base class providing enterprise-grade infrastructure for all module seeders.
    
    Provides:
    - Transaction safety with automatic rollback
    - Performance monitoring and timing
    - Structured logging with different levels
    - Environment-aware behavior
    - Dependency validation framework
    - Standardized error handling
    
    Module seeders inherit from this and implement only their specific business logic.
    """
    
    def __init__(self, db: Session, mode: SeederMode = SeederMode.DEVELOPMENT):
        self.db = db
        self.mode = mode
        self.stats = SeederStats(module_name=self.get_module_name())
        logger.debug(f"Initialized {self.__class__.__name__} in {mode.value} mode")
        
    @contextmanager
    def safe_transaction(self, operation_name: str = "transaction"):
        """
        Context manager for safe database transactions with performance tracking.
        Automatically handles rollback on errors and logs execution time.
        """
        start_time = time.time()
        savepoint = None
        
        try:
            # Create savepoint for nested transaction safety
            savepoint = self.db.begin_nested()
            logger.debug(f"Starting {operation_name} in {self.__class__.__name__}")
            
            yield self.db
            
            # Commit the savepoint
            savepoint.commit()
            
            duration = int((time.time() - start_time) * 1000)
            logger.debug(f"Completed {operation_name} successfully ({duration}ms)")
            
        except Exception as e:
            if savepoint:
                savepoint.rollback()
            
            self.stats.errors += 1
            duration = int((time.time() - start_time) * 1000)
            logger.error(f"Transaction failed in {operation_name} ({duration}ms): {e}")
            raise
    
    def log_progress(self, message: str, level: str = "info"):
        """Standardized progress logging with module context."""
        full_message = f"[{self.get_module_name().upper()}] {message}"
        getattr(logger, level)(full_message)
    
    @abstractmethod
    def get_module_name(self) -> str:
        """Return the module name for this seeder (e.g., 'crm', 'hr')."""
        pass
    
    @abstractmethod
    def should_run_in_mode(self, mode: SeederMode) -> bool:
        """Determine if this seeder should run in the given environment mode."""
        pass
    
    @abstractmethod
    def seed(self) -> SeederStats:
        """Execute the module's seeding logic and return execution statistics."""
        pass
    
    def validate_dependencies(self) -> bool:
        """
        Override to validate seeder dependencies before execution.
        Return False to skip seeder execution.
        """
        return True
    
    def pre_seed_hook(self):
        """Override to add logic that runs before seeding (e.g., cleanup)."""
        pass
    
    def post_seed_hook(self, stats: SeederStats):
        """Override to add logic that runs after successful seeding."""
        pass

class GenericPermissionSeeder:
    """
    Reusable permission upsert utility.
    Contains NO module-specific logic - pure infrastructure code.
    """
    
    def __init__(self, db: Session, model_class: Type, module_name: str = "permissions"):
        self.db = db
        self.model_class = model_class
        self.module_name = module_name
    
    def upsert_permissions(self, permissions: List[Dict[str, str]], 
                          batch_size: int = 50) -> SeederStats:
        """
        Generic permission upsert with batch processing and conflict resolution.
        
        Args:
            permissions: List of permission dictionaries with 'name' and 'description'
            batch_size: Number of permissions to process per batch
        """
        stats = SeederStats(module_name=f"{self.module_name}_permissions")
        start_time = time.time()
        
        # Process in batches for better performance with large datasets
        for i in range(0, len(permissions), batch_size):
            batch = permissions[i:i + batch_size]
            
            for perm_data in batch:
                try:
                    # Validate data quality
                    if not perm_data.get("name") or not perm_data.get("description"):
                        logger.warning(f"Skipping invalid permission: {perm_data}")
                        stats.skipped += 1
                        continue
                    
                    # Check if permission exists
                    existing = self.db.query(self.model_class).filter(
                        self.model_class.name == perm_data["name"]
                    ).first()
                    
                    if existing:
                        # Update if description changed
                        if existing.description != perm_data["description"]:
                            existing.description = perm_data["description"]
                            stats.updated += 1
                            logger.debug(f"Updated permission: {perm_data['name']}")
                        else:
                            stats.skipped += 1
                    else:
                        # Create new permission
                        new_perm = self.model_class(**perm_data)
                        self.db.add(new_perm)
                        stats.created += 1
                        logger.debug(f"Created permission: {perm_data['name']}")
                        
                except Exception as e:
                    logger.error(f"Failed to process permission {perm_data.get('name', 'unknown')}: {e}")
                    stats.errors += 1
                    raise
        
        stats.duration_ms = int((time.time() - start_time) * 1000)
        return stats

class GenericRoleSeeder:
    """
    Reusable role upsert utility.
    Contains NO module-specific logic - pure infrastructure code.
    """
    
    def __init__(self, db: Session, role_model: Type, permission_model: Type, 
                 module_name: str = "roles"):
        self.db = db
        self.role_model = role_model
        self.permission_model = permission_model
        self.module_name = module_name
    
    def upsert_roles(self, roles: Dict[str, List[str]], 
                    validate_permissions: bool = True) -> SeederStats:
        """
        Generic role upsert with permission assignment and validation.
        
        Args:
            roles: Dictionary mapping role names to permission name lists
            validate_permissions: Whether to validate all permissions exist
        """
        stats = SeederStats(module_name=f"{self.module_name}_roles")
        start_time = time.time()
        
        # Build permission lookup once for efficiency
        perm_lookup = {p.name: p for p in self.db.query(self.permission_model).all()}
        
        if not perm_lookup:
            logger.error("No permissions found in database - cannot create roles")
            stats.errors += 1
            return stats
        
        for role_name, perm_names in roles.items():
            try:
                # Validate permissions if requested
                if validate_permissions:
                    missing_perms = [p for p in perm_names if p not in perm_lookup]
                    if missing_perms:
                        error_msg = f"Missing permissions for role {role_name}: {missing_perms}"
                        logger.error(error_msg)
                        stats.errors += 1
                        raise ValueError(error_msg)
                
                # Check if role exists
                existing_role = self.db.query(self.role_model).filter(
                    self.role_model.name == role_name
                ).first()
                
                target_permissions = [perm_lookup[p] for p in perm_names if p in perm_lookup]
                
                if existing_role:
                    # Check if permissions changed
                    current_perm_names = {p.name for p in existing_role.permissions}
                    target_perm_names = {p.name for p in target_permissions}
                    
                    if current_perm_names != target_perm_names:
                        existing_role.permissions = target_permissions
                        stats.updated += 1
                        logger.debug(f"Updated role: {role_name}")
                    else:
                        stats.skipped += 1
                        logger.debug(f"Role unchanged: {role_name}")
                else:
                    # Create new role
                    new_role = self.role_model(name=role_name, is_default=False)
                    new_role.permissions = target_permissions
                    self.db.add(new_role)
                    stats.created += 1
                    logger.debug(f"Created role: {role_name} with {len(target_permissions)} permissions")
                    
            except Exception as e:
                logger.error(f"Failed to process role {role_name}: {e}")
                stats.errors += 1
                raise
        
        stats.duration_ms = int((time.time() - start_time) * 1000)
        return stats

class SeederOrchestrator:
    """
    Enterprise-grade orchestrator for managing multiple module seeders.
    Provides dependency resolution, execution coordination, and comprehensive monitoring.
    Contains NO module-specific logic - only orchestration infrastructure.
    """
    
    def __init__(self, db: Session, mode: SeederMode = SeederMode.DEVELOPMENT):
        self.db = db
        self.mode = mode
        self.seeders: List[BaseSeeder] = []
        self.execution_stats: List[SeederStats] = []
        logger.info(f"Initialized SeederOrchestrator in {mode.value} mode")
    
    def register_seeder(self, seeder_class: Type[BaseSeeder]) -> 'SeederOrchestrator':
        """
        Register a module seeder for execution.
        
        Args:
            seeder_class: Class that inherits from BaseSeeder
        """
        try:
            seeder = seeder_class(self.db, self.mode)
            
            if seeder.should_run_in_mode(self.mode):
                self.seeders.append(seeder)
                logger.info(f"✅ Registered seeder: {seeder.get_module_name()}")
            else:
                logger.info(f"⏭️  Skipped seeder: {seeder.get_module_name()} (not enabled for {self.mode.value})")
                
        except Exception as e:
            logger.error(f"Failed to register seeder {seeder_class.__name__}: {e}")
            raise
            
        return self
    
    def execute_all(self, fail_fast: Optional[bool] = None) -> List[SeederStats]:
        """
        Execute all registered seeders with comprehensive error handling.
        
        Args:
            fail_fast: Stop on first error. Defaults to True for production, False for development.
        """
        if fail_fast is None:
            fail_fast = self.mode == SeederMode.PRODUCTION
        
        start_time = time.time()
        logger.info(f"🚀 Starting orchestrated seeding ({len(self.seeders)} modules, fail_fast={fail_fast})")
        
        for i, seeder in enumerate(self.seeders, 1):
            module_name = seeder.get_module_name()
            
            try:
                logger.info(f"[{i}/{len(self.seeders)}] Executing {module_name} seeder...")
                
                # Validate dependencies before execution
                if not seeder.validate_dependencies():
                    error_msg = f"Dependencies not met for {module_name}"
                    logger.error(error_msg)
                    
                    if fail_fast:
                        raise ValueError(error_msg)
                    else:
                        # Create error stats for failed dependency
                        error_stats = SeederStats(module_name=module_name, errors=1)
                        self.execution_stats.append(error_stats)
                        continue
                
                # Execute pre-seed hook
                seeder.pre_seed_hook()
                
                # Execute seeding
                stats = seeder.seed()
                self.execution_stats.append(stats)
                
                # Execute post-seed hook
                seeder.post_seed_hook(stats)
                
                logger.info(f"✅ Completed {module_name}: {stats}")
                
            except Exception as e:
                error_msg = f"Seeder {module_name} failed: {e}"
                logger.error(error_msg)
                
                if fail_fast:
                    logger.critical(f"Stopping execution due to {module_name} failure (fail_fast=True)")
                    raise
                else:
                    # Create error stats for failed seeder
                    error_stats = SeederStats(module_name=module_name, errors=1)
                    self.execution_stats.append(error_stats)
                    logger.warning(f"Continuing despite {module_name} failure (fail_fast=False)")
        
        total_duration = int((time.time() - start_time) * 1000)
        self._print_execution_summary(total_duration)
        
        return self.execution_stats
    
    def _print_execution_summary(self, total_duration: int):
        """Print comprehensive execution summary with visual formatting."""
        if not self.execution_stats:
            print("⚠️  No seeders were executed")
            return
        
        # Calculate aggregate statistics
        total_created = sum(s.created for s in self.execution_stats)
        total_updated = sum(s.updated for s in self.execution_stats)
        total_skipped = sum(s.skipped for s in self.execution_stats)
        total_errors = sum(s.errors for s in self.execution_stats)
        avg_success_rate = sum(s.success_rate for s in self.execution_stats) / len(self.execution_stats)
        
        # Print header
        print(f"\n{'='*60}")
        print(f"🎯 SEEDING ORCHESTRATION COMPLETE")
        print(f"{'='*60}")
        
        # Print overall statistics
        print(f"⏱️  Total Duration: {total_duration}ms")
        print(f"🏷️  Environment: {self.mode.value.upper()}")
        print(f"📊 Overall Stats: {total_created} created, {total_updated} updated, {total_skipped} skipped")
        print(f"📈 Success Rate: {avg_success_rate:.1f}%")
        
        if total_errors > 0:
            print(f"❌ Errors: {total_errors}")
        
        # Print module breakdown
        print(f"\n📋 Module Execution Results:")
        print(f"{'-'*60}")
        
        for stats in self.execution_stats:
            status_icon = "✅" if stats.errors == 0 else "❌"
            success_rate = f"({stats.success_rate:.0f}%)" if stats.total_processed > 0 else ""
            print(f"   {status_icon} {stats} {success_rate}")
        
        print(f"{'='*60}\n")
        
        # Log summary for monitoring systems
        logger.info(f"Orchestration summary: {len(self.execution_stats)} modules, "
                   f"{total_created + total_updated} operations, {total_errors} errors, {total_duration}ms")

class SeederRegistry:
    """
    Registry for managing available seeders across the application.
    Provides discovery and validation of seeder implementations.
    """
    
    def __init__(self):
        self._seeders: Dict[str, Type[BaseSeeder]] = {}
    
    def register(self, seeder_class: Type[BaseSeeder]):
        """Register a seeder class in the global registry."""
        if not issubclass(seeder_class, BaseSeeder):
            raise ValueError(f"{seeder_class.__name__} must inherit from BaseSeeder")
        
        # Get module name from seeder instance (temporary instance for validation)
        temp_db = None  # We don't need a real session for module name
        try:
            module_name = seeder_class.__new__(seeder_class).get_module_name()
        except:
            raise ValueError(f"Could not determine module name for {seeder_class.__name__}")
        
        if module_name in self._seeders:
            logger.warning(f"Overriding existing seeder for module: {module_name}")
        
        self._seeders[module_name] = seeder_class
        logger.debug(f"Registered seeder: {module_name} -> {seeder_class.__name__}")
    
    def get_seeder(self, module_name: str) -> Optional[Type[BaseSeeder]]:
        """Get seeder class by module name."""
        return self._seeders.get(module_name)
    
    def list_modules(self) -> List[str]:
        """List all registered module names."""
        return list(self._seeders.keys())
    
    def create_orchestrator(self, db: Session, mode: SeederMode, 
                          modules: Optional[List[str]] = None) -> SeederOrchestrator:
        """
        Create an orchestrator with specified modules.
        
        Args:
            modules: List of module names to include. If None, includes all registered modules.
        """
        orchestrator = SeederOrchestrator(db, mode)
        
        target_modules = modules or self.list_modules()
        
        for module_name in target_modules:
            seeder_class = self.get_seeder(module_name)
            if seeder_class:
                orchestrator.register_seeder(seeder_class)
            else:
                logger.warning(f"No seeder registered for module: {module_name}")
        
        return orchestrator

# Global seeder registry instance
seeder_registry = SeederRegistry()