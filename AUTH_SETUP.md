# Инструкция по запуску авторизации

## 1. Подготовка — сгенерируйте ключ шифрования


Создай `.env` :

Сгенерируй JWT_SECRET и вставь в `.env`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` должен выглядеть так:
```
DATABASE_URL=postgresql+asyncpg://dispute:dispute@postgres:5432/dispute
JWT_SECRET=сюда_вставить_сгенерированный_ключ
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
```

---

## 2. Запуск

```bash
docker compose up --build
```

После запуска API доступно на `http://localhost:8000`.
Документация Swagger: `http://localhost:8000/docs`.

---

## 3. Первый вход — создание администратора

При первом запуске в базе нет ни одного пользователя. Нужно создать администратора вручную через базу данных.

Подключись к контейнеру PostgreSQL:
```bash
docker exec -it dispute-postgres psql -U dispute -d dispute
```

Вставь администратора (пароль `admin123` уже захеширован):
```sql
INSERT INTO users (id, username, password_hash, role, "createdAt")
VALUES (
    gen_random_uuid(),
    'admin',
    '$2b$12$6TqhfxoiPk5DiFE/SdxSzOJhT/rtFjSQHXecVGBaG/xVR4LQlk/eK',
    'ADMIN',
    now()
);
```

Создастся админ, с которым можно логиниться через `POST /api/v1/login` 
 
> {
  "username": "admin",
  "password": "admin123"
}

После входа пароль можно поменять через `PATCH /api/v1/change-password`


---

## 4. Роли пользователей

Ранее уже создали первого администратора. Далее администратор может создавать операторов. 

| Роль | Что может |
|------|-----------|
| ADMIN | Создавать пользователей, смотреть список пользователей, менять свой пароль |
| OPERATOR | Только менять свой пароль и работать с диспутами |