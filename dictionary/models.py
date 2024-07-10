from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models, transaction
from django.db.models import F, Q
from django.forms import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        "Each superuser is a staff member."
        return self.is_superuser


class Word(models.Model):
    word = models.TextField()
    language = models.ForeignKey("Language", on_delete=models.CASCADE)
    translations = models.ManyToManyField(
        "self",
        through="Translation",
        symmetrical=False,
        related_name="translated_words",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["word", "language"], name="unique_word_language"
            )
        ]

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = self.word.lower()
        super().save(*args, **kwargs)


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Translation(models.Model):
    from_word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name="source_word"
    )
    to_word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name="target_word"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["to_word", "from_word"],
                name="unique_translation_pair_reverse"
            ),
        ]

    def __str__(self):
        return f"{self.from_word} -> {self.to_word}"
    
    def save(self, *args, **kwargs):
        if self.from_word.language == self.to_word.language:
            raise ValidationError("from_word and to_word cannot have the same language.")
        super().save(*args, **kwargs)
        
    @classmethod
    def get_translations(cls, word, source_language, target_language):
        return cls.objects.filter(
            from_word__word=word,
            from_word__language__code=source_language,
            to_word__language__code=target_language
        )
    
    @classmethod
    def create_translations(
            cls,
            word: str,
            source_lang_code: str,
            target_lang_code: str,
            translations: list
        ) -> None:
        """
        Creates translations for a given word from one language to another.

        This method retrieves or creates Word instances for the given word and its translations, 
        and associates them with the appropriate Language instances. 
        It also creates Translation instances to represent the translations from the 
        given word to each of its translations.

        Args:
            word (str): The word to translate.
            source_lang_code (str): The language code of the language the word is in.
            target_lang_code (str): The language code of the language to translate the word to.
            translations (list): A list of dictionaries, each containing a translation of the word. 
                                  Each dictionary must have a "text" key associated with the translated word.
        """
        with transaction.atomic():
            source_lang = Language.objects.get(code=source_lang_code)
            target_lang = Language.objects.get(code=target_lang_code)
            from_word = Word.objects.get_or_create(word=word, language=source_lang)[0]
            for translation in translations:
                to_word = Word.objects.get_or_create(word=translation["text"], language=target_lang)[0]
                cls.objects.get_or_create(from_word=from_word, to_word=to_word)


class Dictionary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dictionaries")
    translations = models.ManyToManyField(Translation, related_name="+")
    source_language = models.ForeignKey(
        Language, related_name="+", on_delete=models.CASCADE
    )
    target_language = models.ForeignKey(
        Language, related_name="+", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(source_language=F('target_language')),
                name='different_languages',
                violation_error_message='Source and target languages must be different.'
            ),
            models.UniqueConstraint(
                fields=['user', 'source_language', 'target_language'],
                name='unique_language_pair_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user}'s dictionary"
