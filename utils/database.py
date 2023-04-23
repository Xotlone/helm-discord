from typing import Union
import sqlite3

from dotenv import load_dotenv
import disnake

from utils.basic import log

load_dotenv('.env')


class Database:
    def __init__(self):
        self.database = sqlite3.connect('database.db')
        self.cursor = self.database.cursor()

    def __call__(self, command: str, *args):
        try:
            if len(args) > 0:
                out = self.cursor.execute(command, args)
            else:
                out = self.cursor.execute(command)
            self.database.commit()
            log(f'Запрос "{command}"\nВыполнен', 'Database', 'debug')
            return out

        except self.database.Error as error:
            try:
                self.cursor.execute('rollback')
                log('ОТКАТ', 'DATABASE')
            except self.database.OperationalError:
                pass
            log(error, 'DATABASE', 'error')
            log(command, 'DATABASE', 'error')
            raise error

    def mass(self, complex_command: str, *args) -> dict:
        commands = complex_command.split(';')
        outputs = {}
        if args != ():
            for command in commands:
                outputs[command] = self(command, args)
        else:
            for command in commands:
                outputs[command] = self(command)

        return outputs

    def schema(self, name: str, *args):
        with open(f'schemes/{name}.sql', 'r') as f:
            if args != ():
                self.mass(f.read(), args)
            else:
                self.mass(f.read())
            log(f'Схема {name}.sql выполнена', 'DATABASE')


cursor = Database()


async def is_proxy(inter: Union[disnake.Interaction, disnake.TextChannel], feedback=True) -> bool:
    user = inter.author
    proxy = user.id in map(lambda x: x[0], cursor('SELECT id FROM proxies').fetchall())
    if not proxy:
        log('Неудачная попытка вызвать КДП', 'PROXY')
        if feedback:
            embed = disnake.Embed(
                color=disnake.Color.dark_red(),
                title='Вы не являетесь доверенным пользователем'
            )
            embed.set_author(name=user.name, icon_url=user.avatar.url)
            await inter.send(embed=embed, ephemeral=True)
        return False
    log('Вызвана КДП', 'PROXY', 'warn')
    return True
