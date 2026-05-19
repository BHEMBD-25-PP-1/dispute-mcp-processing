AUTH_ERROR = {
    "description": "Не авторизован",
    "content": {"application/json": {"example": {"message": "Invalid token", "code": "AUTH_ERROR"}}},
}

FORBIDDEN_ERROR = {
    "description": "Доступ запрещен",
    "content": {"application/json": {"example": {"message": "Forbidden", "code": "FORBIDDEN_ERROR"}}},
}

VALIDATION_ERROR = {
    "description": "Ошибка валидации",
    "content": {
        "application/json": {
            "example": {
                "message": "Ошибка валидации",
                "code": "VALIDATION_ERROR",
                "details": [],
            }
        }
    },
}
