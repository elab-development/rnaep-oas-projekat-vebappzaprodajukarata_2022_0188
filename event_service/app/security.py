from fastapi import Header, HTTPException


def get_current_user_role(x_user_role: str | None = Header(default=None)):
    if x_user_role is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authenticated user role"
        )

    return x_user_role


def require_admin(x_user_role: str | None = Header(default=None)):
    if x_user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )

    return x_user_role