// Old baseline commits initialize synchronously; current builds load a chunk.
export async function waitForCalculatorReady(page){
 await page.waitForFunction(()=>!document.getElementById('calculatorLoadStatus')||document.getElementById('calculatorSection').dataset.calculatorReady==='true');
}
