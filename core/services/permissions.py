"""
Модуль для проверки прав доступа пользователя к бизнес-элементам.
Реализует проверку прав на основе ролевой модели доступа (RBAC).
"""

from typing import Optional

from core.models import AccessRule, BusinessElement, User


def has_access(
    *,
    user: User,
    element_name: str,
    action: str,
    owner_id: Optional[int] = None,
) -> bool:
    """
    Проверяет, имеет ли пользователь доступ к указанному действию над элементом.

    Args:
        user: Пользователь, для которого проверяются права
        element_name: Имя бизнес-элемента (например, 'products', 'users')
        action: Действие для проверки ('read', 'read_all', 'create',
                'update', 'update_all', 'delete', 'delete_all')
        owner_id: ID владельца объекта (опционально, для проверки прав на конкретный объект)

    Returns:
        bool: True если доступ разрешен, False если запрещен

    Логика работы:
        1. Если элемент не существует - доступ запрещен
        2. Получаем все правила доступа для ролей пользователя и элемента
        3. Для каждого правила проверяем:
           - Для действий с суффиксом '_all' (read_all, update_all, delete_all):
             проверяем соответствующее поле '_all_permission'
           - Для действий без суффикса '_all' (read, update, delete):
             * если правило разрешает действие на все объекты ('_all_permission') - доступ разрешен
             * если правило разрешает действие только на свои объекты ('_permission')
               и пользователь является владельцем - доступ разрешен
           - Для действия 'create': проверяем create_permission
    """

    # 1. Проверяем существование бизнес-элемента
    try:
        element = BusinessElement.objects.get(name=element_name)
    except BusinessElement.DoesNotExist:
        return False

    # 2. Получаем все правила доступа пользователя для данного элемента
    rules = AccessRule.objects.filter(
        role__userrole__user=user,
        element=element,
    ).select_related("role")

    # 3. Проверяем каждое правило
    for rule in rules:
        # Действия с суффиксом '_all' (работают со всеми объектами)
        if action == "read_all" and rule.read_all_permission:
            return True

        if action == "update_all" and rule.update_all_permission:
            return True

        if action == "delete_all" and rule.delete_all_permission:
            return True

        # Действие 'create' (не требует проверки владельца)
        if action == "create" and rule.create_permission:
            return True

        # Действия без суффикса '_all' (могут требовать проверки владельца)
        # Определяем, является ли пользователь владельцем объекта
        is_owner = owner_id is not None and owner_id == user.id

        # Проверка действия 'read'
        if action == "read":
            # Если правило разрешает чтение всех объектов
            if rule.read_all_permission:
                return True
            # Если правило разрешает чтение только своих объектов и пользователь - владелец
            if rule.read_permission and is_owner:
                return True

        # Проверка действия 'update'
        elif action == "update":
            # Если правило разрешает обновление всех объектов
            if rule.update_all_permission:
                return True
            # Если правило разрешает обновление только своих объектов и пользователь - владелец
            if rule.update_permission and is_owner:
                return True

        # Проверка действия 'delete'
        elif action == "delete":
            # Если правило разрешает удаление всех объектов
            if rule.delete_all_permission:
                return True
            # Если правило разрешает удаление только своих объектов и пользователь - владелец
            if rule.delete_permission and is_owner:
                return True

    # 4. Если ни одно правило не разрешило доступ
    return False


def get_user_permissions(user: User) -> dict:
    """
    Получает все разрешения пользователя в структурированном виде.

    Args:
        user: Пользователь, для которого нужно получить разрешения

    Returns:
        dict: Словарь с разрешениями в формате:
              {
                  'element_name': {
                      'read': bool,
                      'read_all': bool,
                      'create': bool,
                      'update': bool,
                      'update_all': bool,
                      'delete': bool,
                      'delete_all': bool,
                  },
                  ...
              }
    """
    permissions = {}

    # Получаем все правила доступа для всех ролей пользователя
    rules = AccessRule.objects.filter(
        role__userrole__user=user,
    ).select_related("element", "role")

    # Группируем правила по элементам
    for rule in rules:
        element_name = rule.element.name

        if element_name not in permissions:
            permissions[element_name] = {
                "read": False,
                "read_all": False,
                "create": False,
                "update": False,
                "update_all": False,
                "delete": False,
                "delete_all": False,
            }

        # Объединяем разрешения из разных ролей (OR логика)
        element_perms = permissions[element_name]

        element_perms["read"] = element_perms["read"] or rule.read_permission
        element_perms["read_all"] = (
            element_perms["read_all"] or rule.read_all_permission
        )
        element_perms["create"] = element_perms["create"] or rule.create_permission
        element_perms["update"] = element_perms["update"] or rule.update_permission
        element_perms["update_all"] = (
            element_perms["update_all"] or rule.update_all_permission
        )
        element_perms["delete"] = element_perms["delete"] or rule.delete_permission
        element_perms["delete_all"] = (
            element_perms["delete_all"] or rule.delete_all_permission
        )

    return permissions


def check_permission_for_element(
    user: User,
    element_name: str,
    action: str,
    resource_owner_id: Optional[int] = None,
) -> bool:
    """
    Альтернативный интерфейс для проверки прав доступа.
    Более понятное название для использования в коде.

    Args:
        user: Пользователь
        element_name: Имя бизнес-элемента
        action: Действие для проверки
        resource_owner_id: ID владельца ресурса (опционально)

    Returns:
        bool: True если доступ разрешен
    """
    return has_access(
        user=user,
        element_name=element_name,
        action=action,
        owner_id=resource_owner_id,
    )


def user_can_create(user: User, element_name: str) -> bool:
    """Проверяет, может ли пользователь создавать объекты элемента."""
    return check_permission_for_element(user, element_name, "create")


def user_can_read(
    user: User, element_name: str, resource_owner_id: Optional[int] = None
) -> bool:
    """Проверяет, может ли пользователь читать объекты элемента."""
    return check_permission_for_element(user, element_name, "read", resource_owner_id)


def user_can_read_all(user: User, element_name: str) -> bool:
    """Проверяет, может ли пользователь читать все объекты элемента."""
    return check_permission_for_element(user, element_name, "read_all")


def user_can_update(
    user: User, element_name: str, resource_owner_id: Optional[int] = None
) -> bool:
    """Проверяет, может ли пользователь обновлять объекты элемента."""
    return check_permission_for_element(user, element_name, "update", resource_owner_id)


def user_can_update_all(user: User, element_name: str) -> bool:
    """Проверяет, может ли пользователь обновлять все объекты элемента."""
    return check_permission_for_element(user, element_name, "update_all")


def user_can_delete(
    user: User, element_name: str, resource_owner_id: Optional[int] = None
) -> bool:
    """Проверяет, может ли пользователь удалять объекты элемента."""
    return check_permission_for_element(user, element_name, "delete", resource_owner_id)


def user_can_delete_all(user: User, element_name: str) -> bool:
    """Проверяет, может ли пользователь удалять все объекты элемента."""
    return check_permission_for_element(user, element_name, "delete_all")
