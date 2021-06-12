from django.contrib.auth.hashers import make_password, identify_hasher
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db.models import EmailField, CharField, BooleanField, DateTimeField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, name=None, full_name=None,
                    is_active=True, is_staff=None, is_admin=None):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('User must write your email, sha')
        if not password:
            raise ValueError('User must provide his password, sha')
        email = self.normalize_email(email)  # скорее всего normalize_email проверяет на валидность
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.is_active = is_active

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, name=None):
        user = self.create_user(email=email, name=name, password=password, is_staff=True, is_admin=True)
        return user

    def create_staffuser(self, email, password=None, name=None):
        user = self.create_user(email=email, name=name, password=password, is_staff=True, is_admin=False)
        return user


class User(AbstractBaseUser):
    email = EmailField(unique=True, max_length=255)
    name = CharField(max_length=255, null=True, blank=True)
    full_name = CharField(max_length=255, null=True, blank=True)
    staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    admin = BooleanField(default=False)
    timestamp = DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        if self.name:
            return self.name
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    #
    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def save(self, *args, **kwargs):

        try:
            # мы используем здесь identify_hasher, потому что нам надо, захэшировать пароль
            # неважно при create или update.
            # механизм слежующий:
            # identify_hasher вызывает ValueError если пароль не захэшированный
            # отлавливаем ошибку,  и применяем функцию make_password

            # но отличие точно в том, что make_password - независимая функция из модуля hashers
            # а set_password - bound method в классе AbstractBaseUser, который использует make_password
            # от которого кстати наследован кастомный User.
            # так что определять его повторно без изменений - нет смысла
            # другой вариант захэшировать пароль см. в serializers.py
            _alg = identify_hasher(self.password)
        except ValueError:
            self.password = make_password(self.password)

        # if not self.id and not self.staff and not self.admin:
        #     self.password = make_password(self.password)
        #     функция make_password хэширет пароль, который мы задаем через поле формы

        print(self.password)
        super().save(*args, **kwargs)
