import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import SafetySetting
import os
import base64
import asyncio
import openai
import discord
from discord.ext import commands
from google.cloud import speech
from google.auth import default, transport
from google.cloud import texttospeech
from spotify.commands import musica, album, artista



import requests

API_BASE = "https://unmulled-buccal-kellye.ngrok-free.dev/api/v1"
TOKEN = "zzz"




def transcription_call_audio(audio_data):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(

        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="pt-BR",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
    return None


class LaraListener:
    def __init__(self):
        self.buffer = bytearray()

    def processar_pacote(self, data):
        # Acumula o áudio bruto da call
        self.buffer.extend(data)

        # Se o buffer estiver grande o suficiente (ex: 3 segundos)
        if len(self.buffer) > 320000:
            text = transcription_call_audio(bytes(self.buffer))
            self.buffer.clear()
            return text
        return None

def gerar_voz_lara(text):
    client = texttospeech.TextToSpeechClient()

    ssml_text = f"<speak>{text}<break time='1s'/></speak>"
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(

        language_code="pt-BR",
        name="pt-BR-Wavenet-C"
    )
    audio_config = texttospeech.AudioConfig(

        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=-2,
        speaking_rate=1.15
    )


    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open("lara_voz.mp3", "wb") as out:
        out.write(response.audio_content)
    return "lara_voz.mp3"

PROJECT_ID = "ia-bot-gamer-disc"

credentials, _ = default()
auth_request = transport.requests.Request()
credentials.refresh(auth_request)


client = openai.OpenAI(
    base_url=f"https://us-east5-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-east5/endpoints/openapi",
    api_key=credentials.token,
)


vertexai.init(project=PROJECT_ID, location='us-east5')

config_settings = [

    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                  threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                  threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                  threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                  threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
]
# O caminho completo para o Llama 4 Scout que você ativou
MODEL_ID = "llama-4-scout-17b-16e-instruct-maas"
model = GenerativeModel(MODEL_ID, safety_settings=config_settings)



def responder_como_lara(user_question):
    prompt_system = ("""Você é Lara, uma especialista em tecnologia e suporte técnico, com comunicação casual e direta, semelhante a alguém experiente respondendo rapidamente em chats ou fóruns, mas mantendo clareza e boa escrita.

**Personalidade:**

* Técnica experiente, prática e objetiva.
* Comunicação direta, com leve sarcasmo e humor pontual.
* Inteligente, analítica e focada em resolver problemas.
* Tem experiência com computadores, sistemas operacionais, redes e troubleshooting.

**Estilo de comunicação:**

* Linguagem informal, mas clara e compreensível.
* Explicações diretas ao ponto, evitando enrolação.
* Pode usar leve ironia ou humor, sem exageros.
* Evita termos excessivamente técnicos sem explicação.

**Diretrizes de comportamento:**

1. Sempre priorizar a solução do problema do usuário.
2. Explicar passo a passo quando necessário.
3. Sugerir alternativas caso a primeira solução não funcione.
4. Manter consistência no estilo direto e confiante.
5. Evitar julgamentos ou linguagem ofensiva.
6. Adaptar a explicação ao nível de conhecimento do usuário.

---)

    response = client.chat.completions.create(
        model="meta/llama-4-scout-17b-16e-instruct-maas",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": user_question}
        ],
        max_tokens=4096,
        temperature=1.0
    )
    return response.choices[0].message.content


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="&", intents=intents)

@bot.event
async def on_ready():
    print(f'Lara Logged in: {bot.user.name}')

@bot.command()
async def enter(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Entre em uma call primeiro.")

@bot.command(name="musica")
async def musica_command(ctx, *, nome: str):
    resposta = musica(nome)
    await ctx.send(resposta)

@bot.command(name="artista")
async def artista_command(ctx, *, nome: str):
    resposta = artista(nome)
    await ctx.send(resposta)

@bot.command(name="album")
async def album_command(ctx, *, nome: str):
    resposta = album(nome)
    await ctx.send(resposta)


@bot.command()
async def jogo(ctx, *, nome_do_jogo):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "ngrok-skip-browser-warning": "true",
        "Accept": "application/json"
    }

    params = {
        "query": nome_do_jogo
    }

    await ctx.send(f"Buscando dados de **{nome_do_jogo}**...")

    try:
        r = requests.get(
            f"{API_BASE}/games/search",
            headers=headers,
            params=params,
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()

            if not data:
                await ctx.send("Nada encontrado.")
                return

            jogo = data[0]  # primeiro resultado

            # Extrair gêneros
            generos = ", ".join([g["name"] for g in jogo.get("genres", [])]) or "N/A"

            embed = discord.Embed(
                title=jogo.get("name", "Desconhecido"),
                color=0x00ff99
            )

            embed.add_field(name="ID", value=jogo.get("id", "N/A"), inline=True)
            embed.add_field(name="Nota", value=jogo.get("rating", "N/A"), inline=True)
            embed.add_field(name="Metacritic", value=jogo.get("metacritic", "N/A"), inline=True)
            embed.add_field(name="Lançamento", value=jogo.get("released", "N/A"), inline=True)
            embed.add_field(name="Tempo médio de jogo", value=f"{jogo.get('playtime', 0)}h", inline=True)
            embed.add_field(name="Gêneros", value=generos, inline=False)

            if jogo.get("background_image"):
                embed.set_image(url=jogo["background_image"])

            await ctx.send(embed=embed)



        else:
            erro_msg = f"Erro {r.status_code}: {r.text}"

            if len(erro_msg) > 1900:
                erro_msg = erro_msg[:1900] + "\n\n... (erro truncado)"

            await ctx.send(erro_msg)

    except Exception as e:
        await ctx.send(f"Erro ao conectar na API: {e}")

@bot.command()
async def lara(ctx, *, pergunta):
    print(f"Lara processando pergunta de {ctx.author}: {pergunta}")

    # 1. Gera o texto debochado
    resposta_texto = responder_como_lara(pergunta)

    # 2. Gera o áudio (Certifique-se de que corrigiu para 'input' com N na função gerar_voz_lara!)
    audio_path = gerar_voz_lara(resposta_texto)

    # 3. Responde no chat de texto
    await ctx.send(f"{resposta_texto}")

    # 4. Lógica de Voz (Onde estava o erro)
    if ctx.author.voice:
        # Pega o cliente de voz se ele já existir no servidor
        vc = ctx.voice_client

        if vc is None:
            # Caso 1: Ela NÃO está na call ainda. Conecta agora.
            channel = ctx.author.voice.channel
            vc = await channel.connect()
        elif vc.channel != ctx.author.voice.channel:
            # Caso 2: Ela está na call, mas em outro canal. Move para o seu.
            await vc.move_to(ctx.author.voice.channel)

        await asyncio.sleep(0.5)
       
        if vc.is_playing():
            vc.stop()  
        options = "-loglevel error"
        # Toca o áudio usando o motor do FFmpeg
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio_path))
    else:
        await ctx.send("Entre em alguma call se quiser me ouvir.")
@bot.command()
async def rala(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectando.")
    else:
        await ctx.send("Bot desconectado. Não estou em nenhuma call.")

bot.run('seu_token_aqui')


"""print("--- LARA ONLINE ---")
pergunta = "xxx"
print(f"Você: {pergunta}")


resposta = responder_como_lara(pergunta)
print(f"Lara: {resposta}")
print ("\n [Gerando Audio]")
audio_arquive = gerar_voz_lara(resposta)
print(f"Sucesso! O arquivo: {audio_arquive} foi gerado.")"""