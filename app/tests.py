import pytest
from django.core.exceptions import ValidationError
from app.models import Registration  


@pytest.mark.django_db
def test_create_registration():
    """Test creating a Registration object"""
    user = Registration.objects.create(
        username="junaid",
        email="junaid@example.com",
        password="securepassword123"  # in real apps use hashed passwords
    )
    assert user.username == "junaid"
    assert user.email == "junaid@example.com"
    assert str(user) == "junaid"


@pytest.mark.django_db
def test_email_uniqueness():
    """Test that email must be unique"""
    Registration.objects.create(
        username="user1",
        email="test@example.com",
        password="password123"
    )
    with pytest.raises(Exception):
        Registration.objects.create(
            username="user2",
            email="test@example.com",  # duplicate email
            password="password456"
        )


@pytest.mark.django_db
def test_invalid_email():
    """Test invalid email raises ValidationError"""
    user = Registration(
        username="bademailuser",
        email="not-an-email",
        password="password123"
    )
    with pytest.raises(ValidationError):
        user.full_clean() 

