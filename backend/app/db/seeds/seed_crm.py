from app.models.permission import Permission
from app.models.role import Role

def seed_crm(db):
    # Define CRM-related permissions
    crm_permissions = [
        {"name": "view_crm", "description": "View customer profiles and sales data"},
        {"name": "edit_crm", "description": "Edit customer records and pipelines"},
        {"name": "create_lead", "description": "Create new leads"},
        {"name": "assign_lead", "description": "Assign leads to team members"},
        {"name": "convert_lead", "description": "Convert leads into customers"},
    ]

    for data in crm_permissions:
        perm = Permission(**data)
        db.merge(perm)
    db.commit()
    print("✅ CRM permissions seeded.")

    # Reload permissions to fetch their DB IDs
    perm_lookup = {p.name: p for p in db.query(Permission).all()}

    crm_roles = {
        "crm_manager": ["view_crm", "edit_crm", "assign_lead", "convert_lead"],
        "crm_agent": ["view_crm", "create_lead"],
    }

    for role_name, perms in crm_roles.items():
        role = Role(name=role_name, is_default=False)
        role.permissions = [perm_lookup[p] for p in perms]
        db.merge(role)
    db.commit()
    print("✅ CRM roles seeded.")