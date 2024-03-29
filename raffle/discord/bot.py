import os
import discord
import raffle.db.utils as rdbu
import pandas as pd
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

rdbu.load_sample_data()


@bot.command(name='test')
async def test_event(ctx):
    print('test event triggered')
    await ctx.send("The cake is a lie")


@bot.command(name='show_sales', help='Lists the last n sales')
async def show_sales(ctx, n_sales: int):
    sales = pd.DataFrame(rdbu.get_last_sales(n_sales))
    sales.drop(columns=['time_created', 'drawing_id'])

    await ctx.send(f"```{sales.to_string(columns=['id', 'user_name', 'num_tickets', 'prize_addition'])}```")


@bot.command(name='add_sale', help="Add a sale to the current drawing for the specified user_id, number of tickets "
                                   "sold, and (optionally) specify whether or not the sale is a prize addition only.")
async def add_sale(ctx, user_id: str, num_tickets: int, prize_addition: bool = False):
    if ctx.message.mentions is not None and user_id.startswith('<@'):
        user_id = ctx.message.mentions[0].nick if ctx.message.mentions[0].nick is not None\
                                                    else ctx.message.mentions[0].name
        user_id = "@" + user_id

    sale_id = rdbu.add_sale(
        user_id=user_id,
        tickets_sold=num_tickets,
        prize_add=prize_addition)
    sale_str = get_sale_display(sale_id)
    await ctx.send(f'```Added sale with id={sale_id}. The new sale data is:\n\n{sale_str}\n\n'
                   f'Use "!edit_sale" to make changes if necessary. See "!help edit_sale" for info.```')


@bot.command(name='edit_sale', help='Edit a sale that already exists in the database given the sale id. Use '
                                    'show_sales to see recent sales. See "!help show_sales."')
async def edit_sale(ctx, sale_id: int, tickets_sold: int = None, prize_add: bool = None):
    rdbu.edit_sale(sale_id, tickets_sold, prize_add)
    sale_str = get_sale_display(sale_id)
    str_out = f'```Successfully edited sale_id={sale_id}. The updated sale data is:\n\n{sale_str}```'

    await ctx.send(str_out)


def get_sale_display(sale_id: int):
    s = rdbu.get_sale(sale_id)
    idx = pd.Index([0])
    sale_str = pd.DataFrame(s, index=idx).to_string(columns=['id', 'user_name', 'num_tickets', 'prize_addition'])
    return sale_str

# @edit_sale.error
# async def info_error(ctx, error):
#     # passes errors to the discord channel
#     await ctx.send(error.__str__())


bot.run(TOKEN)
