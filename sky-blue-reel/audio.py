import numpy as np, json, wave
SR=44100; T=15.0; N=int(SR*T)
ev=json.load(open('events.json'))
L=np.zeros(N); R=np.zeros(N)
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR)
    if i>=N or i+len(sig)<=0: return
    s=sig[:N-i]*gain; l=np.sqrt((1-pan)/2); r=np.sqrt((1+pan)/2)
    L[i:i+len(s)]+=s*l*1.414; R[i:i+len(s)]+=s*r*1.414
def tt(d): return np.arange(int(d*SR))/SR
rng=np.random.default_rng(1)
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
bpm=128; beat=60/bpm
def note(m): return 440*2**((m-69)/12)
# ---- drums
def kick():
    t=tt(.35); f=45+110*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*1.0 + rng.standard_normal(len(t))*np.exp(-t*200)*.15
def clap():
    t=tt(.22); n=rng.standard_normal(len(t)); n=n-lp(n,.25)
    env=np.exp(-t*25)+.6*np.exp(-np.maximum(t-.012,0)*25)*(t>.012)
    return n*env*.45
def hat(open_=False):
    t=tt(.12 if not open_ else .3); n=rng.standard_normal(len(t)); n=n-lp(n,.6)
    return n*np.exp(-t*(60 if not open_ else 14))*.16
K,C,Hc,Ho=kick(),clap(),hat(),hat(True)
nb=int(T/beat)+1
for b in range(nb):
    t=b*beat
    intro = t<0.9   # sparse first moments
    if not intro: add(K,t,.9)
    if b%2==1 and not intro: add(C,t,.8,.1)
    add(Hc,t+beat/2,.9,-.3); 
    if b%4==3: add(Ho,t+beat/2,.6,.3)
    else: add(Hc,t,.5,.3)
# ---- chords I-V-vi-IV in C, bass + pluck arps
prog=[[60,64,67],[55,59,62,67],[57,60,64],[53,57,60,65]]
roots=[36,43,45,41]
def pluck(f,d=.35,bright=1.0):
    t=tt(d); s=np.sin(2*np.pi*f*t)+.5*bright*np.sin(2*np.pi*2*f*t)*np.exp(-t*20)+.25*np.sin(2*np.pi*4*f*t)*np.exp(-t*35)
    return s*np.exp(-t*9)*np.minimum(1,t*400)
def bass(f,d):
    t=tt(d); s=np.sign(np.sin(2*np.pi*f*t))*.4+np.sin(2*np.pi*f*t); s=lp(s,.08)
    return s*np.minimum(1,t*200)*np.exp(-t*3)*np.minimum(1,(d-t)*80)
bar=4*beat; s16=beat/4
arp=[0,1,2,1,2,0,1,2]
for b in range(int(T/bar)+1):
    ch=prog[b%4]; r=roots[b%4]; t0=b*bar
    for k in range(8):
        add(bass(note(r),beat/2*.95),t0+k*beat/2,.38)
    for k in range(16):
        m=ch[arp[k%8]%len(ch)]+12+(12 if k%8>=6 else 0)
        add(pluck(note(m)),t0+k*s16,.16,(-.5 if k%2 else .5))
    # pad
    t=tt(bar); pad=sum(np.sin(2*np.pi*note(m)*t+np.sin(2*np.pi*.3*t))+.3*np.sin(2*np.pi*note(m)*1.005*t) for m in ch)
    add(pad*np.minimum(1,t*6)*np.minimum(1,(bar-t)*6),t0,.035)
# ---- SFX
def whoosh(d=.5):
    t=tt(d); n=rng.standard_normal(len(t)); a=np.clip(.02+.5*(t/d)**2,0,.9)
    y=np.empty_like(n); acc=0
    for i in range(len(n)): acc+=a[i]*(n[i]-acc); y[i]=acc
    return y*np.sin(np.pi*t/d)**2*1.6
def impact():
    t=tt(1.0); f=60*np.exp(-t*2)+35; s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4)
    n=rng.standard_normal(len(t)); n=lp(n,.05)*np.exp(-t*6)
    cr=rng.standard_normal(len(t)); cr=(cr-lp(cr,.5))*np.exp(-t*3)*.25
    return s+n*2+cr
def pop(i):
    t=tt(.09); f=500+700*(t/.09)+60*(i%5); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*45)*.6
def boing(i):
    t=tt(.45); f0=240+40*(i%4); f=f0*(1+.35*np.exp(-t*6)*np.sin(2*np.pi*14*t))+f0*.6*np.exp(-t*8)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)*np.minimum(1,t*300)
def chime(f,d=.9):
    t=tt(d); return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6))*np.exp(-t*5)*np.minimum(1,t*500)
def shimmer():
    out=np.zeros(int(1.2*SR))
    for k,m in enumerate([72,76,79,84,88,91,96]):
        c=chime(note(m),.9); i=int(k*.05*SR); out[i:i+len(c)]+=c[:len(out)-i]
    return out*.35
for i,t in enumerate(ev['words']): add(pop(i),t,.28,(-.3 if i%2 else .3))
for t in ev['drops']: add(impact(),t,.55)
for t in ev['whoosh']: add(whoosh(.5),t-.1,.5)
add(whoosh(.35),12.5,.3)
add(shimmer(),ev['split']-.02,.9)
for i,t in enumerate(sorted(ev['hits'])): add(boing(i),t,.42,float(np.sin(i*1.7))*.6)
for i,t in enumerate(ev['sparkles']):
    if t<12.8: add(chime(note([84,88,91,96][i%4]),.5),t,.12,float(np.sin(i))*.7)
add(chime(note(79),1.5),14.0,.3); add(chime(note(84),1.4),14.08,.3); add(chime(note(91),1.2),14.16,.25)
# master
x=np.stack([L,R],1); x=np.tanh(x*1.1)
fade=np.ones(N); fl=int(.35*SR); fade[-fl:]=np.linspace(1,0,fl); x*=fade[:,None]
x=x/np.max(np.abs(x))*.93
w=wave.open('audio.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((x*32767).astype('<i2').tobytes()); w.close(); print('ok')
