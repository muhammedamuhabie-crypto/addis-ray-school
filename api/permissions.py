from rest_framework.permissions import BasePermission


class IsDirector(BasePermission):
    message = "Director access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "DIRECTOR"
        )


class IsTeacher(BasePermission):
    message = "Teacher access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "TEACHER"
        )


class IsStudent(BasePermission):
    message = "Student access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "STUDENT"
        )


class IsDirectorOrTeacher(BasePermission):
    message = "Director or Teacher access required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["DIRECTOR", "TEACHER"]
        )
