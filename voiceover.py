"""Arabic voiceover for the ZA Dose explainer: one mp3 per line of script.json (runs on GitHub Actions)."""
import asyncio, json, os, subprocess
import edge_tts

S = json.load(open('script.json', encoding='utf-8'))
OUT = 'out'

async def one(voice, sid, text):
    d = f'{OUT}/{voice}'
    os.makedirs(d, exist_ok=True)
    path = f'{d}/{sid}.mp3'
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, voice, rate=S.get('rate', '+0%')).save(path)
            return path
        except Exception as e:
            print('retry', sid, e)
            await asyncio.sleep(3 * (attempt + 1))
    raise RuntimeError(sid)

async def main():
    durs = {}
    for v in S['voices']:
        durs[v] = {}
        for line in S['lines']:
            sid, text = line[0], line[-1]
            p = await one(v, sid, text)
            d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip()
            durs[v][sid] = float(d or 0)
            print(v, sid, durs[v][sid])
    json.dump(durs, open(f'{OUT}/durations.json', 'w'), indent=1)

asyncio.run(main())
