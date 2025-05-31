from app.db import execute_query

async def has_permission(user_id: int, permission: str):
    query = """
    SELECT 1 FROM user_role ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON p.id = rp.permission_id
    WHERE ur.user_id = %s AND p.name = %s
    """
    result = await execute_query(query, (user_id, permission), fetch_one=True)
    return bool(result)

async def get_user_roles(user_id: int):
    roles = await execute_query(
        "SELECT r.name FROM user_role ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = %s",
        (user_id,),
        fetch_all=True
    )
    return [role["name"] for role in roles] if roles else []

async def is_admin(user_id: int):
    return "admin" in get_user_roles(user_id=user_id)