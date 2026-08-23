import socket, json, time

def send(t, p, timeout=60):
    s = socket.create_connection(('127.0.0.1', 9877), timeout=timeout); s.settimeout(timeout)
    s.sendall(json.dumps({'type': t, 'params': p}).encode())
    buf = b''
    while True:
        c = s.recv(65536)
        if not c: break
        buf += c
        try: json.loads(buf); break
        except: continue
    s.close()
    return json.loads(buf)

d = json.load(open('sources/Reprises/Pink Floyd/Breathe/_scenes_notes.json', encoding='utf-8'))
for si in sorted(d, key=int):
    st = d[si]
    for at in ['0','1','2','3','4','6']:
        arr = st.get(at, [])
        if not arr: continue
        length = st['length']
        # create clip on slot si, track at
        send('create_clip', {'track_index': int(at), 'clip_index': int(si), 'length': length})
        for i in range(0, len(arr), 200):
            send('add_notes_to_clip', {'track_index': int(at), 'clip_index': int(si), 'notes': arr[i:i+200]})
        print(f'sc{si} tr{at}: {len(arr)} notes -> clip {si} (len {length})')
        time.sleep(0.1)
print('done')
