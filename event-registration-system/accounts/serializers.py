from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "role",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        """Validate that both password fields match."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."},
            )

        return attrs

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        validated_data.pop("password2")
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "bio",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
        )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# UserRegistrationSerializer handles user sign-up data. It accepts email,
# username, password, password2, role, first name, and last name.
#
# password and password2 are write-only so they can be sent to the API but are
# never returned in API responses.
#
# validate checks that password and password2 match. This prevents creating an
# account when the user mistyped their password confirmation.
#
# create removes password2, removes password from the normal field data, and
# calls create_user. create_user is important because it hashes the password
# before saving it.
#
# UserLoginSerializer describes the login request body. It is a plain Serializer
# because it does not create or update a database object.
#
# UserProfileSerializer controls what profile data is returned and updated. id,
# email, and role are read-only so users cannot change protected account values
# through the profile endpoint.
#
# Important decisions that were made and why
#
# get_user_model is used instead of importing accounts.User directly. This is
# the recommended Django pattern for projects with a custom user model.
#
# The registration serializer lets role be provided because this project has
# MEMBER and ORGANIZER account types.
#
# The profile serializer keeps email and role read-only because those values
# often need separate workflows or admin approval in real systems.
#
# What you should read and understand before you review the code
#
# Read DRF Serializer and ModelSerializer basics.
#
# Read write_only fields so you understand why passwords are accepted but not
# returned.
#
# Read Django create_user so you understand password hashing.
#
# Read serializer validate and create methods.
#
# ============================================================
# END OF REVIEW
# ============================================================
