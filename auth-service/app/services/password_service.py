import bcrypt


def hash_password(plain: str) -> str:
    """Хеширует пароль bcrypt'ом со случайной солью.

    Аналог BCryptPasswordEncoder.encode() из Spring Security.
    Два вызова с одним паролем дают разные хеши: соль случайна и
    хранится внутри самого хеша, поэтому колонка «соль» не нужна.
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    """Проверяет пароль против хеша (BCryptPasswordEncoder.matches())."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # повреждённый хеш в базе — считаем пароль неверным, а не роняем сервис
        return False
