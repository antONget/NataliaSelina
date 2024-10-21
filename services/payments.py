import logging

import yookassa
from yookassa import Payment
import uuid
from config_data.config import Config, load_config

config: Config = load_config()
yookassa.Configuration.account_id = config.tg_bot.yookassa_id
yookassa.Configuration.secret_key = config.tg_bot.yookassa_key


# def create_payment_(amount: str, chat_id: int, content: str):
#     payment = Payment.create({
#         "amount": {
#             "value": amount,
#             "currency": "RUB"
#         },
#         "confirmation": {
#             "type": "redirect",
#             "return_url": "https://t.me/dr_selina_bot"
#         },
#         "capture": True,
#         "description": content,
#         "metadata": {
#           "order_id": "37"
#         }
#     })


def create_payment(amount: str, chat_id: int, content: str):
    logging.info(f"create_payment {amount} {chat_id} {content}")
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me./dr_selina_bot"
        },
        "description": 'Продукт для покупки',
        "meta_data": {
            "order_id": str(chat_id)
        },
        "receipt": {
            "customer": {
                "email": "email@yandex.ru"
            },
            "items": [
                {
                    "description": content,
                    "quantity": 1,
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "service"
                },
            ]
        },
    }, id_key)
    print(payment.confirmation.confirmation_url)
    return payment.confirmation.confirmation_url, payment.id


def check_payment(payment_id: str):
    payment = yookassa.Payment.find_one(payment_id)
    return payment.status
