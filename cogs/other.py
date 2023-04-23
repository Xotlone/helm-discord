import disnake
from disnake.ext import commands as dis_commands
import pandas as pd
from sqlite3 import OperationalError

from utils.basic import ProgressBar
from utils.database import cursor, is_proxy
import config
import commands_list


class Other(dis_commands.Cog):
    def __init__(self, bot: dis_commands.Bot):
        self.bot = bot

    @dis_commands.slash_command(**commands_list.sql.to_dict())
    async def sql(self, inter: disnake.CommandInteraction, request: str):
        if inter.author.id == config.OWNER:
            out = cursor.mass(request)
            out_list = []
            for out_item in out.values():
                try:
                    df_item = pd.DataFrame(out_item.fetchall())
                    if not df_item.empty:
                        out_list.append(str(df_item))
                except OperationalError:
                    pass
            out_list = '\n'.join(out_list)
            embed = disnake.Embed(
                color=config.EMBED_COLOR,
                title='SQL запрос',
                description=f'Выход:\n`{out_list}`'
            )
            if out_list == '':
                embed.description = f'Запрос выполнен успешно'
            embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
            await inter.send(embed=embed)

        else:
            embed = disnake.Embed(
                color=disnake.Color.dark_red(),
                title='SQL запрос',
                description='Эта команда только для владельца'
            )
            await inter.send(embed=embed, ephemeral=True)

    @dis_commands.slash_command(**commands_list.info.to_dict())
    async def info(self, inter: disnake.CommandInteraction):
        pass

    @info.sub_command(**commands_list.info.sub['proxies'].to_dict())
    async def info_proxies(self, inter: disnake.CommandInteraction):
        raw_proxies_list = cursor('SELECT * FROM proxies').fetchall()

        proxies_list = [f'{self.bot.get_user(proxie[0]).name} ({proxie[1]})' for proxie in raw_proxies_list]
        embed = disnake.Embed(
            color=config.EMBED_COLOR,
            title='Доверенные пользователи',
            description='Доверенные пользователи могут участвовать в заполнении и настройке __всех__ наборов данных. '
                        '||Цифра в скобках - количество добавленных строк в наборы данных.||'
        )
        embed.add_field(name='Список', value=', '.join(proxies_list))
        await inter.send(embed=embed)

    @info.sub_command(**commands_list.info.sub['dataset'].to_dict())
    async def info_dataset(self, inter: disnake.CommandInteraction):
        embed = disnake.Embed(
            color=config.EMBED_COLOR,
            title='Наборы данных',
            description=f'Наборы данных нужны для составления {int(config.TRAINING_SET * 100)}% *обучающей* и '
                        f'{round((1 - config.TRAINING_SET) * 100)}% *проверочной* выборки. *Обучающая выборка* нужна '
                        'для тренировки алгоритма машинного обучения, *проверочная* - для проверки качества обучения.'
        )

        dialog_is_filled = bool(cursor('SELECT fill_dialog FROM guilds WHERE id = ?', inter.guild_id).fetchone()[0])
        dialog_is_filled = f'{"включено" if dialog_is_filled else "выключено"}'
        dialog_progress = cursor('SELECT COUNT(*) FROM dataset_dialog').fetchone()[0]
        dialog_progress = ProgressBar(config.DATASET_DIALOG_LIMIT, dialog_progress, advanced=True)
        embed.add_field(
            name='"dialog"',
            value='Набор даных для ответа на сообщения.\n'
                  f'Заполнение: **{dialog_is_filled}**;\n'
                  f'Прогресс заполнения: **{dialog_progress}**.'
        )

        await inter.send(embed=embed)

    @dis_commands.slash_command(**commands_list.option.to_dict())
    async def option(self, inter: disnake.CommandInteraction, key: str, value: bool):
        if await is_proxy(inter, inter.author):
            cursor(f'UPDATE guilds SET fill_{key} = {int(value)} WHERE id = {inter.guild.id}')
            embed = disnake.Embed(
                color=config.EMBED_COLOR,
                title=f'Состояние заполнения `{key}` изменено на `{"True" if value else "False"}`'
            )
            embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
            await inter.send(embed=embed)

    @dis_commands.slash_command(**commands_list.logging.to_dict())
    @dis_commands.has_permissions(administrator=True)
    async def logging(self, inter: disnake.CommandInteraction, channel: disnake.TextChannel, condition: bool = True):
        if type(channel) == disnake.TextChannel:
            if condition:
                cursor(f'UPDATE guilds SET logging_chnl = {channel.id} WHERE id = {inter.guild_id}')
                embed = disnake.Embed(
                    color=config.EMBED_COLOR,
                    title='Назначен канал для логирования',
                    description=f'В канал {channel.mention} теперь отправляются оповещения о следующих событиях:\n'
                                'Удаление/редактирование сообщения, выход/исключение участника с сервера.'
                )
                embed.set_author(name=inter.author.name, url=inter.author.avatar.url)
                await inter.send(embed=embed)
            else:
                cursor(f'UPDATE guilds SET logging_chnl = NULL WHERE id = {inter.guild_id}')
                embed = disnake.Embed(
                    color=config.EMBED_COLOR,
                    title='Канал для логирования отключён'
                )
                embed.set_author(name=inter.author.name, url=inter.author.avatar.url)
                await inter.send(embed=embed)
        else:
            embed = disnake.Embed(
                color=disnake.Color.dark_red(),
                title='Канал для логирования должен быть текстовым'
            )
            embed.set_author(name=inter.author.name, url=inter.author.avatar.url)
            await inter.send(embed=embed, ephemeral=True)


def setup(bot: dis_commands.Bot):
    bot.add_cog(Other(bot))
