"""
test_api.py - API tests (run with: python manage.py test myapp)

Django creates a temporary database and we point MEDIA_ROOT at a temporary
folder, so your real data and files are never touched.
"""
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from myapp.models import Project, Diagram



class OwnershipTests(APITestCase):
    """A user must only see and modify their own projects and diagrams."""

    def setUp(self):
        # Fresh media folder for every test, so files never collide.
        media = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)

        User = get_user_model()
        self.alice = User.objects.create_user("Alice", "A", "alice@test.com", "pw-Alice-123")
        self.bob = User.objects.create_user("Bob", "B", "bob@test.com", "pw-Bob-123")
        self.project = Project.objects.create(name="p", description="d", owner=self.alice)
        self.diagram = Diagram.objects.create(
            name="d", description="d", project=self.project,
            file=SimpleUploadedFile("a.bpmn", b"<definitions/>"),
        )

    def test_project_list_shows_only_own_projects(self):
        self.client.force_authenticate(self.bob)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_unknown_project_returns_404(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get("/api/projects/99999/")
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_list_diagrams_of_a_project(self):
        self.client.force_authenticate(self.bob)
        response = self.client.get(f"/api/projects/{self.project.id}/create-diagrams/")
        self.assertEqual(response.json(), [])

    def test_other_user_cannot_open_a_diagram(self):
        self.client.force_authenticate(self.bob)
        response = self.client.get(
            f"/api/projects/{self.project.id}/diagrams/{self.diagram.id}/")
        self.assertEqual(response.status_code, 404)

    def test_owner_can_open_own_diagram(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get(
            f"/api/projects/{self.project.id}/diagrams/{self.diagram.id}/")
        self.assertEqual(response.status_code, 200)