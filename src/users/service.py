import bcrypt
import aiosqlite
from fastapi import HTTPException, status
from src.users.schemas import UserRegisterSchema


def get_password_hash(password: str) -> str:
    pwd_encoded = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_encoded, salt).decode("utf-8")


async def get_user_by_id(user_id: int, db: aiosqlite.Connection) -> dict:
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return dict(row)


async def register_new_user(user: UserRegisterSchema, db: aiosqlite.Connection) -> dict:
    cursor = await db.execute(
        "SELECT id FROM users WHERE lower(email) = lower(?) AND is_deleted = 0",
        (user.email,),
    )
    if await cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    cursor = await db.execute(
        "SELECT id FROM users WHERE lower(email) = lower(?) AND is_deleted = 1",
        (user.email,),
    )
    if await cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is registered but inactive.",
        )
    hashed_password = get_password_hash(user.password)
    cursor = await db.execute(
        "INSERT INTO users (email, username, password) VALUES (?, ?, ?) RETURNING *",
        (user.email, user.username, hashed_password),
    )
    row = await cursor.fetchone()
    await db.commit()
    return dict(row)


async def delete_user(user_id: int, db: aiosqlite.Connection) -> dict:
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = dict(row)
    if user["is_deleted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already deleted"
        )
    await db.execute(
        "UPDATE users SET is_deleted = 1, is_active = 0, token_version = token_version + 1 WHERE id = ?",
        (user_id,),
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return dict(await cursor.fetchone())


async def invalidate_user_token(user_id: int, db: aiosqlite.Connection) -> None:
    cursor = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not await cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await db.execute(
        "UPDATE users SET token_version = token_version + 1 WHERE id = ?",
        (user_id,),
    )
    await db.commit()


async def update_user(
    user_id: int, update_data: dict, db: aiosqlite.Connection
) -> dict:
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = dict(row)

    if "email" in update_data and not user["is_deleted"]:
        cursor = await db.execute(
            "SELECT id FROM users WHERE lower(email) = lower(?) AND id != ?",
            (update_data["email"], user_id),
        )
        if await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    set_clauses = ", ".join(f"{key} = ?" for key in update_data)
    values = list(update_data.values()) + [user_id]
    await db.execute(f"UPDATE users SET {set_clauses} WHERE id = ?", values)
    await db.commit()
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return dict(await cursor.fetchone())
