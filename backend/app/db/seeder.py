# backend/app/db/seeder.py
"""
Main seeder orchestrator - imports module seeders and coordinates execution.
Contains NO module-specific logic - only orchestration and CLI interface.

This file is the entry point for all seeding operations and provides:
- Environment detection and mode selection
- Schema creation coordination (until Alembic migration)
- Module seeder registration and execution
- CLI interface with comprehensive options
- Comprehensive logging and error reporting
"""

from app.models.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.db.seeds.seed_factory import SeederMode, SeederOrchestrator, seeder_registry

# Import module seeders to trigger registration
from app.db.seeds.seed_crm import CRMSeeder
# from app.db.seeds.seed_hr import HRSeeder        # Add when ready
# from app.db.seeds.seed_inventory import InventorySeeder  # Add when ready
# from app.db.seeds.seed_finance import FinanceSeeder      # Add when ready

# Legacy seeders (TODO: Convert to factory pattern)
from app.db.seeds import seed_leads, seed_superuser, seed_users

import logging
import sys
import time
from typing import Optional, List

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/seeder.log', mode='a')  # Log to file for audit trail
    ]
)
logger = logging.getLogger(__name__)

def determine_seeding_mode() -> SeederMode:
    """
    Determine seeding mode from environment configuration.
    Provides intelligent defaults based on deployment environment.
    """
    env = getattr(settings, 'ENV', 'development').lower()
    
    mode_mapping = {
        'development': SeederMode.DEVELOPMENT,
        'dev': SeederMode.DEVELOPMENT,
        'staging': SeederMode.PRODUCTION,
        'prod': SeederMode.PRODUCTION,
        'production': SeederMode.PRODUCTION,
        'test': SeederMode.TEST,
        'testing': SeederMode.TEST
    }
    
    detected_mode = mode_mapping.get(env, SeederMode.DEVELOPMENT)
    logger.info(f"Environment '{env}' mapped to seeding mode: {detected_mode.value}")
    
    return detected_mode

