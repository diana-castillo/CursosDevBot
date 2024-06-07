import asyncio
import inspect
from discord import Intents, Client, TextChannel, Message

class DiscordBot(Client):

    def __init__(self):

        # Hace llamar el constructor del paquete de discord
        intents: Intents = Intents.default()
        intents.message_content = True
        intents.messages = True
        super().__init__(intents=intents)

        self.task_seg: asyncio.Task = None
        self.task_obt: asyncio.Task = None

        self.last_course: str = None
        self.keyword_seg: str = None
        self.keyword_obt: str = None

        self.id_ch_seg: int = None
        self.id_ch_obt: int = None
        
        self.channel_seg: TextChannel = None
        self.channel_obt: TextChannel = None
        
    
    async def on_ready(self):
        self.channel_seg = self.get_channel(self.id_ch_seg)
        self.channel_obt = self.get_channel(self.id_ch_obt)

        print(f'Conectado como {self.user}')
        print(f'El bot responderá en {self.channel_seg.name} y en {self.channel_obt.name}')

    async def send_message(self, run_seg_coroutine: bool) -> None:
        try:
            channel = "seg-de-cursos" if run_seg_coroutine else "obt-de-cursos"
            keyword = self.keyword_seg  if run_seg_coroutine else self.keyword_obt
            msg = f'La corutina en {channel} con la palabra clave {keyword}'

            while True:
                response: list = await self.get_response(run_seg_coroutine)
                print(f'{msg} obtuvo {len(response)} resultados.')

                if not len(response) and not run_seg_coroutine: 
                    await self.channel_obt.send(content= f"No se encontraron cursos.")

                for r in response:
                    if(run_seg_coroutine):
                        await self.channel_seg.send(content= f"[{r['title']}]({r['link']})")
                    else:
                        await self.channel_obt.send(content= f"[{r['title']}]({r['link']})")

                if(not run_seg_coroutine): break
                await asyncio.sleep(60*60*2)  # Espera 2 horas antes de enviar el próximo mensaje

            print(f'{msg} finalizó con exito.')

        except asyncio.CancelledError:
            print(f'{msg} fue terminada.') 
            return

    async def on_message(self, message: Message) -> None:
        # Verifica que el mensaje no sea del bot
        if message.author == self.user:
            return

        if(message.channel == self.channel_seg):
            self.keyword_seg = message.content
            await self.channel_seg.send(content=f'¡Perfecto! A partir de ahora, te enviaré cursos específicos sobre {self.keyword_seg}. Aquí tienes el último en la serie.')
            self.last_course = None

            if(type(self.task_seg) == asyncio.Task): self.task_seg.cancel()
            self.task_seg = asyncio.create_task(self.send_message(run_seg_coroutine=True))
        
        if(message.channel == self.channel_obt):
            self.keyword_obt = message.content
            await self.channel_obt.send(content=f'¡Perfecto! A continuación se te enviará una lista de cursos que coinciden con la palabra {self.keyword_obt}.')
            await self.channel_obt.send(content=f'Obteniendo cursos...')

            if(type(self.task_obt) == asyncio.Task): self.task_obt.cancel()
            self.task_obt = asyncio.create_task(self.send_message(run_seg_coroutine=False))

    def start_bot(self, token: str, id_ch_seg: int, id_ch_obt: int):
        self.id_ch_seg = id_ch_seg
        self.id_ch_obt = id_ch_obt
        self.run(token=token)