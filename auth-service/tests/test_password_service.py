from app.services.password_service import hash_password, verify_password


def test_hash_and_verify_roundtrip():
    password_hash = hash_password("s3cret-password")
    assert verify_password("s3cret-password", password_hash)


def test_wrong_password_does_not_verify():
    password_hash = hash_password("s3cret-password")
    assert not verify_password("wrong-password", password_hash)


def test_same_password_gives_different_hashes():
    # соль случайна и хранится внутри хеша — двух одинаковых хешей не бывает
    assert hash_password("s3cret-password") != hash_password("s3cret-password")


def test_corrupted_hash_does_not_crash():
    # битая строка в базе вместо хеша -> "пароль неверен", а не исключение
    assert not verify_password("s3cret-password", "not-a-bcrypt-hash")
