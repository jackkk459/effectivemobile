"""
Django команда для заполнения базы данных тестовыми данными.
Использование: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import AccessRule, BusinessElement, Role, User, UserRole
from core.services.auth import hash_password


class Command(BaseCommand):
    help = (
        "Заполняет базу данных начальными данными (пользователи, роли, правила доступа)"
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE("Начинаю заполнение базы данных тестовыми данными...")
        )

        try:
            with transaction.atomic():
                self._create_business_elements()
                self._create_roles()
                self._create_users()
                self._assign_roles()
                self._create_access_rules()

            self.stdout.write(
                self.style.SUCCESS("✅ Успешно заполнил базу данных тестовыми данными!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка при заполнении данных: {e}"))
            raise

    def _create_business_elements(self):
        """Создание бизнес-элементов системы."""
        elements = [
            "products",
            "users",
            "roles",
            "access_rules",
        ]

        for element_name in elements:
            BusinessElement.objects.get_or_create(name=element_name)
            self.stdout.write(f"  ✓ Создал бизнес-элемент: {element_name}")

    def _create_roles(self):
        """Создание ролей пользователей."""
        roles_data = [
            {"name": "admin", "description": "Администратор системы"},
            {"name": "manager", "description": "Менеджер"},
            {"name": "user", "description": "Обычный пользователь"},
            {"name": "guest", "description": "Гость (только чтение)"},
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data["name"], defaults={"name": role_data["name"]}
            )
            status = "создана" if created else "уже существует"
            self.stdout.write(f"  ✓ Роль {role.name} - {status}")

    def _create_users(self):
        """Создание тестовых пользователей."""
        users_data = [
            {
                "email": "admin@example.com",
                "first_name": "Иван",
                "last_name": "Петров",
                "patronymic": "Сергеевич",
                "password": "admin123",
                "roles": ["admin"],
            },
            {
                "email": "manager@example.com",
                "first_name": "Анна",
                "last_name": "Сидорова",
                "patronymic": "Ивановна",
                "password": "manager123",
                "roles": ["manager"],
            },
            {
                "email": "user1@example.com",
                "first_name": "Дмитрий",
                "last_name": "Кузнецов",
                "patronymic": "Александрович",
                "password": "user123",
                "roles": ["user"],
            },
            {
                "email": "user2@example.com",
                "first_name": "Ольга",
                "last_name": "Смирнова",
                "patronymic": "Викторовна",
                "password": "user123",
                "roles": ["user"],
            },
            {
                "email": "guest@example.com",
                "first_name": "Сергей",
                "last_name": "Васильев",
                "patronymic": "Петрович",
                "password": "guest123",
                "roles": ["guest"],
            },
        ]

        for user_data in users_data:
            email = user_data["email"]

            # Проверяем, существует ли пользователь
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "patronymic": user_data["patronymic"],
                    "password_hash": hash_password(user_data["password"]),
                    "is_active": True,
                },
            )

            # Если пользователь существовал, обновляем пароль
            if not created:
                user.password_hash = hash_password(user_data["password"])
                user.save(update_fields=["password_hash"])

            # Сохраняем роли для назначения позже
            user_data["obj"] = user
            user_data["created"] = created

            status = "создан" if created else "обновлён"
            self.stdout.write(f"  ✓ Пользователь {email} - {status}")

    def _assign_roles(self):
        """Назначение ролей пользователям."""
        # Очищаем существующие связи (для тестовых данных)
        UserRole.objects.all().delete()

        # Назначаем роли по данным из _create_users
        user_assignments = [
            ("admin@example.com", ["admin"]),
            ("manager@example.com", ["manager"]),
            ("user1@example.com", ["user"]),
            ("user2@example.com", ["user"]),
            ("guest@example.com", ["guest"]),
        ]

        for email, role_names in user_assignments:
            try:
                user = User.objects.get(email=email)

                for role_name in role_names:
                    role = Role.objects.get(name=role_name)
                    UserRole.objects.create(user=user, role=role)
                    self.stdout.write(
                        f"  ✓ Назначил роль {role_name} пользователю {email}"
                    )

            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Пользователь {email} не найден")
                )
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Роль {role_name} не найдена")
                )

    def _create_access_rules(self):
        """Создание правил доступа для ролей."""
        # Очищаем существующие правила (для тестовых данных)
        AccessRule.objects.all().delete()

        # Получаем все элементы и роли
        elements = BusinessElement.objects.all()
        roles = Role.objects.all()

        # Правила доступа по умолчанию
        # Формат: (role_name, element_name, {права})
        default_rules = [
            # Админ - все права на всё
            (
                "admin",
                "products",
                {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
            ),
            (
                "admin",
                "users",
                {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
            ),
            (
                "admin",
                "roles",
                {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
            ),
            (
                "admin",
                "access_rules",
                {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
            ),
            # Менеджер - полные права на продукты, чтение пользователей
            (
                "manager",
                "products",
                {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "delete_permission": True,
                },
            ),
            (
                "manager",
                "users",
                {
                    "read_all_permission": True,
                    "read_permission": True,
                },
            ),
            # Обычный пользователь - права только на свои продукты
            (
                "user",
                "products",
                {
                    "read_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "delete_permission": True,
                },
            ),
            # Гость - только чтение продуктов
            (
                "guest",
                "products",
                {
                    "read_permission": True,
                },
            ),
        ]

        # Применяем правила
        for role_name, element_name, permissions in default_rules:
            try:
                role = Role.objects.get(name=role_name)
                element = BusinessElement.objects.get(name=element_name)

                rule, created = AccessRule.objects.get_or_create(
                    role=role, element=element, defaults=permissions
                )

                if not created:
                    # Обновляем существующее правило
                    for key, value in permissions.items():
                        setattr(rule, key, value)
                    rule.save()

                status = "создано" if created else "обновлено"
                self.stdout.write(
                    f"  ✓ Правило доступа ({role_name} → {element_name}) - {status}"
                )

            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Роль {role_name} не найдена")
                )
            except BusinessElement.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Элемент {element_name} не найден")
                )

        self.stdout.write(
            self.style.NOTICE(
                "  Всего создано правил доступа: {}".format(AccessRule.objects.count())
            )
        )

    def _show_summary(self):
        """Вывод итоговой статистики."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("ИТОГОВАЯ СТАТИСТИКА:"))
        self.stdout.write(f"  Пользователей: {User.objects.count()}")
        self.stdout.write(f"  Ролей: {Role.objects.count()}")
        self.stdout.write(f"  Бизнес-элементов: {BusinessElement.objects.count()}")
        self.stdout.write(f"  Правил доступа: {AccessRule.objects.count()}")
        self.stdout.write(f"  Назначений ролей: {UserRole.objects.count()}")

        # Выводим тестовые учетные данные
        self.stdout.write("\n" + self.style.NOTICE("ТЕСТОВЫЕ УЧЕТНЫЕ ДАННЫЕ:"))
        self.stdout.write("  Админ: admin@example.com / admin123")
        self.stdout.write("  Менеджер: manager@example.com / manager123")
        self.stdout.write("  Пользователь: user1@example.com / user123")
        self.stdout.write("  Гость: guest@example.com / guest123")

        self.stdout.write("\n" + self.style.NOTICE("ЗАМЕЧАНИЯ:"))
        self.stdout.write("  - Все пароли хешированы с использованием bcrypt")
        self.stdout.write("  - Для сброса данных используйте: python manage.py flush")
        self.stdout.write("=" * 50)
