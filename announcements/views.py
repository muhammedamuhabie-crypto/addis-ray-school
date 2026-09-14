from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Announcement


def _audience_for_user(user):
    if user.role == "DIRECTOR":
        return "All Teachers & Students"
    if user.role == "TEACHER":
        return "All Students"
    return ""


@login_required
def announcement_list(request):
    if request.user.role == "DIRECTOR":
        announcements = Announcement.objects.select_related("posted_by").all()
    elif request.user.role == "TEACHER":
        announcements = Announcement.objects.select_related("posted_by").filter(
            audience__in=["All Teachers & Students", "All Students"]
        )
    elif request.user.role == "STUDENT":
        announcements = Announcement.objects.select_related("posted_by").filter(
            audience__in=["All Teachers & Students", "All Students"]
        )
    else:
        announcements = Announcement.objects.none()

    return render(
        request,
        "announcements/list.html",
        {"announcements": announcements},
    )


@login_required
def announcement_create(request):
    if request.user.role not in ["DIRECTOR", "TEACHER"]:
        messages.error(
            request,
            "You do not have permission to create announcements."
        )
        return redirect("announcement_list")

    audience = _audience_for_user(request.user)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        priority = request.POST.get("priority", "NORMAL")

        if not title or not message:
            messages.error(
                request,
                "Title and message are required."
            )
            return render(
                request,
                "announcements/create.html",
                {
                    "priorities": Announcement.PRIORITY_CHOICES,
                    "audience": audience,
                },
            )

        if priority not in dict(Announcement.PRIORITY_CHOICES):
            priority = "NORMAL"

        Announcement.objects.create(
            title=title,
            audience=audience,
            message=message,
            priority=priority,
            posted_by=request.user,
        )

        messages.success(
            request,
            "Announcement posted successfully."
        )
        return redirect("announcement_list")

    return render(
        request,
        "announcements/create.html",
        {
            "priorities": Announcement.PRIORITY_CHOICES,
            "audience": audience,
        },
    )


@login_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.user.role not in ["DIRECTOR", "TEACHER"]:
        messages.error(
            request,
            "You do not have permission to edit announcements."
        )
        return redirect("announcement_list")

    if announcement.posted_by_id != request.user.id:
        messages.error(
            request,
            "You can only edit your own announcements."
        )
        return redirect("announcement_list")

    audience = _audience_for_user(request.user)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        priority = request.POST.get("priority", "NORMAL")

        if not title or not message:
            messages.error(
                request,
                "Title and message are required."
            )
            return render(
                request,
                "announcements/edit.html",
                {
                    "announcement": announcement,
                    "priorities": Announcement.PRIORITY_CHOICES,
                    "audience": audience,
                },
            )

        if priority not in dict(Announcement.PRIORITY_CHOICES):
            priority = "NORMAL"

        announcement.title = title
        announcement.audience = audience
        announcement.message = message
        announcement.priority = priority
        announcement.save()

        messages.success(
            request,
            "Announcement updated successfully."
        )
        return redirect("announcement_list")

    return render(
        request,
        "announcements/edit.html",
        {
            "announcement": announcement,
            "priorities": Announcement.PRIORITY_CHOICES,
            "audience": audience,
        },
    )


@login_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.user.role not in ["DIRECTOR", "TEACHER"]:
        messages.error(
            request,
            "You do not have permission to delete announcements."
        )
        return redirect("announcement_list")

    if announcement.posted_by_id != request.user.id:
        messages.error(
            request,
            "You can only delete your own announcements."
        )
        return redirect("announcement_list")

    if request.method == "POST":
        announcement.delete()
        messages.success(
            request,
            "Announcement deleted successfully."
        )

    return redirect("announcement_list")
