var hostname;

(function() {
  'use strict';
  window.addEventListener('load', async function() {
    hostname = document.getElementById('hostname').value;
    initControlPanel();
  }, false);
})();

function initControlPanel(){

  // reset button listener
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

  document.getElementById(`loop-delay-range`).addEventListener('input', (e) => {
    console.log(`setLoopDelay: ${parseFloat(e.target.value)}`);
    setLoopDelay(parseFloat(e.target.value));
  });

  document.getElementById(`start-loop`).addEventListener('click', (e) => {
    startLoop();
  });

  document.getElementById(`stop-loop`).addEventListener('click', (e) => {
    stopLoop();
  });

  document.getElementById(`set-lfsr-button`).addEventListener('click', (e) => {
    setLFSR();
  });

  document.getElementById(`clear-lfsr-button`).addEventListener('click', (e) => {
    clearLFSR();
  });

  document.getElementById(`flip-lfsr-button`).addEventListener('click', (e) => {
    flipDirection();
    setLFSR();
  });

  document.getElementById(`set-strobe-button`).addEventListener('click', (e) => {
    setStrobe();
  });

  document.getElementById(`strobe-enable`).addEventListener('click', (e) => {
    console.log(`e.target.checked: ${e.target.checked}`);
    enableStrobe(e.target.checked);
  });

  document.getElementById('delay-inc-button').addEventListener('click', (e) => {
    nudgeDelayAmount(parseFloat(document.getElementById('nudge-amount').value)*0.01);
  });

  document.getElementById('delay-dec-button').addEventListener('click', (e) => {
    nudgeDelayAmount(-parseFloat(document.getElementById('nudge-amount').value)*0.01);
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
    'state':[],
    'update': document.getElementById(`register-update`).checked
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
      console.log(result);
    }
  });
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

function enableLFSR(){
  let data = {};
  data.type='set';
  data.target='lfsr_enabled';
  
  updateController(data);
}

function enableLFSR(){
  let data = {};
  data.type='set';
  data.target='lfsr_disabled';
  
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
  console.log(data);
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

function clearStrobe(){
  let data = {};
  data.type='clear';
  data.target='strobe';

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
