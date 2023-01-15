from disnake.ext import commands
import asyncpg
import disnake
import random
from datetime import date, datetime , timedelta
import os


intents = disnake.Intents.default()
intents.members = False


class Hanknyeon(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(".."),
            status=disnake.Status.idle,
            activity=disnake.Game("THE BOYZ - MAVERICK"),
            intents=intents
        ) 
        self.conn: asyncpg.Connection = None   #type:ignore
        self.curr: asyncpg.Connection = None   #type:ignore
        self.card_cd = {}
        self.petal = "<:HN_Petals:1033787290708889611>"
        self.owner_id = 756018524413100114
        self.data = {}
        self.deleted = []
        self.rare = {
            1:"\u273F\u2740\u2740\u2740\u2740",
            2:"\u273F\u273F\u2740\u2740\u2740",
            3:"\u273F\u273F\u273F\u2740\u2740",
            4:"\u273F\u273F\u273F\u273F\u2740",
            5:"\u273F\u273F\u273F\u273F\u273F"
        }
        self.chats = []
        

    def get_color(self):
        return random.choice([0xFFC0CB, 0xFFB6C1, 0xFF69B4, 0xFF1493, 0xDB7093, 0xC71585, 0xD8BFD8, 0xDDA0DD, 0xDA70D6, 0xEE82EE, 0xFF00FF, 0xfcb8b8])


    async def get_inventory(self, user_id, limit=False):
        if not limit:
            r = await self.conn.fetch("SELECT cards from CARDS WHERE user_id=$1", user_id)
            return [] if not r else [[l["cards"]] for l in r]
        else:
            r = await self.conn.fetch(f"SELECT cards from CARDS WHERE user_id=$1 AND cards LIKE '{limit}%' LIMIT 25", user_id)
            return [] if not r else [[l["cards"]] for l in r]
                
            
    async def insert_card(self, user_id, card):
        r = await self.conn.fetch("SELECT cards from CARDS WHERE user_id=$1", user_id)
        added = False
        conn = await self.conn.acquire()
        async with conn.transaction():
                for cards in r:
                    c = cards['cards'][:8]
                    if c == card:
                        card = f"{card} {int(cards['cards'][9:])+1}"
                        await self.conn.execute("UPDATE CARDS SET cards=$1 WHERE user_id=$2 AND cards=$3", card, user_id, cards['cards'])
                        added = True
                if not added:
                    card = card + " 1"
                    await self.conn.execute("INSERT INTO CARDS(user_id, cards) VALUES($1,$2)", user_id, card)
        await self.conn.release(conn)


    async def add_card_data(self, name, grop, rarity, id, limit):
        conn = await self.conn.acquire()
        async with conn.transaction():
            if limit:
                EndDate = date.today()
                await self.conn.execute("INSERT INTO LIMITED(card, date) VALUES($1, $2)", id, EndDate)
            await self.conn.execute("INSERT INTO CARDS_DATA(name, grop, rarity, ID) VALUES($1, $2, $3, $4)", name, grop, rarity, id)
            self.data[id] = {"name":name, "group":grop, "rarity":rarity}
        await self.conn.release(conn)


    def sort_time(self, s:int):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        time_dict = {int(w):" week", int(d):" day", int(h):" hour", int(m):" minute", int(s):" second"}
        for item in time_dict.keys():
            if int(item) > 1:
                time_dict[item] = time_dict[item] + "s"
        return " ".join(str(i) + k for i, k in time_dict.items() if i!=0)
    

    async def get_cards_data(self):
        conn = await self.conn.acquire()
        async with conn.transaction():
            r = await self.conn.fetch("SELECT * from CARDS_DATA")
            r2 = await self.conn.fetch("SELECT * FROM deleted")
            for cards in r:
                self.data[cards["id"]] = {"name":cards["name"], "rarity":cards["rarity"], "group":cards["grop"]}
            for de in r2:
                if r2:
                    self.deleted.append(de["id"])
        await self.conn.release(conn)


    async def delete_card(self, id, limit=False, from_existance=False):
        conn = await self.conn.acquire()
        async with conn.transaction():
            if not from_existance:
                if limit:
                    await self.conn.execute("DELETE FROM LIMITED WHERE card=$1", id)
                await self.conn.execute("INSERT INTO deleted(id) VALUES($1)", id)
                self.deleted.append(id)
            if from_existance:
                await self.conn.execute("DELETE FROM CARDS_DATA WHERE id=$1", id)
                query = f"DELETE FROM CARDS WHERE cards LIKE '{id}%'"
                await self.conn.execute(query)
                await self.conn.execute("DELETE FROM folder WHERE id=$1", id)
                os.remove(f"pics/{id}.png")
            self.data.pop(id)
        await self.conn.release(conn)


    async def limited_cards(self):
        r = await self.conn.fetch("SELECT * FROM LIMITED")
        return [] if not r else [[l["card"], l["date"]] for l in r]
    

    async def remove_cards(self, user_id, card, num=1, forced=None):
        conn = await self.conn.acquire()
        async with conn.transaction():
            r = await self.conn.fetch("SELECT cards from CARDS WHERE user_id=$1", user_id,)
            if forced:
                await self.conn.execute("DELETE FROM CARDS WHERE user_id=$1 AND cards=$2", user_id, forced)
                await self.conn.release(conn)
            else:
                for c in r:
                    if c["cards"].startswith(card):
                        n = int(c["cards"].split(" ")[1])
                        if n-num == 0:
                            await self.conn.execute("DELETE FROM CARDS WHERE user_id=$1 AND cards=$2", user_id, c["cards"])
                            l:dict = await self.folder(user_id, get=True)
                            print(l)
                            if l:
                                for key, value in l.items():
                                    if c["cards"].split(" ")[0] in value:
                                        await self.conn.execute("DELETE FROM folder WHERE user_id=$1 AND id=$2", user_id, c["cards"].split(" ")[0])
                        else:
                            card = c["cards"].split(" ")[0] + " " + str(n-num)
                            await self.conn.execute("UPDATE CARDS SET cards=$1 WHERE user_id=$2 AND cards=$3", card, user_id, c["cards"])
        await self.conn.release(conn)

    
    async def insert_fav(self, user_id, fav=" "):
        conn = await self.curr.acquire()
        async with conn.transaction():
            r = await self.curr.fetchrow("SELECT fav_card FROM profile WHERE user_id=$1", user_id)
            if r["fav_card"]:
                await self.curr.execute("UPDATE profile SET fav_card=$1 WHERE user_id=$2", fav, user_id)
        await self.curr.release(conn)

    
    async def get_profile(self, user_id):
        r = await self.curr.fetchrow("SELECT * FROM profile WHERE user_id=$1", user_id)
        if r:
            dc = {"user_id":r["user_id"], "startdate":r["startdate"], "fav_card":r["fav_card"], "coins":r["coins"], "daily_dt":r["daily_dt"], "daily_streak":r["daily_streak"]}
            return dc
        else:
            return None
                

    async def create_profile(self, user_id):
        conn = await self.curr.acquire()
        async with conn.transaction():
            new_d = datetime.now() - timedelta(2)
            new_dt = new_d.timestamp()
            tmstmp = datetime.now().timestamp()
            await self.curr.execute("INSERT INTO profile(user_id, startdate, fav_card, coins, daily_dt, daily_streak) VALUES($1, $2, $3, $4, $5, $6)", user_id, tmstmp, " ", 0, new_dt, 0)
        await self.curr.release(conn)
    

    async def add_coins(self, user_id, coins:int, remove=False):
        conn = await self.curr.acquire()
        async with conn.transaction():
            r = await self.curr.fetchrow("SELECT coins FROM profile WHERE user_id=$1", user_id)
            coin = coins + r["coins"]
            await self.curr.execute("UPDATE profile SET coins=$1 WHERE user_id=$2", coin, user_id)
        await self.curr.release(conn)
    

    async def remove_coins(self, user_id, coins:int, remove=False):
        conn = await self.curr.acquire()
        async with conn.transaction():
            r = await self.curr.fetchrow("SELECT coins FROM profile WHERE user_id=$1", user_id)
            coin =  r["coins"] - coins
            await self.curr.execute("UPDATE profile SET coins=$1 WHERE user_id=$2", coin, user_id)
        await self.curr.release(conn)


    async def daily(self, user_id, get=False, set=False, streak:int=0):
        r = await self.curr.fetchrow("SELECT daily_dt, daily_streak, coins FROM profile WHERE user_id=$1", user_id)
        if get:
           return r["daily_dt"], r["daily_streak"], r["coins"]
        conn = await self.curr.acquire()
        async with conn.transaction():
            if set:
                streak_lis = [125, 250, 375, 500, 625, 850, 1000]
                tmstmp = datetime.now().timestamp()
                await self.curr.execute("UPDATE profile SET coins=$1, daily_streak=$2, daily_dt=$3 WHERE user_id=$4", streak_lis[streak]+r["coins"], streak + 1, tmstmp, user_id)
        await self.curr.release(conn)
        return streak_lis[streak]


    async def folder(self, user_id, name=None, get=False, add=False, ids=None, delete=False):
        if get:
            r = await self.conn.fetch("SELECT * FROM folder WHERE user_id=$1", user_id)
            if r:
                names = []
                dc = {}
                for i in r:
                    if i["name"] not in names:
                        names.append(i["name"])
                for j in names:
                    dc[j] = []
                    for k in r:
                        if k["name"] == j:
                            dc[j].append(k[2])
                return dc
        conn = await self.conn.acquire()
        async with conn.transaction():
            if add:
                values = [(user_id, name, id ) for id in ids]
                await self.conn.executemany("INSERT INTO folder(user_id, name, id) VALUES($1, $2, $3)", values)
            if delete:
                if not ids:
                    await self.conn.execute("DELETE FROM folder WHERE user_id=$1 AND name=$2", user_id, name,)
                else:
                    params = [(user_id, name, id) for id in ids]
                    await self.conn.executemany("DELETE FROM folder WHERE user_id=$1 AND name=$2 AND id=$3", params)
        await self.conn.release(conn)

    
    async def binder(self, user_id, ids=None, get=False, n=False):
        r = await self.curr.fetchrow("SELECT * FROM binder WHERE user_id=$1", user_id)
        if get:
            return None if not r else r["user_id"], r["card"]
        conn = await self.curr.acquire()
        async with conn.transaction():
            
            if n:
                await self.curr.release(conn)
                await self.curr.execute("INSERT INTO binder(user_id, card) VALUES($1, $2)", user_id, "n")
            elif r:
                await self.curr.execute("UPDATE binder SET card=$1 WHERE user_id=$2", " ".join(ids), user_id)
            else:
                await self.curr.execute("INSERT INTO binder(user_id, card) VALUES($1, $2)", user_id, " ".join(ids))
        await self.curr.release(conn)


    async def chat(self, channel:disnake.TextChannel=None, get=False, remove=False):
        r = await self.curr.fetch("SELECT * FROM chat_ch")
        ch_li = [l["ch_id"] for l in r]
        if get:
            return ch_li
        else:
            conn = await self.curr.acquire()
            async with conn.transaction():
                if remove:
                    await self.curr.execute("DELETE FROM chat_ch WHERE ch_id=$1", channel.id)
                else:
                    ch_ids = [ch.id for ch in channel.guild.text_channels]
                    comm = set(ch_ids) & set(ch_li)
                    print(comm)
                    if not list(comm):
                        await self.curr.execute("INSERT INTO chat_ch(ch_id) VALUES($1)", channel.id)
                    else:
                        await self.curr.execute("UPDATE chat_ch SET ch_id=$1 WHERE ch_id=$2", channel.id, list(comm)[0])
                        self.chats.remove(list(comm)[0])
                    self.chats.append(channel.id)
            await self.curr.release(conn)
                        
