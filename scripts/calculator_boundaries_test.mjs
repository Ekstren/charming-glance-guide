import assert from 'node:assert/strict';
import {parse} from 'acorn';
import {analyze} from 'eslint-scope';
import {readFileSync} from 'node:fs';
for(const name of ['model','engine','controller']){
 const ast=parse(readFileSync(`src/calculator/${name}.mjs`,'utf8'),{ecmaVersion:2022,sourceType:'module',ranges:true});
 const globals=new Set(analyze(ast,{ecmaVersion:2022,sourceType:'module'}).globalScope.through.map(r=>r.identifier.name));
 const forbidden=name==='controller'?['localStorage']:['document','window','localStorage','navigator'];
 for(const id of forbidden)assert(!globals.has(id),`${name} must not access ${id} directly`);
}
console.log('Calculator math and persistence boundaries passed.');
