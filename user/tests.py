from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# Create your tests here.

class ModelTests(TestCase):
    """Test for User model."""
    
    def test_create_user_with_email(self):
        """Test creating an user with email."""
        email= "candidateUser@Example.COM"
        password= "StrongPass123!"
        role= "CAN"
        resume= "uploads/resume.pdf"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            role=role,
            resume=resume
         )
        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.role, role)
        self.assertEqual(user.resume.name, "uploads/resume.pdf")
        
    def test_create_user_with_no_email(self):
        """Test creating user with no email should fail."""
        password = "StrongPass123!"
        role = "CAN"
        resume = "uploads/resume.pdf"
        
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=None,  # Explicitly pass None
                password=password,
                role=role,
                resume=resume
            )

    def test_create_user_with_empty_email(self):
        """Test creating user with empty email should fail."""
        password = "StrongPass123!"
        role = "CAN"
        resume = "uploads/resume.pdf"
        
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email="",  # Explicitly pass empty string
                password=password,
                role=role,
                resume=resume
            )
            
    def test_create_super_user(self):
        """Test creating super user. """
        email= "admin@example.com"
        password= "StrongPass123!"
        super_user = get_user_model().objects.create_superuser(
            email = email,
            password= password
        )
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)
        
    def test_user_email_gets_normalized(self):
        """Test user email gets normalized."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "test2@example.com"],
            ["TEST3@EXAMPLE.COM", "test3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        
        for i, (email, expected) in enumerate(sample_emails):
            user = get_user_model().objects.create_superuser(
                email=email, 
                username=f'testuser{i}',  # Adds unique username
                password='testpass123'
            )
            self.assertEqual(user.email, expected)
    
    def test_user_with_invalid_role(self):
        """Test invalid role gets rejected."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='test@example.com',
                password='testpass123',
                role='INVALID_ROLE'
            )
    
    def test_user_candidate_without_resume(self):
        """Test candidate without resume."""
        with self.assertRaises(ValidationError) as context:
            get_user_model().objects.create_user(
                email='candidate@example.com',
                password='StrongPass123!',
                role='CAN'
                # no resume - should raise ValidationError
            )
        self.assertIn('Candidates must provide a resume', str(context.exception))

    def test_employer_user_without_company(self):
        """Test employer without company."""
        with self.assertRaises(ValidationError) as context:
            get_user_model().objects.create_user(
                email='employer@example.com',
                password='StrongPass123!',
                role='EMP',
                # no company - should raise ValidationError
            )
        self.assertIn('Employers must provide a company name', str(context.exception))

    def test_user_with_duplicate_email_fail(self):
        """Test user with duplicate email fails."""
        user1 = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='EMP',
            company='Test Company'  # Required for employer
        )
        
        with self.assertRaises(ValidationError) as context:
            get_user_model().objects.create_user(
                email='test@example.com',  # Same email
                password='testpass1234',
                role='EMP',
                company='Another Company'
            )
        self.assertIn('email already exists', str(context.exception).lower())
                

            
        