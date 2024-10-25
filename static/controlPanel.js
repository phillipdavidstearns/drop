(function() {
  'use strict';
  window.addEventListener('load', async function() {
    initControlPanel();
  }, false);
})();

function initControlPanel(){

  //Register Controls

  document.getElementById(`register-reset-button`).addEventListener('click', async (e) => {
    resetRegisterControls();
    await setRegister();
  });

  document.getElementById(`register-invert-button`).addEventListener('click', async (e) => {
    invertRegisterControls();
    await setRegister();
  });

  document.getElementById(`register-randomize-button`).addEventListener('click', async (e) => {
    randomizeRegisterControls();
    await setRegister();
  });

  document.getElementById(`register-set-button`).addEventListener('click', async (e) => {
    await setRegister();
  });

  for(let i = 0; i < 8; i++){
    document.getElementById(`register-bit-${i}`).addEventListener('change', async (e) => {
      await setRegister();
    });
  }

  // Loop timing controls

  document.getElementById('loop-delay-min').addEventListener('click', (e) =>{
    let delay_elem = document.getElementById(`loop-delay-value`);
    delay_elem.value=0.0;
    delay_elem.dispatchEvent(new Event('input'));
  });

  document.getElementById('loop-delay-max').addEventListener('click', (e) =>{
    let delay_elem = document.getElementById(`loop-delay-value`);
    delay_elem.value=1.0;
    delay_elem.dispatchEvent(new Event('input'));
  });

  document.getElementById(`loop-delay-range`).addEventListener('input', (e) => {
    let delay_elem = document.getElementById(`loop-delay-value`);
    delay_elem.value = e.target.value;
    delay_elem.dispatchEvent(new Event('input'));
  });

  document.getElementById(`loop-delay-value`).addEventListener('input', async (e) =>{
    await setLoopDelay(parseFloat(e.target.value));
  });

  document.getElementById(`run-loop`).addEventListener('change', async (e) => {
    if(e.target.checked){
      await startLoop();
    } else {
      await stopLoop();
    }
  });

  // LFSR Controls

  document.getElementById(`lfsr-enable`).addEventListener('click', async (e) => {
    await setLFSR();
  });

  document.getElementById('direction-select').addEventListener('change', async (e) => {
    if(document.getElementById(`lfsr-enable`).checked){
      await setLFSR();
    }
  });

  document.getElementById(`flip-lfsr-button`).addEventListener('click', async (e) => {
    flipDirection();
    await setLFSR();
  });

  //configures the refreshing of the LFSR settings in real-time
  for(let i = 1; i <= 3; i++){
    document.getElementById(`tap-${i}-enable`).addEventListener('change', async (e) => {
      await setLFSR();
    });
    document.getElementById(`tap-${i}-value`).addEventListener('change', async (e) => {
      let en = document.getElementById(`tap-${i}-enable`);
      if(en.checked){
        await setLFSR();
      }
    });
    document.getElementById(`tap-${i}-randomize-button`).addEventListener('click', (e) => {
      let q = document.getElementById(`tap-${i}-value`);
      q.value = Math.floor(8 * Math.random());
      q.dispatchEvent(new Event('change'));
    });
  }
  document.getElementById('mod-enable').addEventListener('change', async (e) => {
    await setLFSR();
  });
  document.getElementById('mod-source-select').addEventListener('change', async (e) => {
    if(document.getElementById('mod-enable').checked){
      await setLFSR();
    }
  });
  document.getElementById('mod-value').addEventListener('change', async (e) => {
    if(document.getElementById('mod-enable').checked){
      await setLFSR();
    }
  });
  document.getElementById(`mod-randomize-button`).addEventListener('click', async (e) => {
    let q = document.getElementById(`mod-value`);
    q.value = Math.floor(8 * Math.random());
    let sel = document.getElementById(`mod-source-select`);
    sel.options.selectedIndex = Math.floor(7 * Math.random());
    if(document.getElementById('mod-enable').checked){
      await setLFSR();
    }
  });

  // Strobe Controls

  document.getElementById(`set-strobe-button`).addEventListener('click', async (e) => {
    await setStrobe();
  });

  document.getElementById(`strobe-live`).addEventListener('change', async (e) => {
    if(e.target.checked){
      document.getElementById(`set-strobe-button`).disabled=true;
      await setStrobe();
    } else {
      document.getElementById(`set-strobe-button`).disabled=false;
    }
  });

  document.getElementById('invert-on-count').addEventListener('change', async (e) => {
    if(document.getElementById(`strobe-live`).checked){
      await setStrobe();
    }
  });
  document.getElementById('invert-off-count').addEventListener('change', async (e) => {
    if(document.getElementById(`strobe-live`).checked){
      await setStrobe();
    }
  });
  document.getElementById('mute-on-count').addEventListener('change', async (e) => {
    if(document.getElementById(`strobe-live`).checked){
      await setStrobe();
    }
  });
  document.getElementById('mute-off-count').addEventListener('change', async (e) => {
    if(document.getElementById(`strobe-live`).checked){
      await setStrobe();
    }
  });

  document.getElementById('strobe-invert-enable').addEventListener('change', async (e) => {
    await setStrobe();
  });

  document.getElementById('strobe-mute-enable').addEventListener('change', async (e) => {
    await setStrobe();
  });

  document.getElementById(`strobe-enable`).addEventListener('click', async (e) => {
    await setStrobe();
  });

  document.getElementById('delay-inc-button').addEventListener('click', (e) => {
    nudgeDelayAmount(parseFloat(document.getElementById('nudge-amount').value)*0.01);
  });

  document.getElementById('delay-dec-button').addEventListener('click', (e) => {
    nudgeDelayAmount(-parseFloat(document.getElementById('nudge-amount').value)*0.01);
  });

  document.getElementById('start-ramp').addEventListener('click', (e) => {
    e.target.disabled = true;
    document.getElementById('stop-ramp').disabled=false;
    startRamp();
  });

  document.getElementById('stop-ramp').addEventListener('click', (e) => {
    e.target.disabled = true;
    document.getElementById('start-ramp').disabled=false;
  });

  document.getElementById('start-percent-range').addEventListener('input', (e) =>{
    document.getElementById('start-percent').value = e.target.value;
  });
  document.getElementById('start-percent').addEventListener('input', (e) =>{
    document.getElementById('start-percent-range').value = e.target.value;
  });

  document.getElementById('end-percent-range').addEventListener('input', (e) =>{
    document.getElementById('end-percent').value = e.target.value;
  });
  document.getElementById('end-percent').addEventListener('input', (e) => {
    document.getElementById('end-percent-range').value = e.target.value;
  });

  document.getElementById('ramp-duration').addEventListener('input', (e) => {
    document.getElementById('ramp-duration-range').value = e.target.value;
  });
  document.getElementById('ramp-duration-range').addEventListener('input', (e) => {
    document.getElementById('ramp-duration').value = e.target.value;
  });

  // get current percentage and apply to widgets
  document.getElementById('loop-current').addEventListener('click', async (e) => {
    const result = await getCurrentPercentage();
    document.getElementById('loop-delay-range').value = result;
  });
  document.getElementById('ramp-start-current').addEventListener('click', async (e) => {
    const result = await getCurrentPercentage();
    const elem = document.getElementById('start-percent-range');
    elem.value = result;
    elem.dispatchEvent(new Event('input'));
  });
  document.getElementById('ramp-end-current').addEventListener('click', async (e) => {
    const result = await getCurrentPercentage();
    const elem = document.getElementById('end-percent-range');
    elem.value = result;
    elem.dispatchEvent(new Event('input'));
  });
}

