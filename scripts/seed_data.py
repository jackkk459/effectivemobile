# scripts/seed_data.py
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import AccessRule, BusinessElement, Role, User, UserRole
from core.services.auth import hash_password


def seed_initial_data():
    print("Seeding initial data...")

    # 1. Создаем бизнес-элементы
    elements = [
        "products",
        "users",
        "roles",
        "access_rules",
    ]

    for element_name in elements:
        BusinessElement.objects.get_or_create(name=element_name)
        print(f"✓ Created element: {element_name}")

    # 2. Создаем роли
    admin_role, _ = Role.objects.get_or_create(name="admin")
    manager_role, _ = Role.objects.get_or_create(name="manager")
    user_role, _ = Role.objects.get_or_create(name="user")

    print(f"✓ Created role: {admin_role.name}")
    print(f"✓ Created role: {manager_role.name}")
    print(f"✓ Created role: {user_role.name}")

    # 3. Создаем тестового администратора
    admin_user, created = User.objects.get_or_create(
        email="admin@example.com",
        defaults={
            "first_name": "Admin",
            "last_name": "System",
            "password_hash": hash_password("admin123"),
        },
    )

    if created:
        UserRole.objects.create(user=admin_user, role=admin_role)
        print(f"✓ Created admin user: admin@example.com / admin123")

    # 4. Создаем тестового менеджера
    manager_user, created = User.objects.get_or_create(
        email="manager@example.com",
        defaults={
            "first_name": "Manager",
            "last_name": "Test",
            "password_hash": hash_password("manager123"),
        },
    )

    if created:
        UserRole.objects.create(user=manager_user, role=manager_role)
        print(f"✓ Created manager user: manager@example.com / manager123")

    # 5. Назначаем права для ролей
    all_elements = BusinessElement.objects.all()

    # Админ получает все права на все элементы
    for element in all_elements:
        AccessRule.objects.get_or_create(
            role=admin_role,
            element=element,
            defaults={
                "read_all_permission": True,
                "create_permission": True,
                "update_all_permission": True,
                "delete_all_permission": True,
            },
        )

    # Менеджер получает ограниченные права
    products_element = BusinessElement.objects.get(name="products")
    AccessRule.objects.get_or_create(
        role=manager_role,
        element=products_element,
        defaults={
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,  # Только свои
            "delete_permission": True,  # Только свои
        },
    )

    # Обычный пользователь - только чтение своих продуктов
    AccessRule.objects.get_or_create(
        role=user_role,
        element=products_element,
        defaults={
            "read_permission": True,
            "create_permission": True,
            "update_permission": True,
            "delete_permission": True,
        },
    )

    print("✓ Access rules created")
    print("✅ Seeding completed successfully!")


if __name__ == "__main__":
    seed_initial_data()
