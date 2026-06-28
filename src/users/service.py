import json
import logging
import os
import bcrypt
from fastapi import HTTPException, status
from src.users.schemas import UserRegisterSchema

JSON_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def get_password_hash(password: str) -> str:
    pwd_encoded = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_encoded, salt).decode("utf-8")


def load_users_from_file() -> list[dict]:
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from users.json")
        return []


def save_users_to_file(users: list[dict]) -> None:
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


def get_user_by_id(user_id: int) -> dict:
    users = load_users_from_file()
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def register_new_user(user: UserRegisterSchema) -> dict:
    users = load_users_from_file()

    if any(
        user_existing["email"].lower() == user.email.lower()
        for user_existing in users
        if user_existing["is_deleted"] is False
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if any(
        user_existing["email"].lower() == user.email.lower()
        for user_existing in users
        if user_existing["is_deleted"] is True
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is registered but inactive.",
        )

    hashed_password = get_password_hash(user.password)
    new_id = max([user["id"] for user in users], default=0) + 1
    new_user = {
        "id": new_id,
        "email": user.email,
        "username": user.username,
        "password": hashed_password,
        "is_active": False,
        "is_deleted": False,
        "token_version": 0,
        "role": "user",
    }

    users.append(new_user)
    save_users_to_file(users)

    return new_user


def delete_user(user_id: int) -> dict:
    users = load_users_from_file()
    user_to_delete = None
    for user in users:
        if user["id"] == user_id:
            user_to_delete = user
            break
    if user_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_to_delete["is_deleted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already deleted"
        )
    users[users.index(user_to_delete)]["is_deleted"] = True
    users[users.index(user_to_delete)]["is_active"] = False
    users[users.index(user_to_delete)]["token_version"] = (
        users[users.index(user_to_delete)].get("token_version", 0) + 1
    )
    save_users_to_file(users)
    return user_to_delete


def invalidate_user_token(user_id: int) -> dict:
    users = load_users_from_file()
    find_user = False
    for user in users:
        if user["id"] == user_id:
            user["token_version"] = user.get("token_version", 0) + 1
            save_users_to_file(users)
            find_user = True
            break

    if not find_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


def update_user(user_id: int, update_data: dict) -> dict:
    users = load_users_from_file()
    user_to_update = None
    for user in users:
        if user["id"] == user_id:
            user_to_update = user
            break

    if user_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if "email" in update_data and not user_to_update["is_deleted"]:
        for user_existing in users:
            if (
                user_existing["email"].lower() == update_data["email"].lower()
                and user_existing["id"] != user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

    for key, value in update_data.items():
        if value is not None:
            user_to_update[key] = value

    save_users_to_file(users)
    return user_to_update
