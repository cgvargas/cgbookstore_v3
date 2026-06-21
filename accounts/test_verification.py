from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Book
from accounts.models import ReadingProgress, BookShelf

class ReadingVerificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='reader', password='password123')
        
        self.book = Book.objects.create(
            title="Book of Mysteries",
            isbn="1234567890123",
            page_count=100,
            publication_date=date(2024, 1, 1)
        )
        
        # Start reading (adds to reading shelf and creates progress)
        self.shelf = BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type='reading'
        )
        self.progress, _ = ReadingProgress.objects.get_or_create(
            user=self.user,
            book=self.book,
            defaults={'total_pages': 100}
        )

    def test_random_page_assigned_on_creation(self):
        """Test that a random verification page between 15% and 85% is assigned."""
        self.assertIsNotNone(self.progress.verification_page)
        self.assertTrue(15 <= self.progress.verification_page <= 85)

    def test_update_progress_requires_verification_at_100_percent(self):
        """Test that progress update to 100% flags requires_verification."""
        response = self.client.post(
            reverse('core:update_reading_progress'),
            data={'book_id': self.book.id, 'current_page': 100},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['progress']['requires_verification'])
        self.assertEqual(data['progress']['verification_status'], 'pending')
        
        # Refresh progress
        self.progress.refresh_from_db()
        self.assertFalse(self.progress.is_verified)
        self.assertTrue(self.progress.is_finished)

    @patch('core.services.verification_service.verify_reading_page_with_gemini')
    def test_submit_verification_success(self, mock_verify):
        """Test successful verification flow."""
        # Mock Gemini approval
        mock_verify.return_value = {
            'is_valid': True,
            'confidence': 0.9,
            'reason': 'The text belongs to the correct book page.'
        }
        
        # Create a mock image file
        img_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        mock_image = SimpleUploadedFile("page.gif", img_content, content_type="image/gif")
        
        # We need the progress to be at 100% first
        self.progress.current_page = 100
        self.progress.save()
        
        # Call verification endpoint
        response = self.client.post(
            reverse('core:submit_page_verification'),
            data={
                'book_id': self.book.id,
                'verification_image': mock_image,
                'isbn_scanned': 'true'
            }
        )
        
        if response.status_code != 200:
            print("SUCCESS TEST RESPONSE FAILED:", response.status_code, response.content)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['verified'])
        self.assertEqual(data['xp_gained'], 50)
        
        # Refresh progress
        self.progress.refresh_from_db()
        self.assertTrue(self.progress.is_verified)
        self.assertTrue(self.progress.is_finished)
        self.assertEqual(self.progress.verification_status, 'approved')
        self.assertTrue(self.progress.isbn_scanned)
        
        # Verify book shelf updated to "read"
        self.assertFalse(BookShelf.objects.filter(user=self.user, book=self.book, shelf_type='reading').exists())
        self.assertTrue(BookShelf.objects.filter(user=self.user, book=self.book, shelf_type='read').exists())
        
        # Verify XP awarded to user profile (50 XP for verified completion + 10 XP for "Lidos" shelf entry)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, 60)

    @patch('core.services.verification_service.verify_reading_page_with_gemini')
    def test_submit_verification_failure(self, mock_verify):
        """Test rejected verification flow."""
        # Mock Gemini rejection
        mock_verify.return_value = {
            'is_valid': False,
            'confidence': 0.1,
            'reason': 'Image does not contain a book.'
        }
        
        img_content = b'invalid_image_content'
        mock_image = SimpleUploadedFile("page.gif", img_content, content_type="image/gif")
        
        self.progress.current_page = 100
        self.progress.save()
        
        response = self.client.post(
            reverse('core:submit_page_verification'),
            data={
                'book_id': self.book.id,
                'verification_image': mock_image,
                'isbn_scanned': 'false'
            }
        )
        
        if response.status_code != 200:
            print("FAILURE TEST RESPONSE FAILED:", response.status_code, response.content)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertFalse(data['verified'])
        
        self.progress.refresh_from_db()
        self.assertFalse(self.progress.is_verified)
        self.assertTrue(self.progress.is_finished)
        self.assertEqual(self.progress.verification_status, 'rejected')
        
        # Book shelf remains "reading"
        self.assertTrue(BookShelf.objects.filter(user=self.user, book=self.book, shelf_type='reading').exists())
        self.assertFalse(BookShelf.objects.filter(user=self.user, book=self.book, shelf_type='read').exists())
        
        # No XP awarded
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, 0)
