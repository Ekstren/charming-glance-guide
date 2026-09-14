import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
const {commit}=JSON.parse(readFileSync('scripts/visual-baseline.json','utf8'));
const temp=mkdtempSync(path.join(tmpdir(),'sxs-perf-')),reference=path.join(temp,'reference');mkdirSync(reference);
const output=path.resolve('test-results/performance');mkdirSync(output,{recursive:true});
try{
 execFileSync('git',['archive','--format=tar',`--output=${path.join(temp,'reference.tar')}`,commit]);
 execFileSync('tar',['-xf',path.join(temp,'reference.tar'),'-C',reference]);
 const samples={baseline:[],candidate:[]};
 for(let repeat=0;repeat<3;repeat++)for(const [name,root] of [['baseline',reference],['candidate',process.cwd()]]){
  const file=path.join(output,`${name}-${repeat}.json`);
  execFileSync(process.execPath,['scripts/calculator_perf_check.mjs'],{env:{...process.env,SXS_PERF_CPU_RATE:'4',SXS_PERF_ROOT:root,SXS_PERF_OUTPUT:file},stdio:'pipe'});
  samples[name].push(JSON.parse(readFileSync(file,'utf8')));
  console.log(`4× CPU slowdown: ${name} sample ${repeat+1}/3`);
 }
 const fingerprint=row=>row.results.map(({ms,solveMs,...result})=>result);
 for(const row of samples.candidate)assert.deepEqual(fingerprint(row),fingerprint(samples.baseline[0]),'Calculator recommendations changed from the approved baseline');
 const median=values=>values.sort((a,b)=>a-b)[Math.floor(values.length/2)];
 const summarize=rows=>({averageMs:median(rows.map(r=>r.averageMs)),worstMs:median(rows.map(r=>r.worstMs)),loadMs:median(rows.map(r=>r.loadMs)),initialOpenMs:median(rows.map(r=>r.initialOpenMs)),firstUseMs:median(rows.map(r=>r.loadMs+r.initialOpenMs)),longestTaskMs:Math.max(0,...rows.flatMap(r=>r.longTasks))});
 const baseline=summarize(samples.baseline),candidate=summarize(samples.candidate);
 writeFileSync(path.join(output,'summary.json'),JSON.stringify({commit,cpuRate:4,viewport:390,baseline,candidate},null,2));
 console.log(JSON.stringify({baseline,candidate},null,2));
 assert(candidate.firstUseMs<=baseline.firstUseMs*1.5+250,'First calculator use regression');
 assert(candidate.averageMs<=baseline.averageMs*1.5+100,'Mobile average solve regression');
 assert(candidate.worstMs<=baseline.worstMs*1.5+250,'Mobile worst solve regression');
 assert(candidate.longestTaskMs<=Math.max(1000,baseline.longestTaskMs*1.5),'Mobile main-thread blocking regression');
}finally{rmSync(temp,{recursive:true,force:true});}
