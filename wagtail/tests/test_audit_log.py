from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from wagtail.log_actions import LogActionRegistry
from wagtail.models import (
    Page,
    PageLogEntry,
    PageViewRestriction,
    Task,
    Workflow,
    WorkflowTask,
)
from wagtail.models.audit_log import ModelLogEntry
from wagtail.test.testapp.models import FullFeaturedSnippet, SimplePage
from wagtail.test.utils import WagtailTestUtils

from wagtail.log_actions.models import LogEntry
from wagtail.log_actions.tests.utils import LogEntryQuerySetTestMixin

class TestAuditLogManager(WagtailTestUtils, TestCase):
    def setUp(self):
        self.user = self.create_superuser(
            username="administrator",
            email="administrator@email.com",
            password="password",
        )
        self.page = Page.objects.get(pk=1)
        self.simple_page = self.page.add_child(
            instance=SimplePage(
                title="Simple page", slug="simple", content="Hello", owner=self.user
            )
        )

    def test_log_action(self):
        now = timezone.now()

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.edit", user=self.user
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)

    def test_get_for_model(self):
        PageLogEntry.objects.log_action(self.page, "wagtail.edit")
        PageLogEntry.objects.log_action(self.simple_page, "wagtail.edit")

        entries = PageLogEntry.objects.get_for_model(SimplePage)
        self.assertEqual(entries.count(), 2)
        self.assertListEqual(
            list(entries), list(PageLogEntry.objects.filter(page=self.simple_page))
        )

    def test_get_for_user(self):
        self.assertEqual(
            PageLogEntry.objects.get_for_user(self.user).count(), 1
        )  # the create from setUp
###


    def test_log_entry_created_for_deletion_action(self):
        now = timezone.now()

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.delete", user=self.user
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)

    def test_log_entry_created_for_related_object_creation(self):
        now = timezone.now()

        with freeze_time(now):
            task = Task.objects.create(title="New Task")
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.create_related_object", user=self.user, related_object=task
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, task)

    def test_log_entry_created_for_related_object_deletion(self):
        now = timezone.now()
        task = Task.objects.create(title="New Task")

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.delete_related_object", user=self.user, related_object=task
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, task)

    def test_log_entry_created_for_page_restriction_change(self):
        now = timezone.now()
        restriction = PageViewRestriction.objects.create(page=self.page)

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.change_view_restriction", user=self.user, related_object=restriction
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, restriction)

    def test_log_entry_created_for_full_featured_snippet_change(self):
        now = timezone.now()
        snippet = FullFeaturedSnippet.objects.create(title="New Snippet")

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.edit_full_featured_snippet", user=self.user, related_object=snippet
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, snippet)

    def test_log_entry_created_for_model_log_entry_addition(self):
        now = timezone.now()
        model_log_entry = ModelLogEntry.objects.create(model="TestModel", message="New log entry")

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.add_model_log_entry", user=self.user, related_object=model_log_entry
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, model_log_entry)

    def test_log_entry_created_for_workflow_task_change(self):
        now = timezone.now()
        workflow = Workflow.objects.create(name="New Workflow")
        workflow_task = WorkflowTask.objects.create(workflow=workflow, task=self.page)

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.change_workflow_task", user=self.user, related_object=workflow_task
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, workflow_task)

    def test_log_entry_created_for_log_entry_deletion(self):
        now = timezone.now()
        log_entry = LogEntry.objects.create(action="TestAction", user=self.user)

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.delete_log_entry", user=self.user, related_object=log_entry
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, log_entry)

    def test_log_entry_created_for_user_change(self):
        now = timezone.now()
        user_to_change = get_user_model().objects.create_user(username="testuser")

        with freeze_time(now):
            entry = PageLogEntry.objects.log_action(
                self.page, "wagtail.change_user", user=self.user, related_object=user_to_change
            )

        self.assertEqual(entry.content_type, self.page.content_type)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.timestamp, now)
        self.assertEqual(entry.related_object, user_to_change)

    def test_validation_error_raised_on_log_action_without_action(self):
        with self.assertRaises(ValidationError):
            PageLogEntry.objects.log_action(self.page, "", user=self.user)




    ########################################


