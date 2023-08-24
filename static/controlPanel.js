var hostname;

(function() {
  'use strict';
  window.addEventListener('load', async function() {
    hostname = document.getElementById('hostname').value;
    initControlPanel();
  }, false);
})();

function initControlPanel(){

  document.getElementById(`register-reset-button`).addEventListener('click', (e) => {
    resetRegisterControls();
    setRegister();
  });

  document.getElementById(`register-invert-button`).addEventListener('click', (e) => {
    invertRegisterControls();
    setRegister();
  });

  document.getElementById(`register-randomize-button`).addEventListener('click', (e) => {
    randomizeRegisterControls();
    setRegister();
  });

  document.getElementById(`register-set-button`).addEventListener('click', (e) => {
    setRegister();
  });

  for(let i = 0; i < 8; i++){
    document.getElementById(`register-bit-${i}`).addEventListener('change',(e) => {
      setRegister();
    });
  }

  document.getElementById(`loop-delay-range`).addEventListener('input', (e) => {
    let delay_elem = document.getElementById(`loop-delay-value`);
    delay_elem.value = e.target.value;
    delay_elem.dispatchEvent(new Event('input'));
  });

  document.getElementById(`loop-delay-value`).addEventListener('input', (e) =>{
    document.getElementById(`loop-delay-range`).value = e.target.value;
    setLoopDelay(parseFloat(e.target.value));
  });

  document.getElementById(`run-loop`).addEventListener('change', (e) => {
    if(e.target.checked){
      startLoop();
    } else {
      stopLoop();
    }
  });

  document.getElementById(`lfsr-enable`).addEventListener('click', (e) => {
    enableLFSR(e.target.checked);
  });

  document.getElementById(`flip-lfsr-button`).addEventListener('click', (e) => {
    flipDirection();
    setLFSR();
  });

  document.getElementById(`set-strobe-button`).addEventListener('click', (e) => {
    setStrobe();
  });

  document.getElementById(`strobe-live`).addEventListener('change', (e) => {
    if(e.target.checked){
      document.getElementById(`set-strobe-button`).disabled=true;
    } else {
      document.getElementById(`set-strobe-button`).disabled=false;
    }
  });

  document.getElementById('invert-on-count').addEventListener('change', (e) => {
    if(document.getElementById(`strobe-live`).checked){
      setStrobe();
    }
  });
  document.getElementById('invert-off-count').addEventListener('change', (e) => {
    if(document.getElementById(`strobe-live`).checked){
      setStrobe();
    }
  });
  document.getElementById('mute-on-count').addEventListener('change', (e) => {
    if(document.getElementById(`strobe-live`).checked){
      setStrobe();
    }
  });
  document.getElementById('mute-off-count').addEventListener('change', (e) => {
    if(document.getElementById(`strobe-live`).checked){
      setStrobe();
    }
  });

  document.getElementById('strobe-invert-enable').addEventListener('change', (e) => {
    setStrobe();
  });

  document.getElementById('strobe-mute-enable').addEventListener('change', (e) => {
    setStrobe();
  });

  document.getElementById(`strobe-enable`).addEventListener('click', (e) => {
    enableStrobe(e.target.checked);
  });

  document.getElementById('delay-inc-button').addEventListener('click', (e) => {
    nudgeDelayAmount(parseFloat(document.getElementById('nudge-amount').value)*0.01);
  });

  document.getElementById('delay-dec-button').addEventListener('click', (e) => {
    nudgeDelayAmount(-parseFloat(document.getElementById('nudge-amount').value)*0.01);
  });

  //configures the refreshing of the LFSR settings in real-time
  for(let i = 1; i <= 3; i++){
    document.getElementById(`tap-${i}-enable`).addEventListener('change', (e) => {
      setLFSR();
    });
    document.getElementById(`tap-${i}-value`).addEventListener('change', (e) => {
      let en = document.getElementById(`tap-${i}-enable`);
      if(en.checked){
        setLFSR();
      }
    });
    document.getElementById(`tap-${i}-randomize-button`).addEventListener('click', (e) => {
      let q = document.getElementById(`tap-${i}-value`);
      q.value = Math.floor(8 * Math.random());
      q.dispatchEvent(new Event('change'));
    });
  }
  document.getElementById('mod-enable').addEventListener('change', (e) => {
    setLFSR();
  });
  document.getElementById('mod-source-select').addEventListener('change', (e) => {
    if(document.getElementById('mod-enable').checked){
      setLFSR();
    }
  });
  document.getElementById('mod-value').addEventListener('change', (e) => {
    if(document.getElementById('mod-enable').checked){
      setLFSR();
    }
  });
  document.getElementById(`mod-randomize-button`).addEventListener('click', (e) => {
    let q = document.getElementById(`mod-value`);
    q.value = Math.floor(8 * Math.random());
    let sel = document.getElementById(`mod-source-select`);
    sel.options.selectedIndex = Math.floor(7 * Math.random());
    if(document.getElementById('mod-enable').checked){
      setLFSR();
    }
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

function setRegister() {
  let data = {};
  data.type='set';
  data.target='register';
  data.parameters={
    'state':[]
  };

  for(let i=0;i<8;i++){
    data.parameters.state.push(document.getElementById(`register-bit-${i}`).checked ? 1 : 0);
  }

  updateController(data);
}

function updateController(data){
  fetch(`http://${hostname}.local`, {
    method:'POST',
    body:JSON.stringify(data)
  })
  .then((response) => {
    if(response.ok){
      return response.json();
    } else {
      return null
    }
  })
  .then((result) => {
    if(result){
      // console.log(result);
    }
  })
  .catch((error) => console.error(error));
}

function setLoopDelay(delay){
  let data = {};
  data.type='set';
  data.target='loop_delay';
  data.parameters={
    'value' : delay
  };

  updateController(data);
}

function multLoopDelay(value){
  let data = {};
  data.type='set';
  data.target='mult_loop_delay';
  data.parameters={
    'value' : value
  };

  updateController(data);
}

function divLoopDelay(value){
  let data = {};
  data.type='set';
  data.target='div_loop_delay';
  data.parameters={
    'value' : value
  };

  updateController(data);
}

function startLoop(){
  let data = {};
  data.type='set';
  data.target='loop';
  data.parameters={
    'retrigger' : true
  };

  updateController(data);
}

function stopLoop(){
  let data = {};
  data.type='set';
  data.target='loop';
  data.parameters={
    'retrigger' : false
  };

  updateController(data);
}

function enableLFSR(value){
  let data = {};
  data.type='set';
  if(value){
    data.target='lfsr_enabled';
  }else{
    data.target='lfsr_disabled';
  }
  
  updateController(data);
}

function setLFSR(){
  let data = {};
  data.type='set';
  data.target='lfsr';
  data.parameters={
    'taps' : [],
    'modQ' : parseInt(document.getElementById(`mod-value`).value),
    'modEnabled' : document.getElementById('mod-enable').checked,
    'modSource' : null,
    'direction' : 'left'
  };
  for(let i = 1; i <= 3;i++){
    if(document.getElementById(`tap-${i}-enable`).checked){
      data.parameters.taps.push(parseInt(document.getElementById(`tap-${i}-value`).value));
    }
  }
  const directions = document.getElementById('direction-select').options
  data.parameters.direction = directions[directions.selectedIndex].value;
  const sources = document.getElementById('mod-source-select').options
  data.parameters.modSource = parseInt(sources[sources.selectedIndex].value);

  updateController(data);
}

function setStrobe(){
  let data = {};
  data.type='set';
  data.target='strobe';
  data.parameters={
    'invert_enabled': document.getElementById('strobe-invert-enable').checked,
    'invert_on': parseInt(document.getElementById('invert-on-count').value),
    'invert_off': parseInt(document.getElementById('invert-off-count').value),
    'mute_enabled': document.getElementById('strobe-mute-enable').checked,
    'mute_on': parseInt(document.getElementById('mute-on-count').value),
    'mute_off': parseInt(document.getElementById('mute-off-count').value)
  };
  updateController(data);
}

function enableStrobe(value){
  let data = {};
  data.type='set';
  if(value){
    data.target='strobe_enabled';
  }else{
    data.target='strobe_disabled';
  }

  updateController(data);
}

function nudgeDelayAmount(value){
  let data = {};
  data.type='set';
  data.target='nudge_delay';
  data.parameters={'value':value};

  updateController(data);
}

function setTempo(value){
  let tempo = parseFloat(document.getElementById('tempo-base').value);
  let data = {};
  data.type='set';
  data.target='tempo';
  data.parameters={
    'value': value * ( 60 / tempo )
  };

  updateController(data);
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
      }
    } else {
      range.value = parseFloat(range.value) + increment;
    }
    range.dispatchEvent(new Event('input'));
    step++;
    setTimeout(rampInterval, interval, interval, increment, steps, step);
  }
}