def create_schema_if_needed(db_session) -> bool:
    """
    Create database schema if it doesn't exist.
    
    TODO: Replace with proper Alembic migrations in production.
    This is a temporary solution for development convenience.
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("No existing tables found - creating database schema")
            Base.metadata.create_all(bind=engine)
            logger.info(f"✅ Database schema created successfully")
            return True
        else:
            logger.info(f"Found {len(existing_tables)} existing tables - skipping schema creation")
            logger.debug(f"Existing tables: {', '.join(existing_tables)}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to create database schema: {e}")
        raise

def seed_legacy_modules(db_session, mode: SeederMode) -> None:
    """
    Seed modules that haven't been converted to factory pattern yet.
    
    TODO: Convert these modules to factory pattern and remove this function.
    This is temporary compatibility code.
    """
    try:
        if mode == SeederMode.DEVELOPMENT:
            logger.info("Seeding legacy modules (development mode only)...")
            
            # Seed test leads
            seed_leads.seed_leads(db_session)
            
            # Seed development users
            seed_users.seed_test_user()
            seed_superuser.seed_superuser()
            
            logger.info("✅ Legacy modules seeded successfully")
        else:
            logger.info(f"Skipping legacy modules in {mode.value} mode (development only)")
            
    except Exception as e:
        logger.error(f"Legacy module seeding failed: {e}")
        
        # In production, legacy failures should stop the process
        if mode == SeederMode.PRODUCTION:
            logger.critical("Legacy seeding failure in production - stopping")
            raise
        else:
            logger.warning("Continuing despite legacy seeding errors (non-production mode)")

def seed_all(mode: Optional[SeederMode] = None, modules: Optional[List[str]] = None) -> None:
    """
    Main seeding orchestrator function.
    
    Args:
        mode: Override the seeding mode (otherwise auto-detected from environment)
        modules: List of specific modules to seed (otherwise seeds all registered modules)
    """
    
    # Determine seeding mode
    if mode is None:
        mode = determine_seeding_mode()
    
    logger.info(f"🌱 Starting database seeding process")
    logger.info(f"🏷️  Mode: {mode.value}")
    logger.info(f"📦 Modules: {modules or 'all registered modules'}")
    
    overall_start_time = time.time()
    db_session = SessionLocal()
    
    try:
        # Create schema if needed (TODO: replace with Alembic migrations)
        schema_created = create_schema_if_needed(db_session)
        
        if schema_created:
            logger.info("🆕 New database detected - running complete seeding process")
        else:
            logger.info("🔄 Existing database - running incremental seeding")
        
        # Execute factory pattern seeders
        logger.info("🏭 Starting factory pattern seeders...")
        
        # Create orchestrator and register seeders
        orchestrator = seeder_registry.create_orchestrator(db_session, mode, modules)
        
        # Execute all registered seeders
        factory_stats = orchestrator.execute_all()
        
        # Execute legacy seeders (temporary until they're converted)
        logger.info("🔙 Processing legacy seeders...")
        seed_legacy_modules(db_session, mode)
        
        # Calculate and report final results
        total_duration = int((time.time() - overall_start_time) * 1000)
        total_operations = sum(s.total_processed for s in factory_stats) if factory_stats else 0
        total_errors = sum(s.errors for s in factory_stats) if factory_stats else 0
        
        # Success summary
        print(f"\n🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total Execution Time: {total_duration}ms")
        print(f"🏷️  Environment Mode: {mode.value.upper()}")
        print(f"📈 Total Operations: {total_operations}")
        
        if total_errors > 0:
            print(f"⚠️  Warning: {total_errors} errors encountered (check logs for details)")
        else:
            print(f"✨ Perfect execution - zero errors!")
        
        logger.info(f"🏁 Seeding orchestration completed successfully in {total_duration}ms")
        
    except Exception as e:
        total_duration = int((time.time() - overall_start_time) * 1000)
        logger.error(f"💥 Critical seeding failure after {total_duration}ms: {e}")
        print(f"\n💥 SEEDING FAILED: {e}")
        print(f"📝 Check logs/seeder.log for detailed error information")
        raise
        
    finally:
        db_session.close()
        logger.debug("Database session closed")

def list_available_modules() -> List[str]:
    """List all registered module seeders for CLI help."""
    return seeder_registry.list_modules()

def main():
    """
    CLI entry point with comprehensive argument parsing and help.
    Provides flexible interface for different seeding scenarios.
    """
    import argparse
    
    # Get available modules for help text
    available_modules = list_available_modules()
    modules_help = f"Available modules: {', '.join(available_modules)}" if available_modules else "No modules registered"
    
    parser = argparse.ArgumentParser(
        description="ERP Database Seeder with Factory Pattern",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python -m app.db.seeder                           # Auto-detect mode, seed all modules
  python -m app.db.seeder --mode development        # Force development mode
  python -m app.db.seeder --mode production         # Force production mode  
  python -m app.db.seeder --modules crm hr          # Seed only CRM and HR modules
  python -m app.db.seeder -v                        # Verbose logging
  python -m app.db.seeder --list-modules            # Show available modules

{modules_help}
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["development", "production", "test"],
        default=None,
        help="Override seeding mode (default: auto-detect from environment)"
    )
    
    parser.add_argument(
        "--modules",
        nargs="+",
        metavar="MODULE",
        help="Seed only specific modules (default: all registered modules)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Enable verbose debug logging"
    )
    
    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="List all available module seeders and exit"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be seeded without making changes (future feature)"
    )
    
    args = parser.parse_args()
    
    # Handle list modules request
    if args.list_modules:
        modules = list_available_modules()
        if modules:
            print("Available module seeders:")
            for module in sorted(modules):
                print(f"  • {module}")
        else:
            print("No module seeders registered")
        sys.exit(0)
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Parse mode argument
    mode = SeederMode(args.mode) if args.mode else None
    if args.mode:
        logger.info(f"Mode override specified: {args.mode}")
    
    # Validate modules if specified
    modules = None
    if args.modules:
        available = list_available_modules()
        invalid_modules = [m for m in args.modules if m not in available]
        if invalid_modules:
            print(f"❌ Invalid modules: {', '.join(invalid_modules)}")
            print(f"Available modules: {', '.join(available)}")
            sys.exit(1)
        modules = args.modules
        logger.info(f"Module filter specified: {modules}")
    
    # Handle dry run (future feature)
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No database changes will be made")
        print("🔍 Dry run functionality not yet implemented")
        print("This feature will show what would be seeded without making changes")
        sys.exit(0)
    
    # Execute seeding
    try:
        seed_all(mode, modules)
        print(f"\n🚀 SUCCESS: Database seeding completed!")
        print(f"🎯 Your ERP system is ready for {(mode or determine_seeding_mode()).value} environment")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("Seeding interrupted by user")
        print(f"\n⏹️  Seeding interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.critical(f"Seeding process failed: {e}")
        print(f"\n💥 CRITICAL FAILURE: {e}")
        print(f"📝 Detailed logs available in: logs/seeder.log")
        print(f"🔧 Check your database connection and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()# backend/app/db/seeder.py
"""
Main seeder orchestrator - imports module seeders and coordinates execution.
Contains NO module-specific logic - only orchestration and CLI interface.
"""

from app.models.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.db.seeds.seed_factory import SeederMode, SeederOrchestrator

# Import module seeders
from app.db.seeds.seed_crm import CRMSeeder
# from app.db.seeds.seed_hr import HRSeeder        # Future
# from app.db.seeds.seed_inventory import InventorySeeder  # Future

# Legacy seeders (to be converted)
from app.db.seeds import seed_leads, seed_superuser, seed_users

import logging
import sys
import time
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def determine_seeding_mode() -> SeederMode:
    """Determine seeding mode from environment."""
    env = getattr(settings, 'ENV', 'development').lower()
    
    return {
        'development': SeederMode.DEVELOPMENT,
        'staging': SeederMode.PRODUCTION,
        'production': SeederMode.PRODUCTION,
        'test': SeederMode.TEST
    }.get(env, SeederMode.DEVELOPMENT)

def create_schema_if_needed(db_session) -> bool:
    """Create schema if needed (TODO: replace with Alembic)."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if not inspector.get_table_names():
            logger.info("Creating database schema...")
            Base.metadata.create_all(bind=engine)
            return True
        return False
    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        raise

