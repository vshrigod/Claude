import {createRequire} from 'module';const require=createRequire(import.meta.url);const {chromium}=require('playwright');
import fs from 'fs';
const [,,mode,a,b,out='frames']=process.argv;
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
page.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text())});
page.on('pageerror',e=>console.log('PAGEERR',e.message));
await page.goto('http://localhost:8765/index.html');
await page.waitForFunction(()=>window.READY===true,null,{timeout:120000});
fs.mkdirSync(out,{recursive:true});
if(mode==='events'){fs.writeFileSync('events.json',JSON.stringify(await page.evaluate(()=>window.EVENTS)));}
else if(mode==='stills'){for(const t of a.split(',').map(Number)){await page.evaluate(t=>window.renderAt(t),t);await page.screenshot({path:`${out}/still_${t.toFixed(2)}.jpg`,type:'jpeg',quality:85});}}
else{const f0=+a,f1=+b;const t0=Date.now();
  for(let f=f0;f<f1;f++){await page.evaluate(t=>window.renderAt(t),f/30);await page.screenshot({path:`${out}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:95});
   if(f%30==0)console.log('frame',f,((Date.now()-t0)/(f-f0+1)).toFixed(0),'ms/f');}}
await browser.close();