function resetRegisterControls(){
  for(let i=0;i<8;i++){
    document.getElementById(`register-bit-${i}`).checked = false;
  }
}

function invertRegisterControls(){
  for(let i=0;i<8;i++){
    document.getElementById(`register-bit-${i}`).checked ^= true;
  }
}

function randomizeRegisterControls(){
  for(let i=0;i<8;i++){
    document.getElementById(`register-bit-${i}`).checked = Math.random() < 0.5;
  }
}

async function send_request(url, method, data){
  let settings = {}
  if(method !== 'GET'){
    settings.body = JSON.stringify(data)
  }
  settings.method = `${method.toUpperCase()}`
  const {result} = await fetch(url, settings)
  .then(async (response) => await response.json())
  .catch((error) => console.error(error));
  return result;
}

async function getCurrentPercentage(){
  let url='/delay';
  let method='GET';
  let data = {};
  const result = await send_request(url, method, data);
  return result;
}

async function setRegister() {
  let url='/?target=register';
  let method='POST';
  let data = {'parameters': {'state': []}};

  for(let i=0;i<8;i++){
    data.parameters.state.push(document.getElementById(`register-bit-${i}`).checked ? 1 : 0);
  }

  const result = await send_request(url, method, data);
  return result;
}

async function setLoopDelay(delay){
  let url='/?target=loop_delay';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.value = delay;

  const result = await send_request(url, method, data);
  document.getElementById('loop-delay-range').value = result;
  return result;
}

async function multLoopDelay(mult){
  let url='/?target=mult_loop_delay';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.value =  mult;

  const result = await send_request(url, method, data);
  document.getElementById('loop-delay-range').value = result;
  return result;
}

