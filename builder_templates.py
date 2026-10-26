"""App Builder 模板 + 修改验证器。所有颜色/主题需求由 LLM 处理，代码不硬编码。"""

import difflib
import re


# ============================================================
# 2048 V1：干净版，首次生成用
# ============================================================
TEMPLATE_2048_BASE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>2048</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;background:#faf8ef;display:flex;flex-direction:column;align-items:center;padding:20px;margin:0;min-height:100vh}
  h1{color:#776e65;margin:10px 0}
  .stats{display:flex;gap:12px;margin-bottom:16px}
  .stat{background:#bbada0;color:#fff;padding:8px 16px;border-radius:6px;text-align:center}
  .stat .label{font-size:11px;opacity:.9}
  .stat .value{font-size:20px;font-weight:bold}
  #grid{display:grid;grid-template-columns:repeat(4,80px);grid-template-rows:repeat(4,80px);gap:8px;background:#bbada0;padding:10px;border-radius:8px}
  .cell{width:80px;height:80px;background:#cdc1b4;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;color:#776e65;transition:all .1s;overflow:hidden;user-select:none;line-height:1}
  .cell[data-v="2"]{background:#eee4da}
  .cell[data-v="4"]{background:#ede0c8}
  .cell[data-v="8"]{background:#f2b179;color:#f9f6f2}
  .cell[data-v="16"]{background:#f59563;color:#f9f6f2}
  .cell[data-v="32"]{background:#f67c5f;color:#f9f6f2}
  .cell[data-v="64"]{background:#f65e3b;color:#f9f6f2}
  .cell[data-v="128"]{background:#edcf72;color:#f9f6f2;font-size:24px}
  .cell[data-v="256"]{background:#edcc61;color:#f9f6f2;font-size:24px}
  .cell[data-v="512"]{background:#edc850;color:#f9f6f2;font-size:24px}
  .cell[data-v="1024"]{background:#edc53f;color:#f9f6f2;font-size:20px}
  .cell[data-v="2048"]{background:#edc22e;color:#f9f6f2;font-size:20px}
  .cell.big{font-size:18px}
  .cell.huge{font-size:15px}
  button{background:#8f7a66;color:#f9f6f2;border:none;padding:10px 20px;border-radius:6px;font-size:14px;cursor:pointer;margin-top:16px;font-family:inherit}
  button:hover{filter:brightness(1.1)}
  .hint{color:#776e65;font-size:12px;margin-top:12px}
</style>
</head>
<body>
<h1>2048</h1>
<div class="stats">
  <div class="stat"><div class="label">得分</div><div class="value" id="score">0</div></div>
  <div class="stat"><div class="label">最高分</div><div class="value" id="best">0</div></div>
</div>
<button onclick="newGame()">新游戏</button>
<div id="grid"></div>
<div class="hint">方向键或 W/A/S/D 移动，也可在手机上滑动</div>
<script>
const SIZE=4, K_BEST='2048-best';
let grid=[],score=0,best=0;
try{ best = parseInt(localStorage.getItem(K_BEST)||'0')||0; }catch(e){}
document.getElementById('best').textContent=best;
function newGame(){grid=Array.from({length:SIZE},function(){return Array(SIZE).fill(0);});score=0;addTile();addTile();render();}
function addTile(){var empty=[];for(var i=0;i<SIZE;i++)for(var j=0;j<SIZE;j++)if(!grid[i][j])empty.push([i,j]);if(!empty.length)return;var p=empty[Math.floor(Math.random()*empty.length)];grid[p[0]][p[1]]=Math.random()<0.9?2:4;}
function render(){var g=document.getElementById('grid');g.innerHTML='';for(var i=0;i<SIZE;i++)for(var j=0;j<SIZE;j++){var d=document.createElement('div');d.className='cell';var v=grid[i][j];if(v){d.textContent=v;d.dataset.v=v;var len=String(v).length;if(len>=5)d.classList.add('huge');else if(len===4)d.classList.add('big');}g.appendChild(d);}document.getElementById('score').textContent=score;if(score>best){best=score;try{localStorage.setItem(K_BEST,String(best));}catch(e){}document.getElementById('best').textContent=best;}}
function slide(row){var arr=row.filter(function(v){return v;});for(var i=0;i<arr.length-1;i++)if(arr[i]===arr[i+1]){arr[i]*=2;score+=arr[i];arr.splice(i+1,1);}while(arr.length<SIZE)arr.push(0);return arr;}
function move(dir){var old=JSON.stringify(grid);for(var i=0;i<SIZE;i++){var row=[];for(var j=0;j<SIZE;j++){if(dir==='left')row.push(grid[i][j]);if(dir==='right')row.unshift(grid[i][j]);if(dir==='up')row.push(grid[j][i]);if(dir==='down')row.unshift(grid[j][i]);}row=slide(row);for(var j=0;j<SIZE;j++){var k=(dir==='right'||dir==='down')?SIZE-1-j:j;if(dir==='left'||dir==='right')grid[i][k]=row[j];else grid[k][i]=row[j];}}if(JSON.stringify(grid)!==old){addTile();render();}}
document.addEventListener('keydown',function(e){var k=e.key.toLowerCase();if(k==='arrowleft'||k==='a')move('left');if(k==='arrowright'||k==='d')move('right');if(k==='arrowup'||k==='w')move('up');if(k==='arrowdown'||k==='s')move('down');});
var sx,sy;
document.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;});
document.addEventListener('touchend',function(e){if(!sx||!sy)return;var dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;if(Math.abs(dx)>Math.abs(dy))move(dx>0?'right':'left');else move(dy>0?'down':'up');sx=sy=0;});
newGame();
</script>
</body>
</html>"""


# ============================================================
# 待办 V2：编辑 + 筛选 + 持久化（Isabella 问题 2）
# ============================================================
TEMPLATE_TODO = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>待办清单</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:-apple-system,sans-serif;max-width:560px;margin:40px auto;padding:0 20px;background:#f5f7fb;color:#1e293b}
  h1{color:#2563eb;margin-bottom:20px}
  .input-row{display:flex;gap:8px;margin-bottom:16px}
  input[type=text]{flex:1;padding:10px 12px;border:1px solid #cbd5e1;border-radius:6px;font-size:14px;font-family:inherit}
  input[type=text]:focus{outline:none;border-color:#2563eb}
  button{padding:10px 18px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-family:inherit;font-size:14px}
  button:hover{background:#1d4ed8}
  .filters{display:flex;gap:6px;margin-bottom:16px}
  .filter-btn{padding:6px 14px;background:transparent;color:#64748b;border:1px solid #cbd5e1;font-size:13px;border-radius:6px;cursor:pointer;font-family:inherit}
  .filter-btn.active{background:#2563eb;color:#fff;border-color:#2563eb}
  .todo{display:flex;align-items:center;gap:10px;padding:12px;background:#fff;border-radius:6px;margin-bottom:8px;border:1px solid #e2e8f0}
  .todo.done .text{text-decoration:line-through;color:#94a3b8}
  .todo .text{flex:1;font-size:14px;cursor:pointer;padding:2px 0;word-break:break-word}
  .todo .text:hover{color:#2563eb}
  .todo input[type=text]{flex:1;padding:4px 8px;font-size:14px}
  .todo .actions{display:flex;gap:4px;flex-shrink:0}
  .todo .edit-btn,.todo .del-btn{padding:4px 10px;font-size:12px}
  .todo .edit-btn{background:#f59e0b}
  .todo .edit-btn:hover{background:#d97706}
  .todo .del-btn{background:#ef4444}
  .todo .del-btn:hover{background:#dc2626}
  .empty{text-align:center;color:#94a3b8;padding:40px 20px;font-size:14px}
  .toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1e293b;color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;opacity:0;transition:opacity .25s;pointer-events:none;z-index:10}
  .toast.show{opacity:1}
  .toast.error{background:#ef4444}
</style>
</head>
<body>
<h1>待办清单</h1>
<div class="input-row">
  <input type="text" id="inp" placeholder="输入待办事项…" onkeydown="if(event.key==='Enter')addTask()">
  <button onclick="addTask()">添加</button>
</div>
<div class="filters">
  <button class="filter-btn active" data-filter="all" onclick="setFilter('all')">全部</button>
  <button class="filter-btn" data-filter="active" onclick="setFilter('active')">未完成</button>
  <button class="filter-btn" data-filter="done" onclick="setFilter('done')">已完成</button>
</div>
<div id="list"></div>
<div class="toast" id="toast"></div>
<script>
var DATA_KEY='todos-v2', FILTER_KEY='todo-filter-v2';
function loadData(){try{return JSON.parse(localStorage.getItem(DATA_KEY))||[];}catch(e){return [];}}
function saveData(list){try{localStorage.setItem(DATA_KEY,JSON.stringify(list));}catch(e){}}
var todos=loadData(), filter='all';
try{filter=localStorage.getItem(FILTER_KEY)||'all';}catch(e){}
var editingId=null, _idSeq=0;
function nextId(){_idSeq++;return Date.now()*10000+_idSeq;}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function showToast(msg,isError){var el=document.getElementById('toast');el.textContent=msg;el.className='toast show'+(isError?' error':'');clearTimeout(el._t);el._t=setTimeout(function(){el.className='toast';},2000);}
function addTask(){var inp=document.getElementById('inp'),v=inp.value.trim();if(!v){showToast('请输入任务内容',true);return;}todos.push({id:nextId(),text:v,done:false});saveData(todos);inp.value='';inp.focus();render();showToast('已添加');}
function toggleTask(id){var t=todos.find(function(x){return x.id===id;});if(t){t.done=!t.done;saveData(todos);render();}}
function deleteTask(id){todos=todos.filter(function(x){return x.id!==id;});saveData(todos);render();showToast('已删除');}
function startEdit(id){editingId=id;render();}
function saveEdit(id){var inp=document.getElementById('edit-inp');if(!inp)return;var v=inp.value.trim();if(!v){showToast('任务名不能为空',true);return;}var t=todos.find(function(x){return x.id===id;});if(t){t.text=v;saveData(todos);}editingId=null;render();showToast('已更新');}
function cancelEdit(){editingId=null;render();}
function setFilter(f){filter=f;editingId=null;try{localStorage.setItem(FILTER_KEY,f);}catch(e){}render();}
function render(){
  document.querySelectorAll('.filter-btn').forEach(function(b){b.classList.toggle('active',b.dataset.filter===filter);});
  var box=document.getElementById('list');
  var filtered=todos.filter(function(t){if(filter==='active')return !t.done;if(filter==='done')return t.done;return true;});
  if(filtered.length===0){var msg=(filter==='done')?'还没有已完成的任务':(filter==='active')?'所有任务都完成了 🎉':'还没有任务，添加一个吧';box.innerHTML='<div class="empty">'+msg+'</div>';return;}
  box.innerHTML='';
  filtered.forEach(function(t){
    var row=document.createElement('div');row.className='todo'+(t.done?' done':'');
    if(editingId===t.id){
      row.innerHTML='<input type="checkbox" '+(t.done?'checked':'')+' disabled><input type="text" id="edit-inp" value="'+esc(t.text)+'"><div class="actions"><button class="edit-btn" onclick="saveEdit('+t.id+')">保存</button><button class="del-btn" onclick="cancelEdit()">取消</button></div>';
      box.appendChild(row);
      var inp=document.getElementById('edit-inp');
      if(inp){inp.focus();inp.select();inp.onkeydown=function(e){if(e.key==='Enter')saveEdit(t.id);if(e.key==='Escape')cancelEdit();};}
    }else{
      row.innerHTML='<input type="checkbox" '+(t.done?'checked':'')+' onchange="toggleTask('+t.id+')"><span class="text" onclick="toggleTask('+t.id+')">'+esc(t.text)+'</span><div class="actions"><button class="edit-btn" onclick="startEdit('+t.id+')">编辑</button><button class="del-btn" onclick="deleteTask('+t.id+')">删除</button></div>';
      box.appendChild(row);
    }
  });
}
render();
</script>
</body>
</html>"""

# ============================================================
# 计算器（完整持久化）
# ============================================================
TEMPLATE_CALC = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>计算器</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#1e293b}
  .calc{background:#0f172a;padding:20px;border-radius:12px;width:280px}
  .display{background:#1e293b;color:#fff;padding:20px;text-align:right;font-size:28px;border-radius:8px;margin-bottom:12px;overflow:hidden;font-family:monospace}
  .btns{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
  .btns button{padding:20px;font-size:18px;border:none;border-radius:8px;background:#334155;color:#fff;cursor:pointer;font-family:inherit}
  .btns button:hover{background:#475569}
  .btns .op{background:#3b82f6}
  .btns .eq{background:#10b981}
</style></head><body>
<div class="calc">
<div class="display" id="d">0</div>
<div class="btns">
<button onclick="c()">C</button><button onclick="del()">⌫</button><button class="op" onclick="op('/')">÷</button><button class="op" onclick="op('*')">×</button>
<button onclick="num('7')">7</button><button onclick="num('8')">8</button><button onclick="num('9')">9</button><button class="op" onclick="op('-')">-</button>
<button onclick="num('4')">4</button><button onclick="num('5')">5</button><button onclick="num('6')">6</button><button class="op" onclick="op('+')">+</button>
<button onclick="num('1')">1</button><button onclick="num('2')">2</button><button onclick="num('3')">3</button><button class="eq" onclick="eq()">=</button>
<button onclick="num('0')" style="grid-column:span 2">0</button><button onclick="num('.')">.</button>
</div></div>
<script>
var cur='0', prev=null, ope=null, K='calc-state-v1';
function save(){ try{ localStorage.setItem(K, JSON.stringify({cur:cur,prev:prev,ope:ope})); }catch(e){} }
function load(){
  try{
    var s = JSON.parse(localStorage.getItem(K) || 'null');
    if (s) { cur = s.cur || '0'; prev = s.prev; ope = s.ope; }
  }catch(e){}
}
function upd(){ document.getElementById('d').textContent = cur; save(); }
function num(n){ if(cur==='0' && n!=='.') cur=n; else cur+=n; upd(); }
function c(){ cur='0'; prev=null; ope=null; upd(); }
function del(){ cur = cur.length > 1 ? cur.slice(0,-1) : '0'; upd(); }
function op(o){ if(ope && prev!==null) eq(); prev=parseFloat(cur); ope=o; cur='0'; save(); }
function eq(){
  if(ope===null) return;
  var b = parseFloat(cur), r = 0;
  if(ope==='+') r = prev + b;
  if(ope==='-') r = prev - b;
  if(ope==='*') r = prev * b;
  if(ope==='/') r = b === 0 ? 'ERR' : prev / b;
  cur = String(r); ope = null; prev = null; upd();
}
load(); upd();
</script></body></html>"""


# ============================================================
# 番茄钟（完整持久化）
# ============================================================
TEMPLATE_POMODORO = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>番茄钟</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0f172a;color:#e6ebf5}
  h1{font-size:20px;margin-bottom:20px}
  .timer{font-size:96px;font-family:monospace;font-weight:bold;color:#60a5fa;margin-bottom:8px}
  .mode{font-size:14px;color:#94a3b8;margin-bottom:24px}
  .btns{display:flex;gap:12px}
  button{padding:12px 28px;font-size:15px;border:none;border-radius:8px;background:#3b82f6;color:#fff;cursor:pointer;font-family:inherit}
  button.secondary{background:#334155}
  button:hover{filter:brightness(1.15)}
</style></head><body>
<h1>🍅 番茄钟</h1>
<div class="mode" id="mode">工作时间</div>
<div class="timer" id="timer">25:00</div>
<div class="btns">
  <button id="toggle" onclick="toggle()">开始</button>
  <button class="secondary" onclick="reset()">重置</button>
</div>
<script>
var WORK = 25 * 60, BREAK = 5 * 60;
var mode = 'work', remain = WORK, timer = null, running = false;
var K = 'pomo-state-v1';
function fmt(s){ return String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0'); }
function save(){ try{ localStorage.setItem(K, JSON.stringify({mode:mode,remain:remain})); }catch(e){} }
function load(){
  try{
    var s = JSON.parse(localStorage.getItem(K) || 'null');
    if (s) { mode = s.mode || 'work'; remain = typeof s.remain === 'number' ? s.remain : WORK; }
  }catch(e){}
}
function render(){
  document.getElementById('timer').textContent = fmt(remain);
  document.getElementById('mode').textContent = mode === 'work' ? '工作时间' : '休息时间';
  document.getElementById('toggle').textContent = running ? '暂停' : '开始';
  save();
}
function toggle(){
  if (running) { clearInterval(timer); running = false; render(); return; }
  running = true; render();
  timer = setInterval(function(){
    remain--;
    if (remain <= 0) {
      clearInterval(timer); running = false;
      if (mode === 'work') { mode = 'break'; remain = BREAK; }
      else { mode = 'work'; remain = WORK; }
    }
    render();
  }, 1000);
}
function reset(){ clearInterval(timer); running = false; mode = 'work'; remain = WORK; render(); }
load(); render();
</script></body></html>"""


# ============================================================
# 记账本
# ============================================================
TEMPLATE_LEDGER = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>记账本</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:-apple-system,sans-serif;max-width:640px;margin:40px auto;padding:0 20px;background:#f5f7fb;color:#1e293b}
  h1{color:#7c3aed}
  .row{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}
  input,select{padding:10px;border:1px solid #cbd5e1;border-radius:6px;font-size:14px;font-family:inherit}
  input{flex:1;min-width:120px}
  button{padding:10px 20px;background:#7c3aed;color:#fff;border:none;border-radius:6px;cursor:pointer;font-family:inherit}
  button:hover{filter:brightness(1.1)}
  .list{background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e2e8f0}
  .item{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f1f5f9;gap:8px}
  .item:last-child{border-bottom:none}
  .amt{font-family:monospace;font-weight:bold;color:#dc2626}
  .amt.income{color:#059669}
  .stats{display:flex;gap:16px;margin:16px 0;padding:16px;background:#fff;border-radius:8px;border:1px solid #e2e8f0}
  .stat{flex:1;text-align:center}
  .stat .l{font-size:11px;color:#94a3b8;margin-bottom:4px}
  .stat .v{font-family:monospace;font-size:18px;font-weight:bold}
  .del{background:none;border:none;color:#ef4444;cursor:pointer;font-size:12px;padding:4px 8px}
  .toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
    background:#1e293b;color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;
    opacity:0;transition:opacity .25s;pointer-events:none;z-index:10}
  .toast.show{opacity:1}
  .toast.error{background:#ef4444}
</style></head><body>
<h1>💰 记账本</h1>
<div class="stats">
  <div class="stat"><div class="l">收入</div><div class="v" id="s-in" style="color:#059669">¥0</div></div>
  <div class="stat"><div class="l">支出</div><div class="v" id="s-out" style="color:#dc2626">¥0</div></div>
  <div class="stat"><div class="l">结余</div><div class="v" id="s-net">¥0</div></div>
</div>
<div class="row">
  <input id="desc" placeholder="描述">
  <input id="amt" type="number" placeholder="金额" style="max-width:120px">
  <select id="type"><option value="out">支出</option><option value="in">收入</option></select>
  <button onclick="add()">添加</button>
</div>
<div class="list" id="list"></div>
<div class="toast" id="toast"></div>
<script>
var K = 'ledger-v2';
function loadData(){ try{ return JSON.parse(localStorage.getItem(K)) || []; }catch(e){ return []; } }
function saveData(v){ try{ localStorage.setItem(K, JSON.stringify(v)); }catch(e){} }
var items = loadData();
var _idSeq = 0;
function nextId(){ _idSeq++; return Date.now() * 10000 + _idSeq; }
function esc(s){
  return String(s).replace(/[&<>"']/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
  });
}
function showToast(msg, err){
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (err ? ' error' : '');
  clearTimeout(el._t);
  el._t = setTimeout(function(){ el.className = 'toast'; }, 1800);
}
function add(){
  var d = document.getElementById('desc').value.trim();
  var a = parseFloat(document.getElementById('amt').value);
  var t = document.getElementById('type').value;
  if (!d) { showToast('请填写描述', true); return; }
  if (!a || a <= 0) { showToast('请输入有效金额', true); return; }
  items.unshift({ id: nextId(), desc: d, amt: a, type: t });
  saveData(items);
  document.getElementById('desc').value = '';
  document.getElementById('amt').value = '';
  render();
  showToast('已添加');
}
function del(id){
  items = items.filter(function(i){ return i.id !== id; });
  saveData(items);
  render();
  showToast('已删除');
}
function render(){
  var box = document.getElementById('list');
  var inS = 0, outS = 0;
  box.innerHTML = items.map(function(i){
    if (i.type === 'in') inS += i.amt; else outS += i.amt;
    return '<div class="item">' +
      '<span>' + esc(i.desc) + '</span>' +
      '<div><span class="amt ' + (i.type === 'in' ? 'income' : '') + '">' +
      (i.type === 'in' ? '+' : '-') + '¥' + i.amt.toFixed(2) + '</span>' +
      '<button class="del" onclick="del(' + i.id + ')">删除</button></div>' +
      '</div>';
  }).join('') || '<div class="item" style="color:#94a3b8;justify-content:center">暂无记录</div>';
  document.getElementById('s-in').textContent = '¥' + inS.toFixed(2);
  document.getElementById('s-out').textContent = '¥' + outS.toFixed(2);
  document.getElementById('s-net').textContent = '¥' + (inS - outS).toFixed(2);
}
render();
</script></body></html>"""


# ============================================================
# 贪吃蛇（持久化最高分）
# ============================================================
TEMPLATE_SNAKE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>贪吃蛇</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0f172a;color:#e6ebf5}
  h1{font-size:20px;margin-bottom:12px}
  canvas{background:#1e293b;border-radius:8px}
  .score{font-size:14px;color:#94a3b8;margin-bottom:12px}
  .hint{font-size:12px;color:#64748b;margin-top:12px}
</style></head><body>
<h1>🐍 贪吃蛇</h1>
<div class="score">得分：<span id="score">0</span> · 最高分：<span id="best">0</span></div>
<canvas id="c" width="400" height="400"></canvas>
<div class="hint">方向键 / WASD 控制</div>
<script>
var cvs = document.getElementById('c');
var ctx = cvs.getContext('2d');
var S = 20, W = 20, H = 20, K_BEST = 'snake-best-v1';
var snake = [{x:10,y:10}], dir = {x:1,y:0}, food = {x:15,y:15};
var score = 0, over = false, tick = null, best = 0;
try { best = parseInt(localStorage.getItem(K_BEST) || '0') || 0; } catch(e){}
document.getElementById('best').textContent = best;
function saveBest(v){ try{ localStorage.setItem(K_BEST, String(v)); }catch(e){} }
function reset(){
  snake = [{x:10,y:10}]; dir = {x:1,y:0}; score = 0; over = false;
  placeFood();
  document.getElementById('score').textContent = 0;
  clearInterval(tick); tick = setInterval(step, 120);
  draw();
}
function placeFood(){
  do { food = {x: Math.floor(Math.random()*W), y: Math.floor(Math.random()*H)}; }
  while (snake.some(function(s){ return s.x===food.x && s.y===food.y; }));
}
function step(){
  if (over) return;
  var h = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
  if (h.x < 0 || h.x >= W || h.y < 0 || h.y >= H ||
      snake.some(function(s){ return s.x===h.x && s.y===h.y; })) {
    over = true; clearInterval(tick);
    ctx.fillStyle = 'rgba(0,0,0,.7)';
    ctx.fillRect(0,0,cvs.width,cvs.height);
    ctx.fillStyle = '#f87171';
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('游戏结束', cvs.width/2, cvs.height/2);
    setTimeout(reset, 1500);
    return;
  }
  snake.unshift(h);
  if (h.x === food.x && h.y === food.y) {
    score++;
    document.getElementById('score').textContent = score;
    if (score > best) { best = score; saveBest(best); document.getElementById('best').textContent = best; }
    placeFood();
  } else { snake.pop(); }
  draw();
}
function draw(){
  ctx.fillStyle = '#1e293b';
  ctx.fillRect(0,0,cvs.width,cvs.height);
  ctx.fillStyle = '#ef4444';
  ctx.fillRect(food.x*S+2, food.y*S+2, S-4, S-4);
  snake.forEach(function(s,i){
    ctx.fillStyle = i === 0 ? '#60a5fa' : '#3b82f6';
    ctx.fillRect(s.x*S+1, s.y*S+1, S-2, S-2);
  });
}
document.addEventListener('keydown', function(e){
  var k = e.key.toLowerCase();
  if ((k === 'arrowup' || k === 'w') && dir.y === 0) dir = {x:0,y:-1};
  if ((k === 'arrowdown' || k === 's') && dir.y === 0) dir = {x:0,y:1};
  if ((k === 'arrowleft' || k === 'a') && dir.x === 0) dir = {x:-1,y:0};
  if ((k === 'arrowright' || k === 'd') && dir.x === 0) dir = {x:1,y:0};
});
reset();
</script></body></html>"""


# ============================================================
# 天气卡片
# ============================================================
TEMPLATE_WEATHER = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>天气卡片</title>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;
    background:linear-gradient(135deg,#1e3a8a,#312e81);color:#fff}
  .card{background:rgba(255,255,255,.1);backdrop-filter:blur(10px);padding:40px;border-radius:20px;
    min-width:300px;text-align:center;border:1px solid rgba(255,255,255,.2)}
  .city{font-size:20px;margin-bottom:8px}
  .temp{font-size:64px;font-weight:bold;font-family:monospace}
  .desc{font-size:16px;opacity:.8;margin-top:4px}
  .detail{display:flex;gap:20px;margin-top:24px;justify-content:center;font-size:13px;opacity:.85}
  select{margin-top:16px;padding:8px 12px;border-radius:8px;border:none;background:rgba(255,255,255,.2);color:#fff;font-size:14px;font-family:inherit;cursor:pointer;width:100%}
  select option{color:#1e293b}
</style></head><body>
<div class="card">
  <div class="city" id="city">北京</div>
  <div class="temp" id="temp">22°</div>
  <div class="desc" id="desc">晴</div>
  <div class="detail">
    <div>湿度 <span id="hum">45%</span></div>
    <div>风速 <span id="wind">12 km/h</span></div>
  </div>
  <select id="sel" onchange="load()">
    <option>北京</option><option>上海</option><option>广州</option>
    <option>深圳</option><option>杭州</option><option>成都</option>
  </select>
</div>
<script>
var K = 'weather-city-v1';
var DATA = {
  '北京': {temp:22, desc:'晴', hum:45, wind:12},
  '上海': {temp:26, desc:'多云', hum:65, wind:8},
  '广州': {temp:30, desc:'阵雨', hum:75, wind:10},
  '深圳': {temp:29, desc:'晴', hum:70, wind:15},
  '杭州': {temp:24, desc:'阴', hum:60, wind:9},
  '成都': {temp:20, desc:'小雨', hum:80, wind:6}
};
function load(){
  var c = document.getElementById('sel').value;
  var d = DATA[c];
  document.getElementById('city').textContent = c;
  document.getElementById('temp').textContent = d.temp + '°';
  document.getElementById('desc').textContent = d.desc;
  document.getElementById('hum').textContent = d.hum + '%';
  document.getElementById('wind').textContent = d.wind + ' km/h';
  try{ localStorage.setItem(K, c); }catch(e){}
}
try{
  var saved = localStorage.getItem(K);
  if (saved && DATA[saved]) document.getElementById('sel').value = saved;
}catch(e){}
load();
</script></body></html>"""


# ============================================================
# 物流数据面板
# ============================================================
TEMPLATE_LOGISTICS = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>物流数据面板</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body{font-family:sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#0f172a;color:#e6ebf5}
  h1{color:#60a5fa;margin-bottom:20px}
  .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
  .stat{background:#1e293b;padding:20px;border-radius:12px;border:1px solid #334155}
  .stat .l{font-size:12px;color:#94a3b8;margin-bottom:8px;text-transform:uppercase}
  .stat .v{font-size:28px;font-weight:bold;font-family:monospace;color:#60a5fa}
  .charts{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .chart-card{background:#1e293b;padding:20px;border-radius:12px;border:1px solid #334155}
  .chart-card h3{font-size:14px;color:#94a3b8;margin-bottom:16px}
  .chart-card canvas{max-height:260px}
  .loading{text-align:center;color:#94a3b8;padding:40px}
  .error{color:#f87171;padding:20px;text-align:center;line-height:1.8}
</style></head><body>
<h1>📦 物流数据面板</h1>
<div id="content" class="loading">加载中…</div>
<script>
function esc(s){
  return String(s).replace(/[&<>"']/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
  });
}
async function load(){
  try {
    var r = await fetch('/api/public/dashboard');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    render(await r.json());
  } catch (e) {
    document.getElementById('content').innerHTML =
      '<div class="error">加载失败：' + esc(e.message) +
      '<br/><small>请确保在 RouteMind 站点内打开</small></div>';
  }
}
function render(d){
  var sd = d.status_distribution || {};
  var html = '<div class="stats">' +
    '<div class="stat"><div class="l">总订单</div><div class="v">' + (d.total || 0).toLocaleString() + '</div></div>' +
    '<div class="stat"><div class="l">已送达</div><div class="v" style="color:#34d399">' + (sd['Delivered'] || 0).toLocaleString() + '</div></div>' +
    '<div class="stat"><div class="l">在途</div><div class="v" style="color:#60a5fa">' + (sd['In Transit'] || 0).toLocaleString() + '</div></div>' +
    '<div class="stat"><div class="l">异常</div><div class="v" style="color:#f87171">' + (sd['Exception'] || 0).toLocaleString() + '</div></div>' +
    '</div>' +
    '<div class="charts">' +
    '<div class="chart-card"><h3>按承运商</h3><canvas id="c1"></canvas></div>' +
    '<div class="chart-card"><h3>按洲分布</h3><canvas id="c2"></canvas></div>' +
    '</div>';
  document.getElementById('content').innerHTML = html;
  document.getElementById('content').className = '';
  new Chart(document.getElementById('c1'), {
    type: 'bar',
    data: {
      labels: (d.carriers || []).map(function(c){ return c.name; }),
      datasets: [{ data: (d.carriers || []).map(function(c){ return c.count; }),
        backgroundColor: 'rgba(96,165,250,.75)', borderRadius: 6 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,.05)' }, beginAtZero: true }
      }
    }
  });
  new Chart(document.getElementById('c2'), {
    type: 'doughnut',
    data: {
      labels: (d.continents || []).map(function(c){ return c.name; }),
      datasets: [{ data: (d.continents || []).map(function(c){ return c.count; }),
        backgroundColor: ['#60a5fa','#8b5cf6','#fbbf24','#34d399','#f87171'],
        borderColor: '#0f172a', borderWidth: 3 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { color: '#94a3b8', boxWidth: 10, padding: 10 } } }
    }
  });
}
load();
</script></body></html>"""


# ============================================================
# 首次生成：只匹配模板名，2048 返回干净 V1
# ============================================================
def match_template(instruction: str):
    t = (instruction or "").lower()
    if "2048" in t or ("游戏" in t and "贪吃" not in t and "snake" not in t):
        return TEMPLATE_2048_BASE, "2048 游戏"
    if "待办" in t or "todo" in t or "清单" in t or "任务" in t:
        return TEMPLATE_TODO, "待办清单"
    if "计算器" in t or "calc" in t:
        return TEMPLATE_CALC, "计算器"
    if "番茄" in t or "pomodoro" in t or "专注" in t:
        return TEMPLATE_POMODORO, "番茄钟"
    if "记账" in t or "账本" in t or "ledger" in t:
        return TEMPLATE_LEDGER, "记账本"
    if "贪吃蛇" in t or "snake" in t:
        return TEMPLATE_SNAKE, "贪吃蛇"
    if "天气" in t or "weather" in t:
        return TEMPLATE_WEATHER, "天气卡片"
    if "物流" in t or "订单" in t or "logistics" in t:
        return TEMPLATE_LOGISTICS, "物流数据面板"
    return None, None


# ============================================================
# 功能关键词标记（用于验证"功能是否实现"）
# 注意：不包含颜色！颜色由 LLM 自由发挥，不做具体色值检查
# ============================================================
INTENT_MARKERS = {
    "撤销": ["undo", "history", "撤销"],
    "undo": ["undo", "history", "撤销"],
    "回退": ["undo", "history", "撤销"],
    "排名": ["rank", "ranking", "排行", "leaderboard"],
    "排行": ["rank", "ranking", "排行", "leaderboard"],
    "排行榜": ["rank", "ranking", "排行", "leaderboard"],
    "音效": ["audio", "sound", "beep", "Audio"],
    "声音": ["audio", "sound", "beep"],
    "暂停": ["pause", "暂停"],
    "计时": ["timer", "setInterval", "计时"],
    "排序": ["sort", "排序"],
    "搜索": ["search", "filter", "搜索"],
    "批量": ["batch", "批量", "selectAll"],
    "编辑": ["edit", "rename", "编辑"],
    "筛选": ["filter", "筛选"],
    "统计": ["stats", "statistics", "统计"],
    "图表": ["chart", "Chart", "图表"],
}


# ============================================================
# 验证修改是否真正生效
# 策略：宽松但守住底线
#   ✅ 代码确实变了
#   ✅ 长度没缩短太多
#   ✅ 指令提到的功能要有对应关键词
#   ❌ 不检查颜色具体值
# ============================================================
def validate_modification(old_code: str, new_code: str, instruction: str):
    errors = []
    if not old_code or not new_code:
        return ["代码为空"]

    if old_code.strip() == new_code.strip():
        return ["新代码与旧代码完全相同"]

    # 代码必须真的变了
    ratio = difflib.SequenceMatcher(None, old_code, new_code).ratio()
    if ratio > 0.98:
        errors.append(f"相似度 {ratio:.1%}，几乎没改动")

    # 不能丢太多
    if len(new_code) < len(old_code) * 0.5:
        errors.append(f"新代码比原代码短 {100 - len(new_code)*100//len(old_code)}%，可能丢了原有功能")

    # 功能关键词检查（只检查功能，不检查颜色）
    new_lower = new_code.lower()
    for intent, markers in INTENT_MARKERS.items():
        if intent in instruction:
            if not any(m.lower() in new_lower for m in markers):
                errors.append(f"未实现「{intent}」功能")

    return errors