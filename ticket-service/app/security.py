from fastapi import Header, HTTPException


def get_current_user_id(x_user_id: int | None = Header(default=None)):
    if x_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authenticated user id"
        )

    return x_user_id