async function divLoopDelay(div){
  let url='/?target=div_loop_delay';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.value = div;

  const result = await send_request(url, method, data);
  document.getElementById('loop-delay-range').value = result;
  return result;
}

async function startLoop(){
  let url='/?target=loop';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.retrigger = true;

  const result = await send_request(url, method, data);
  return result;
}

async function stopLoop(){
  let url='/?target=loop';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.retrigger = false;

  const result =  await send_request(url, method, data);
  return result;
}

async function setLFSR(){
  let url='/?target=lfsr';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters={
    'taps' : [],
    'modQ' : parseInt(document.getElementById(`mod-value`).value),
    'modEnabled' : document.getElementById('mod-enable').checked,
    'modSource' : null,
    'direction' : 'left',
    'is_enabled' : document.getElementById(`lfsr-enable`).checked
  };
  for(let i = 1; i <= 3;i++){
    if(document.getElementById(`tap-${i}-enable`).checked){
      data.parameters.taps.push(parseInt(document.getElementById(`tap-${i}-value`).value));
    }
  }
  const directions = document.getElementById('direction-select').options;
  data.parameters.direction = directions[directions.selectedIndex].value;
  const sources = document.getElementById('mod-source-select').options;
  data.parameters.modSource = parseInt(sources[sources.selectedIndex].value);

  const result = await send_request(url, method, data);
  return result;
}

async function setStrobe(){
  let url='/?target=strobe';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters={
    'invert_enabled': document.getElementById('strobe-invert-enable').checked,
    'invert_on': parseInt(document.getElementById('invert-on-count').value),
    'invert_off': parseInt(document.getElementById('invert-off-count').value),
    'mute_enabled': document.getElementById('strobe-mute-enable').checked,
    'mute_on': parseInt(document.getElementById('mute-on-count').value),
    'mute_off': parseInt(document.getElementById('mute-off-count').value),
    'is_enabled': document.getElementById(`strobe-enable`).checked
  };
  const result = await send_request(url, method, data);
  return result;
}

async function nudgeDelayAmount(amount){
  let url='/?target=nudge_delay';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.value = amount;

  const result = await send_request(url, method, data);
  document.getElementById('loop-delay-range').value = result;
  return result;
}

async function setTempo(value){
  let tempo = parseFloat(document.getElementById('tempo-base').value);
  let url='/?target=tempo';
  let method='POST';
  let data = {'parameters':{}};
  data.parameters.value = value * ( 60 / tempo );

 const result =  await send_request(url, method, data);
 document.getElementById('loop-delay-range').value = result;
 return result;
}

function flipDirection() {
  const options = document.getElementById('direction-select').options
  if(options[0].selected){
    options[0].selected=false;
    options[1].selected=true;
  } else {
    options[1].selected=false;
    options[0].selected=true;
  }
}

function startRamp(){
  let end = parseFloat(document.getElementById('end-percent').value);
  let start = parseFloat(document.getElementById('start-percent').value);
  let duration = parseFloat(document.getElementById('ramp-duration').value);
  let steps = Math.floor(20 * duration);
  let interval = 1000 * duration / steps;
  let increment = ( end - start ) / steps;
  let step = 0;
  rampInterval(interval, increment, steps, step);
}

function swapRampStartEnd(){
  let end_elem = document.getElementById('end-percent');
  let start_elem = document.getElementById('start-percent');
  let end = parseFloat(end_elem.value);
  let start = parseFloat(start_elem.value);
  end_elem.value=start;
  start_elem.value=end;
  end_elem.dispatchEvent(new Event('input'));
  start_elem.dispatchEvent(new Event('input'));
}

function rampInterval(interval, increment, steps, step){
  if(document.getElementById('start-ramp').checked && step < steps){
    let range = document.getElementById(`loop-delay-value`);
    if(step == 0){
      range.value = parseFloat(document.getElementById('start-percent').value);
    } else if(step >= steps-1){
      range.value = parseFloat(document.getElementById('end-percent').value);
      document.getElementById('stop-ramp').dispatchEvent(new Event('click'));
      
      if(document.getElementById('ramp-ping-pong').checked){
        swapRampStartEnd();
        document.getElementById('start-ramp').dispatchEvent(new Event('click'));
      } else if(document.getElementById('ramp-up').checked){
        document.getElementById('start-ramp').dispatchEvent(new Event('click'));
      }

    } else {
      range.value = parseFloat(range.value) + increment;
    }
    range.dispatchEvent(new Event('input'));
    step++;
    setTimeout(rampInterval, interval, interval, increment, steps, step);
  }
}
