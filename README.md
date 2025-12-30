# Custom Authentication & Authorization Backend (Django)

## Описание проекта

Данный проект представляет собой минимальное backend-приложение с полностью кастомной системой аутентификации и авторизации, реализованной без использования механизмов Django «из коробки».

Аутентификация основана исключительно на JWT.  
Авторизация реализована на базе ролевой модели доступа (RBAC) с поддержкой ownership.

---

## Архитектура проекта

Проект разделен на логические слои:

core/

├── models/ # ORM-модели (только данные)

├── services/ # Бизнес-логика (auth, jwt, permissions)

├── middleware/ # JWT middleware (установка request.user)

└── management/ # Команды и фикстуры

api/

├── views/ # API endpoints (тонкие контроллеры)

└── urls.py

### Принципы архитектуры

- Четкое разделение ответственности
- Вся бизнес-логика вынесена в `services`
- Middleware отвечает только за идентификацию пользователя
- `request.user` имеет единый источник истины
- Никакого дублирования логики аутентификации и авторизации

---

## Аутентификация

### JWT

Используется JWT access-token.

Payload токена:
- `user_id`
- `email`
- `is_admin`
- `token_version`
- `iat`
- `exp`

Токен передается через заголовок:

Authorization: Bearer <jwt_token>

### Пароли

- Пароли хэшируются с помощью `bcrypt`
- Хранение паролей в открытом виде исключено

### Logout

- Logout реализован через:
  - инкремент `token_version` у пользователя **или**
  - добавление токена в blacklist
- После logout токен считается недействительным

### Удаление аккаунта

- Реализовано мягкое удаление (`soft delete`)
- Пользователь помечается как `is_active = false`
- Все активные токены инвалидируются
- Повторный login невозможен

---

## Авторизация (RBAC)

Используется ролевая модель доступа.

### Основные сущности

#### Roles
Описывает роли пользователей:
- admin
- manager
- user
- guest

#### Business Elements
Описывает ресурсы приложения:
- users
- products
- orders
- stores
- roles
- access_rules

#### Access Rules
Связывает роли и бизнес-элементы, определяя разрешенные действия.

Права доступа:
- `read`
- `read_all`
- `create`
- `update`
- `update_all`
- `delete`
- `delete_all`

Все поля прав имеют тип `boolean`.

---

## Проверка доступа

- **401 Unauthorized** — пользователь не аутентифицирован
- **403 Forbidden** — доступ запрещен правилами

Проверка доступа реализована централизованно в permission-service.

---

## Mock бизнес-объекты

Для демонстрации системы реализованы mock-endpoint’ы без реальных таблиц:

- users
- products
- orders
- stores

Mock-endpoint’ы:
- не содержат бизнес-логики
- проходят через ту же систему аутентификации и авторизации
- возвращают статические данные или ошибки доступа

---

## Admin API

Доступно только для пользователей с ролью `admin`.

Функциональность:
- CRUD ролей
- CRUD бизнес-элементов
- CRUD правил доступа
- Назначение ролей пользователям

---


Запуск проекта
1. Клонировать репозиторий

git clone <repo_url>
cd project

2. Создать .env

cp .env.example .env

3. Запуск через Docker

docker-compose up --build

## API Endpoints

Все POST кроме register/login требуют JWT

POST /auth/register/
POST /auth/login/
POST /auth/logout/
POST /auth/delete/
POST /admin/roles/
POST /admin/access-rules/
POST /admin/assign-role/

GET /mock/products/
GET /admin/roles/
GET /admin/access-rules/