def seed_legacy_modules(db_session, mode: SeederMode) -> None:
    """
    Temporary function for modules not yet converted to factory pattern.
    TODO: Convert these to factory pattern and remove this function.
    """
    if mode == SeederMode.DEVELOPMENT:
        try:
            seed_leads.seed_leads(db_session)
            seed_users.seed_test_user()
            seed_superuser.seed_superuser()
            logger.info("✅ Legacy modules seeded")
        except Exception as e:
            logger.error(f"Legacy seeding failed: {e}")
            if mode == SeederMode.PRODUCTION:
                raise

def seed_all(mode: Optional[SeederMode] = None) -> None:
    """
    Main seeding orchestrator - coordinates all module seeders.
    """
    if mode is None:
        mode = determine_seeding_mode()
    
    logger.info(f"🌱 Starting seeding in {mode.value} mode")
    start_time = time.time()
    
    db_session = SessionLocal()
    
    try:
        # Create schema if needed
        schema_created = create_schema_if_needed(db_session)
        if schema_created:
            logger.info("New database - running full seeding")
        
        # Execute factory pattern seeders
        orchestrator = SeederOrchestrator(db_session, mode)
        
        # Register module seeders (each in their own file)
        orchestrator.register_seeder(CRMSeeder)
        # orchestrator.register_seeder(HRSeeder)         # Add when ready
        # orchestrator.register_seeder(InventorySeeder)  # Add when ready
        
        # Execute all registered seeders
        factory_stats = orchestrator.execute_all()
        
        # Run legacy seeders (temporary)
        seed_legacy_modules(db_session, mode)
        
        # Final summary
        total_duration = int((time.time() - start_time) * 1000)
        print(f"\n🚀 Seeding completed in {total_duration}ms!")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        db_session.close()

def main():
    """CLI entry point with enhanced argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ERP Database Seeder")
    parser.add_argument("--mode", choices=["development", "production", "test"])
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    mode = SeederMode(args.mode) if args.mode else None
    
    try:
        seed_all(mode)
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Critical failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()