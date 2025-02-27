from internal.models import User, Role, Language
from pkg.config import settings
from pkg.database import session_factory


def create_admin_if_not_exist():
    with session_factory() as session:
        if not session.query(User).filter(User.telegram_id == settings.ADMIN_TELEGRAM_ID).first():
            session.add(
                User(
                    telegram_id=settings.ADMIN_TELEGRAM_ID,
                    username=settings.ADMIN_USERNAME,
                    first_name=settings.ADMIN_FIRST_NAME,
                    last_name=settings.ADMIN_LAST_NAME,
                    role=Role.ADMIN
                )
            )
        session.commit()
        session.close()


def get_admins_telegram_id():
    with session_factory() as session:
        admins_telegram_id = [user.telegram_id for user in session.query(User).filter(User.role == Role.ADMIN).all()]
        return admins_telegram_id


CLIENT_LOCALE_MESSAGES = {
    Language.UA: {
        "start": "Привіт, клієнт\n\nВідправ щось в чат і це повідомлення буде відправлено адміністратору",
        "choose_language": "Оберіть мову",
        "choose_issue": "Оберіть тему звернення",
        "sale": "Замовити рекламу",
        "support": "Зв'язатися з адміністрацією",
    },
    Language.RU: {
        "start": "Привет, клиент\n\nОтправь что-то в чат и это сообщение будет отправлено администратору",
        "choose_language": "Выберите язык",
        "choose_issue": "Выберите тему обращения",
        "sale": "Заказать рекламу",
        "support": "Связаться с администрацией",
    }
}
