from disnake import Option, OptionType, Permissions, ChannelType, OptionChoice

from utils.commands import *
import config


sql = Command(
    name='sql',
    desc='Запрос к базе данных SQL',
    options=[
        Option(
            name='request',
            description='Запрос',
            type=OptionType.string,
            required=True
        )
    ]
)

info = Command(
    name='info',
    desc='Информация',
    sub=[
        SubCommand(
            name='proxies',
            desc='Про доверенных пользователей'
        ),
        SubCommand(
            name='dataset',
            desc='Про наборы данных'
        )
    ]
)

option = Command(
    name='option',
    desc='Настройка заполнения обучающих выборок',
    options=[
        Option(
            name='key',
            description='Ключ (название) параметра',
            type=OptionType.string,
            required=True,
            choices=config.ALL_DATASETS
        ),
        Option(
            name='value',
            description='Состояние (вкл/выкл)',
            type=OptionType.boolean,
            required=True,
            choices=[True, False]
        )
    ]
)

dataset = Command(
    name='dataset',
    desc='Взаимодействие с наборами данных',
    sub=[
        SubCommandGroup(
            name='insert',
            sub=[
                SubCommand(
                    name='dialog',
                    desc='Внести ваше последнее сообщение как ответ на идущее до него'
                )
            ]
        ),
        SubCommandGroup(
            name='delete',
            sub=[
                SubCommand(
                    name='dialog',
                    desc='Удаляет последнюю сделанную вами запись'
                )
            ]
        )
    ]
)

logging = Command(
    name='logging',
    desc='Включение отправки логов в текстовый канал',
    options=[
        Option(
            name='channel',
            description='Текстовый канал, в который будут отправлятся сведения о последних действиях на сервере',
            type=OptionType.channel,
            required=True
        ),
        Option(
            name='condition',
            description='Включение (True) или отключение (False) отправки логов',
            type=OptionType.boolean,
            choices=[True, False]
        )
    ]
)
