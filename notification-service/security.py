from fastapi import Header, HTTPException

def get_current_user_id(x_user_id: int | None = Header(default=None)):
    if x_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authenticated user id"
        )
    return x_user_id

def get_current_user_role(x_user_role: str | None = Header(default=None)):
    if x_user_role is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authenticated user role"
        )
    return x_user_role