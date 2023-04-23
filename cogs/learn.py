import disnake
from disnake.ext import commands as dis_commands

import config
import commands_list
from utils.database import cursor, is_proxy


async def dataset_fill_off(inter: disnake.CommandInteraction):
    embed = disnake.Embed(
        color=disnake.Color.dark_red(),
        title='Заполнение отключено',
        description='Заполнение этой обучающей выборки отключено на этом сервере. Для включения введите команду '
                    f'`/option`'
    )
    embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
    await inter.send(embed=embed, ephemeral=True)


async def dataset_full(inter: disnake.CommandInteraction):
    embed = disnake.Embed(
        color=disnake.Color.dark_red(),
        title='Выборка заполнена',
        description=f'Количество строк в этой выборке достигло лимита (`{config.DATASET_DIALOG_LIMIT}`)'
    )
    embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
    await inter.send(embed=embed, ephemeral=True)


class Learn(dis_commands.Cog):
    def __init__(self, bot: dis_commands.Bot):
        self.bot = bot

    @dis_commands.slash_command(**commands_list.dataset.to_dict())
    async def dataset(self, inter: disnake.CommandInteraction):
        pass

    @dataset.sub_command_group(**commands_list.dataset.sub['insert'].to_dict())
    async def dataset_insert(self, inter: disnake.CommandInteraction):
        pass

    @dataset_insert.sub_command(**commands_list.dataset.sub['insert'].sub['dialog'].to_dict())
    async def dataset_insert_dialog(self, inter: disnake.CommandInteraction):
        if await is_proxy(inter):
            is_fill = bool(cursor('SELECT fill_dialog FROM guilds WHERE id = ?', inter.guild_id).fetchone()[0])

            if is_fill:
                dialog_progress = cursor('SELECT COUNT(*) FROM dataset_dialog').fetchone()[0]

                if dialog_progress < config.DATASET_DIALOG_LIMIT:
                    history = list(await inter.channel.history(limit=config.DIALOG_SEARCH_LIMIT).flatten())
                    msg_exist = False
                    x = None
                    y = None

                    for idx, msg in enumerate(history):
                        y = history[idx - 1]
                        x = msg
                        if y.author == inter.author and \
                                x.author != y.author and \
                                'http' not in x.content and \
                                'http' not in y.content and \
                                not x.author.bot:
                            msg_exist = True
                            break

                    if msg_exist:
                        all_x = map(lambda _x: _x[0], cursor('SELECT x FROM dataset_dialog').fetchall())

                        if x.content in all_x:
                            embed = disnake.Embed(
                                color=disnake.Color.dark_red(),
                                title='Такая запись уже существует',
                                description=f'Ответ на "{x.content}" уже кем-то записан'
                            )
                        else:
                            cursor('''INSERT INTO dataset_dialog (speaker_id, listener_id, x, y)
                                      VALUES (?, ?, ?, ?)''', x.author.id, y.author.id, x.content, y.content)

                            embed = disnake.Embed(
                                color=config.EMBED_COLOR,
                                title='Ответ записан',
                                description=f'Ответ успешно записан!\n"{y.content}"\n"{x.content}"'
                            )
                            fill_count = cursor(f'''SELECT COUNT(*) FROM dataset_dialog
                                                    WHERE listener_id = ? LIMIT 1''', inter.author.id).fetchone()[0]

                            embed.set_footer(text=f'Ваш вклад в обучение: {fill_count} записей')

                    else:
                        embed = disnake.Embed(
                            color=disnake.Color.dark_red(),
                            title='Экземпляр `запрос-ответ` не найден',
                            description='Критерии поиска:\n'
                                        '1. Ответ должен быть написан **вами**;\n'
                                        '2. Автор запроса **не** может быть автором ответа;\n'
                                        '3. В запросе или в ответе **не** должно быть ссылки.\n\n'
                                        f'Диапазон поиска: {config.DIALOG_SEARCH_LIMIT} последних сообщений в текущем '
                                        'текстовом канале. '
                        )
                    embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
                    await inter.send(embed=embed, ephemeral=True)

                else:
                    await dataset_full(inter)
            else:
                await dataset_fill_off(inter)

    @dataset.sub_command_group(**commands_list.dataset.sub['delete'].to_dict())
    async def dataset_delete(self, inter: disnake.CommandInteraction):
        pass

    @dataset_delete.sub_command(**commands_list.dataset.sub['delete'].sub['dialog'].to_dict())
    async def dataset_delete_dialog(self, inter: disnake.CommandInteraction):
        if await is_proxy(inter):
            x, y = cursor(f'''SELECT x, y FROM dataset_dialog 
                              WHERE idx = (SELECT MAX(idx) FROM dataset_dialog
                                           WHERE listener_id = ?)''', inter.author.id).fetchone()

            cursor('DELETE FROM dataset_dialog WHERE listener_id = ? AND x = ?', inter.author.id, x)

            fill_count = cursor(f'''SELECT COUNT(*) FROM dataset_dialog
                                    WHERE listener_id = ? LIMIT 1''', inter.author.id).fetchone()[0]

            embed = disnake.Embed(
                color=config.EMBED_COLOR,
                title='Последняя запись удалена',
                description=f'"{x}"\n"{y}"'
            )
            embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
            embed.set_footer(text=f'Ваш вклад в обучение: {fill_count} записей')
            await inter.send(embed=embed, ephemeral=True)


def setup(bot: dis_commands.Bot):
    bot.add_cog(Learn(bot))
