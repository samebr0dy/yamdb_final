from rest_framework import permissions


class AuthPostOrReadOnly(permissions.BasePermission):
    """Проверяю только методы GET, аутентификация и POST."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                and request.user.is_authenticated)


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Пермишион проверяет, является ли пользователь админом
    автором или модератором.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Пермишион - админ или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or not request.user.is_anonymous
            and request.user.is_admin
        )


class IsAdminOrAuth(permissions.BasePermission):
    """Пермишион проверяет, админ или аутентифицированный юзер."""

    def has_permission(self, request, view):
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_admin
        )


class IsAdminOrSuperuser(permissions.BasePermission):
    """Пермишион проверяет, админ или суперюзер."""

    def has_permission(self, request, view):
        return (not request.user.is_anonymous
                and request.method in ['GET', 'POST', 'HEAD', 'OPTIONS',
                                       'PATCH', 'DELETE']
                and request.user.is_admin
                or request.method in ['POST', 'DELETE']
                and request.user.is_superuser)


class IsAdminOrUserOrReadOnly(permissions.BasePermission):
    """
    Пермишион проверяет, является ли пользователь админом
    или обычным пользователем.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_staff
                )


class IsAuthorizedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Пермишион проверяет, является ли пользователь
        аутентифицированным.
        """
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                )
