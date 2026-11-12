"""
apps/users/models.py
SafeGuard AI — Custom User model aur UserProfile define ho raha hai yahan.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ---------------------------------------------------------------------------
# User Manager
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    """
    Custom manager jo email ko username ki jagah use karta hai.
    """

    def create_user(self, email, display_name, password=None, **extra_fields):
        # Email validate karna zaroori hai — bina email ke user nahi banega
        if not email:
            raise ValueError('Email address dena zaroori hai.')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, display_name=display_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, display_name, password=None, **extra_fields):
        # Superuser ke liye staff aur superuser flags true hone chahiye
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser ka is_staff=True hona chahiye.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser ka is_superuser=True hona chahiye.')

        return self.create_user(email, display_name, password, **extra_fields)


# ---------------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    """
    SafeGuard AI ka custom User model — email se login hota hai.
    """

    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('guardian', 'Guardian'),
        ('admin', 'Admin'),
    ]

    # Yaha user ka UUID primary key set ho raha hai — auto-generated, editable nahi
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='User ID',
    )

    # Email login identifier hai — unique hona chahiye
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name='Email Address',
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Phone Number',
    )

    display_name = models.CharField(
        max_length=150,
        verbose_name='Display Name',
    )

    # Date of birth optional hai — user provide kare tab hi save hoga
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date of Birth',
    )

    preferred_language = models.CharField(
        max_length=10,
        default='en',
        verbose_name='Preferred Language',
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        db_index=True,
        verbose_name='Role',
    )

    # Yeh field children ke accounts ke liye hai — agar guardian manage kar raha ho
    is_guardian_managed = models.BooleanField(
        default=False,
        verbose_name='Is Guardian Managed',
    )

    # Guardian/parent ka reference — self-referential FK
    guardian_user = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_users',
        verbose_name='Guardian User',
    )

    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    # AbstractBaseUser already has last_login — override to allow null
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Last Login')

    objects = UserManager()

    # Email se login hoga, username se nahi
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
            models.Index(fields=['role'], name='user_role_idx'),
            models.Index(fields=['is_active'], name='user_active_idx'),
        ]

    def __str__(self):
        return f'{self.display_name} <{self.email}>'

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.display_name


# ---------------------------------------------------------------------------
# UserProfile Model
# ---------------------------------------------------------------------------

class UserProfile(models.Model):
    """
    User ke additional details — profile picture, bio, emergency message.
    One-to-one relationship with User.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Profile ID',
    )

    # Har user ka ek hi profile hoga — CASCADE se delete hoga jab user delete ho
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User',
    )

    bio = models.TextField(blank=True, verbose_name='Bio')

    profile_picture_url = models.URLField(blank=True, verbose_name='Profile Picture URL')

    # Emergency message jo contacts ko bheja jayega — default message set hai
    emergency_message = models.TextField(
        blank=True,
        default='I need help! Please contact me.',
        verbose_name='Emergency Message',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'Profile of {self.user.display_name}'
